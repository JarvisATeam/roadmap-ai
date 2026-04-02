"""Blocker-related CLI commands."""
from datetime import datetime, timezone

import click

from roadmap.storage.db import get_session
from roadmap.storage.models import Blocker, Mission, Milestone, Step

try:
    from rich.console import Console
    from rich.table import Table
except ImportError:
    from roadmap.cli.display_fallback import Console, Table

console = Console()


def _find_step(session, identifier: str):
    matches = session.query(Step).filter(Step.id.like(f"{identifier}%")).all()
    if not matches:
        console.print(f"[red]❌ Task {identifier} not found[/red]")
        return None
    if len(matches) > 1:
        console.print(f"[yellow]⚠️ Multiple tasks match '{identifier}'. Specify more characters:[/yellow]")
        for step in matches:
            console.print(f"  - {step.id} {step.description}")
        return None
    return matches[0]


def _find_blocker(session, identifier: str):
    matches = session.query(Blocker).filter(Blocker.id.like(f"{identifier}%")).all()
    if not matches:
        console.print(f"[red]❌ Blocker {identifier} not found[/red]")
        return None
    if len(matches) > 1:
        console.print(f"[yellow]⚠️ Multiple blockers match '{identifier}'. Specify more characters:[/yellow]")
        for blocker in matches:
            console.print(f"  - {blocker.id} {blocker.description} (status={blocker.status})")
        return None
    return matches[0]


@click.command('block')
@click.argument('task_id')
@click.argument('reason')
def block_task(task_id, reason):
    """Create blocker for a task and set status to blocked."""
    from roadmap.cli.main import ensure_db

    ensure_db()
    with get_session() as session:
        step = _find_step(session, task_id)
        if not step:
            return
        blocker = Blocker(
            step_id=step.id,
            description=reason,
            status='active',
            created_at=datetime.now(timezone.utc)
        )
        step.status = 'blocked'
        session.add(blocker)
        session.commit()
        console.print(f"[yellow]🚧 Blocked:[/yellow] {step.description}")
        console.print(f"   Blocker ID: {blocker.id}")


@click.command('list-blocks')
def list_blocks():
    """List active blockers."""
    from roadmap.cli.main import ensure_db

    ensure_db()
    with get_session() as session:
        blockers = (
            session.query(Blocker)
            .join(Step)
            .join(Milestone)
            .join(Mission)
            .order_by(Blocker.created_at.desc())
            .all()
        )
        table = Table(title="Blockers")
        table.add_column("ID", style="cyan")
        table.add_column("Task")
        table.add_column("Status")
        table.add_column("Reason")
        table.add_column("Created")
        for blocker in blockers:
            created = blocker.created_at.strftime('%Y-%m-%d %H:%M') if blocker.created_at else '-'
            table.add_row(
                blocker.id,
                blocker.step.description,
                blocker.status,
                blocker.description,
                created,
            )
        if blockers:
            console.print(table)
        else:
            console.print("[green]No blockers recorded.[/green]")


@click.command('unblock')
@click.argument('blocker_id')
@click.option('--notes', '-n', help='Resolution notes')
def unblock_task(blocker_id, notes):
    """Resolve a blocker and revert task status to todo."""
    from roadmap.cli.main import ensure_db

    ensure_db()
    with get_session() as session:
        blocker = _find_blocker(session, blocker_id)
        if not blocker:
            return
        if blocker.status == 'resolved':
            console.print(f"[yellow]Blocker {blocker.id} already resolved.[/yellow]")
            return
        blocker.status = 'resolved'
        blocker.resolved_at = datetime.now(timezone.utc)
        if notes:
            timestamp = blocker.resolved_at.strftime('%Y-%m-%d %H:%M')
            entry = f"[{timestamp}] {notes}"
            blocker.resolution_notes = (blocker.resolution_notes + '\n' + entry) if blocker.resolution_notes else entry
        blocker.step.status = 'todo'
        session.commit()
        console.print(f"[green]✅ Unblocked:[/green] {blocker.step.description}")
        console.print(f"   Blocker ID: {blocker.id}")
