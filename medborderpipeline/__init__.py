"""medborderpipeline — monitor official cross-border medication rule pages,
triage changes with AI assistance, alert a human reviewer, and publish a
static signpost page from verified entries only.

Governance principle: AI proposes, a human disposes. Nothing on the public
page is AI-generated; summaries appear only after a named reviewer verifies
them against the official source.
"""

__version__ = "1.0.0"

USER_AGENT = (
    "medborder-monitor/1.0 (+non-commercial travel-health research; "
    "monitors official government pages for changes; contact via repository)"
)

DISCLAIMER = (
    "This tool monitors official government sources for changes to "
    "cross-border medication import rules and links to those sources. It does "
    "not provide legal or travel-health advice and does not authorise carrying "
    "any medication across any border. Rules are set and enforced by national "
    "authorities and change without notice; the authoritative source is always "
    "the destination authority's own published rule. Any summary shown is "
    "orientation only and may be out of date. Travellers and clinicians must "
    "confirm requirements directly with the relevant destination authority "
    "before travel."
)
