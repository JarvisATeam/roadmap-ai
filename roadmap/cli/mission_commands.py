"""Mission management CLI commands."""

from datetime import datetime, timezone

import click
import json

from roadmap.storage.db import get_session
from roadmap.storage.models import Mission, Milestone, Step
from roadmap.core.id_resolver import (
    AmbiguousIDError,
    IDNotFoundError,
    load_state_snapshot,
    resolve_mission_id,
)


@click.command("add-mission")
@click.argument("title")
@click.option("--revenue", type=int, default=0, help="Revenue target (€)")
@click.option("--description", default="", help="Mission description")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def add_mission_command(title: str, revenue: int, description: str, as_json: bool):
    """Create a new mission with revenue target."""
    session = get_session()
    try:
        mission = Mission(title=title, description=description, revenue=revenue)
        session.add(mission)
        session.flush()
        mission.mission_code = f"M-{mission.id[:8]}"
        session.commit()
        payload = {
            "id": mission.id,
            "mission_code": mission.mission_code,
            "title": mission.title,
            "revenue": mission.revenue or 0,
        }
        if as_json:
            click.echo(json.dumps(payload, indent=2))
        else:
            click.echo(f"✅ Mission created: {mission.mission_code}")
            click.echo(f"   Title: {title}")
            if revenue:
                click.echo(f"   Revenue: €{revenue}")
    finally:
        session.close()


@click.command("list-missions")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_missions_command(as_json: bool):
    """List all missions."""
    session = get_session()
    try:
        missions = session.query(Mission).all()
        if as_json:
            payload = {
                "missions": [
                    {
                        "id": m.id,
                        "mission_code": m.mission_code or m.id[:8],
                        "title": m.title,
                        "revenue": m.revenue or 0,
                        "status": m.status,
                    }
                    for m in missions
                ],
                "count": len(missions),
            }
            click.echo(json.dumps(payload, indent=2))
        else:
            if not missions:
                click.echo("No missions found. Create one with 'roadmap add-mission'")
                return
            click.echo(f"Missions ({len(missions)}):\n")
            for mission in missions:
                code = mission.mission_code or mission.id[:8]
                click.echo(f"  {code} | {mission.title}")
                if mission.revenue:
                    click.echo(f"    Revenue: €{mission.revenue}")
                click.echo(f"    Status: {mission.status}")
                click.echo()
    finally:
        session.close()


@click.command("add-step")
@click.argument("mission_code")
@click.argument("description")
@click.option("--energy", type=int, default=3, help="Energy level (1-10)")
@click.option("--due", "-d", type=click.DateTime(formats=["%Y-%m-%d"]), default=None, help="Due date (YYYY-MM-DD)")
@click.option("--milestone", "milestone_title", default=None, help="Milestone title (creates if missing)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def add_step_command(mission_code: str, description: str, energy: int, due, milestone_title: str, as_json: bool):
    """Add a step to a mission."""
    from roadmap.storage.models import Step

    session = get_session()
    try:
        mission = (
            session.query(Mission)
            .filter(
                (Mission.mission_code == mission_code)
                | (Mission.id.like(f"{mission_code}%"))
            )
            .first()
        )
        if not mission:
            click.echo(f"Error: Mission '{mission_code}' not found", err=True)
            click.echo("Use 'roadmap list-missions' to see available missions")
            raise SystemExit(1)

        if milestone_title:
            milestone = (
                session.query(Milestone)
                .filter_by(mission_id=mission.id, title=milestone_title)
                .first()
            )
            if not milestone:
                order = session.query(Milestone).filter_by(mission_id=mission.id).count() + 1
                milestone = Milestone(
                    mission_id=mission.id,
                    title=milestone_title,
                    order=order,
                )
                session.add(milestone)
                session.flush()
        else:
            milestone = (
                session.query(Milestone)
                .filter_by(mission_id=mission.id)
                .order_by(Milestone.order)
                .first()
            )
            if not milestone:
                milestone = Milestone(mission_id=mission.id, title="Backlog", order=1)
                session.add(milestone)
                session.flush()

        due_date = due.replace(tzinfo=timezone.utc) if due and not due.tzinfo else due

        step = Step(
            milestone_id=milestone.id,
            description=description,
            energy=energy,
            due_date=due_date,
        )
        session.add(step)
        session.commit()

        payload = {
            "id": step.id,
            "description": step.description,
            "energy": step.energy,
            "mission_code": mission.mission_code or mission.id[:8],
            "milestone": milestone.title,
        }
        if as_json:
            click.echo(json.dumps(payload, indent=2))
        else:
            click.echo(f"✅ Step added to {payload['mission_code']}")
            click.echo(f"   Description: {description}")
            click.echo(f"   Energy: {energy}")
            click.echo(f"   Milestone: {milestone.title}")
    finally:
        session.close()


@click.command("list-steps")
@click.option("--mission", "-m", help="Filter by mission identifier (supports short prefix)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_steps_command(mission: str, as_json: bool):
    """List steps optionally filtered by mission."""
    resolved_mission_id = None
    if mission:
        snapshot = load_state_snapshot()
        try:
            resolved_mission_id = resolve_mission_id(mission, snapshot)
        except IDNotFoundError:
            raise click.ClickException(f"Mission not found for prefix '{mission}'")
        except AmbiguousIDError as exc:
            sample = ", ".join(exc.matches[:3])
            raise click.ClickException(
                f"Prefix '{mission}' matches multiple missions: {sample}"
            )

    session = get_session()
    try:
        query = (
            session.query(Step, Milestone, Mission)
            .join(Milestone, Step.milestone_id == Milestone.id)
            .join(Mission, Milestone.mission_id == Mission.id)
            .order_by(Mission.title.asc(), Milestone.order.asc(), Step.created_at.asc())
        )
        if resolved_mission_id:
            query = query.filter(Mission.id == resolved_mission_id)
        rows = query.all()
    finally:
        session.close()

    steps = [
        {
            "id": step.id,
            "title": step.description,
            "status": step.status,
            "mission_id": mission_row.id,
            "mission_title": mission_row.title,
            "milestone": milestone.title,
            "due_date": step.due_date.isoformat() if step.due_date else None,
            "energy": step.energy or 3,
            "created_at": step.created_at.isoformat() if step.created_at else None,
        }
        for step, milestone, mission_row in rows
    ]

    if as_json:
        payload = {
            "steps": steps,
            "count": len(steps),
            "filter_mission": resolved_mission_id,
        }
        click.echo(json.dumps(payload, indent=2))
        return

    if not steps:
        click.echo("No steps found.")
        return

    click.echo(f"Steps ({len(steps)}):\n")
    for item in steps:
        short_id = item["id"][:8]
        click.echo(f"{short_id} | {item['title']}")
        click.echo(f"  Mission: {item['mission_title']} ({item['mission_id'][:8]})")
        click.echo(f"  Milestone: {item['milestone']}")
        click.echo(f"  Status: {item['status']}")
        if item["due_date"]:
            click.echo(f"  Due: {item['due_date'][:10]}")
        else:
            click.echo("  Due: -")
        click.echo("")
