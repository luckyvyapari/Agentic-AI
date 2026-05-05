import os
import subprocess
from typing import TypedDict, Annotated, List, Dict, Optional
from operator import add
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import interrupt
from langchain_core.runnables import RunnableConfig
from logger import log_event, init_db

# Initialize DB on start
init_db()

# Configuration
folder = "deployed_apps"

# Define the State
class State(TypedDict):
    request: str
    code: str
    feedback: Optional[str]
    tests: Optional[str]
    test_results: Optional[str]
    approved: bool
    file_name: str
    logs: Annotated[List[str], add]
    iteration: int

# Initialize LLM
llm = ChatOllama(model="llama3.2", temperature=0)

def coder_node(state: State, config: RunnableConfig = None):
    """Generates Python code based on the request."""
    print("--- NODES: CODER ---")
    thread_id = config.get("configurable", {}).get("thread_id", "unknown") if config else "unknown"
    
    iteration = state.get("iteration", 0) + 1
    
    prompt = f"""You are an expert Python developer. 
    User Request: {state['request']}
    
    Previous Feedback (if any): {state.get('feedback', 'None')}
    Current Code (if any): {state.get('code', 'None')}
    Test Results (if any): {state.get('test_results', 'None')}
    
    Generate professional, clean, and documented Python code. 
    Only return the code block. No explanations.
    """
    
    response = llm.invoke([SystemMessage(content="Return only Python code."), HumanMessage(content=prompt)])
    code = response.content.replace("```python", "").replace("```", "").strip()
    
    log_event(thread_id, "CODER", iteration, "Success", {"code": code})
    
    return {
        "code": code,
        "iteration": iteration,
        "logs": ["Code generated/updated by Coder."]
    }

def critic_node(state: State, config: RunnableConfig = None):
    """Review the code for issues."""
    print("--- NODES: CRITIC ---")
    thread_id = config.get("configurable", {}).get("thread_id", "unknown") if config else "unknown"
    iteration = state.get("iteration", 0)
    
    prompt = f"""You are a Senior Architect. Review the following code for bugs, PEP8 compliance, and logical errors.
    
    CODE:
    {state['code']}
    
    If the code is good, respond with 'GOOD'. 
    If there are issues, provide concise feedback.
    """
    
    response = llm.invoke([SystemMessage(content="Return 'GOOD' or concise feedback."), HumanMessage(content=prompt)])
    critic_feedback = response.content.strip()
    
    log_event(thread_id, "CRITIC", iteration, "Feedback Provided", {"feedback": critic_feedback})
    
    if "GOOD" in critic_feedback.upper() and len(critic_feedback) < 10:
        return {
            "approved": True,
            "feedback": None,
            "logs": ["Critic gave a thumbs up."]
        }
    else:
        return {
            "approved": False,
            "feedback": critic_feedback,
            "logs": [f"Critic identified issues: {critic_feedback}"]
        }

def human_review_node(state: State, config: RunnableConfig = None):
    """Interrupts the graph for human review."""
    print("--- NODES: HUMAN REVIEW ---")
    thread_id = config.get("configurable", {}).get("thread_id", "unknown") if config else "unknown"
    iteration = state.get("iteration", 0)
    
    log_event(thread_id, "HUMAN_REVIEW", iteration, "Awaiting Input", {"code": state['code']})
    
    # The interrupt returns whatever is passed to Command(resume=...)
    human_input = interrupt({
        "task": "Review the generated code",
        "code": state['code'],
        "request": state['request'],
        "critic_feedback": state.get("feedback")
    })
    
    # Process input
    if isinstance(human_input, dict):
        action = human_input.get("action", "feedback")
        code = human_input.get("code", state["code"])
        feedback = human_input.get("feedback", "")
    else:
        # Fallback for CLI/string input
        action = "approve" if str(human_input).lower().startswith("approve") else "feedback"
        code = state["code"]
        feedback = str(human_input)

    status = "Approved" if action == "approve" else "Changes Requested"
    log_event(thread_id, "HUMAN_REVIEW", iteration, status, {"feedback": feedback})
    
    return {
        "code": code,
        "approved": (action == "approve"),
        "feedback": feedback if action != "approve" else None,
        "logs": [f"Human decision: {status}"]
    }

def tester_node(state: State, config: RunnableConfig = None):
    """Generates and executes unit tests."""
    print("--- NODES: TESTER ---")
    thread_id = config.get("configurable", {}).get("thread_id", "unknown") if config else "unknown"
    iteration = state.get("iteration", 0)
    prompt = f"""You are a QA Engineer. Generate comprehensive unit tests for the following Python code:
    {state['code']}
    Use the `unittest` framework. Return only the code block. No explanations.
    """
    
    response = llm.invoke([SystemMessage(content="Return only Python unit tests."), HumanMessage(content=prompt)])
    tests = response.content.replace("```python", "").replace("```", "").strip()
    
    # 2. Execute Tests
    tmp_code = "tmp_app.py"
    tmp_test = "tmp_test.py"
    
    with open(tmp_code, "w") as f: f.write(state['code'])
    with open(tmp_test, "w") as f: f.write(tests)
    
    result = subprocess.run(["python3", tmp_test], capture_output=True, text=True)
    
    # Cleanup
    if os.path.exists(tmp_code): os.remove(tmp_code)
    if os.path.exists(tmp_test): os.remove(tmp_test)
    
    success = result.returncode == 0
    test_log = "Tests passed! ✅" if success else f"Tests failed! ❌\n{result.stderr}"
    
    log_event(thread_id, "TESTER", iteration, "Passed" if success else "Failed", {"results": test_log})
    
    return {
        "tests": tests,
        "test_results": test_log,
        "approved": success,
        "logs": [f"Unit tests executed: {'Passed' if success else 'Failed'}"]
    }

def deployer_node(state: State, config: RunnableConfig = None):
    """Saves the final code and tests to a folder."""
    print("--- NODES: DEPLOYER ---")
    thread_id = config.get("configurable", {}).get("thread_id", "unknown") if config else "unknown"
    iteration = state.get("iteration", 0)
    os.makedirs(folder, exist_ok=True)
    
    # Save Code
    file_path = os.path.join(folder, f"{state['file_name']}.py")
    with open(file_path, "w") as f:
        f.write(state['code'])
        
    # Save Tests
    test_path = os.path.join(folder, f"test_{state['file_name']}.py")
    with open(test_path, "w") as f:
        f.write(state['tests'])
        
    log_event(thread_id, "DEPLOYER", iteration, "Completed", {"folder": folder})
    
    return {
        "logs": state.get("logs", []) + [f"System deployed to /{folder}"]
    }

def decide_next_step(state: State):
    """Routes based on approval status and iteration count."""
    if state["approved"]:
        return "tester"
    
    if state.get("iteration", 0) >= 5:
        return "human_review" # Force human intervention if stuck
    return "coder"

def after_critic_logic(state: State):
    if state["approved"]:
        return "human_review"
    return "coder"

def after_tester_logic(state: State):
    if state["approved"]:
        return "deployer"
    
    if state.get("iteration", 0) >= 5:
        return END # Stop if we can't fix it after 5 tries
    return "coder"

# Build Graph
workflow = StateGraph(State)

workflow.add_node("coder", coder_node)
workflow.add_node("critic", critic_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("tester", tester_node)
workflow.add_node("deployer", deployer_node)

workflow.set_entry_point("coder")

workflow.add_edge("coder", "critic")

workflow.add_conditional_edges(
    "critic",
    after_critic_logic,
    {
        "human_review": "human_review",
        "coder": "coder"
    }
)

workflow.add_conditional_edges(
    "human_review",
    decide_next_step,
    {
        "tester": "tester",
        "coder": "coder"
    }
)

workflow.add_conditional_edges(
    "tester",
    after_tester_logic,
    {
        "deployer": "deployer",
        "coder": "coder",
        END: END
    }
)

workflow.add_edge("deployer", END)

# Compile with Checkpointer
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
