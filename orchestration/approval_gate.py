#!/usr/bin/env python3
"""Approval Gate — Policy-based decision engine for agent tasks"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Literal, Optional

SCHEMAS_DIR = Path(__file__).parent / "schemas"

DecisionType = Literal["approved", "rejected", "deferred", "revise"]
DeciderType = Literal["AVA", "HUMAN", "POLICY"]

class ApprovalGate:
    """Policy-based approval gate for agent orchestration"""
    
    def __init__(self):
        self.policies = self._load_policies()
    
    def decide(self, task: Dict, decided_by: DeciderType = "POLICY", 
               reason: Optional[str] = None) -> Dict:
        """Make approval decision on a task"""
        
        # Run policy checks
        decision, auto_reason, confidence = self._evaluate_policies(task)
        
        # Human/AVA can override
        if decided_by in ["AVA", "HUMAN"] and reason:
            final_reason = reason
        else:
            final_reason = auto_reason
        
        # Build decision record
        decision_record = {
            "task_id": task["task_id"],
            "decision": decision,
            "decided_by": decided_by,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "reason": final_reason,
            "confidence": confidence,
            "requires_human": confidence < 0.7
        }
        
        # Validate against schema
        self._validate_decision(decision_record)
        
        return decision_record
    
    def _evaluate_policies(self, task: Dict) -> tuple[DecisionType, str, float]:
        """Evaluate task against policies"""
        
        agent = task.get("agent_role")
        verb = task.get("verb")
        priority = task.get("priority", 3)
        
        # POLICY 1: CODEX execute requires high priority or explicit approval
        if agent == "CODEX" and verb == "execute":
            if priority >= 4:
                return "approved", "High priority CODEX task auto-approved", 0.85
            else:
                return "deferred", "CODEX execute requires priority ≥4 or manual approval", 0.6
        
        # POLICY 2: GINIE proposals always approved
        if agent == "GINIE" and verb == "propose":
            return "approved", "GINIE proposals auto-approved", 0.95
        
        # POLICY 3: AVA validation always approved
        if agent == "AVA" and verb in ["validate", "approve"]:
            return "approved", "AVA validation auto-approved", 0.9
        
        # POLICY 4: Unknown agent/verb → reject
        if agent == "HUMAN_ONLY":
            return "rejected", "Task requires human intervention", 0.99
        
        # Default: defer to human
        return "deferred", f"No policy for {agent}/{verb}", 0.5
    
    def _load_policies(self) -> Dict:
        """Load approval policies (placeholder for future config)"""
        return {
            "codex_min_priority": 4,
            "ginie_auto_approve": True,
            "ava_auto_approve": True,
            "unknown_reject": True
        }
    
    def _validate_decision(self, decision: Dict):
        """Validate decision against schema"""
        import jsonschema
        schema = json.loads((SCHEMAS_DIR / "agent_decision.json").read_text())
        jsonschema.validate(decision, schema)

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: ./approval_gate.py <task_file>")
        sys.exit(1)
    
    task_file = Path(sys.argv[1])
    if not task_file.exists():
        print(f"Error: Task file not found: {task_file}")
        sys.exit(1)
    
    task = json.loads(task_file.read_text())
    
    gate = ApprovalGate()
    decision = gate.decide(task)
    
    print(json.dumps(decision, indent=2))
    
    # Update task status based on decision
    from queue_manager import QueueManager
    qm = QueueManager()
    
    if decision["decision"] == "approved":
        qm.update_status(task["task_id"], "approved")
        print(f"\n✓ Task {task['task_id']} APPROVED", file=sys.stderr)
    elif decision["decision"] == "rejected":
        qm.update_status(task["task_id"], "blocked", 
                        blocked_reason=decision["reason"])
        print(f"\n✗ Task {task['task_id']} REJECTED", file=sys.stderr)
    elif decision["decision"] in ["deferred", "revise"]:
        qm.update_status(task["task_id"], "pending",
                        blocked_reason=f"{decision['decision']}: {decision['reason']}")
        print(f"\n⏸ Task {task['task_id']} {decision['decision'].upper()}", file=sys.stderr)
