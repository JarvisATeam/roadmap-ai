"""Export engine for roadmap plans."""
import json
import csv
import io
from pathlib import Path
from typing import Dict, Any, Optional, Union


class ExportEngine:
    """Export plans to various formats."""

    def to_markdown(self, plan: Dict[str, Any], output_path: Optional[Union[str, Path]] = None) -> str:
        """Export plan to Markdown format."""
        lines = []
        
        # Header
        project = plan.get("project", "Untitled")
        lines.append(f"# Roadmap: {project}")
        lines.append("")
        
        if plan.get("generated"):
            lines.append(f"Generated: {plan['generated']}")
            lines.append("")
        
        # Milestones
        milestones = plan.get("milestones", [])
        if milestones:
            lines.append("## Milestones")
            lines.append("")
        
        for ms in milestones:
            status = ms.get("status", "unknown")
            status_display = self._format_status(status)
            date_str = f" ({ms.get('target_date', 'No date')})" if ms.get("target_date") else ""
            
            lines.append(f"### {ms.get('id', '?')}: {ms.get('title', 'Untitled')}{date_str} - {status_display}")
            lines.append("")
            
            tasks = ms.get("tasks", [])
            if tasks:
                lines.append("**Tasks:**")
                for task in tasks:
                    task_status = task.get("status", "unknown")
                    icon = self._status_icon(task_status)
                    owner = f" (@{task.get('owner')})" if task.get("owner") else ""
                    lines.append(f"- {icon} {task.get('id', '?')}: {task.get('title', 'Untitled')}{owner} - {task_status}")
                lines.append("")
        
        content = "\n".join(lines)
        
        if output_path:
            Path(output_path).write_text(content)
        
        return content

    def to_json(self, plan: Dict[str, Any], output_path: Optional[Union[str, Path]] = None, pretty: bool = False) -> str:
        """Export plan to JSON format."""
        indent = 2 if pretty else None
        content = json.dumps(plan, indent=indent)
        
        if output_path:
            Path(output_path).write_text(content)
        
        return content

    def to_csv(self, plan: Dict[str, Any], output_path: Optional[Union[str, Path]] = None) -> str:
        """Export plan tasks to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "milestone_id", "milestone_title", "milestone_date", "milestone_status",
            "task_id", "task_title", "task_owner", "task_status"
        ])
        
        # Data rows
        for ms in plan.get("milestones", []):
            for task in ms.get("tasks", []):
                writer.writerow([
                    ms.get("id", ""),
                    ms.get("title", ""),
                    ms.get("target_date", ""),
                    ms.get("status", ""),
                    task.get("id", ""),
                    task.get("title", ""),
                    task.get("owner", ""),
                    task.get("status", "")
                ])
        
        content = output.getvalue()
        
        if output_path:
            Path(output_path).write_text(content)
        
        return content

    def summary(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary statistics for plan."""
        milestones = plan.get("milestones", [])
        
        task_status = {}
        milestone_status = {}
        total_tasks = 0
        
        for ms in milestones:
            # Count milestone status
            ms_status = ms.get("status", "unknown")
            milestone_status[ms_status] = milestone_status.get(ms_status, 0) + 1
            
            # Count task status
            for task in ms.get("tasks", []):
                total_tasks += 1
                t_status = task.get("status", "unknown")
                task_status[t_status] = task_status.get(t_status, 0) + 1
        
        return {
            "plan_id": plan.get("plan_id", ""),
            "project": plan.get("project", ""),
            "total_milestones": len(milestones),
            "total_tasks": total_tasks,
            "milestone_status": milestone_status,
            "task_status": task_status
        }

    def _format_status(self, status: str) -> str:
        """Format status for display."""
        mapping = {
            "on_track": "On Track",
            "at_risk": "At Risk",
            "delayed": "Delayed",
            "completed": "Completed"
        }
        return mapping.get(status, status)

    def _status_icon(self, status: str) -> str:
        """Get icon for status."""
        mapping = {
            "done": "✅",
            "in_progress": "🔄",
            "not_started": "⏳",
            "blocked": "🚫"
        }
        return mapping.get(status, "○")
