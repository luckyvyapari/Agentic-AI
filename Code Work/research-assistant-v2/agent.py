import os
from typing import TypedDict, List, Annotated, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from langchain_ollama import ChatOllama
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
llm = ChatOllama(model="llama3.2", temperature=0)
search_tool = TavilySearch(max_results=5)

# --- Nodes using Command for routing ---

def search_node(state: State) -> Command[Literal["writer"]]:
    print("\n>> [NODE: search] Gathering information...")
    question = state["question"]
    results = search_tool.invoke({"query": question})
    search_context = [res["content"] for res in results.get("results", [])]
    
    return Command(
        update={"search_results": search_context},
        goto="writer"
    )

def writer_node(state: State) -> Command[Literal["critic"]]:
    print("\n>> [NODE: writer] Drafting report...")
    question = state["question"]
    search_results = "\n\n".join(state["search_results"])
    
    prompt = f"""You are a research assistant. Write a structured report on: {question}
    Research Results: {search_results}"""
    
    response = llm.invoke([SystemMessage(content="Expert technical writer."), HumanMessage(content=prompt)])
    
    return Command(
        update={"draft_report": response.content, "revision_count": 1},
        goto="critic"
    )

def critic_node(state: State) -> Command[Literal["revise", "human_review"]]:
    print("\n>> [NODE: critic] Scoring report...")
    draft = state["draft_report"]
    rev_count = state.get("revision_count", 0)
    
    prompt = f"""Review the following research report. 
Score it from 1 to 10 (where 10 is perfect) and provide bullet-point feedback for improvement.

Report:
{draft}

Format your response EXACTLY like this:
SCORE: [number]
FEEDBACK: [points]"""

    response = llm.invoke([
        SystemMessage(content="You are a strict academic editor. You must provide a numerical score."), 
        HumanMessage(content=prompt)
    ])
    content = response.content
    
    # Improved parsing
    import re
    score_match = re.search(r"SCORE:\s*(\d+)", content, re.IGNORECASE)
    if score_match:
        score = int(score_match.group(1))
    else:
        score = 5 # fallback
        
    print(f"   [Critic Score: {score}/10]")
    
    # Routing Logic
    if score >= 8 or rev_count >= 3:
        next_step = "human_review"
    else:
        next_step = "revise"
        
    return Command(
        update={"critic_score": score, "critic_feedback": content},
        goto=next_step
    )

def revise_node(state: State) -> Command[Literal["critic"]]:
    current_rev = state.get("revision_count", 1)
    print(f"\n>> [NODE: revise] Revision #{current_rev + 1}...")
    
    prompt = f"Revise report based on:\nCritic: {state.get('critic_feedback')}\nHuman: {state.get('human_feedback')}\nDraft: {state['draft_report']}"
    response = llm.invoke([SystemMessage(content="Meticulous editor."), HumanMessage(content=prompt)])
    
    return Command(
        update={"draft_report": response.content, "revision_count": current_rev + 1},
        goto="critic"
    )

def human_review_node(state: State) -> Command[Literal["pdf_generator", "revise"]]:
    print("\n>> [NODE: human_review] Interrupting for human feedback...")
    
    # The new latest way: use interrupt() to pause and get input
    # This will pause the graph and return the value provided in the next resume() call
    human_input = interrupt({
        "question": "Please review the draft and feedback.",
        "draft": state["draft_report"],
        "critic_score": state["critic_score"],
        "critic_feedback": state["critic_feedback"]
    })
    
    # human_input is expected to be a dict: {"approved": bool, "feedback": str}
    approved = human_input.get("approved", False)
    feedback = human_input.get("feedback", "")
    
    if approved:
        return Command(
            update={"approved": True, "human_feedback": feedback},
            goto="pdf_generator"
        )
    else:
        return Command(
            update={"approved": False, "human_feedback": feedback},
            goto="revise"
        )

def pdf_node(state: State):
    print("\n>> [NODE: pdf_generator] Creating PDF...")
    # (PDF generation logic stays similar)
    filename = "research_report_v2.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("Research Report (Command Pattern)", styles['Title']), Spacer(1, 12)]
    for line in state["draft_report"].split('\n'):
        if line.strip(): story.append(Paragraph(line, styles['BodyText']))
    doc.build(story)
    
    return {"final_report": filename, "approved": True}

# Build Graph - Notice how simplified this becomes!
workflow = StateGraph(State)

# We just add the nodes. The routing is handled INSIDE the nodes via Command.
workflow.add_node("search", search_node)
workflow.add_node("writer", writer_node)
workflow.add_node("critic", critic_node)
workflow.add_node("revise", revise_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("pdf_generator", pdf_node)

# We only need the START edge. Every other transition is handled by Command(goto=...)
workflow.add_edge(START, "search")
workflow.add_edge("pdf_generator", END)

# Checkpointer for interrupt support
memory = MemorySaver()

# Compile - No need for interrupt_before anymore! 
# The interrupt() call inside human_review_node handles it dynamically.
graph = workflow.compile(checkpointer=memory)
