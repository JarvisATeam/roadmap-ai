# Export & Reporting Guide

## Quick Start

```python
from roadmap.core.export import ExportEngine

engine = ExportEngine()

# Export to Markdown
engine.to_markdown(plan, output_path="roadmap.md")

# Export to JSON  
engine.to_json(plan, output_path="roadmap.json", pretty=True)

# Export to CSV
engine.to_csv(plan, output_path="tasks.csv")

# Get summary
summary = engine.summary(plan)
print(f"Tasks: {summary['total_tasks']}")
from datetime import date
from pathlib import Path

def daily_export(plan):
    today = date.today().isoformat()
    output_dir = Path(f"exports/{today}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    engine = ExportEngine()
    engine.to_markdown(plan, output_path=output_dir / "roadmap.md")
    engine.to_json(plan, output_path=output_dir / "roadmap.json")
    engine.to_csv(plan, output_path=output_dir / "tasks.csv")
eof
