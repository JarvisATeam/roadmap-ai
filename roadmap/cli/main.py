import builtins
import click
from roadmap.storage.db import init_db, get_session
from roadmap.storage.models import Mission, Milestone, Step, CheckIn
from roadmap.core.recovery import RecoveryEngine
from datetime import datetime

@click.group()
def cli():
    '''roadmap.ai - Never lose the thread again'''
    pass

@cli.command()
def init():
    '''Initialize roadmap database'''
    init_db()
    click.echo("✅ Database initialized at ~/.roadmap/roadmap.db")

@cli.command()
@click.argument('title')
def create(title):
    '''Create a new mission'''
    session = get_session()
    mission = Mission(title=title)
    session.add(mission)
    session.commit()
    click.echo(f"✅ Mission created: {mission.title}")
    click.echo(f"   ID: {mission.id}")
    session.close()

@cli.command()
@click.argument('mission_id')
@click.argument('title')
@click.option('--success', help='Success criteria')
def milestone(mission_id, title, success):
    '''Add milestone to mission'''
    session = get_session()
    milestone = Milestone(
        mission_id=mission_id,
        title=title,
        success_criteria=success
    )
    session.add(milestone)
    session.commit()
    click.echo(f"✅ Milestone added: {milestone.title}")
    session.close()

@cli.command()
@click.argument('milestone_id')
@click.argument('action')
def step(milestone_id, action):
    '''Add step to milestone'''
    session = get_session()
    step = Step(
        milestone_id=milestone_id,
        action=action
    )
    session.add(step)
    session.commit()
    click.echo(f"✅ Step added: {step.action}")
    click.echo(f"   ID: {step.id}")
    session.close()

@cli.command()
@click.argument('step_id')
def done(step_id):
    '''Mark step as done'''
    session = get_session()
    step = session.query(Step).filter_by(id=step_id).first()
    
    if not step:
        click.echo("❌ Step not found")
        session.close()
        return
    
    step.status = 'done'
    step.completed_at = datetime.utcnow()
    session.commit()
    click.echo(f"✅ Step completed: {step.action}")
    session.close()

@cli.command()
@click.argument('mission_id')
@click.argument('summary')
@click.option('--blockers', help='Current blockers')
@click.option('--mood', type=click.Choice(['high', 'medium', 'low']), default='medium')
def checkin(mission_id, summary, blockers, mood):
    '''Log a check-in for mission'''
    session = get_session()
    checkin_entry = CheckIn(
        mission_id=mission_id,
        progress_summary=summary,
        blockers_text=blockers,
        mood=mood
    )
    session.add(checkin_entry)
    session.commit()
    click.echo(f"✅ Check-in logged")
    click.echo(f"   Mood: {mood}")
    if blockers:
        click.echo(f"   Blockers: {blockers}")
    session.close()

@cli.command()
def status():
    '''Show current status of all missions'''
    session = get_session()
    missions = session.query(Mission).filter_by(status='active').all()
    
    if not missions:
        click.echo("No active missions. Create one with: roadmap create <title>")
        return
    
    for mission in missions:
        click.echo(f"\n📋 {mission.title}")
        click.echo(f"   Created: {mission.created_at.strftime('%Y-%m-%d')}")
        
        milestones = session.query(Milestone).filter_by(mission_id=mission.id).all()
        if milestones:
            click.echo(f"   Milestones: {len(milestones)}")
            for ms in milestones:
                status_icon = "✅" if ms.status == 'completed' else "🔄" if ms.status == 'in_progress' else "⏳"
                click.echo(f"     {status_icon} {ms.title}")
                
                steps = session.query(Step).filter_by(milestone_id=ms.id).all()
                if steps:
                    for s in steps:
                        step_icon = "✅" if s.status == 'done' else "🔄" if s.status == 'in_progress' else "☐"
                        click.echo(f"        {step_icon} {s.action}")
    
    session.close()

@cli.command(name='open')
@click.argument('mission_id', required=False)
def open_brief(mission_id):
    '''Show re-entry brief (30-second context recovery)'''
    engine = RecoveryEngine()
    
    if mission_id:
        brief = engine.generate_brief(mission_id)
        if brief:
            click.echo(engine.format_brief(brief))
        else:
            click.echo("❌ Mission not found")
    else:
        brief_text = engine.get_active_mission_brief()
        if brief_text:
            click.echo(brief_text)
        else:
            click.echo("No active missions. Create one with: roadmap create <title>")

@cli.command()
@click.argument('mission_id')
@click.option('--format', type=click.Choice(['markdown', 'json', 'csv', 'summary']), default='markdown')
@click.option('--output', type=click.Path(), help='Output file (default: stdout)')
def export(mission_id, format, output):
    """Export mission plan in various formats"""
    from roadmap.core.export import ExportEngine
    
    session = get_session()
    mission = session.query(Mission).filter_by(id=mission_id).first()
    
    if not mission:
        click.echo(f"❌ Mission not found: {mission_id}")
        session.close()
        return
    
    # Build plan dict
    plan = {
        "plan_id": mission.id,
        "title": mission.title,
        "milestones": []
    }
    
    for ms in mission.milestones:
        milestone = {
            "id": ms.id,
            "title": ms.title,
            "success_criteria": ms.success_criteria,
            "steps": []
        }
        for step in ms.steps:
            milestone["steps"].append({
                "id": step.id,
                "action": step.action,
                "status": step.status,
                "completed_at": step.completed_at.isoformat() if step.completed_at else None
            })
        plan["milestones"].append(milestone)
    
    session.close()
    
    engine = ExportEngine()
    
    if format == 'markdown':
        result = engine.to_markdown(plan)
    elif format == 'json':
        result = engine.to_json(plan)
    elif format == 'csv':
        result = engine.to_csv(plan)
    elif format == 'summary':
        result = engine.summary(plan)
    
    if output:
        with builtins.open(output, 'w') as f:
            f.write(result)
        click.echo(f"✅ Exported to {output}")
    else:
        click.echo(result)

@cli.command()
@click.argument('file1')
@click.argument('file2')
def diff(file1, file2):
    """Compare two JSON plan files"""
    import json
    from roadmap.core.plan_diff import PlanDiffEngine
    
    try:
        with builtins.open(file1) as f1:
            plan1 = json.load(f1)
        with builtins.open(file2) as f2:
            plan2 = json.load(f2)
    except FileNotFoundError as e:
        click.echo(f"❌ File not found: {e}")
        return
    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON: {e}")
        return
    
    # Extract steps from plans
    def extract_steps(plan):
        steps = []
        for ms in plan.get("milestones", []):
            for step in ms.get("steps", []):
                steps.append({
                    "id": step.get("id", ""),
                    "action": step.get("action", step.get("title", "")),
                    "status": step.get("status", "unknown")
                })
        return steps
    
    engine = PlanDiffEngine()
    result = engine.compute_diff(extract_steps(plan1), extract_steps(plan2))
    
    click.echo(f"\n📊 Plan Comparison")
    click.echo(f"{'='*50}")
    click.echo(f"✅ Completed: {len(result.completed)}")
    click.echo(f"⏭  Skipped: {len(result.skipped)}")
    click.echo(f"➕ Added: {len(result.added)}")
    click.echo(f"⏰ Delayed: {len(result.delayed)}")
    click.echo(f"🎯 On track: {len(result.on_track)}")
    click.echo(f"📈 Drift score: {result.drift_score}")
    
    if result.has_drift:
        click.echo(f"\n⚠️  Drift detected: {result.summary}")


def main():
    cli()


if __name__ == '__main__':
    main()
