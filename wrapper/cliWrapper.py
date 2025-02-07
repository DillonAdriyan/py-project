import os
import re
from collections import Counter
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
import pyfiglet

console = Console()

def parse_history(file_path):
    """Parse terminal history file and return a list of commands and full invocations."""
    commands = []
    full_invocations = []
    pattern = re.compile(r"^: \d+:\d+;")  # Match Zsh history metadata

    try:
        with open(file_path, 'rb') as file:
            for line in file:
                try:
                    line = line.decode('utf-8', errors='replace').strip()
                    if not line:
                        continue

                    if pattern.match(line):
                        parts = line.split(";")
                        if len(parts) < 2:
                            continue

                        command = parts[1].strip()
                        full_invocations.append(command)
                        base_command = command.split(" ", 1)[0] if " " in command else command
                        commands.append(base_command)
                except Exception as line_error:
                    console.print(f"[yellow]Warning: Could not process line - {line_error}[/yellow]")

    except IOError as e:
        console.print(f"[bold red]Error reading file: {e}[/bold red]")
        return [], []

    return commands, full_invocations

def analyze_commands(commands, top_n=5):
    """Analyze base command frequency and sort by usage."""
    counter = Counter(commands)
    return counter.most_common(top_n)

def analyze_invocations(full_invocations, top_n=5):
    """Analyze full invocation frequency and sort by usage."""
    counter = Counter(full_invocations)
    return counter.most_common(top_n)

def display_cli_wrapped(commands, invocations, total_commands, font_size="small"):
    """Display the CLI Wrapped output with rich styling and layout."""
    # Generate ASCII art for the year
    ascii_art = pyfiglet.figlet_format("2024", font=font_size)
    console.print(Panel(
        Text(ascii_art, style="bold yellow"),
        title="CLI Wrapped",
        border_style="bold blue"
    ))

    # Create layout for tables
    layout = Layout()
    layout.split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1)
    )

    # Top Commands Table
    table_commands = Table(title="Top Commands", show_lines=True, header_style="bold white")
    table_commands.add_column("#", justify="right", style="bold cyan", width=2)
    table_commands.add_column("Command", style="bold green")
    table_commands.add_column("Count", justify="right", style="bold magenta")
    for i, (cmd, count) in enumerate(commands, 1):
        table_commands.add_row(
            str(i), 
            cmd, 
            str(count)
        )
    
    # Top Invocations Table
    table_invocations = Table(title="Top Invocations", show_lines=True, header_style="bold white")
    table_invocations.add_column("#", justify="right", style="bold cyan", width=2)
    table_invocations.add_column("Invocation", style="bold green")
    table_invocations.add_column("Count", justify="right", style="bold magenta")
    for i, (inv, count) in enumerate(invocations, 1):
        table_invocations.add_row(
            str(i), 
            inv[:50] + ('...' if len(inv) > 50 else ''), 
            str(count)
        )

    # Update layout with panels
    layout["left"].update(Panel(table_commands, border_style="dim"))
    layout["right"].update(Panel(table_invocations, border_style="dim"))

    console.print(layout)

    # Total Commands with styled panel
    commands_ran_text = Text(f"{total_commands:,} Commands", style="bold white")
    commands_ran_ascii = pyfiglet.figlet_format(str(total_commands), font="big")
    console.print(Panel(
        Text(commands_ran_ascii, style="bold yellow"),
        title=commands_ran_text,
        border_style="bold green"
    ))
def main():
    history_file = os.path.expanduser("~/.zsh_history")

    if not Path(history_file).exists():
        console.print(f"[bold red]Error:[/bold red] History file '{history_file}' not found!")
        return

    commands, full_invocations = parse_history(history_file)
    if not commands:
        console.print("[bold red]No commands found.[/bold red]")
        return

    top_commands = analyze_commands(commands)
    top_invocations = analyze_invocations(full_invocations)
    total_commands = len(commands)

    display_cli_wrapped(top_commands, top_invocations, total_commands, font_size="big")

if __name__ == "__main__":
    main()