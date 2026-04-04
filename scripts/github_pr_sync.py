#!/usr/bin/env python3
"""
GitHub PR Lane — Sync PRs to Roadmap missions
Usage: python scripts/github_pr_sync.py
"""
import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from github import Github, GithubException

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "panel_output" / "pr_lane.json"

def main():
    # Check for token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        error = {
            "roadmap_version": "0.3.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": "github-pr-sync",
            "data": {"error": "GITHUB_TOKEN not set"},
            "metadata": {"status": "blocked"}
        }
        OUTPUT.parent.mkdir(exist_ok=True)
        OUTPUT.write_text(json.dumps(error, indent=2))
        print("❌ GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Connect to GitHub
        g = Github(token)
        repo = g.get_repo("JarvisATeam/roadmap-ai")
        
        # Fetch open PRs
        prs = list(repo.get_pulls(state="open", sort="updated", direction="desc"))
        
        # Build PR data
        pr_data = []
        for pr in prs[:20]:  # Last 20 PRs
            pr_data.append({
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "author": pr.user.login,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat(),
                "url": pr.html_url,
                "labels": [label.name for label in pr.labels],
                "mergeable": pr.mergeable,
                "draft": pr.draft
            })
        
        # Generate output
        output = {
            "roadmap_version": "0.3.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": "github-pr-sync",
            "data": {
                "repository": "JarvisATeam/roadmap-ai",
                "open_prs": len(prs),
                "pull_requests": pr_data
            },
            "metadata": {
                "status": "success",
                "pr_count": len(pr_data),
                "rate_limit_remaining": g.rate_limiting[0]
            }
        }
        
        OUTPUT.parent.mkdir(exist_ok=True)
        OUTPUT.write_text(json.dumps(output, indent=2))
        
        print(f"✅ Synced {len(pr_data)} PRs")
        print(f"   Output: {OUTPUT}")
        return 0
        
    except GithubException as e:
        error = {
            "roadmap_version": "0.3.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": "github-pr-sync",
            "data": {"error": str(e)},
            "metadata": {"status": "failed"}
        }
        OUTPUT.parent.mkdir(exist_ok=True)
        OUTPUT.write_text(json.dumps(error, indent=2))
        print(f"❌ GitHub API error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
