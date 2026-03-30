import click
from roadmap.storage.db import init_db, get_session
from roadmap.storage.models import Mission, Milestone, Step
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
    
    session.close()

@cli.command()
def open():
    '''Show re-entry brief (30-second context recovery)'''
    click.echo("⚡ RE-ENTRY BRIEF (placeholder - full implementation in Phase 4)")

def main():
    cli()

if __name__ == '__main__':
    main()
