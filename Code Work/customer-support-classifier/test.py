import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from agent import graph

console = Console()

def run_tests():
    test_cases = [
        {
            "id": "TC-001",
            "name": "Urgent Security Issue",
            "message": "URGENT: My account is being hacked! I see unauthorized transactions and I can't log in from my desktop."
        },
        {
            "id": "TC-002",
            "name": "Standard Billing Query",
            "message": "Hi, I was charged twice for my subscription this month. Can you please refund the duplicate charge?"
        },
        {
            "id": "TC-003",
            "name": "Technical Bug Report",
            "message": "The mobile app keeps crashing whenever I try to upload a profile picture. I am using an iPhone 13 with iOS 17."
        },
        {
            "id": "TC-004",
            "name": "General Inquiry",
            "message": "Hello, I am interested in your enterprise plan. Could you send me some pricing information for a team of 50?"
        },
        {
            "id": "TC-005",
            "name": "Spam Ticket",
            "message": "CONGRATULATIONS!!! You have won a $1000 Amazon Gift Card. Click here to claim: http://scam-link.com/free-money"
        }
    ]

    console.print(Panel.fit("[bold blue]Customer Support Classifier - Automated Test Suite[/bold blue]", border_style="blue"))
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        for case in test_cases:
            task_id = progress.add_task(description=f"Testing {case['name']}...", total=1)
            
            start_time = time.time()
            try:
                response = graph.invoke({"message": case["message"]})
                duration = time.time() - start_time
                
                results.append({
                    "id": case["id"],
                    "name": case["name"],
                    "priority": response.get("priority", "N/A"),
                    "category": response.get("category", "N/A"),
                    "status": response.get("status", "N/A"),
                    "time": f"{duration:.2f}s"
                })
            except Exception as e:
                results.append({
                    "id": case["id"],
                    "name": case["name"],
                    "priority": "ERROR",
                    "category": str(e)[:30] + "...",
                    "status": "FAILED",
                    "time": "N/A"
                })
            
            progress.update(task_id, advance=1)

    # Display Results Table
    table = Table(title="[bold]Test Execution Summary[/bold]", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("Test Case")
    table.add_column("Priority")
    table.add_column("Category")
    table.add_column("Status")
    table.add_column("Time")

    for res in results:
        priority_style = "bold red" if res["priority"] == "Urgent" else "bold green" if res["priority"] == "Standard" else "yellow"
        status_style = "bold cyan" if res["status"] == "escalated" else "green" if res["status"] == "replied" else "dim"
        
        table.add_row(
            res["id"],
            res["name"],
            f"[{priority_style}]{res['priority']}[/{priority_style}]",
            res["category"],
            f"[{status_style}]{res['status']}[/{status_style}]",
            res["time"]
        )

    console.print(table)
    console.print("\n[bold green]Tests completed successfully![/bold green]")

if __name__ == "__main__":
    run_tests()
