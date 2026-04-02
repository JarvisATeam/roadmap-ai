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


@click.command('status')
@click.option('--detailed', '-d', is_flag=True, help='Show task details')
def show_status(detailed):
    """Show mission and milestone status."""
    from roadmap.cli.main import ensure_db, get_active_mission

    ensure_db()
    with get_session() as session:
        mission = get_active_mission(session)
        if not mission:
            console.print("No active mission")
            return
        console.print(f"\n[bold cyan]Mission:[/bold cyan] {mission.title}")
        if mission.created_at:
            console.print(f"Started: {mission.created_at.strftime('%Y-%m-%d')}\n")
        table = Table(title="Milestones")
        table.add_column("Milestone", style="cyan")
        table.add_column("Tasks", justify="right")
        table.add_column("Done", justify="right")
        table.add_column("Progress", justify="right")
        for ms in mission.milestones:
            total = len(ms.steps)
            done = sum(1 for s in ms.steps if s.status == 'done')
            pct = (done / total * 100) if total else 0
            table.add_row(ms.title, str(total), str(done), f"{pct:.0f}%")
        console.print(table)
        if detailed:
            console.print("\n[bold]Task Details:[/bold]")
            for ms in mission.milestones:
                console.print(f"\n[cyan]{ms.title}[/cyan]")
                for step in ms.steps:
                    icon = '✅' if step.status == 'done' else '⏳'
                    stars = '⭐' * (step.priority or 0)
                    console.print(f"  {icon} {step.description} {stars}")
