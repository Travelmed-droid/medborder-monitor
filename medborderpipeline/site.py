"""Generate the static signpost page into docs/ for GitHub Pages.

Design: a clinician's reference, not a marketing page. The organising idea is
verification freshness — every country card leads with when it was last
checked against its official source, because that is the single fact a
clved user needs to judge how far to trust the entry. Palette and type are
chosen to read as an instrument panel: deep slate, a single verification-green
signal, warm paper. The official link is always the primary action.
"""

import json
import html
from pathlib import Path
from datetime import datetime, timezone

from . import DISCLAIMER

DOCS = Path("docs")


def _esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def build_site(registry_path: str = "registry.json",
               changelog_path: str = "state/changelog.json") -> Path:
    reg = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    countries = reg["countries"]

    changelog = []
    cl = Path(changelog_path)
    if cl.exists():
        changelog = json.loads(cl.read_text(encoding="utf-8"))

    verified = sum(1 for c in countries if c.get("last_verified"))
    total = len(countries)
    built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    cards = "\n".join(_card(c) for c in sorted(countries, key=lambda x: x["name"]))
    recent = [e for e in changelog if e.get("reviewed")][:8]
    changerows = "\n".join(
        f'<li><span class="cl-date">{_esc(e.get("detected",""))}</span>'
        f'<span class="cl-country">{_esc(e.get("country",""))}</span></li>'
        for e in recent
    ) or '<li class="cl-empty">No verified changes recorded yet.</li>'

    doc = _TEMPLATE.format(
        verified=verified, total=total, built=built,
        cards=cards, changerows=changerows, disclaimer=_esc(DISCLAIMER),
    )
    DOCS.mkdir(exist_ok=True)
    out = DOCS / "index.html"
    out.write_text(doc, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    return out


def _card(c: dict) -> str:
    verified = bool(c.get("last_verified"))
    state_cls = "verified" if verified else "unverified"
    if verified:
        badge = f'<span class="badge ok">Verified {_esc(c["last_verified"])}</span>'
        summary = f'<p class="summary">{_esc(c["verified_summary"])}</p>' if c.get("verified_summary") else ""
    else:
        badge = '<span class="badge pending">Not yet verified</span>'
        summary = '<p class="summary muted">Not yet verified by a reviewer. Use the official source directly.</p>'

    fetch_err = c.get("fetch_error")
    err = f'<p class="fetcherr">Source fetch issue at last check: {_esc(fetch_err)}</p>' if fetch_err else ""

    return f"""<article class="card {state_cls}">
  <header>
    <span class="flag">{_esc(c["code"])}</span>
    <h3>{_esc(c["name"])}</h3>
    {badge}
  </header>
  <p class="authority">{_esc(c["authority"])}</p>
  {summary}
  {err}
  <a class="src" href="{_esc(c["url"])}" target="_blank" rel="noopener">Open official source &rarr;</a>
</article>"""


_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cross-Border Medication Rules — Monitoring Demonstration</title>
<style>
  :root {{
    --paper:#F5F2EC; --ink:#1B2A32; --slate:#24424E; --line:#D8D2C6;
    --ok:#2E7D5B; --okbg:#E3F0E8; --pend:#9A7B3F; --pendbg:#F3EAD5;
    --muted:#6B7A80;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
    font-family:"Iowan Old Style","Palatino Linotype",Georgia,serif; line-height:1.5; }}
  .wrap {{ max-width:1080px; margin:0 auto; padding:0 20px; }}
  header.top {{ border-bottom:3px solid var(--slate); padding:34px 0 20px; }}
  .eyebrow {{ font-family:ui-monospace,"SF Mono",Menlo,monospace; font-size:12px;
    letter-spacing:.18em; text-transform:uppercase; color:var(--slate); margin:0 0 8px; }}
  h1 {{ font-size:2.1rem; margin:0 0 6px; letter-spacing:-.01em; }}
  .sub {{ color:var(--muted); margin:0; max-width:60ch; }}
  .meter {{ display:flex; gap:26px; margin:22px 0 4px; flex-wrap:wrap; align-items:baseline; }}
  .meter .n {{ font-size:2rem; font-weight:700; color:var(--slate);
    font-family:ui-monospace,Menlo,monospace; }}
  .meter .l {{ font-size:13px; color:var(--muted); }}
  .demo {{ background:var(--pendbg); border:1px solid #E4D2A8; color:#5F4A1E;
    padding:12px 16px; border-radius:8px; margin:20px 0; font-size:.95rem; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
    gap:16px; margin:26px 0; }}
  .card {{ background:#fff; border:1px solid var(--line); border-radius:12px;
    padding:18px; display:flex; flex-direction:column; gap:8px; }}
  .card.verified {{ border-left:5px solid var(--ok); }}
  .card.unverified {{ border-left:5px solid var(--pend); }}
  .card header {{ display:flex; align-items:center; gap:10px; margin:0; border:0; padding:0; }}
  .flag {{ font-family:ui-monospace,Menlo,monospace; font-weight:700; font-size:.8rem;
    background:var(--slate); color:#fff; padding:3px 7px; border-radius:5px; }}
  .card h3 {{ font-size:1.15rem; margin:0; flex:1; }}
  .badge {{ font-size:.72rem; padding:3px 9px; border-radius:20px; white-space:nowrap;
    font-family:ui-monospace,Menlo,monospace; }}
  .badge.ok {{ background:var(--okbg); color:var(--ok); }}
  .badge.pending {{ background:var(--pendbg); color:var(--pend); }}
  .authority {{ font-size:.9rem; color:var(--slate); margin:0; font-weight:600; }}
  .summary {{ font-size:.92rem; margin:2px 0; }}
  .summary.muted, .muted {{ color:var(--muted); }}
  .fetcherr {{ font-size:.8rem; color:#A6552B; margin:0; }}
  .src {{ margin-top:auto; font-family:ui-monospace,Menlo,monospace; font-size:.85rem;
    color:var(--slate); text-decoration:none; font-weight:700; padding-top:6px; }}
  .src:hover {{ text-decoration:underline; }}
  .cols {{ display:grid; grid-template-columns:2fr 1fr; gap:28px; margin:10px 0 40px; }}
  @media (max-width:760px) {{ .cols {{ grid-template-columns:1fr; }} }}
  .panel h2 {{ font-size:1rem; text-transform:uppercase; letter-spacing:.08em;
    color:var(--slate); border-bottom:1px solid var(--line); padding-bottom:6px; }}
  ul.cl {{ list-style:none; padding:0; margin:0; }}
  ul.cl li {{ display:flex; gap:12px; padding:7px 0; border-bottom:1px dotted var(--line);
    font-size:.88rem; }}
  .cl-date {{ font-family:ui-monospace,Menlo,monospace; color:var(--muted); }}
  .cl-empty {{ color:var(--muted); }}
  .disclaimer {{ background:#fff; border:1px solid var(--line); border-radius:12px;
    padding:18px 20px; font-size:.86rem; color:var(--ink); }}
  footer {{ border-top:3px solid var(--slate); padding:18px 0 50px; color:var(--muted);
    font-size:.82rem; }}
  a {{ color:var(--slate); }}
</style>
</head>
<body>
<header class="top"><div class="wrap">
  <p class="eyebrow">Travel Health · Monitoring Demonstration</p>
  <h1>Cross-border medication rules</h1>
  <p class="sub">A monitored index of official government sources on bringing personal
  medications across borders. The link is the answer; summaries are orientation only.</p>
  <div class="meter">
    <span><span class="n">{verified}</span> <span class="l">verified entries</span></span>
    <span><span class="n">{total}</span> <span class="l">countries monitored</span></span>
    <span><span class="l">Page built {built}</span></span>
  </div>
</div></header>

<div class="wrap">
  <div class="demo"><strong>Demonstration pilot.</strong> This page is a working
  prototype maintained by an individual pharmacist, not an official ISTM or
  government resource. Do not rely on it for travel decisions. Always confirm with
  the destination authority via the official links below.</div>

  <div class="grid">{cards}</div>

  <div class="cols">
    <section class="panel"><h2>How this works</h2>
      <p>Software checks each official source page on a schedule and detects when the
      text changes. An AI step sorts substantive rule changes from cosmetic ones and
      drafts a note. A pharmacist then verifies each change against the official
      source before any summary appears here. Cards without a verification date have
      not yet been checked by a reviewer — use the official link directly.</p>
      <p><strong>AI proposes; a human disposes.</strong> Nothing on this page is
      published from AI output alone.</p>
    </section>
    <aside class="panel"><h2>Recent verified changes</h2>
      <ul class="cl">{changerows}</ul>
    </aside>
  </div>

  <div class="disclaimer">{disclaimer}</div>
</div>

<footer><div class="wrap">
  Monitoring demonstration · built with the medborder pipeline ·
  AI-assisted change triage, human-verified publication.
</div></footer>
</body>
</html>"""
