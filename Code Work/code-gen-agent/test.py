import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from agent import graph

console = Console()

from langgraph.types import Command
import time

def run_interactive_agent():
    # Initial state
    console.print(Panel("[bold cyan]PYTHON CODE GENERATOR AGENT[/bold cyan]\nBuilding Multi-Agent Systems with Human-in-the-Loop", expand=False))
    
    request = input("\nWhat Python program should I write? (e.g., 'a simple calculator'): ")
    file_name = input("Enter a filename for your project (e.g., 'calc'): ")
    
    initial_input = {
        "request": request,
        "file_name": file_name,
        "approved": False,
        "iteration": 0,
        "logs": []
    }
    
    config = {"configurable": {"thread_id": "code_gen_session_" + str(int(time.time()))}}
    
    # Start the graph
    events = graph.stream(initial_input, config, stream_mode="values")
    
    while True:
        # Process events
        last_event = None
        for event in events:
            last_event = event
            if "logs" in event and event["logs"]:
                console.print(f"[bold blue]>>[/bold blue] {event['logs'][-1]}")
        
        # Check state
        state = graph.get_state(config)
        
        # If no next nodes, we are done
        if not state.next:
            console.print("\n" + "="*60)
            console.print(Panel("[bold green]DEPLOYMENT SUCCESSFUL![/bold green]\nFiles are ready in the 'deployed_system' folder.", border_style="green"))
            break
        
        # If we hit an interrupt
        if state.tasks and any(t.interrupts for t in state.tasks):
            interrupt_data = state.tasks[0].interrupts[0].value
            
            console.print(Panel(f"[bold yellow]HUMAN REVIEW REQUIRED[/bold yellow]\nRequest: {interrupt_data['request']}", style="yellow"))
            
            # Show Code
            syntax = Syntax(interrupt_data['code'], "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Generated Code", border_style="blue"))
            
            # Show Critic/Test Feedback
            current_state = state.values
            if "feedback" in current_state and current_state["feedback"]:
                console.print(Panel(current_state["feedback"], title="🔍 Critic Feedback", border_style="yellow"))
            
            if "test_results" in current_state and current_state["test_results"]:
                console.print(Panel(current_state["test_results"], title="🧪 Test Results", border_style="blue"))
            
            # Get User Action
            action = input("\n[bold green]Action:[/bold green] Type 'approve' or provide feedback for changes: ").strip()
            
            if not action:
                console.print("[red]Input cannot be empty.[/red]")
                # We need to restart the loop but stay at the same state
                events = [] 
                continue
            
            # Resume graph with the human input
            events = graph.stream(Command(resume=action), config, stream_mode="values")
        else:
            # If for some reason we are not interrupted but have a next node, just continue streaming
            events = graph.stream(None, config, stream_mode="values")


if __name__ == "__main__":
    run_interactive_agent()
