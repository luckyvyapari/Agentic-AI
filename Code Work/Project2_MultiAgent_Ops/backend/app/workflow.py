from typing import List, Optional, Annotated, Sequence
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import operator
import json

# Initialize LLM
llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434")

class AgentState(dict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: Annotated[str, lambda x, y: y]
    logs: Annotated[List[dict], operator.add]
    pending_tool_call: Annotated[Optional[dict], lambda x, y: y]
    approved: Annotated[bool, lambda x, y: y]

# --- Agent Nodes ---

def supervisor_node(state: AgentState):
    """The Supervisor decides which agent should act next using the LLM."""
    messages = state.get("messages", [])
    
    # We use a simple prompt to decide routing
    prompt = [
        SystemMessage(content="""You are a workflow supervisor.
        Decide the next step based on the conversation history.
        - If the user wants to know something but facts are not yet gathered, route to 'researcher'.
        - If facts are gathered and an action is needed (like cleanup/delete), route to 'executor'.
        - If the user's request is satisfied or an action was just completed, route to 'FINISH'.
        Respond with ONLY 'researcher', 'executor', or 'FINISH'."""),
        *messages
    ]
    
    response = llm.invoke(prompt)
    decision = response.content.strip().lower()
    
    if "executor" in decision:
        next_agent = "executor"
    elif "researcher" in decision:
        next_agent = "researcher"
    else:
        next_agent = "FINISH"
        
    result = {
        "next": next_agent, 
        "logs": [{"node": "supervisor", "action": f"Routed to {next_agent}"}]
    }
    
    if next_agent == "executor":
        result["pending_tool_call"] = {"tool": "disk_cleanup", "params": {"path": "/var/logs"}}
        
    return result

def researcher_node(state: AgentState):
    # Simulated data gathering
    return {
        "messages": [AIMessage(content="FACTS: Disk usage is currently at 85% with 2.4GB of logs in /var/logs.")],
        "next": "supervisor",
        "logs": [{"node": "researcher", "action": "Gathered system facts"}]
    }

def executor_node(state: AgentState):
    if state.get("approved"):
        return {
            "messages": [AIMessage(content="Action executed: /var/logs cleaned. Disk usage reduced to 40%.")],
            "next": "supervisor",
            "approved": False,
            "pending_tool_call": None,
            "logs": [{"node": "executor", "action": "Executed log cleanup"}]
        }
    
    # Request approval
    return {
        "pending_tool_call": {"tool": "disk_cleanup", "params": {"path": "/var/logs"}},
        "next": "executor",
        "logs": [{"node": "executor", "action": "Paused for human approval"}]
    }

# --- Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("executor", executor_node)

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges(
    "supervisor",
    lambda x: x["next"],
    {
        "researcher": "researcher",
        "executor": "executor",
        "FINISH": END
    }
)

workflow.add_edge("researcher", "supervisor")
workflow.add_edge("executor", "supervisor")

memory = MemorySaver()
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["executor"] 
)
