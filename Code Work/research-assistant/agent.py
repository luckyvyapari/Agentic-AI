import os
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import operator

load_dotenv()

# Define State
class State(TypedDict):
    question: str
    search_results: List[str]
    draft_report: str
    critic_score: int
    critic_feedback: str
    human_feedback: str
    final_report: str
    approved: bool
    revision_count: int

# Initialize Tools and LLMs
# Using Ollama llama3.2 as requested
llm = ChatOllama(model="llama3.2", temperature=0)
search_tool = TavilySearch(max_results=5)

# Nodes
def search_node(state: State):
    print("\n>> [NODE: search] Gathering information from the web...")
    question = state["question"]
    results = search_tool.invoke({"query": question})
    search_context = [res["content"] for res in results.get("results", [])]
    return {"search_results": search_context}

def writer_node(state: State):
    print("\n>> [NODE: writer] Writing initial research report...")
    question = state["question"]
    search_results = "\n\n".join(state["search_results"])
    
    prompt = f"""You are a research assistant. Based on the following research results, write a comprehensive, structured report on: {question}

Research Results:
{search_results}

The report should have:
1. Executive Summary
2. Key Findings
3. Detailed Analysis
4. Sources/References"""

    messages = [
        SystemMessage(content="You are an expert technical writer."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    return {"draft_report": response.content, "revision_count": 1}

def revise_node(state: State):
    current_rev = state.get("revision_count", 1)
    print(f"\n>> [NODE: revise] Improving report (Revision #{current_rev + 1})...")
    
    question = state["question"]
    draft = state["draft_report"]
    critic_feedback = state.get("critic_feedback", "None")
    human_feedback = state.get("human_feedback", "None")
    
    prompt = f"""Revise the research report on: {question}

Current Draft:
{draft}

Critic Feedback to address:
{critic_feedback}

Human Feedback to address:
{human_feedback}

Please provide an improved version of the report, addressing all feedback points."""

    messages = [
        SystemMessage(content="You are a meticulous technical editor."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    return {
        "draft_report": response.content, 
        "revision_count": current_rev + 1
    }

def critic_node(state: State):
    print("\n>> [NODE: critic] Reviewing and scoring the report...")
    draft = state["draft_report"]
    
    prompt = f"""Review the following research report. Score it from 1 to 10 (where 10 is perfect) and provide bullet-point feedback for improvement.
    
Report:
{draft}

Format your response exactly like this:
SCORE: [1-10]
FEEDBACK: [Bullet points]"""

    messages = [
        SystemMessage(content="You are a strict academic editor."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    content = response.content
    
    # Parse score and feedback
    try:
        score_line = [l for l in content.split("\n") if "SCORE:" in l][0]
        score = int(score_line.split(":")[1].strip())
    except:
        score = 5 # fallback
        
    return {"critic_score": score, "critic_feedback": content}

def human_review_node(state: State):
    # This node is essentially a placeholder for where the interrupt happens.
    # In a real app, the state is modified by the human through the checkpointer.
    print("\n>> [NODE: human_review] Waiting for human approval...")
    return state

def pdf_node(state: State):
    print("\n>> [NODE: pdf_generator] Generating premium PDF report...")
    report_content = state["draft_report"]
    filename = "research_report.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add Title
    story.append(Paragraph("Research Report", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Simple logic to handle common headers and body text
    lines = report_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('###'):
            story.append(Paragraph(line.replace('#', '').strip(), styles['Heading3']))
        elif line.startswith('##'):
            story.append(Paragraph(line.replace('#', '').strip(), styles['Heading2']))
        elif line.startswith('#'):
            story.append(Paragraph(line.replace('#', '').strip(), styles['Heading1']))
        elif line.startswith('**') or line.startswith('* '):
            # Basic bullet/bold support
            story.append(Paragraph(line, styles['BodyText']))
        else:
            story.append(Paragraph(line, styles['BodyText']))
            
        story.append(Spacer(1, 6))
    
    doc.build(story)
    
    return {"final_report": filename, "approved": True}

# Edges and Logic
def after_critic_logic(state: State):
    score = state["critic_score"]
    rev_count = state.get("revision_count", 0)
    
    # If score is good OR we've revised too many times, go to human
    if score >= 8 or rev_count >= 3:
        return "human_review"
    else:
        return "revise"

def after_human_logic(state: State):
    if state.get("approved", False):
        return "pdf_generator"
    else:
        return "revise"

# Build Graph
workflow = StateGraph(State)

workflow.add_node("search", search_node)
workflow.add_node("writer", writer_node)
workflow.add_node("revise", revise_node)
workflow.add_node("critic", critic_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("pdf_generator", pdf_node)

workflow.add_edge(START, "search")
workflow.add_edge("search", "writer")
workflow.add_edge("writer", "critic")
workflow.add_edge("revise", "critic")

workflow.add_conditional_edges(
    "critic",
    after_critic_logic,
    {
        "human_review": "human_review",
        "revise": "revise"
    }
)

workflow.add_conditional_edges(
    "human_review",
    after_human_logic,
    {
        "pdf_generator": "pdf_generator",
        "revise": "revise"
    }
)

workflow.add_edge("pdf_generator", END)

# Checkpointer
memory = MemorySaver()

# Compile with interrupt
graph = workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]
)
