# Deployment Guide — Cross-Border Medication Monitor

A step-by-step setup you can complete in an afternoon. No terminal or coding
experience needed. Everything runs free on GitHub.

---

## What you are setting up

- A **monitor** that checks each country's official medication-import page on a
  schedule (weekly) and notices when the text changes.
- An **AI triage step** (Claude) that sorts real rule changes from cosmetic
  website edits and drafts a note — but never publishes anything.
- A **reviewer queue**: substantive changes open a GitHub *Issue* for you to
  verify against the official source.
- A **public page** (GitHub Pages) that shows only entries you have verified,
  each with a "last verified" date, plus links to every official source.

Guiding rule, kept everywhere: **AI proposes, a human disposes.** Nothing
reaches the page without your sign-off.

---

## One-time setup

### Step 1 — Create a GitHub account
Go to github.com and sign up (free). Verify your email.

### Step 2 — Create the repository
1. Click the **+** (top right) → **New repository**.
2. Name it, e.g. `medborder-monitor`.
3. Choose **Public** (required for free GitHub Pages).
4. Click **Create repository**.

### Step 3 — Upload the project files
1. On the new repo page, click **uploading an existing file**.
2. Drag in *all* the files and folders from this project (the
   `medborderpipeline` folder, `.github` folder, `registry.json`,
   `requirements.txt`, `.gitignore`, and the `state` and `docs` folders).
   - Tip: if drag-and-drop misses the folders, upload the loose files first,
     then use **Add file → Upload files** again for each folder's contents.
3. At the bottom, click **Commit changes**.

### Step 4 — Add your Claude API key as a secret
1. Get a key from console.anthropic.com (Settings → API Keys).
2. In your repo: **Settings → Secrets and variables → Actions → New repository secret**.
3. Name it exactly `ANTHROPIC_API_KEY`. Paste your key as the value. Save.
   - If you skip this, the system still works — it just routes *every* change
     to you for review instead of pre-filtering. Safe, just more manual.

### Step 5 — Turn on GitHub Pages
1. **Settings → Pages**.
2. Under **Build and deployment → Source**, choose **GitHub Actions**.

### Step 6 — Allow Actions to run
1. **Settings → Actions → General**.
2. Under **Workflow permissions**, select **Read and write permissions**. Save.

---

## Running it

### First run (do this now)
1. Go to the **Actions** tab.
2. Click **Weekly medication-rule monitor** on the left.
3. Click **Run workflow → Run workflow**.
4. Wait ~2 minutes. The first run stores a baseline for every country and
   builds the page. No change-alerts appear on the first run (nothing to
   compare against yet).

### See your page
Your site is at:
`https://YOUR-USERNAME.github.io/medborder-monitor/`
Every country starts as **"Not yet verified"** — that is correct.

### From then on
The monitor runs itself every Monday. You do not need to do anything unless a
change is found.

---

## Your weekly job as reviewer (only when there's a change)

1. You get a GitHub **Issue** titled "Review needed: [country]".
2. Open it. Read the AI's DRAFT note and the diff — then **open the official
   source link and read it yourself**. This is the step that matters.
3. If a rule genuinely changed, edit `registry.json` (click the file →
   pencil icon):
   - set `"last_verified"` to today, e.g. `"2026-07-01"`
   - write `"verified_summary"` in your own words
   - **Commit changes**.
4. If it was just noise, simply close the Issue.
5. The page rebuilds automatically and now shows your verified entry.

That's it. Verifying one country takes a few minutes.

---

## Before you share the link publicly

- The page is labelled a **demonstration pilot** on purpose. Leave that banner
  in place until ISTM formally governs the resource. It protects you.
- Verify a handful of countries first (Japan, UAE, UK, Australia are good
  starters) so the demo shows real verified entries.
- Double-check each seeded official URL actually loads the rule page — some
  government sites reorganise. Fix any dead links in `registry.json`.

---

## Adjustments you might want

- **Check more/less often:** edit `.github/workflows/monitor.yml`, the `cron`
  line. `"0 13 * * 1"` means Mondays 13:00 UTC.
- **Add a country:** copy a block in `registry.json`, fill in the authority and
  official URL, commit. It appears as "Not yet verified" until you verify it.
- **Change wording/look of the page:** the template lives in
  `medborderpipeline/site.py`.

---

## If something doesn't work

- **Actions run failed (red X):** click the run to see which step. Most often
  it's Step 6 (permissions) not set, or a country URL that blocks automated
  fetching — the log names the country. Fetch failures show on the page as a
  small note and never masquerade as a rule.
- **Page 404s:** Pages can take a few minutes after the first successful run;
  confirm Step 5 is set to **GitHub Actions**.
- **No AI notes on alerts:** the `ANTHROPIC_API_KEY` secret name must match
  exactly. Without it everything still routes to you safely.
