"""Task management commands."""
from datetime import datetime, timezone

import click

from roadmap.storage.db import get_session
from roadmap.storage.models import Mission, Milestone, Step

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:
    from roadmap.cli.display_fallback import Console, Panel, Table

console = Console()


def _find_step_by_prefix(session, prefix: str):
    matches = session.query(Step).filter(Step.id.like(f"{prefix}%")).all()
    if not matches:
        console.print(f"[red]❌ Task {prefix} not found[/red]")
        return None
    if len(matches) > 1:
        console.print(f"[yellow]⚠️ Multiple tasks match '{prefix}'. Specify more characters:[/yellow]")
        for step in matches:
            console.print(f"  - {step.id} {step.description}")
        return None
    return matches[0]


def _show_next_task(session):
    next_step = (
        session.query(Step)
        .join(Milestone)
        .join(Mission)
        .filter(
            Mission.status == 'active',
            Step.status.in_(['todo', 'in_progress'])
        )
        .order_by(Step.priority.desc(), Step.created_at)
        .first()
    )
    if next_step:
        content = f"""[bold]{next_step.description}[/bold]\n\nID: {next_step.id}\nStatus: {next_step.status}\nPriority: {'⭐' * (next_step.priority or 0)}\nMilestone: {next_step.milestone.title}"""
        if next_step.due_date:
            content += f"\nDue: {next_step.due_date.strftime('%Y-%m-%d')}"
        if next_step.tags:
            content += f"\nTags: {next_step.tags}"
        panel = Panel(content, title="Next Task", border_style="cyan")
        console.print(panel)
    else:
        console.print("[green]🎉 No pending tasks![/green]")


@click.command('complete')
@click.argument('task_id')
@click.option('--notes', '-n', help='Completion notes')
def complete_task(task_id, notes):
    """Mark a task as completed."""
    from roadmap.cli.main import ensure_db

    ensure_db()
    with get_session() as session:
        step = _find_step_by_prefix(session, task_id)
        if not step:
            return
        if step.status == 'done':
            console.print(f"[yellow]Task {step.id} is already completed.[/yellow]")
            return
        step.status = 'done'
        step.completed_at = datetime.now(timezone.utc)
        if notes:
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
            entry = f"[{timestamp}] {notes}"
            step.notes = (step.notes + '\n' + entry) if step.notes else entry
        session.commit()
        console.print(f"[green]✅ Completed:[/green] {step.description}")
        console.print('\n' + '─' * 40)
        _show_next_task(session)

