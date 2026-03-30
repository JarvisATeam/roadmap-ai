from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class DriftType(Enum):
    SKIPPED = 'skipped'
    ADDED = 'added'
    DELAYED = 'delayed'
    REORDERED = 'reordered'
    COMPLETED_EARLY = 'completed_early'


@dataclass
class PlanEntry:
    '''A single planned item with its actual outcome'''
    step_id: str
    planned_action: str
    planned_date: Optional[datetime] = None
    actual_status: Optional[str] = None
    actual_date: Optional[datetime] = None
    drift_type: Optional[DriftType] = None
    drift_reason: Optional[str] = None


@dataclass
class PlanDiffResult:
    '''Result of comparing planned vs actual'''
    completed: list = field(default_factory=list)
    skipped: list = field(default_factory=list)
    added: list = field(default_factory=list)
    delayed: list = field(default_factory=list)
    on_track: list = field(default_factory=list)
    drift_score: float = 0.0

    @property
    def has_drift(self):
        return len(self.skipped) > 0 or len(self.added) > 0 or len(self.delayed) > 0

    @property
    def summary(self):
        parts = []
        if self.completed:
            parts.append(f'{len(self.completed)} completed')
        if self.skipped:
            parts.append(f'{len(self.skipped)} skipped')
        if self.added:
            parts.append(f'{len(self.added)} added')
        if self.delayed:
            parts.append(f'{len(self.delayed)} delayed')
        if self.on_track:
            parts.append(f'{len(self.on_track)} on track')
        return ', '.join(parts) if parts else 'No activity'


class PlanDiffEngine:
    '''Compares planned steps vs actual outcomes to detect drift'''

    def compute_diff(self, planned_steps, actual_steps):
        '''Compare planned vs actual and return PlanDiffResult
        
        Args:
            planned_steps: list of dicts with id, action, planned_date
            actual_steps: list of dicts with id, action, status, completed_at
        
        Returns:
            PlanDiffResult with categorized items
        '''
        result = PlanDiffResult()

        planned_ids = {s['id'] for s in planned_steps}
        actual_by_id = {s['id']: s for s in actual_steps}
        actual_ids = {s['id'] for s in actual_steps}

        # Check each planned step
        for step in planned_steps:
            sid = step['id']
            if sid in actual_by_id:
                actual = actual_by_id[sid]
                status = actual.get('status', 'todo')

                if status == 'done':
                    entry = PlanEntry(
                        step_id=sid,
                        planned_action=step['action'],
                        planned_date=step.get('planned_date'),
                        actual_status='done',
                        actual_date=actual.get('completed_at')
                    )
                    result.completed.append(entry)

                elif status == 'skipped':
                    entry = PlanEntry(
                        step_id=sid,
                        planned_action=step['action'],
                        actual_status='skipped',
                        drift_type=DriftType.SKIPPED,
                        drift_reason=actual.get('skip_reason', 'No reason given')
                    )
                    result.skipped.append(entry)

                elif status == 'todo' or status == 'in_progress':
                    if step.get('planned_date') and actual.get('due_date'):
                        if actual['due_date'] > step['planned_date']:
                            entry = PlanEntry(
                                step_id=sid,
                                planned_action=step['action'],
                                planned_date=step.get('planned_date'),
                                actual_status=status,
                                drift_type=DriftType.DELAYED
                            )
                            result.delayed.append(entry)
                        else:
                            entry = PlanEntry(
                                step_id=sid,
                                planned_action=step['action'],
                                actual_status=status
                            )
                            result.on_track.append(entry)
                    else:
                        entry = PlanEntry(
                            step_id=sid,
                            planned_action=step['action'],
                            actual_status=status
                        )
                        result.on_track.append(entry)
            else:
                # Planned but not in actuals at all
                entry = PlanEntry(
                    step_id=sid,
                    planned_action=step['action'],
                    actual_status='missing',
                    drift_type=DriftType.SKIPPED
                )
                result.skipped.append(entry)

        # Check for added items (in actual but not planned)
        for step in actual_steps:
            if step['id'] not in planned_ids:
                entry = PlanEntry(
                    step_id=step['id'],
                    planned_action=step['action'],
                    actual_status=step.get('status', 'todo'),
                    drift_type=DriftType.ADDED,
                    drift_reason=step.get('add_reason', 'Unplanned addition')
                )
                result.added.append(entry)

        # Calculate drift score (0.0 = perfect, 1.0 = total drift)
        total = len(planned_steps) + len(result.added)
        if total > 0:
            drifted = len(result.skipped) + len(result.added) + len(result.delayed)
            result.drift_score = round(drifted / total, 2)

        return result

    def format_diff(self, diff_result):
        '''Format PlanDiffResult as human-readable string'''
        lines = []

        if diff_result.completed:
            lines.append('\n✅ COMPLETED:')
            for entry in diff_result.completed:
                lines.append(f'  - {entry.planned_action}')

        if diff_result.skipped:
            lines.append('\n⏭ SKIPPED:')
            for entry in diff_result.skipped:
                reason = f' ({entry.drift_reason})' if entry.drift_reason else ''
                lines.append(f'  - {entry.planned_action}{reason}')

        if diff_result.added:
            lines.append('\n➕ ADDED (unplanned):')
            for entry in diff_result.added:
                reason = f' ({entry.drift_reason})' if entry.drift_reason else ''
                lines.append(f'  - {entry.planned_action}{reason}')

        if diff_result.delayed:
            lines.append('\n⏰ DELAYED:')
            for entry in diff_result.delayed:
                lines.append(f'  - {entry.planned_action}')

        if diff_result.on_track:
            lines.append('\n🎯 ON TRACK:')
            for entry in diff_result.on_track:
                lines.append(f'  - {entry.planned_action}')

        lines.append(f'\n📊 Drift score: {diff_result.drift_score} (0.0=perfect, 1.0=total drift)')
        lines.append(f'Summary: {diff_result.summary}')

        return '\n'.join(lines)
