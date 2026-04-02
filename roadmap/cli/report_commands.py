"""Report CLI commands."""

from __future__ import annotations

import click

from roadmap.core.json_export import create_envelope, to_json, get_base_metadata


@click.command("report")
@click.option("--daily", is_flag=True, help="Generate daily ops report")
@click.option("--mission", "mission_code", help="Filter by mission code")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--markdown", is_flag=True, help="Output as Markdown")
def report_command(daily: bool, mission_code: str, as_json: bool, markdown: bool):
    """Generate operational reports."""
    if not daily:
        click.echo("Use --daily to generate a daily operations report.")
        return

    from roadmap.storage.db import get_session
    from roadmap.storage.models import Mission
    from roadmap.core.nta import smart_next
    from roadmap.core.predictor import get_risk_summary
    from roadmap.core.revenue import mission_forecast
    from roadmap.core.decisions import list_decisions

    session = get_session()
    try:
        query = session.query(Mission)
        if mission_code:
            query = query.filter(
                (Mission.mission_code == mission_code)
                | (Mission.id.like(f"{mission_code}%"))
            )
        missions = query.all()
        missions_data = [
            {
                "id": mission.id,
                "mission_code": mission.mission_code or mission.id[:8],
                "title": mission.title,
                "revenue": mission.revenue or 0,
            }
            for mission in missions
        ]

        report = {
            "missions_count": len(missions_data),
            "sections": {}
        }

        recommendation = smart_next()
        report["sections"]["smart_next"] = {
            "title": "Next Recommended Task",
            "recommendation": recommendation
        }

        risks = get_risk_summary(mission_id=mission_code)
        report["sections"]["risks"] = {
            "title": "Risk Summary",
            "summary": risks
        }

        forecasts = []
        for mission in missions_data:
            fc = mission_forecast(mission["mission_code"])
            if "error" not in fc:
                forecasts.append(fc)
        report["sections"]["forecasts"] = {
            "title": "Mission Forecasts",
            "missions": forecasts
        }

        recent_decisions = list_decisions()[-5:]
        report["sections"]["decisions"] = {
            "title": "Recent Decisions",
            "recent": recent_decisions,
            "count": len(recent_decisions)
        }

        if as_json:
            envelope = create_envelope(
                command="report --daily",
                data=report,
                metadata={**get_base_metadata(), "filter_mission": mission_code}
            )
            click.echo(to_json(envelope))
        elif markdown:
            _print_report_markdown(report)
        else:
            _print_report_tui(report)
    finally:
        session.close()


def _print_report_tui(report: dict):
    click.echo("╔═════════════════════════════════════════════╗")
    click.echo("║ DAILY OPS REPORT                            ║")
    click.echo("╠═════════════════════════════════════════════╣")

    rec = report["sections"]["smart_next"]["recommendation"]
    click.echo("║ 🎯 NEXT RECOMMENDATION                      ║")
    if rec:
        click.echo(f"║   {rec.get('task_name', rec.get('task_id', 'Unknown'))[:40]:<43} ║")
        click.echo(f"║   Score: {rec.get('score', 0):<34} ║")
    else:
        click.echo("║   No available steps                        ║")

    click.echo("║                                             ║")
    click.echo("║ ⚠️  RISK SUMMARY                             ║")
    risks = report["sections"]["risks"]["summary"]
    click.echo(f"║   Blocked: {risks.get('blocked_steps', 0)} | Warnings: {len(risks.get('warnings', [])):<5} ║")

    click.echo("║                                             ║")
    click.echo("║ 📊 MISSION FORECASTS                        ║")
    for fc in report["sections"]["forecasts"]["missions"][:3]:
        title = fc.get("mission_name", "Unknown")[:20]
        prob = fc.get("completion_probability", 0)
        days = fc.get("days_remaining", "?")
        click.echo(f"║   {title}: {prob*100:.0f}% ({days} days)           ║")

    click.echo("║                                             ║")
    click.echo("║ 📝 RECENT DECISIONS                         ║")
    for decision in report["sections"]["decisions"]["recent"]:
        text = decision.get("decision", "")[:40]
        click.echo(f"║   • {text:<40} ║")

    click.echo("╚═════════════════════════════════════════════╝")


def _print_report_markdown(report: dict):
    click.echo("# Daily Ops Report")
    click.echo()
    click.echo("## 🎯 Next Recommended Task")
    click.echo()
    rec = report["sections"]["smart_next"]["recommendation"]
    if rec:
        click.echo(f"**{rec.get('task_name', rec.get('step_id', 'Unknown'))}**")
        click.echo(f"- Score: {rec.get('score', 0)}")
    else:
        click.echo("No tasks available")
    click.echo()
    click.echo("## ⚠️ Risk Summary")
    click.echo()
    risks = report["sections"]["risks"]["summary"]
    click.echo(f"- Blocked steps: {risks.get('blocked_steps', 0)}")
    click.echo(f"- Warnings: {len(risks.get('warnings', []))}")
    click.echo()
    click.echo("## 📊 Mission Forecasts")
    click.echo()
    click.echo("| Mission | Probability | Days Remaining |")
    click.echo("|---------|-------------|----------------|")
    for fc in report["sections"]["forecasts"]["missions"]:
        title = fc.get("mission_name", fc.get("mission_code", "Unknown"))[:20]
        prob = fc.get("completion_probability", 0)
        days = fc.get("days_remaining", "?")
        click.echo(f"| {title} | {prob*100:.0f}% | {days} |")
    click.echo()
    click.echo("## 📝 Recent Decisions")
    click.echo()
    for decision in report["sections"]["decisions"]["recent"]:
        click.echo(f"- {decision.get('id')}: {decision.get('decision')} ({decision.get('step_id')})")
