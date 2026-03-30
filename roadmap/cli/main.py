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

@cli.command()
@click.argument('mission_id', required=False)
def open(mission_id):
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

def main():
    cli()

if __name__ == '__main__':
    main()
