"""Main CLI entry point."""
import json
import pathlib
from datetime import datetime, timezone

import click

from roadmap.core.export import ExportEngine
from roadmap.cli.blockers import block_task, list_blocks, unblock_task
from roadmap.cli.tasks import complete_task, show_status
from roadmap.storage.db import get_session, init_db
from roadmap.storage.models import Mission, Milestone, Step

try:
    from rich.console import Console
    from rich.panel import Panel
except ImportError:
    from roadmap.cli.display_fallback import Console, Panel

console = Console()


def ensure_db():
    """Ensure database exists."""
    init_db()


def load_plan(plan_path=None):
    path = pathlib.Path(plan_path) if plan_path else pathlib.Path('plan.json')
    if not path.exists():
        click.echo(f"Plan file not found: {path}", err=True)
        return {}
    return json.loads(path.read_text())


def get_active_mission(session):
    mission = session.query(Mission).filter_by(status='active').first()
    if not mission:
        mission = Mission(
            title='Default Mission',
            description='Auto-created mission',
            status='active',
            started_at=datetime.now(timezone.utc)
        )
        session.add(mission)
        session.flush()
    return mission


def get_or_create_milestone(session, mission, milestone_name):
    milestone = (
        session.query(Milestone)
        .filter_by(mission_id=mission.id, title=milestone_name)
        .first()
    )
    if not milestone:
        order = (
            session.query(Milestone)
            .filter_by(mission_id=mission.id)
            .count()
        )
        milestone = Milestone(
            mission_id=mission.id,
            title=milestone_name or 'Backlog',
            order=order + 1,
            status='active'
        )
        session.add(milestone)
        session.flush()
    return milestone


@click.group()
def main():
    """Mission-oriented project management CLI."""
    pass


@main.command('init')
def init_db_command():
    init_db()
    click.echo("✅ Initialized database")


@main.command('add-task')
@click.argument('description')
@click.option('--milestone', '-m', help='Milestone name')
@click.option('--priority', '-p', type=int, default=3, help='Priority (1-5)')
@click.option('--due', '-d', help='Due date (YYYY-MM-DD)')
@click.option('--tags', '-t', multiple=True, help='Tags (repeatable)')
def add_task(description, milestone, priority, due, tags):
    ensure_db()
    with get_session() as session:
        mission = get_active_mission(session)
        ms = get_or_create_milestone(session, mission, milestone or 'Backlog')
        step = Step(
            milestone_id=ms.id,
            description=description,
            status='todo',
            priority=priority,
            tags=','.join(tags) if tags else None
        )
        if due:
            step.due_date = datetime.strptime(due, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        session.add(step)
        session.commit()
        console.print(f"[green]✅ Added task:[/green] {description}")
        console.print(f"   Milestone: {ms.title}")
        console.print(f"   ID: {step.id}")


@main.command('next')
@click.option('--all', '-a', is_flag=True, help='Show all pending tasks')
def next_task(all):
    ensure_db()
    with get_session() as session:
        query = (
            session.query(Step)
            .join(Milestone)
            .join(Mission)
            .filter(
                Mission.status == 'active',
                Step.status.in_(['todo', 'in_progress'])
            )
            .order_by(Step.priority.desc(), Step.created_at)
        )
        if all:
            tasks = query.limit(10).all()
            if not tasks:
                console.print('[green]🎉 No pending tasks![/green]')
                return
            console.print('\n[bold]Pending Tasks:[/bold]')
            for idx, task in enumerate(tasks, 1):
                stars = '⭐' * (task.priority or 0)
                console.print(f"{idx}. {task.description} {stars}")
                console.print(f"   ID: {task.id}")
                console.print(f"   Milestone: {task.milestone.title}\n")
        else:
            task = query.first()
            if not task:
                console.print('[green]🎉 No pending tasks![/green]')
                return
            content = f"""[bold]{task.description}[/bold]\n\nID: {task.id}\nStatus: {task.status}\nPriority: {'⭐' * (task.priority or 0)}\nMilestone: {task.milestone.title}"""
            if task.due_date:
                content += f"\nDue: {task.due_date.strftime('%Y-%m-%d')}"
            if task.tags:
                content += f"\nTags: {task.tags}"
            panel = Panel(content, title='Next Task', border_style='cyan')
            console.print(panel)


@main.command('summary')
@click.option('--plan', type=click.Path(exists=True), help='Path to plan.json')
def summary(plan):
    data = load_plan(plan)
    mission = data.get('mission', {})
    console.print(f"\n[bold cyan]Mission:[/bold cyan] {mission.get('name', 'Untitled')}")
    description = mission.get('description', '')
    if description:
        console.print(description + '\n')
    for ms in mission.get('milestones', []):
        console.print(f"[bold]{ms['name']}[/bold]")
        for task in ms.get('tasks', []):
            icon = '✅' if task.get('status') == 'done' else '⏳'
            console.print(f"  {icon} {task['description']}")


@main.command('export')
@click.argument('format', type=click.Choice(['markdown', 'html', 'json']))
@click.option('--plan', type=click.Path(exists=True), help='Path to plan.json')
@click.option('--output', '-o', help='Output file path')
def export_plan(format, plan, output):
    import subprocess
    script = pathlib.Path('scripts') / f'export_{format}.py'
    if not script.exists():
        click.echo(f"Export script not found: {script}", err=True)
        return
    cmd = ['python', str(script)]
    if plan:
        cmd.extend(['--plan', plan])
    if output:
        cmd.extend(['--output', output])
    result = subprocess.run(cmd)
    if result.returncode == 0:
        click.echo(f"✅ Exported to {format}")


main.add_command(complete_task)
main.add_command(show_status)
main.add_command(block_task)
main.add_command(list_blocks)
main.add_command(unblock_task)


cli = main

if __name__ == '__main__':
    main()
