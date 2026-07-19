"""State persistence. Everything is plain JSON/text so the whole history is
readable and diffable inside the GitHub repository itself — no database
server, nothing binary."""

import json
import difflib
from pathlib import Path
from datetime import datetime, timezone

STATE_DIR = Path("state")
STATE_FILE = STATE_DIR / "state.json"
SNAP_DIR = STATE_DIR / "snapshots"
CHANGELOG = STATE_DIR / "changelog.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"countries": {}}


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def load_changelog() -> list:
    if CHANGELOG.exists():
        return json.loads(CHANGELOG.read_text(encoding="utf-8"))
    return []


def save_changelog(log: list) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    CHANGELOG.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


def snapshot_path(code: str) -> Path:
    return SNAP_DIR / f"{code}.txt"


def read_snapshot(code: str) -> str | None:
    p = snapshot_path(code)
    return p.read_text(encoding="utf-8") if p.exists() else None


def write_snapshot(code: str, text: str) -> None:
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path(code).write_text(text, encoding="utf-8")


def diff_excerpt(old: str, new: str, max_lines: int = 40) -> str:
    """Unified diff limited to a reviewable excerpt."""
    lines = list(
        difflib.unified_diff(
            old.splitlines(), new.splitlines(),
            fromfile="previous", tofile="current", lineterm="", n=2,
        )
    )
    if len(lines) > max_lines:
        lines = lines[:max_lines] + [f"... ({len(lines) - max_lines} more diff lines truncated)"]
    return "\n".join(lines)


def record_check(state: dict, code: str, *, ok: bool, h: str | None, error: str | None) -> dict:
    """Update per-country state after a fetch; returns the country record."""
    rec = state["countries"].setdefault(code, {})
    rec["last_checked"] = _now()
    if ok:
        rec["last_hash"] = h
        rec["fetch_error"] = None
    else:
        rec["fetch_error"] = error
    return rec


def record_change(code: str, name: str, excerpt: str, triage: dict) -> dict:
    """Append a change event to the changelog and return it."""
    log = load_changelog()
    event = {
        "code": code,
        "country": name,
        "detected": _now(),
        "classification": triage.get("classification", "unclassified"),
        "ai_triaged": bool(triage.get("ai")),
        "ai_note_draft": triage.get("note"),
        "diff_excerpt": excerpt,
        "reviewed": False,
    }
    log.insert(0, event)
    save_changelog(log[:500])
    return event
