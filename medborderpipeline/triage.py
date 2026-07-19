"""AI triage of detected changes, via the Anthropic API.

Boundaries (written into the SOP as policy):
  * The AI only classifies a diff (substantive vs cosmetic) and drafts a note
    for the human reviewer. Its output is labelled DRAFT everywhere.
  * The AI never verifies regulatory content and its text is never published.
  * If no API key is configured, or the call fails, every change is treated
    as substantive and routed to the reviewer — the safe default. AI can only
    demote noise, never approve content.
"""

import os
import json

import requests

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = (
    "You triage changes detected on official government web pages about "
    "bringing personal medications across borders. You are given a text diff. "
    "Classify it and draft a short note for a human clinical reviewer who will "
    "verify everything against the official source themselves.\n\n"
    "Classification rules:\n"
    "- 'substantive': the rule itself may have changed — permitted quantities, "
    "permit or certificate requirements, prohibited substances, penalties, "
    "documentation, application procedures, contact points for permits.\n"
    "- 'cosmetic': navigation, dates/timestamps, styling, unrelated news items, "
    "cookie banners, wording changes with no regulatory meaning.\n"
    "If you are unsure, choose 'substantive'.\n\n"
    "If the diff is not in English, add a brief working translation of the "
    "relevant changed lines in the note, marked as machine translation.\n\n"
    "Respond with ONLY a JSON object, no markdown fences, no preamble:\n"
    '{"classification": "substantive" or "cosmetic", '
    '"note": "2-4 sentence draft note for the reviewer"}'
)


def triage_change(country_name: str, diff_excerpt: str) -> dict:
    """Classify one diff. Returns {'classification': ..., 'note': ..., 'ai': bool}."""
    fallback = {
        "classification": "substantive",
        "note": "AI triage unavailable — routed to reviewer by default. "
                "Review the diff and the official source directly.",
        "ai": False,
    }
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return fallback
    try:
        resp = requests.post(
            API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": MODEL,
                "max_tokens": 500,
                "system": SYSTEM_PROMPT,
                "messages": [{
                    "role": "user",
                    "content": (
                        f"Country: {country_name}\n\n"
                        f"Diff of the official source page text:\n{diff_excerpt[:6000]}"
                    ),
                }],
            },
            timeout=60,
        )
        if resp.status_code != 200:
            return fallback
        data = resp.json()
        text = "".join(
            block.get("text", "") for block in data.get("content", [])
            if block.get("type") == "text"
        )
        text = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)
        classification = parsed.get("classification", "substantive")
        if classification not in ("substantive", "cosmetic"):
            classification = "substantive"
        note = str(parsed.get("note", "")).strip() or fallback["note"]
        return {"classification": classification, "note": note, "ai": True}
    except Exception:
        return fallback
