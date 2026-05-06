import argparse
import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.agent import run_job_application_agent

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Job Application Agent")
    parser.add_argument(
        "--resume",
        required=True,
        help="Absolute path to the candidate resume PDF",
    )
    parser.add_argument(
        "--query",
        required=True,
        help='Example: "Find me Data Analyst jobs in Bangalore and apply my resume."',
    )
    parser.add_argument(
        "--thread-id",
        default="job-application-session",
        help="Session identifier for memory continuity",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    console.print(Panel.fit(f"[bold blue]Job Application Agent[/bold blue]\nQuery: [green]{args.query}[/green]", border_style="blue"))

    with console.status("[bold green]Agent is running pipeline... (This might take a minute)[/bold green]", spinner="dots"):
        result_str = run_job_application_agent(
            user_query=args.query,
            resume_path=args.resume,
            thread_id=args.thread_id,
        )

    try:
        result = json.loads(result_str)
        
        console.print(f"\n[bold cyan]Agent Summary:[/bold cyan]\n{result.get('agent_summary', 'No summary provided')}\n")
        
        table = Table(title="Top Matches Saved", show_header=True, header_style="bold magenta")
        table.add_column("Score", justify="right", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Company", style="yellow")
        
        for match in result.get("top_matches", []):
            table.add_row(
                str(match.get("score", "N/A")),
                match.get("title", ""),
                match.get("company", "")
            )
            
        console.print(table)
        console.print(f"\n[bold]Save Status:[/bold] {result.get('save_status', '')}")

    except json.JSONDecodeError:
        console.print("[bold red]Failed to parse agent output as JSON. Raw output:[/bold red]")
        console.print(result_str)


if __name__ == "__main__":
    main()
