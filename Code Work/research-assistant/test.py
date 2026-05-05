import os
import uuid
from dotenv import load_dotenv
from agent import graph
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
import time

load_dotenv()

console = Console()

def run_test():
    console.clear()
    console.print(Panel("[bold blue]Multi-Agent Research Assistant - Integration Test[/bold blue]\n[italic]Testing Human-in-the-Loop & Multi-Agent Orchestration[/italic]", border_style="blue", title="Setup"))

    # Check for Tavily API Key
    if not os.getenv("TAVILY_API_KEY"):
        console.print("[bold red]Error:[/bold red] TAVILY_API_KEY not found in .env file.")
        return

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    question = "The impact of Ai in jobs"
    
    console.print(f"\n[bold green]>>[/bold green] [bold]Research Topic:[/bold] {question}")
    
    # 1. Start the process
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Searching and writing initial draft...", total=None)
        
        # This will run until it hits the interrupt_before=['human_review']
        for event in graph.stream({"question": question}, config=config, stream_mode="values"):
            pass
            
    # 2. Get current state (Interrupted)
    state = graph.get_state(config)
    state_values = state.values
    # 3. Handle Human Review
    while True:
        state = graph.get_state(config)
        
        # If the graph is interrupted at human_review
        if state.next and "human_review" in state.next:
            current_state = state.values
            draft = current_state.get("draft_report", "")
            critic_feedback = current_state.get("critic_feedback", "")
            score = current_state.get("critic_score", 0)

            console.print(Panel(draft[:1000] + "...", title="Draft Report Preview (First 1000 chars)", border_style="yellow"))
            console.print(Panel(f"Score: {score}/10\n\n{critic_feedback}", title="Critic Feedback", border_style="cyan"))
            
            console.print("\n[bold yellow]⚠ GRAPH INTERRUPTED: Awaiting Human Review[/bold yellow]")
            action = Prompt.ask("Do you [bold green]approve[/bold green] this report? (y/n)", choices=["y", "n"])
            
            if action == "y":
                feedback = Prompt.ask("Any final remarks? (Optional)", default="Looks great!")
                graph.update_state(config, {"approved": True, "human_feedback": feedback}, as_node="human_review")
            else:
                feedback = Prompt.ask("[bold red]What should be improved?[/bold red]")
                graph.update_state(config, {"approved": False, "human_feedback": feedback}, as_node="human_review")
            
            # Resume
            for event in graph.stream(None, config, stream_mode="values"):
                pass
        else:
            break

    # 4. Final Output
    final_state = graph.get_state(config).values
    
    console.print("\n", Panel("[bold green]Test Complete![/bold green] You can open [bold]research_report.pdf[/bold] to see the output.", border_style="green"))
    
    # Summary Table
    table = Table(title="Execution Summary", show_header=True, header_style="bold magenta")
    table.add_column("Property", style="dim")
    table.add_column("Value")
    
    table.add_row("Final Status", "Approved & Completed" if final_state.get("approved") else "Failed")
    table.add_row("PDF Generated", final_state.get("final_report", "N/A"))
    table.add_row("Critic Final Score", str(final_state.get("critic_score", "N/A")))
    table.add_row("Total Revisions", str(final_state.get("revision_count", 1)))
    
    console.print(table)

if __name__ == "__main__":
    run_test()
