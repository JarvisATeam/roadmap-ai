"""ORION CLI commands."""
from __future__ import annotations

import json

import click

from roadmap.core import nta, predictor, revenue


def _render_panel(lines):
    border = "╭" + "─" * 45 + "╮"
    footer = "╰" + "─" * 45 + "╯"
    click.echo(border)
    for line in lines:
        click.echo(f"│ {line.ljust(43)} │")
    click.echo(footer)


@click.command("smart")
@click.argument("subcommand", type=click.Choice(["next"]))
@click.option("--energy", default=5, show_default=True, help="Current energy level (1-10)")
@click.option("--last-task", help="Last completed task ID")
@click.option("--json", "as_json", is_flag=True, help="Render output as JSON")
def smart_command(subcommand: str, energy: int, last_task: str, as_json: bool) -> None:
    """Intelligent next-task logic."""
    if subcommand != "next":
        click.echo("Unsupported smart command.", err=True)
        raise SystemExit(1)
    result = nta.smart_next(current_energy=energy, last_task_id=last_task)
    if not result:
        payload = {"task": None, "message": "No available tasks"}
        if as_json:
            click.echo(json.dumps(payload))
        else:
            click.echo("No available tasks.")
        return
    if as_json:
        click.echo(json.dumps(result, indent=2))
        return
    lines = [
        "RECOMMENDED NEXT TASK",
        "",
        f"{result['task_id']}: {result['task_name'][:30]}",
        f"Score: {result['score']}",
        f"Mission: {result.get('mission_id') or '-'}",
        "",
        "Factors:",
        f"- Revenue weight: {result['factors']['revenue_weight']}",
        f"- Urgency: {result['factors']['urgency']}",
        f"- Energy match: {result['factors']['energy_match']}",
        f"- Context cost: {result['factors']['context_cost']}",
        f"- Risk penalty: {result['factors']['risk_penalty']}",
    ]
    _render_panel(lines)


@click.command("risks")
@click.option("--mission", help="Mission identifier filter")
@click.option("--json", "as_json", is_flag=True, help="Render output as JSON")
def risks_command(mission: str, as_json: bool) -> None:
    """Show risk analysis summary."""
    summary = predictor.get_risk_summary(mission_id=mission)
    if as_json:
        click.echo(json.dumps(summary, indent=2))
        return
    lines = [
        "RISK ANALYSIS",
        "",
        f"Missions analyzed: {summary['missions_analyzed']}",
        f"Blocked tasks: {summary['blocked_tasks']}",
        f"Overdue tasks: {summary['overdue_tasks']}",
        "",
    ]
    if summary["warnings"]:
        lines.append("Warnings:")
        for warning in summary["warnings"][:5]:
            prefix = "🔴" if warning["severity"] == "critical" else "⚠️ "
            lines.append(f"{prefix} {warning['message'][:38]}")
    else:
        lines.append("✓ No warnings")
    _render_panel(lines)


@click.command("value")
@click.argument("task_id")
@click.option("--json", "as_json", is_flag=True, help="Render output as JSON")
def value_command(task_id: str, as_json: bool) -> None:
    """Show task value breakdown."""
    result = revenue.task_value(task_id)
    if "error" in result:
        click.echo(result["error"], err=True)
        raise SystemExit(1)
    if as_json:
        click.echo(json.dumps(result, indent=2))
        return
    lines = [
        f"TASK VALUE: {task_id}",
        "",
        f"Base value: €{result['base_value']}",
        f"Critical path bonus: €{result['critical_bonus']}",
        f"Unblock bonus: €{result['unblock_bonus']}",
        f"Total value: €{result['total_value']}",
        "",
        f"Delay cost/day: €{result['delay_cost_per_day']}",
        f"Cascade multiplier: {result['cascade_multiplier']}x",
    ]
    _render_panel(lines)


@click.command("forecast")
@click.argument("mission_id")
@click.option("--json", "as_json", is_flag=True, help="Render output as JSON")
def forecast_command(mission_id: str, as_json: bool) -> None:
    """Show mission level forecast."""
    result = revenue.mission_forecast(mission_id)
    if "error" in result:
        click.echo(result["error"], err=True)
        raise SystemExit(1)
    if as_json:
        click.echo(json.dumps(result, indent=2))
        return
    progress_total = result["tasks_total"] or 1
    pct = result["tasks_completed"] / progress_total if progress_total else 0
    filled = int(pct * 12)
    bar = "█" * filled + "░" * (12 - filled)
    lines = [
        f"MISSION FORECAST: {result['mission_name']}",
        "",
        f"Revenue: €{result['revenue']}",
        f"Completion probability: {result['completion_probability'] * 100:.0f}%",
        f"Expected completion: {result['expected_completion'] or '-'}",
        f"Days remaining: {result['days_remaining'] or '-'}",
        "",
        f"Progress: {bar} {result['tasks_completed']}/{result['tasks_total']} tasks",
        f"Velocity: {result['velocity']} tasks/day",
    ]
    _render_panel(lines)
