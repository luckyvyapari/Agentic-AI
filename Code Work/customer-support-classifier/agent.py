import os
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from IPython.display import Image, display

load_dotenv()

# Define State
class AgentState(TypedDict):
    message: str
    priority: Literal["Urgent", "Standard", "Spam"]
    category: str
    status: str
    email_draft: str

# Initialize LLM
llm = ChatOllama(model="llama3.2", temperature=0)

# Nodes
def categorize_node(state: AgentState):
    """LLM reads message, assigns priority and category."""
    prompt = ChatPromptTemplate.from_template(
        "Analyze the following customer support ticket:\n\n"
        "Ticket: {message}\n\n"
        "Assign a priority (Urgent, Standard, Spam) and a category (e.g., Technical, Billing, Security, General).\n"
        "Return the result in the format:\n"
        "PRIORITY: [Priority]\n"
        "CATEGORY: [Category]"
    )
    
    chain = prompt | llm
    response = chain.invoke({"message": state["message"]})
    content = response.content
    
    priority = "Standard"
    if "PRIORITY: Urgent" in content:
        priority = "Urgent"
    elif "PRIORITY: Spam" in content:
        priority = "Spam"
        
    category = content.split("CATEGORY: ")[1].strip().split("\n")[0] if "CATEGORY: " in content else "General"
    # Keep it concise
    category = category.split(".")[0].strip()
    
    return {
        "priority": priority,
        "category": category,
        "status": "categorized"
    }

def handle_urgent(state: AgentState):
    """Drafts escalation email for security/senior team."""
    prompt = ChatPromptTemplate.from_template(
        "Draft an URGENT escalation email for the senior technical team regarding this ticket:\n\n"
        "Category: {category}\n"
        "Message: {message}\n\n"
        "Include the priority and a brief summary of why it's urgent."
    )
    chain = prompt | llm
    response = chain.invoke({"category": state["category"], "message": state["message"]})
    
    return {
        "email_draft": response.content,
        "status": "escalated"
    }

def handle_standard(state: AgentState):
    """Drafts polite customer reply."""
    prompt = ChatPromptTemplate.from_template(
        "Draft a polite customer support response for this ticket:\n\n"
        "Category: {category}\n"
        "Message: {message}\n\n"
        "Provide a helpful and professional tone."
    )
    chain = prompt | llm
    response = chain.invoke({"category": state["category"], "message": state["message"]})
    
    return {
        "email_draft": response.content,
        "status": "replied"
    }

def handle_spam(state: AgentState):
    """Updates status to archived, no email sent."""
    return {
        "email_draft": "N/A (Spam Filtered)",
        "status": "archived"
    }

# Conditional Routing Function
def route_by_priority(state: AgentState):
    priority = state["priority"]
    if priority == "Urgent":
        return "urgent"
    elif priority == "Spam":
        return "spam"
    else:
        return "standard"

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("categorize", categorize_node)
builder.add_node("handle_urgent", handle_urgent)
builder.add_node("handle_standard", handle_standard)
builder.add_node("handle_spam", handle_spam)

builder.set_entry_point("categorize")

builder.add_conditional_edges(
    "categorize",
    route_by_priority,
    {
        "urgent": "handle_urgent",
        "standard": "handle_standard",
        "spam": "handle_spam"
    }
)

builder.add_edge("handle_urgent", END)
builder.add_edge("handle_standard", END)
builder.add_edge("handle_spam", END)

# Compile Graph
graph = builder.compile()

def get_graph_image():
    return graph.get_graph().draw_mermaid_png()

if __name__ == "__main__":
    # Test Run
    test_message = "The production database is down! We are losing money!"
    initial_state = {"message": test_message}
    result = graph.invoke(initial_state)
    print(f"Priority: {result['priority']}")
    print(f"Status: {result['status']}")
    print(f"Draft:\n{result['email_draft']}")
