# Phase 3 Deployment Guide — Dashboard JSON Feeds

## Summary
- JSON envelope utilities now ship with every CLI command (smart/risks/value/forecast/decisions/status/report)
- Wrapper script and panel config live in `scripts/` (copy to mission-control repo when ready)
- Because writing to `~/roadmapai/` was blocked, a tarball is available at `/tmp/roadmap_panels_bundle.tar.gz`

## Files to Deploy
```
~/roadmap-ai/scripts/roadmap_panels.sh
~/roadmap-ai/scripts/roadmap_panels.json
```

## Manual Deployment Steps
1. Copy files to mission-control repo
```bash
# On mission-control box (~/roadmapai)
mkdir -p bin config data/roadmap
cp ~/roadmap-ai/scripts/roadmap_panels.sh ~/roadmapai/bin/
chmod +x ~/roadmapai/bin/roadmap_panels.sh
cp ~/roadmap-ai/scripts/roadmap_panels.json ~/roadmapai/config/
```

2. Ensure roadmap CLI has Phase 3 binary (a014f69) built/installed.

3. Test each panel
```bash
cd ~/roadmapai
bin/roadmap_panels.sh smart   # smart_next.json
bin/roadmap_panels.sh risks   # risks.json
bin/roadmap_panels.sh status  # status.json
bin/roadmap_panels.sh report  # daily_report.json
bin/roadmap_panels.sh decisions  # decisions.json
```

4. Verify files
```bash
ls -lh data/roadmap/
cat data/roadmap/smart_next.json | jq '.command'
cat data/roadmap/status.json | jq '.data.missions_count'
```

5. (Optional) Crontab refresh every 15 minutes
```
*/15 * * * * cd ~/roadmapai && bin/roadmap_panels.sh all >> logs/panel_refresh.log 2>&1
```

## Reference JSON Envelope
```
{
  "roadmap_version": "0.3.0",
  "timestamp": "2025-01-15T14:32:00Z",
  "command": "smart next",
  "data": {...},
  "metadata": {
    "missions_count": 2,
    "steps_total": 8,
    "steps_completed": 3,
    "steps_remaining": 5,
    "energy_input": 5
  }
}
```

## Known Issues
- `roadmap_python.sh` in mission-control repo currently lacks support for new commands (status/report); either update script or use `roadmap_panels.sh` directly.
- Direct writes to ~/roadmapai/bin/config were blocked; manual copy required.

