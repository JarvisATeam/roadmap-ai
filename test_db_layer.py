"""Test database layer functionality."""
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from roadmap.storage.db import get_session, init_db
from roadmap.storage.models import Mission, Milestone, Step

with TemporaryDirectory() as tmpdir:
    os.environ["ROADMAP_DB_PATH"] = str(Path(tmpdir) / "test_db.sqlite")

    print("Initializing database...")
    init_db()

    with get_session() as session:
        mission = Mission(
            title="Test Mission",
            description="Testing database layer",
            status='active',
            started_at=datetime.now(timezone.utc)
        )
        session.add(mission)
        session.flush()

        milestone = Milestone(
            mission_id=mission.id,
            title="Test Milestone",
            order=1,
            status='active'
        )
        session.add(milestone)
        session.flush()

        step1 = Step(
            milestone_id=milestone.id,
            description="High priority task",
            status='todo',
            priority=5,
            due_date=datetime.now(timezone.utc) + timedelta(days=7),
            tags="backend,urgent",
            notes="This is a test task"
        )
        step2 = Step(
            milestone_id=milestone.id,
            description="Medium priority task",
            status='in_progress',
            priority=3,
            tags="frontend"
        )
        step3 = Step(
            milestone_id=milestone.id,
            description="Completed task",
            status='done',
            priority=4,
            completed_at=datetime.now(timezone.utc)
        )
        session.add_all([step1, step2, step3])
        session.commit()

        print(f"✅ Created mission: {mission.id}")
        print(f"✅ Created milestone: {milestone.id}")
        print(f"✅ Created step 1: {step1.id}")
        print(f"✅ Created step 2: {step2.id}")
        print(f"✅ Created step 3: {step3.id}")

    print("\n" + "=" * 50)
    print("Database Contents:")
    print("=" * 50 + "\n")

    with get_session() as session:
        missions = session.query(Mission).all()
        print(f"Found {len(missions)} mission(s)\n")
        for mission in missions:
            print(f"Mission: {mission.title}")
            print(f"  Status: {mission.status}")
            if mission.started_at:
                print(f"  Started: {mission.started_at}")
            for milestone in mission.milestones:
                print(f"\n  Milestone: {milestone.title}")
                print(f"    Order: {milestone.order}")
                for step in milestone.steps:
                    print(f"\n    - {step.description}")
                    print(f"      Status: {step.status}")
                    print(f"      Priority: {step.priority}")
                    if step.due_date:
                        print(f"      Due: {step.due_date.strftime('%Y-%m-%d')}")
                    if step.tags:
                        print(f"      Tags: {step.tags}")
                    if step.notes:
                        print(f"      Notes: {step.notes}")
                    if step.completed_at:
                        print(f"      Completed: {step.completed_at.strftime('%Y-%m-%d %H:%M')}")

    print("\n" + "=" * 50)
    print("✅ Database layer test complete!")
    print("=" * 50)
