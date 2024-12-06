import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

def parse_history(file_path, start_date=None, end_date=None):
    """
    Parse terminal history file and filter commands by date range.
    """
    commands = []
    full_invocations = []
    pattern = re.compile(r"^: \d+:\d+;")  # Match Zsh history metadata

    with open(file_path, 'rb') as file:
        for line in file:
            # Decode the line, replacing invalid characters
            line = line.decode('utf-8', errors='replace').strip()
            
            # Skip empty lines
            if not line:
                continue

            # Check if Zsh history metadata exists
            if pattern.match(line):
                # Extract timestamp from Zsh history
                parts = line.split(";")
                if len(parts) < 2:
                    continue
                
                timestamp, command = parts[0], parts[1].strip()
                timestamp = int(timestamp.split(":")[1])

                # Convert timestamp to datetime if filtering by date
                if start_date and end_date:
                    command_date = datetime.fromtimestamp(timestamp)
                    if not (start_date <= command_date <= end_date):
                        continue

                # Add the full command
                full_invocations.append(command)
                
                # Extract the base command
                base_command = command.split(" ", 1)[0] if " " in command else command
                commands.append(base_command)

    return commands, full_invocations

def analyze_commands(commands):
    """
    Analyze base command frequency and sort by usage.
    """
    counter = Counter(commands)
    return counter.most_common(10)

def analyze_invocations(full_invocations):
    """
    Analyze full invocation frequency and sort by usage.
    """
    counter = Counter(full_invocations)
    return counter.most_common(10)

def display_table(title, data):
    """
    Display a styled table using Rich.
    """
    table = Table(title=f"[bold magenta]{title}[/bold magenta]", header_style="bold cyan")
    table.add_column("Rank", justify="right")
    table.add_column("Command")
    table.add_column("Count", justify="right")

    for i, (command, count) in enumerate(data, 1):
        table.add_row(str(i), command, str(count))
    
    console.print(table)

def main():
    # Default history file (modify if using different shell)
    history_file = os.path.expanduser("~/.zsh_history")
    
    # Date range for the past year
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    # Check if history file exists
    if not Path(history_file).exists():
        console.print(f"[bold red]Error:[/bold red] History file '{history_file}' not found!")
        return
    
    # Parse history and filter by date range
    console.print(f"[bold yellow]Parsing history from {history_file}...[/bold yellow]")
    commands, full_invocations = parse_history(history_file, start_date=start_date, end_date=end_date)
    
    if not commands:
        console.print("[bold red]No commands found in the specified date range.[/bold red]")
        return
    
    # Analyze total commands used
    total_commands = len(commands)
    console.print(Panel(f"[bold green]🎉 Total Commands Used: {total_commands} 🎉[/bold green]", style="bold magenta"))
    
    # Analyze base commands
    top_commands = analyze_commands(commands)
    console.print("\n[bold underline]Top 10 Base Commands:[/bold underline]")
    display_table("Base Commands", top_commands)
    
    # Analyze full invocations
    top_invocations = analyze_invocations(full_invocations)
    console.print("\n[bold underline]Top 10 Full Command Invocations:[/bold underline]")
    display_table("Full Command Invocations", top_invocations)
    
    # Save results to a file
    output_file = "cli_command_summary.txt"
    with open(output_file, "w") as f:
        f.write(f"Total Commands Used: {total_commands}\n\n")
        
        f.write("Top 10 Base Commands:\n")
        for i, (cmd, count) in enumerate(top_commands, 1):
            f.write(f"{i}. {cmd} - {count} times\n")
        
        f.write("\nTop 10 Full Command Invocations:\n")
        for i, (inv, count) in enumerate(top_invocations, 1):
            f.write(f"{i}. {inv} - {count} times\n")
    
    console.print(f"\n[bold green]Summary saved to {output_file}[/bold green]")

if __name__ == "__main__":
    main()
