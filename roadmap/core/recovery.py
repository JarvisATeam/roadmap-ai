from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List
from roadmap.storage.db import get_session
from roadmap.storage.models import Mission, Milestone, Step, CheckIn, Decision
from roadmap.core.plan_diff import PlanDiffEngine


@dataclass
class RecoveryBrief:
    '''30-second context recovery for re-entry'''
    mission_title: str
    mission_id: str
    last_session: Optional[datetime] = None
    days_since_last: int = 0
    status_summary: str = ''
    completed_since_last: List[str] = field(default_factory=list)
    plan_drift: List[str] = field(default_factory=list)
    today_focus: List[str] = field(default_factory=list)
    active_blockers: List[str] = field(default_factory=list)
    key_context: List[str] = field(default_factory=list)
    progress_percent: int = 0


class RecoveryEngine:
    '''Generates 30-second re-entry briefs for thread recovery'''

    def __init__(self):
        self.diff_engine = PlanDiffEngine()

    def generate_brief(self, mission_id: str) -> Optional[RecoveryBrief]:
        '''Generate re-entry brief for a mission'''
        session = get_session()
        
        mission = session.query(Mission).filter_by(id=mission_id).first()
        if not mission:
            session.close()
            return None

        brief = RecoveryBrief(
            mission_title=mission.title,
            mission_id=mission.id
        )

        # Get last check-in
        last_checkin = session.query(CheckIn).filter_by(
            mission_id=mission_id
        ).order_by(CheckIn.created_at.desc()).first()

        if last_checkin:
            brief.last_session = last_checkin.created_at
            brief.days_since_last = (datetime.utcnow() - last_checkin.created_at).days
            if last_checkin.blockers_text:
                brief.active_blockers.append(last_checkin.blockers_text)

        # Get milestones and calculate progress
        milestones = session.query(Milestone).filter_by(mission_id=mission_id).all()
        total_steps = 0
        done_steps = 0
        
        for ms in milestones:
            steps = session.query(Step).filter_by(milestone_id=ms.id).all()
            total_steps += len(steps)
            
            for step in steps:
                if step.status == 'done':
                    done_steps += 1
                    # Check if completed since last session
                    if last_checkin and step.completed_at:
                        if step.completed_at > last_checkin.created_at:
                            brief.completed_since_last.append(step.action)
                elif step.status == 'todo':
                    brief.today_focus.append(step.action)
                elif step.status == 'skipped':
                    brief.plan_drift.append(f"Skipped: {step.action}")

        # Calculate progress
        if total_steps > 0:
            brief.progress_percent = int((done_steps / total_steps) * 100)

        # Status summary
        completed_milestones = len([m for m in milestones if m.status == 'completed'])
        brief.status_summary = f"{completed_milestones}/{len(milestones)} milestones, {done_steps}/{total_steps} steps ({brief.progress_percent}%)"

        # Get recent decisions for context
        decisions = session.query(Decision).filter_by(
            mission_id=mission_id
        ).order_by(Decision.created_at.desc()).limit(3).all()
        
        for dec in decisions:
            days_ago = (datetime.utcnow() - dec.created_at).days
            brief.key_context.append(f"{days_ago}d ago: {dec.choice} - {dec.reason}")

        # Limit today_focus to top 3
        brief.today_focus = brief.today_focus[:3]

        session.close()
        return brief

    def format_brief(self, brief: RecoveryBrief) -> str:
        '''Format RecoveryBrief as terminal output'''
        lines = []
        
        lines.append("")
        lines.append("⚡ RE-ENTRY BRIEF (30 seconds)")
        lines.append("")
        lines.append(f"📋 {brief.mission_title}")
        
        if brief.last_session:
            if brief.days_since_last == 0:
                lines.append(f"Last session: Today")
            elif brief.days_since_last == 1:
                lines.append(f"Last session: Yesterday")
            else:
                lines.append(f"Last session: {brief.days_since_last} days ago")
        else:
            lines.append("Last session: First time")
        
        lines.append(f"Status: {brief.status_summary}")
        
        if brief.completed_since_last:
            lines.append("")
            lines.append("✅ COMPLETED SINCE LAST:")
            for item in brief.completed_since_last:
                lines.append(f"  - {item}")
        
        if brief.plan_drift:
            lines.append("")
            lines.append("⚠️ PLAN DRIFT DETECTED:")
            for item in brief.plan_drift:
                lines.append(f"  - {item}")
        
        if brief.today_focus:
            lines.append("")
            lines.append("🎯 TODAY'S FOCUS:")
            for item in brief.today_focus:
                lines.append(f"  - [ ] {item}")
        
        if brief.active_blockers:
            lines.append("")
            lines.append("🚧 BLOCKERS:")
            for item in brief.active_blockers:
                lines.append(f"  - {item}")
        
        if brief.key_context:
            lines.append("")
            lines.append("🧠 KEY CONTEXT:")
            for item in brief.key_context:
                lines.append(f"  - {item}")
        
        lines.append("")
        lines.append("Ready? (yes/review/roadmap)")
        
        return "\n".join(lines)

    def get_active_mission_brief(self) -> Optional[str]:
        '''Get brief for most recent active mission'''
        session = get_session()
        
        mission = session.query(Mission).filter_by(
            status='active'
        ).order_by(Mission.updated_at.desc()).first()
        
        session.close()
        
        if not mission:
            return None
        
        brief = self.generate_brief(mission.id)
        if brief:
            return self.format_brief(brief)
        return None
