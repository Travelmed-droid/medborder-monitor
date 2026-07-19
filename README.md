# Cross-Border Medication Monitor

A human-in-the-loop system that monitors official government pages on bringing
personal medications across borders, uses AI to triage detected changes, routes
substantive changes to a clinician reviewer, and publishes a static signpost
page from **verified entries only**.

> **Governance principle:** *AI proposes, a human disposes.* No AI output is
> ever published. Every summary on the public page is verified by a named
> reviewer against the official source, and carries a "last verified" date.
> The official link is the answer; summaries are orientation only.

## What's here

| Path | Purpose |
|------|---------|
| `registry.json` | The list of monitored countries: authority, official URL, verification status. **The reviewer edits this file.** |
| `medborderpipeline/fetcher.py` | Polite fetch + text extraction of source pages. |
| `medborderpipeline/state.py` | Plain-JSON state, snapshots, diffing. |
| `medborderpipeline/triage.py` | Claude API triage (substantive vs cosmetic). Draft-only. |
| `medborderpipeline/alerter.py` | Writes reviewer alerts (become GitHub Issues). |
| `medborderpipeline/site.py` | Builds the static page into `docs/`. |
| `medborderpipeline/run.py` | Runs the full cycle. |
| `.github/workflows/monitor.yml` | Weekly schedule, alerts, and Pages deploy. |
| `docs/DEPLOYMENT_GUIDE.md` | **Start here** — plain-language setup. |

## Quick start

See `docs/DEPLOYMENT_GUIDE.md`. In short: create a public GitHub repo, upload
these files, add an `ANTHROPIC_API_KEY` secret (optional but recommended), set
Pages source to "GitHub Actions", enable read/write workflow permissions, then
run the workflow once from the Actions tab.

## Run locally (optional)

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...      # optional
python -m medborderpipeline.run      # full cycle
python -m medborderpipeline.run --site   # rebuild page only
```

## Safety boundaries (write these into the SOP)

AI **may**: classify a diff, draft a reviewer note, draft a working
translation, extract text from source PDFs, assist project documentation.

AI **may not**: verify regulatory content, publish anything, generate
citations to rules it has not been shown, or answer individual traveller
questions.

## Status

Demonstration pilot maintained by an individual pharmacist. Not an official
ISTM or government resource. Intended to become an ISTM-governed member resource
under a signed roles matrix (see the Project Charter).
