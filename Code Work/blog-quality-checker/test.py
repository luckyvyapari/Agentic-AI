import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from agent import graph

console = Console()

def run_test():
    topic = "The Future of Artificial Intelligence in Healthcare"
    
    console.print(Panel.fit(
        f"[bold blue]Blog Post Quality Checker - Integration Test[/bold blue]\n[bold white]Topic: {topic}[/bold white]", 
        border_style="blue"
    ))
    
    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=False,
    ) as progress:
        task = progress.add_task(description="Processing Blog Graph (Reflection Pattern)...", total=None)
        
        try:
            # Run the graph
            result = graph.invoke({"topic": topic, "revision_count": 0})
            
            duration = time.time() - start_time
            progress.update(task, description="[bold green]Graph execution complete![/bold green]")
            
            # Summary Table
            table = Table(title="[bold]Workflow Execution Summary[/bold]", show_header=True, header_style="bold magenta")
            table.add_column("Property", style="dim")
            table.add_column("Value")
            
            table.add_row("Topic", result["topic"])
            table.add_row("Revisions", str(result.get("revision_count", 0)))
            table.add_row("Total Time", f"{duration:.2f}s")
            
            console.print("\n")
            console.print(table)
            
            # Show final draft preview
            draft_preview = result["draft"][:500] + "..." if len(result["draft"]) > 500 else result["draft"]
            console.print(Panel(draft_preview, title="[bold green]Final Draft Preview[/bold green]", border_style="green"))
            
            # Show critique preview
            critique_preview = result["critic"][:500] + "..." if len(result["critic"]) > 500 else result["critic"]
            console.print(Panel(critique_preview, title="[bold yellow]Final Editor Feedback[/bold yellow]", border_style="yellow"))
            
        except Exception as e:
            progress.update(task, description=f"[bold red]Error:[/bold red] {str(e)}")
            console.print_exception()

if __name__ == "__main__":
    run_test()
