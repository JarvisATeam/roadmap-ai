"""Status CLI commands for roadmap-ai."""

from __future__ import annotations

import click

from roadmap.storage.db import get_session
from roadmap.storage.models import Mission, Milestone, Step
from roadmap.core.json_export import create_envelope, to_json, get_base_metadata


def _mission_code(mission: Mission) -> str:
    return mission.mission_code or mission.id[:8]


@click.command("status")
@click.option("--mission", "mission_code", help="Filter by mission code")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def status_command(mission_code: str, as_json: bool):
    """Show roadmap status across missions."""
    session = get_session()
    try:
        query = session.query(Mission)
        if mission_code:
            query = query.filter(
                (Mission.mission_code == mission_code) | (Mission.id.like(f"{mission_code}%"))
            )
        missions = query.all()
        missions_data = []
        for mission in missions:
            milestones = (
                session.query(Milestone)
                .filter_by(mission_id=mission.id)
                .order_by(Milestone.order)
                .all()
            )
            milestones_data = []
            for milestone in milestones:
                steps = session.query(Step).filter_by(milestone_id=milestone.id).all()
                steps_data = [
                    {
                        "id": step.id,
                        "description": step.description,
                        "status": step.status,
                        "energy": step.energy or 3,
                        "priority": step.priority or 3,
                    }
                    for step in steps
                ]
                milestones_data.append(
                    {
                        "id": milestone.id,
                        "title": milestone.title,
                        "status": milestone.status,
                        "steps": steps_data,
                        "steps_count": len(steps_data),
                        "steps_done": sum(1 for s in steps_data if s["status"] == "done"),
                    }
                )
            all_steps = [s for ms in milestones_data for s in ms["steps"]]
            missions_data.append(
                {
                    "id": mission.id,
                    "mission_code": _mission_code(mission),
                    "title": mission.title,
                    "status": mission.status,
                    "revenue": mission.revenue or 0,
                    "milestones": milestones_data,
                    "milestones_count": len(milestones_data),
                    "steps_total": len(all_steps),
                    "steps_completed": sum(1 for s in all_steps if s["status"] == "done"),
                    "steps_in_progress": sum(1 for s in all_steps if s["status"] == "in_progress"),
                    "steps_blocked": sum(1 for s in all_steps if s["status"] == "blocked"),
                    "steps_todo": sum(1 for s in all_steps if s["status"] == "todo"),
                }
            )
        if as_json:
            envelope = create_envelope(
                command="status",
                data={"missions": missions_data, "missions_count": len(missions_data)},
                metadata={**get_base_metadata(), "filter_mission": mission_code},
            )
            click.echo(to_json(envelope))
        else:
            _print_status(missions_data)
    finally:
        session.close()


def _print_status(missions_data: list):
    if not missions_data:
        click.echo("No missions found.")
        click.echo("Create one with: roadmap add-mission 'Mission name' --revenue 5000")
        return
    click.echo("╭─────────────────────────────────────────────╮")
    click.echo("│ ROADMAP STATUS                              │")
    click.echo("├─────────────────────────────────────────────┤")
    for mission in missions_data:
        click.echo("│                                             │")
        code = mission.get("mission_code", "-")
        title = mission.get("title", "Unknown")[:30]
        click.echo(f"│ {code}: {title:<34} │")
        click.echo(f"│   Revenue: €{mission.get('revenue', 0):<31} │")
        done = mission.get("steps_completed", 0)
        total = mission.get("steps_total", 0) or 1
        pct = done / total if total else 0
        bar = "█" * int(pct * 20) + "░" * (20 - int(pct * 20))
        click.echo(f"│   Progress: {bar} {done}/{mission.get('steps_total', 0):<3} │")
        click.echo(
            "│   📋 Todo: {todo} | 🔄 In Progress: {ip} | 🚫 Blocked: {blocked:<2} │".format(
                todo=mission.get("steps_todo", 0),
                ip=mission.get("steps_in_progress", 0),
                blocked=mission.get("steps_blocked", 0),
            )
        )
    click.echo("│                                             │")
    click.echo("╰─────────────────────────────────────────────╯")
