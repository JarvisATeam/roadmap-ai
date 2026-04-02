"""CLI commands for decision logging."""
import json

import click

from roadmap.core import decisions


@click.command("decide")
@click.argument("step_id")
@click.argument("decision_text")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def decide_command(step_id: str, decision_text: str, as_json: bool) -> None:
    """Log a decision for a task or mission."""
    decision = decisions.add_decision(step_id, decision_text)
    if as_json:
        click.echo(json.dumps(decision, indent=2))
        return
    click.echo(f"✓ Decision logged: {decision['id']}")
    click.echo(f"  Step: {decision['step_id']}")
    click.echo(f"  Decision: {decision['decision']}")


@click.command("list-decisions")
@click.option("--step", help="Filter by step identifier")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_decisions_command(step: str, as_json: bool) -> None:
    """List recorded decisions."""
    items = decisions.list_decisions(step_id=step)
    if as_json:
        payload = {"decisions": items, "count": len(items)}
        click.echo(json.dumps(payload, indent=2))
        return
    if not items:
        click.echo("No decisions logged yet.")
        return
    click.echo(f"Decisions ({len(items)}):\n")
    for item in items:
        click.echo(f"  {item['id']} | {item['step_id']}")
        click.echo(f"    {item['decision']}")
        click.echo(f"    @ {item['timestamp']}")
        click.echo("")


@click.command("show-decision")
@click.argument("decision_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def show_decision_command(decision_id: str, as_json: bool) -> None:
    """Show a specific decision."""
    decision = decisions.get_decision(decision_id)
    if not decision:
        click.echo(f"Decision {decision_id} not found.", err=True)
        raise SystemExit(1)
    if as_json:
        click.echo(json.dumps(decision, indent=2))
        return
    click.echo(f"Decision: {decision['id']}")
    click.echo(f"Step: {decision['step_id']} ({decision['context'].get('step_type', 'unknown')})")
    click.echo(f"Timestamp: {decision['timestamp']}")
    click.echo("")
    click.echo("Decision:")
    click.echo(f"  {decision['decision']}")
    click.echo("")
    click.echo("Context:")
    for key, value in decision["context"].items():
        click.echo(f"  {key}: {value}")
