"""Generate the static signpost page into docs/ for GitHub Pages.

Design language: an international travel document. The airmail-envelope
border, boarding-pass counters, and passport-stamp verification badges give
the page its travel identity, while the verification date stays the primary
signal — this is a clinician's instrument dressed as a passport, not a
tourism brochure. Self-contained: no external assets required.
"""

import json
import html
from pathlib import Path
from datetime import datetime, timezone

from . import DISCLAIMER

DOCS = Path("docs")

REGION = {
    "US":"Americas","CA":"Americas","MX":"Americas","BR":"Americas","CR":"Americas",
    "PA":"Americas","GT":"Americas","DO":"Americas","CO":"Americas","PE":"Americas",
    "CL":"Americas","AR":"Americas","EC":"Americas","UY":"Americas",
    "GB":"Europe","DE":"Europe","FR":"Europe","ES":"Europe","IT":"Europe","PT":"Europe",
    "GR":"Europe","NL":"Europe","AT":"Europe","CH":"Europe","BE":"Europe","IE":"Europe",
    "SE":"Europe","NO":"Europe","DK":"Europe","PL":"Europe","CZ":"Europe","HR":"Europe",
    "HU":"Europe","TR":"Europe",
    "JP":"Asia-Pacific","AU":"Asia-Pacific","SG":"Asia-Pacific","TH":"Asia-Pacific",
    "IN":"Asia-Pacific","ID":"Asia-Pacific","PH":"Asia-Pacific","CN":"Asia-Pacific",
    "KR":"Asia-Pacific","TW":"Asia-Pacific","HK":"Asia-Pacific","MY":"Asia-Pacific",
    "VN":"Asia-Pacific","NZ":"Asia-Pacific",
    "AE":"Middle East","SA":"Middle East","QA":"Middle East","KW":"Middle East",
    "BH":"Middle East","OM":"Middle East","JO":"Middle East","IL":"Middle East",
    "ZA":"Africa","EG":"Africa","MA":"Africa","KE":"Africa","TZ":"Africa",
    "GH":"Africa","NG":"Africa","ET":"Africa",
}


def _esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def _flag(code: str) -> str:
    """ISO code -> flag emoji (regional indicator pair). No image files needed."""
    try:
        return "".join(chr(0x1F1E6 + ord(ch) - 65) for ch in code.upper()[:2])
    except Exception:
        return "\U0001F3F3"


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
    regions = len({REGION.get(c["code"], "Other") for c in countries})
    built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    cards = "\n".join(_card(c) for c in sorted(countries, key=lambda x: x["name"]))
    recent = [e for e in changelog if e.get("reviewed")][:8]
    changerows = "\n".join(
        f'<li><span class="cl-date">{_esc(e.get("detected",""))}</span>'
        f'<span class="cl-country">{_esc(e.get("country",""))}</span></li>'
        for e in recent
    ) or '<li class="cl-empty">No verified changes recorded yet.</li>'

    doc = _TEMPLATE.format(
        verified=verified, total=total, regions=regions, built=built,
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
    region = REGION.get(c["code"], "Other")
    if verified:
        badge = f'<span class="stamp ok">VERIFIED<br><b>{_esc(c["last_verified"])}</b></span>'
        summary = f'<p class="summary">{_esc(c["verified_summary"])}</p>' if c.get("verified_summary") else ""
    else:
        badge = '<span class="stamp pending">PENDING<br><b>NOT VERIFIED</b></span>'
        summary = '<p class="summary muted">Not yet verified by a reviewer. Use the official source directly.</p>'

    fetch_err = c.get("fetch_error")
    err = f'<p class="fetcherr">\u26A0 Source fetch issue at last check: {_esc(fetch_err)}</p>' if fetch_err else ""

    return f"""<article class="card {state_cls}" data-name="{_esc(c["name"]).lower()} {_esc(c["code"]).lower()} {_esc(region).lower()}">
  <div class="cardtop">
    <span class="flag" role="img" aria-label="{_esc(c["name"])} flag">{_flag(c["code"])}</span>
    <div class="cardtitle">
      <h3>{_esc(c["name"])}</h3>
      <span class="region">{_esc(region)} \u00B7 {_esc(c["code"])}</span>
    </div>
    {badge}
  </div>
  <p class="authority">{_esc(c["authority"])}</p>
  {summary}
  {err}
  <a class="src" href="{_esc(c["url"])}" target="_blank" rel="noopener">\u2708 Open official source</a>
</article>"""


_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cross-Border Medication Rules \u2014 Travel Monitoring Demonstration</title>
<style>
  :root {{
    --paper:#F7F3EA; --card:#FFFDF8; --ink:#1B2A32; --slate:#24424E; --line:#DCD4C4;
    --ok:#2E7D5B; --okbg:#E3F0E8; --pend:#8A6D1F; --pendbg:#F5ECD3;
    --stampred:#B33A3A; --airblue:#2A5A8C; --muted:#6B7A80; --gold:#C9A227;
  }}
  * {{ box-sizing:border-box; }}
  html {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
  body {{ margin:0; background:var(--paper); color:var(--ink); line-height:1.5;
    font-family:"Iowan Old Style","Palatino Linotype",Georgia,serif; }}

  /* airmail par-avion border */
  .airmail {{ height:10px;
    background:repeating-linear-gradient(45deg,
      var(--stampred) 0 14px, #fff 14px 28px, var(--airblue) 28px 42px, #fff 42px 56px); }}

  .wrap {{ max-width:1120px; margin:0 auto; padding:0 20px; }}

  header.top {{ padding:30px 0 18px; border-bottom:3px double var(--slate); }}
  .eyebrow {{ font-family:ui-monospace,"SF Mono",Menlo,monospace; font-size:12px;
    letter-spacing:.22em; text-transform:uppercase; color:var(--stampred); margin:0 0 8px; }}
  .titlerow {{ display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; }}
  h1 {{ font-size:2.15rem; margin:0; letter-spacing:-.01em; }}
  .globe {{ font-size:1.6rem; }}
  .sub {{ color:var(--muted); margin:8px 0 0; max-width:64ch; }}

  /* boarding-pass counters */
  .passrow {{ display:flex; gap:14px; margin:20px 0 4px; flex-wrap:wrap; }}
  .pass {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
    padding:10px 18px 10px 14px; position:relative; overflow:hidden; min-width:150px; }}
  .pass::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:6px;
    background:var(--gold); }}
  .pass .n {{ font-size:1.7rem; font-weight:700; color:var(--slate);
    font-family:ui-monospace,Menlo,monospace; display:block; }}
  .pass .l {{ font-size:11px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted);
    font-family:ui-monospace,Menlo,monospace; }}

  .demo {{ background:var(--pendbg); border:1px dashed var(--pend); color:#5F4A1E;
    padding:12px 16px; border-radius:8px; margin:20px 0 16px; font-size:.95rem; }}

  .toolbar {{ display:flex; gap:10px; align-items:center; margin:0 0 16px; flex-wrap:wrap; }}
  .search {{ flex:1; min-width:230px; border:1px solid var(--line); border-radius:24px;
    padding:11px 18px; font-size:1rem; font-family:inherit; background:var(--card);
    color:var(--ink); outline:none; }}
  .search:focus {{ border-color:var(--slate); }}
  .hint {{ font-size:.8rem; color:var(--muted); font-family:ui-monospace,Menlo,monospace; }}

  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(310px,1fr));
    gap:16px; margin:0 0 26px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
    padding:16px 16px 14px; display:flex; flex-direction:column; gap:8px;
    box-shadow:0 1px 0 rgba(27,42,50,.04); }}
  .card.verified {{ border-left:5px solid var(--ok); }}
  .card.unverified {{ border-left:5px solid var(--pend); }}
  .cardtop {{ display:flex; align-items:flex-start; gap:10px; }}
  .flag {{ font-size:1.7rem; line-height:1; margin-top:2px; }}
  .cardtitle {{ flex:1; }}
  .card h3 {{ font-size:1.13rem; margin:0; }}
  .region {{ font-family:ui-monospace,Menlo,monospace; font-size:.68rem; letter-spacing:.08em;
    text-transform:uppercase; color:var(--muted); }}

  /* passport stamps */
  .stamp {{ font-family:ui-monospace,Menlo,monospace; font-size:.58rem; letter-spacing:.06em;
    text-align:center; line-height:1.5; padding:5px 9px; border-radius:8px;
    border:2px dashed; transform:rotate(3deg); white-space:nowrap; }}
  .stamp b {{ font-size:.66rem; }}
  .stamp.ok {{ color:var(--ok); border-color:var(--ok); background:var(--okbg); }}
  .stamp.pending {{ color:var(--pend); border-color:var(--pend); background:var(--pendbg);
    transform:rotate(-3deg); }}

  .authority {{ font-size:.88rem; color:var(--slate); margin:0; font-weight:600; }}
  .summary {{ font-size:.9rem; margin:0; }}
  .summary.muted, .muted {{ color:var(--muted); }}
  .fetcherr {{ font-size:.78rem; color:#A6552B; margin:0; }}
  .src {{ margin-top:auto; font-family:ui-monospace,Menlo,monospace; font-size:.84rem;
    color:var(--airblue); text-decoration:none; font-weight:700; padding-top:6px; }}
  .src:hover {{ text-decoration:underline; }}
  .noresults {{ display:none; color:var(--muted); font-style:italic; padding:14px 4px; }}

  .cols {{ display:grid; grid-template-columns:2fr 1fr; gap:28px; margin:6px 0 34px; }}
  @media (max-width:760px) {{ .cols {{ grid-template-columns:1fr; }} }}
  .panel h2 {{ font-size:.95rem; text-transform:uppercase; letter-spacing:.09em;
    color:var(--slate); border-bottom:2px solid var(--gold); padding-bottom:6px; }}
  ul.cl {{ list-style:none; padding:0; margin:0; }}
  ul.cl li {{ display:flex; gap:12px; padding:7px 0; border-bottom:1px dotted var(--line);
    font-size:.88rem; }}
  .cl-date {{ font-family:ui-monospace,Menlo,monospace; color:var(--muted); }}
  .cl-empty {{ color:var(--muted); }}
  .disclaimer {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
    padding:16px 20px; font-size:.85rem; }}
  footer {{ border-top:3px double var(--slate); margin-top:8px; padding:16px 0 26px;
    color:var(--muted); font-size:.8rem; }}
  a {{ color:var(--airblue); }}
</style>
</head>
<body>
<div class="airmail"></div>
<header class="top"><div class="wrap">
  <p class="eyebrow">\u2708 Travel Health \u00B7 Par Avion \u00B7 Monitoring Demonstration</p>
  <div class="titlerow">
    <span class="globe">\U0001F30D</span>
    <h1>Cross-border medication rules</h1>
  </div>
  <p class="sub">A monitored index of official government sources on bringing personal
  medications across borders. The link is the answer; summaries are orientation only.</p>
  <div class="passrow">
    <div class="pass"><span class="n">{total}</span><span class="l">Destinations</span></div>
    <div class="pass"><span class="n">{verified}</span><span class="l">Verified entries</span></div>
    <div class="pass"><span class="n">{regions}</span><span class="l">Regions</span></div>
    <div class="pass"><span class="n">\u2708</span><span class="l">Built {built}</span></div>
  </div>
</div></header>

<div class="wrap">
  <div class="demo"><strong>Demonstration pilot.</strong> This page is a working
  prototype maintained by an individual pharmacist, not an official ISTM or
  government resource. Do not rely on it for travel decisions. Always confirm with
  the destination authority via the official links below.</div>

  <div class="toolbar">
    <input class="search" id="q" type="search"
      placeholder="\U0001F50D Search destination \u2014 try &quot;Japan&quot;, &quot;Europe&quot;, or &quot;TH&quot;\u2026"
      oninput="filterCards()">
    <span class="hint" id="count"></span>
  </div>

  <div class="grid" id="grid">{cards}</div>
  <p class="noresults" id="noresults">No destinations match \u2014 try a country name, code, or region.</p>

  <div class="cols">
    <section class="panel"><h2>How this works</h2>
      <p>Software checks each official source page on a schedule and detects when the
      text changes. An AI step sorts substantive rule changes from cosmetic ones and
      drafts a note. A pharmacist then verifies each change against the official
      source before any summary appears here. Cards without a verification stamp have
      not yet been checked by a reviewer \u2014 use the official link directly.</p>
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
  \u2708 Monitoring demonstration \u00B7 built with the medborder pipeline \u00B7
  AI-assisted change triage, human-verified publication.
</div></footer>
<div class="airmail"></div>

<script>
function filterCards() {{
  var q = document.getElementById('q').value.trim().toLowerCase();
  var cards = document.querySelectorAll('#grid .card');
  var shown = 0;
  cards.forEach(function(c) {{
    var hit = !q || c.getAttribute('data-name').indexOf(q) !== -1;
    c.style.display = hit ? '' : 'none';
    if (hit) shown++;
  }});
  document.getElementById('noresults').style.display = shown ? 'none' : 'block';
  document.getElementById('count').textContent = q ? (shown + ' shown') : '';
}}
</script>
</body>
</html>"""
