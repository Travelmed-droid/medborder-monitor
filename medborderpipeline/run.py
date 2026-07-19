"""Entry point. Run the full weekly cycle, or just rebuild the site.

Usage:
  python -m medborderpipeline.run          # full cycle: check, triage, alert, build
  python -m medborderpipeline.run --site   # rebuild the static site only
"""

import sys
import json
from pathlib import Path

from . import fetcher, state, triage, alerter, site


def load_registry(path="registry.json") -> list:
    return json.loads(Path(path).read_text(encoding="utf-8"))["countries"]


def run_cycle() -> None:
    countries = load_registry()
    st = state.load_state()
    substantive = cosmetic = failures = 0

    for c in countries:
        code, name, url = c["code"], c["name"], c["url"]
        print(f"[check] {code} {name}")
        result = fetcher.fetch(url)

        if not result["ok"]:
            failures += 1
            state.record_check(st, code, ok=False, h=None, error=result["error"])
            print(f"        fetch failed: {result['error']}")
            continue

        new_text, new_hash = result["text"], result["hash"]
        prev = st["countries"].get(code, {})
        prev_hash = prev.get("last_hash")
        old_text = state.read_snapshot(code)

        state.record_check(st, code, ok=True, h=new_hash, error=None)
        state.write_snapshot(code, new_text)

        if prev_hash is None:
            print("        baseline stored (first run)")
            continue
        if new_hash == prev_hash:
            print("        no change")
            continue

        excerpt = state.diff_excerpt(old_text or "", new_text)
        t = triage.triage_change(name, excerpt)
        event = state.record_change(code, name, excerpt, t)

        if t["classification"] == "substantive":
            substantive += 1
            path = alerter.write_alert(c, event)
            print(f"        SUBSTANTIVE change -> alert {path.name}")
        else:
            cosmetic += 1
            print("        cosmetic change (logged, not routed)")

    state.save_state(st)
    site.build_site()
    print(f"\nDone. substantive={substantive} cosmetic={cosmetic} fetch_failures={failures}")
    print("Site rebuilt at docs/index.html")


def main() -> None:
    if "--site" in sys.argv:
        out = site.build_site()
        print(f"Site rebuilt at {out}")
        return
    run_cycle()


if __name__ == "__main__":
    main()
