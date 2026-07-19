"""Polite fetching of official source pages and plain-text extraction."""

import re
import time
import hashlib

import requests

from . import USER_AGENT

FETCH_DELAY_SECONDS = 3
TIMEOUT_SECONDS = 30

_TAG_STRIP = re.compile(r"<(script|style|noscript)[^>]*>.*?</\1>", re.S | re.I)
_TAGS = re.compile(r"<[^>]+>")
_WS = re.compile(r"[ \t]+")
_BLANKS = re.compile(r"\n{3,}")


def extract_text(html: str) -> str:
    """Strip HTML to whitespace-normalised text so cosmetic markup changes
    (attributes, scripts, styling) do not register as content changes."""
    text = _TAG_STRIP.sub(" ", html)
    text = _TAGS.sub("\n", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
    lines = [_WS.sub(" ", ln).strip() for ln in text.splitlines()]
    text = "\n".join(ln for ln in lines if ln)
    return _BLANKS.sub("\n\n", text).strip()


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch(url: str) -> dict:
    """Fetch one source page. Returns a dict with ok/text/hash or ok=False
    and an error string. Fetch failures are reported separately from content
    changes so a broken source is never mistaken for a stable rule."""
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en;q=0.9,*;q=0.5"},
            timeout=TIMEOUT_SECONDS,
        )
        time.sleep(FETCH_DELAY_SECONDS)
        if resp.status_code != 200:
            return {"ok": False, "error": f"HTTP {resp.status_code}"}
        text = extract_text(resp.text)
        if len(text) < 200:
            return {"ok": False, "error": "page returned too little text (possibly JS-rendered or blocked)"}
        return {"ok": True, "text": text, "hash": content_hash(text)}
    except requests.RequestException as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
