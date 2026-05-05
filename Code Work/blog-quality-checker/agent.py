from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

class State(TypedDict):
    topic: str
    draft: str
    critic: str
    revision_count: int

# Initialize LLMs
draft_llm = ChatOllama(model="llama3.2", temperature=0.7)
critic_llm = ChatOllama(model="llama3.2", temperature=0.3)

MAX_REVISIONS = 3

def write_draft_node(state: State):
    print("\n>> [NODE: write_draft] Generating initial draft...")
    topic = state["topic"]
    
    messages = [
        SystemMessage(content="You are an expert blog post writer. Write an engaging, well-structured blog post about the given topic. The post should have a catchy title, an introduction, main body paragraphs, and a conclusion."),
        HumanMessage(content=f"Topic: {topic}")
    ]
    
    response = draft_llm.invoke(messages)
    print(">> [NODE: write_draft] Draft generation complete.")
    return {"draft": response.content, "revision_count": state.get("revision_count", 0)}

def critic_node(state: State):
    print("\n>> [NODE: critic] Critiquing draft...")
    draft = state["draft"]
    topic = state["topic"]
    
    messages = [
        SystemMessage(content="You are a strict and detail-oriented blog post editor. Review the draft against the original topic. Provide specific, actionable feedback for improvement. If the draft is excellent and requires no changes, simply respond with 'APPROVE'. Otherwise, list the areas of improvement and end with 'NEEDS IMPROVEMENT'."),
        HumanMessage(content=f"Topic: {topic}\n\nDraft:\n{draft}")
    ]
    
    response = critic_llm.invoke(messages)
    print(">> [NODE: critic] Critique complete.")
    return {"critic": response.content}

def revise_node(state: State):
    print("\n>> [NODE: revise] Revising draft based on critique...")
    draft = state["draft"]
    critic = state["critic"]
    topic = state["topic"]
    revision_count = state.get("revision_count", 0)
    
    messages = [
        SystemMessage(content="You are an expert blog post writer. Revise the blog draft based on the editor's feedback. Ensure the topic is well-covered and all critique points are addressed."),
        HumanMessage(content=f"Topic: {topic}\n\nCurrent Draft:\n{draft}\n\nEditor's Feedback:\n{critic}\n\nPlease provide the updated blog post.")
    ]
    
    response = draft_llm.invoke(messages)
    print(">> [NODE: revise] Revision complete.")
    return {"draft": response.content, "revision_count": revision_count + 1}

def after_critic(state: State):
    critic_output = state["critic"].upper()
    revision_count = state.get("revision_count", 0)
    
    print(f"\n>> [EDGE: after_critic] Evaluating critique (Revision count: {revision_count}/{MAX_REVISIONS})")
    
    if "APPROVE" in critic_output and "NEEDS IMPROVEMENT" not in critic_output:
        print(">> [ROUTING] -> end (Approved)")
        return "end"
    elif revision_count >= MAX_REVISIONS:
        print(">> [ROUTING] -> end (Max Revisions Reached)")
        return "end"
    else:
        print(">> [ROUTING] -> revise (Needs Improvement)")
        return "revise"

# Build the graph
workflow = StateGraph(State)

workflow.add_node("write_draft", write_draft_node)
workflow.add_node("critic", critic_node)
workflow.add_node("revise", revise_node)

workflow.add_edge(START, "write_draft")
workflow.add_edge("write_draft", "critic")
workflow.add_conditional_edges(
    "critic",
    after_critic,
    {
        "revise": "revise",
        "end": END
    }
)
workflow.add_edge("revise", "critic")

# Compile the graph
graph = workflow.compile()
