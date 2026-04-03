#!/usr/bin/env python3
"""Queue Manager for Agent Orchestration"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

QUEUE_DIR = Path(__file__).parent / "queue"
SCHEMAS_DIR = Path(__file__).parent / "schemas"

class QueueManager:
    def __init__(self):
        self.queue_dir = QUEUE_DIR
        self.queue_dir.mkdir(exist_ok=True)
    
    def enqueue(self, agent_role: str, verb: str, payload: Dict, 
                mission_id: Optional[str] = None, 
                step_id: Optional[str] = None,
                priority: int = 3) -> str:
        """Add task to queue"""
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        
        task = {
            "task_id": task_id,
            "agent_role": agent_role,
            "verb": verb,
            "status": "pending",
            "priority": priority,
            "payload": payload,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        if mission_id:
            task["mission_id"] = mission_id
        if step_id:
            task["step_id"] = step_id
        
        # Validate
        self._validate_task(task)
        
        # Write to queue
        queue_file = self.queue_dir / f"{task_id}.json"
        queue_file.write_text(json.dumps(task, indent=2))
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Retrieve task by ID"""
        queue_file = self.queue_dir / f"{task_id}.json"
        if not queue_file.exists():
            return None
        return json.loads(queue_file.read_text())
    
    def update_status(self, task_id: str, status: str, **kwargs):
        """Update task status"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        task["status"] = status
        task["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        for key, value in kwargs.items():
            task[key] = value
        
        self._validate_task(task)
        
        queue_file = self.queue_dir / f"{task_id}.json"
        queue_file.write_text(json.dumps(task, indent=2))
    
    def list_by_status(self, status: str) -> List[Dict]:
        """List all tasks with given status"""
        tasks = []
        for queue_file in self.queue_dir.glob("task-*.json"):
            task = json.loads(queue_file.read_text())
            if task.get("status") == status:
                tasks.append(task)
        return sorted(tasks, key=lambda t: t.get("priority", 0), reverse=True)
    
    def list_by_agent(self, agent_role: str) -> List[Dict]:
        """List all tasks for given agent"""
        tasks = []
        for queue_file in self.queue_dir.glob("task-*.json"):
            task = json.loads(queue_file.read_text())
            if task.get("agent_role") == agent_role:
                tasks.append(task)
        return tasks
    
    def _validate_task(self, task: Dict):
        """Validate task against schema"""
        import jsonschema
        schema = json.loads((SCHEMAS_DIR / "agent_task.json").read_text())
        jsonschema.validate(task, schema)

if __name__ == "__main__":
    # Demo
    qm = QueueManager()
    
    # Enqueue a task
    task_id = qm.enqueue(
        agent_role="GINIE",
        verb="propose",
        payload={"description": "Test proposal"},
        priority=4
    )
    print(f"✓ Enqueued: {task_id}")
    
    # Update status
    qm.update_status(task_id, "proposed")
    print(f"✓ Updated status to: proposed")
    
    # List pending
    pending = qm.list_by_status("proposed")
    print(f"✓ Found {len(pending)} proposed tasks")
