import uuid
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from langgraph.types import Command
from agent import graph

console = Console()

def run_research():
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    console.print(Panel("[bold blue]Multi-Agent Research Assistant (V2 Command Pattern)[/bold blue]\n[italic]Using latest LangGraph 'Command' and 'interrupt' features[/italic]", expand=False))
    
    question = console.input("[bold green]What do you want me to research? [/bold green]")
    
    # Start the graph
    events = graph.stream({"question": question}, config, stream_mode="values")
    
    while True:
        try:
            for event in events:
                # In latest LangGraph, 'interrupt' state is indicated in the thread state
                pass
            
            # Check if we are at an interrupt
            state = graph.get_state(config)
            
            if state.next:
                # We hit an interrupt or just finished a node and are waiting for the next step?
                # Actually, with interrupt(), state.next will contain the node that called interrupt()
                
                # Check for interrupts specifically
                if state.tasks and any(t.interrupts for t in state.tasks):
                    # We have an interrupt!
                    interrupt_data = state.tasks[0].interrupts[0].value
                    
                    console.print("\n" + "="*50)
                    console.print(Panel(f"[bold yellow]HUMAN REVIEW REQUIRED[/bold yellow]\nNode: {state.next[0]}", style="yellow"))
                    
                    # Display the draft
                    console.print(Panel(Markdown(interrupt_data['draft']), title="[bold]Current Draft Report[/bold]", border_style="blue"))
                    
                    # Display Critic Score/Feedback
                    score_color = "green" if interrupt_data['critic_score'] >= 8 else "red"
                    console.print(Panel(f"Score: [{score_color}]{interrupt_data['critic_score']}/10[/{score_color}]\n\n{interrupt_data['critic_feedback']}", 
                                       title="Critic Feedback", border_style="magenta"))
                    
                    # Ask user for input
                    action = console.input("\n[bold cyan]Options: [a] Approve & Generate PDF, [r] Request Revision (or type feedback): [/bold cyan]").lower()
                    
                    if action == 'a':
                        user_input = {"approved": True, "feedback": "Approved by human."}
                    elif action == 'r':
                        feedback = console.input("[bold yellow]What should be improved? [/bold yellow]")
                        user_input = {"approved": False, "feedback": feedback}
                    else:
                        # Assume anything else is direct feedback for revision
                        user_input = {"approved": False, "feedback": action}
                    
                    # Resume the graph with Command(resume=...)
                    console.print("\n[italic]Resuming graph...[/italic]")
                    events = graph.stream(Command(resume=user_input), config, stream_mode="values")
                    continue # Go back to the top of the loop to process events
                
            # If state.next is empty, it means END
            if not state.next:
                final_state = state.values
                console.print(Panel(f"[bold green]Task Completed![/bold green]\nFinal PDF: [italic]{final_state.get('final_report', 'N/A')}[/italic]", border_style="green"))
                break
            
        except StopIteration:
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            break

if __name__ == "__main__":
    run_research()
