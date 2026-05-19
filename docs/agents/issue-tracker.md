# Issue tracker: Local Markdown

Issues and PRDs for this repo live as markdown files inside `.planning/`, alongside the rest of the GSD workflow state. GitHub Issues are not used — this keeps strategic and tactical tracking on one surface (see CONTEXT.md for the Vault / Canonical / Drift / Reconciliation vocabulary).

## Layout

- **General issues** — `.planning/issues/<feature-slug>/<NN>-<slug>.md`, numbered from `01`. Each `<feature-slug>` directory may optionally contain a `PRD.md` describing the feature as a whole.
- **Reconciliation findings** (Drift surfaced by Verification) — `.planning/reconciliation/<vendor>/<NN>-<slug>.md`. The per-Vendor split mirrors the per-Vendor gating policy for v2 Reconciliation work: Elexon, ENTSO-E, ENTSO-G, GIE, NESO, Open-Meteo each get their own subdirectory.
- **Index files** — optional but recommended once a directory holds more than ~5 entries. `INDEX.md` lists each finding by status.

## Conventions

- One issue per file. Filename starts with a two-digit ordinal, then a short kebab-case slug.
- Triage state lives in YAML frontmatter as a `status:` field. Use the role strings defined in `triage-labels.md` (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) plus `open` (default) and `closed` (when resolved without deletion).
- Comments and conversation history append to the bottom of the file under a `## Comments` heading. Sign each comment with an ISO date prefix (`2026-05-19:`).
- Closed issues stay in-tree as a historical record; do not delete them. Move them to a `closed/` subdirectory once the count gets noisy.

## File template

```markdown
---
status: open
created: 2026-05-19
tags: [drift, structural]              # optional, freeform
related: [PLAN-7, REQ-ENTSOE-02]       # optional cross-refs to GSD artefacts
---

# <Short title>

## Context

<What this finding is. For Reconciliation findings: which layer disagrees
with which, and which is the Canonical winner per CONTEXT.md.>

## Acceptance

<What "closed" looks like in concrete terms.>

## Comments

<empty until triage begins>
```

## When a skill says "publish to the issue tracker"

Create a new file under the appropriate directory:

- General work → `.planning/issues/<feature-slug>/<NN>-<slug>.md` (create the directory if needed)
- Reconciliation Drift findings → `.planning/reconciliation/<vendor>/<NN>-<slug>.md`

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path directly.

## When to consider flipping back to GitHub Issues

If any of the following becomes true, re-open this decision:

- A collaborator joins and they need to triage from outside the repo
- A verifier CI workflow needs to auto-create findings (`gh issue create` flips the tooling-cost balance)
- Active findings exceed ~100 and the markdown directory becomes hard to navigate
- Recruiter visibility on the public Issues tab becomes a stated PROJECT.md value

The reverse migration is harder than this one (history doesn't transfer cleanly), so don't flip casually — wait for a concrete trigger.
