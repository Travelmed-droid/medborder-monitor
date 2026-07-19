"""Alerting. Substantive changes are written as Markdown alert files that a
GitHub Actions step turns into a GitHub Issue (the reviewer's queue). This
needs no email server and no secrets beyond the repo's own token.

Each alert contains the AI draft note, the diff excerpt, and the official
source link. The reviewer verifies against the source, edits the registry,
and closes the issue — the one step never automated.
"""

from pathlib import Path
from datetime import datetime, timezone

ALERT_DIR = Path("state/alerts")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def write_alert(country: dict, event: dict) -> Path:
    """Write one Markdown alert for a substantive change. Returns the path."""
    ALERT_DIR.mkdir(parents=True, exist_ok=True)
    code = country["code"]
    path = ALERT_DIR / f"{_stamp()}-{code}.md"

    ai_flag = "AI-triaged" if event.get("ai_triaged") else "no AI triage (default routing)"
    body = f"""# Review needed: {country['name']} ({code})

**Detected:** {event['detected']}
**Classification:** {event['classification']} ({ai_flag})
**Authority:** {country['authority']}
**Official source:** {country['url']}

## DRAFT note (AI-generated — verify before trusting)

> {event.get('ai_note_draft') or '(none)'}

## What the reviewer must do

1. Open the official source above and read the relevant section yourself.
2. Decide what actually changed (or mark this alert as noise).
3. If the rule changed, update `registry.json` for `{code}`:
   - set `last_verified` to today (YYYY-MM-DD)
   - write `verified_summary` in your own words
4. Commit the change. The site rebuilds from verified entries only.
5. Close this issue.

<details>
<summary>Diff excerpt (official source page text)</summary>

```diff
{event.get('diff_excerpt') or '(no diff captured)'}
```
</details>

---
*AI proposes, a human disposes. Nothing above is published to the resource
until a reviewer verifies it against the official source.*
"""
    path.write_text(body, encoding="utf-8")
    return path


def clear_alerts() -> None:
    """Remove processed alert files (called after the workflow opens issues)."""
    if ALERT_DIR.exists():
        for f in ALERT_DIR.glob("*.md"):
            f.unlink()
