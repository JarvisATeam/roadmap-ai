# Export Audit — 2026-04-01

## Commands Run

```bash
cd ~/roadmap-ai
source venv/bin/activate
pytest -k export --maxfail=1 --disable-warnings -q
python - <<'PY'
import json
from pathlib import Path
from roadmap.core.export import ExportEngine
plan = json.loads(Path('plan-v2.json').read_text())
engine = ExportEngine()
print({'markdown': len(engine.to_markdown(plan)),
       'json': len(engine.to_json(plan)),
       'csv': len(engine.to_csv(plan))})
PY
python - <<'PY'
import json
from pathlib import Path
from roadmap.core.export import ExportEngine
plan = json.loads(Path('plan-v2.json').read_text())
engine = ExportEngine()
engine.to_markdown(plan, output_path='plan.md')
engine.to_json(plan, output_path='plan.json')
engine.to_csv(plan, output_path='plan.csv')
PY
bash scripts/export_markdown.sh
bash scripts/export_json.sh
bash scripts/export_csv.sh
bash scripts/test_exports.sh
```

## Results

| Check | Status | Notes |
|-------|--------|-------|
| `pytest -k export` | ✅ 19 passed (0 failed) | warning only from SQLAlchemy 2.0 deprecation |
| Markdown export | ✅ length 491 chars | `plan.md` generated |
| JSON export | ✅ length 750 chars | `plan.json` generated |
| CSV export | ✅ length 677 chars | `plan.csv` generated |
| `scripts/export_markdown/json/csv.sh` | ✅ wrappers load `plan-v2.json`, write to `exports/` |
| `scripts/test_exports.sh` | ✅ runs wrappers, verifies file sizes + JSON validity |

Generated files look valid (see `exports/plan.*` in repo root). `.gitignore` updated so artifacts stay untracked.

## Next Steps (Phase 1 roadmap)

Wrappers/tests (1.1.2–1.1.5) are now done. Remaining work for Phase 1.1:

- Wire `scripts/test_exports.sh` into a pre-commit hook (1.1.6) so commits fail if exports break.
- Keep `exports/` artifacts ignored (git config is in place).

CLI layer (phase 1.2) remains open — `roadmap-ai` lacks `add-task`, `complete`, `next`, etc. We should scope those commands next.
