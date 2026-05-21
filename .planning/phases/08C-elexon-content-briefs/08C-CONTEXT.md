# Phase 8C: Elexon content briefs (triangulated research for Claude-Design) - Context

**Gathered:** 2026-05-20
**Status:** Ready to execute
**Supersedes:** Phase 8B AI-port output (archived to `.planning/archive/08B-ai-ports/elexon/`); preserves the Phase 8B build-script override path

<domain>
## Phase Boundary

User direction change (2026-05-20): The Phase 8B AI-port output is acknowledged as **sub-optimal** in editorial quality. The new path is **Option C — Fully authored**: all 33 Elexon dataset pages will be hand-designed externally in Claude Design and dropped into `authored-pages/elexon/<slug>.html`. The orchestrator's (AI's) role shifts from rendering HTML to **preparing the content briefs** that Claude Design renders from.

A content brief is a structured markdown document, one per dataset, that triangulates three sources of truth:

1. **Vault**: `vault/elexon/<slug>.md` (already vendored locally; YAML frontmatter + structured sections — last-verified date, overview, API endpoint, silver layer, known issues, changelog)
2. **Gridflow codebase**: cross-repo at `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\` — Pydantic schemas (`src/gridflow/schemas/elexon.py`), silver transformers (`src/gridflow/silver/elexon/<slug>.py`), connector endpoints (`src/gridflow/connectors/elexon/endpoints.py`)
3. **Live vendor docs**: Elexon BMRS Swagger UI (`https://bmrs.elexon.co.uk/api-documentation/endpoint/...`) — fetched via WebFetch per dataset

When the three sources disagree (e.g., vault says column is non-nullable but gridflow code declares `Optional[str]`; or vendor docs show a new field the vault hasn't captured yet), the brief flags the discrepancy in its `discrepancies_found` frontmatter so the user can decide whether to (a) trust gridflow source-of-truth and update the vault, (b) trust vendor docs and update gridflow, or (c) ignore as cosmetic.

**In scope:**
- 33 Elexon content briefs at `content-briefs/elexon/<slug>.md`
- Per-brief recipe document (`08C-BRIEF-RECIPE.md`) defining the exact structure, voice, citation requirements, and discrepancy-reporting protocol
- Structural checks per brief (frontmatter completeness, all required sections present, schema row count matches gridflow Pydantic field count, sample data has citation, etc.)
- Master cross-reference index for the user: which datasets had which discrepancies, ready for triage

**Out of scope:**
- ENTSO-E briefs (Phase 9 — 49 datasets)
- Four-vendor briefs (Phase 10 — 81 datasets across ENTSO-G, GIE, NESO, Open-Meteo)
- Authoring the HTML pages themselves — that's user-side work in Claude Design
- Reverting the Phase 8B build-script override — kept (still useful for the 2 reference pages and future Claude-Design output)
- Reverting the Phase 8 Iteration-2 template changes — kept (still serves the 31 long-tail Elexon pages that haven't been Claude-Designed yet)
- Re-validating fuelhh/system_prices briefs against their existing Claude-Design outputs (would be valuable but adds turnaround; can be done later as a separate test)

</domain>

<decisions>
## Implementation Decisions

### Brief location

- **D-01:** **Top-level `content-briefs/<vendor>/<slug>.md`.** Sibling to `vault/`, `authored-pages/`, `site/`. Tracked in git. Not gitignored. Matches the project convention of "source content lives at the top level, derived output lives under `site/` (gitignored)."
  - **Why:** Discoverable at a glance, separates research output from planning state (`.planning/` is for GSD process, not for deliverable content), parallels `vault/` (the input) and `authored-pages/` (the output of Claude Design'ing).

### Triangulation rigor

- **D-02:** **Three sources mandatory, citations required, discrepancies surfaced.** For each schema column, the brief MUST cite gridflow Pydantic source (file:line). For each sample row, the brief MUST cite either a gridflow test fixture, a vendor curl response (with date), or document that the row is synthesized (and what constraints it respects). For each caveat, the brief MUST cite either vault Known Issues line, gridflow Implementation Delta line, or document that it's domain-knowledge derived.
  - **Why:** The user's pivot to Option C is motivated by quality. Triangulated content > single-source content > extrapolated content. Forcing citations keeps the agent honest; absence of citation is a structural-check failure.

### Discrepancy reporting

- **D-03:** **All discrepancies flagged in frontmatter, never silently resolved.** When vault says X and gridflow says Y, the brief's frontmatter `discrepancies_found:` lists the discrepancy (with both sources + the orchestrator's recommendation). The brief body uses the **gridflow value** as the source of truth (per PROJECT.md SoT hierarchy: gridflow code > live API > vault > on-site), but flags the vault delta for downstream triage (potentially looping back to Phase 7 reconciliation).
  - **Why:** Silent resolution masks real Vault drift. Phase 7 just closed 40 reconciliation findings; this phase should not reintroduce un-flagged drift. The frontmatter discrepancy log becomes the input to a Phase 7-style mini-reconciliation if patterns emerge.

### Editorial voice

- **D-04:** **Brand-aligned per CLAUDE.md: editorial-quiet, cream + Fraunces aesthetic, domain depth over polish, no SaaS framing, no "live" indicators.** The brief's editorial layer (short tagline, lede, overview prose, caveats) must use voice samples already in the codebase: `authored-pages/elexon/fuelhh.html` (Claude-Design output), `authored-pages/elexon/system_prices.html` (AI-port, verified). Specifically:
  - Tagline pattern: `{noun phrase} {italic-accent ending}.` (5-10 words)
  - Lede: 2-4 sentences, concrete (no marketing voice), opens with what the dataset IS, mentions canonical use
  - Overview: 3 paragraphs (what / how-fetched / cadence), inline `<code>` chips for identifiers
  - Caveats: numbered, concrete, with code identifiers inline; tells reader something they'd otherwise discover the hard way

### Execution model

- **D-05:** **Single background opus-4.7 agent, sequential per-dataset, atomic commit per brief.** Quality > throughput. Opus 4.7 (not sonnet) because content briefs are research+synthesis = reasoning-intensive. Sequential not parallel because cross-brief voice consistency matters (4 agents producing 8 briefs each = 4 different voice variants).
  - **Why:** The user's pivot was triggered by sonnet's AI-port quality being sub-optimal. Switching to opus + sequential + per-brief verification trades execution time for output quality. Background = doesn't block user's terminal; can run overnight again if needed.

</decisions>

<specifics>
## Provisional Implementation Notes

### Directory structure post-phase

```
content-briefs/
└── elexon/
    ├── agpt.md
    ├── agws.md
    ├── atl.md
    ├── bmunits_reference.md
    ├── boal.md
    ... (33 total, one per vault/elexon/*.md)
    └── windfor.md
```

### Brief frontmatter shape

```yaml
---
slug: <slug>
vendor: elexon
vendor_label: Elexon BMRS
api_code: <FROM_GRIDFLOW_CONNECTOR_OR_VAULT_H1>
last_verified: <FROM_VAULT_FRONTMATTER>
sources_consulted:
  - vault/elexon/<slug>.md
  - gridflow/src/gridflow/schemas/elexon.py::<PydanticClassName>
  - gridflow/src/gridflow/silver/elexon/<slug>.py::<TransformerClassName>
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (relevant function)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/...
discrepancies_found:
  - source_a: "vault Known-Issues #2"
    source_a_says: "..."
    source_b: "gridflow schemas/elexon.py L142"
    source_b_says: "..."
    orchestrator_recommendation: "<trust gridflow | trust vault | needs Phase-7 mini-recon>"
  - (or empty list if none found)
ready_for_claude_design: true
checked_at: 2026-05-20T...Z
---
```

### Per-brief structural checks

After writing each brief, the executor verifies:

1. Frontmatter parses as valid YAML
2. `sources_consulted` has ≥3 entries (vault + at least one gridflow file + at least vendor docs URL or note about why unavailable)
3. `discrepancies_found` is a list (empty list is OK; absent key is a failure — must explicitly declare none found)
4. All required sections present (see recipe): Editorial / Hero metadata / Stats strip / Sidebar / Overview / Sample chart / Schema / Sample data / Dataset-specific or noted as omitted / API & ingestion / Caveats / Related
5. Schema section has at least N rows where N = field count in the Pydantic class (grep gridflow source file for `class <Name>(BaseModel):` body)
6. Every schema row cites file:line in gridflow source
7. Every sample-data row has a citation (test fixture, vendor curl date, or "synthesised — respects constraints X, Y")
8. Every caveat cites its source
9. Body uses inline `<code>` chip syntax (matches Claude-Design pattern) — at least 5 occurrences per brief on average
10. Tagline matches pattern `{phrase} {phrase-with-italic-accent}.` (verifiable by regex)
11. No vault content quoted verbatim without attribution
12. ready_for_claude_design: true is set only if all checks pass

Failures append to `.planning/phases/08C-elexon-content-briefs/BRIEF-LOG.md`, no commit, continue to next.

</specifics>

<questions_answered>
## Questions Resolved Before Planning

- **Q-1:** Where do briefs live? → `content-briefs/<vendor>/<slug>.md` (top-level, tracked) per D-01
- **Q-2:** What format? → Markdown with YAML frontmatter (D-02)
- **Q-3:** Voice/aesthetic? → Brand-aligned per CLAUDE.md, references = fuelhh.html + system_prices.html (D-04)
- **Q-4:** What about Phase 8B AI-ports? → Archived to `.planning/archive/08B-ai-ports/elexon/` (user choice 2026-05-20); fuelhh + system_prices stay in `authored-pages/` as reference
- **Q-5:** Scope? → Elexon only this phase (33 briefs); ENTSO-E + four-vendor are Phase 9 + Phase 10 respectively
- **Q-6:** What model executes? → Opus 4.7 in background (D-05)

## Questions Still Open

- **Q-A:** What happens to fuelhh + system_prices briefs? Are they retroactively produced for completeness, or skipped because their HTML output already exists? — **Decision in plan: produce briefs for them too (33 total, not 31)**. Validates the brief format against known-good Claude-Design output (fuelhh) and known-good AI-port output (system_prices).
- **Q-B:** What does the user do with discrepancies the briefs flag? → Out of scope for Phase 8C. The discrepancy log is the deliverable; triage is a future session.
- **Q-C:** When does Phase 7 mini-reconciliation re-open? → Only if Phase 8C surfaces >5 same-shape discrepancies. Tracked in the closure SUMMARY.

</questions_answered>

<deferred>
## Deferred to later phases

- Producing briefs for ENTSO-E (49) — Phase 9
- Producing briefs for ENTSO-G + GIE + NESO + Open-Meteo (81) — Phase 10
- Re-doing fuelhh + system_prices HTML via Claude Design from the new briefs (validation pass) — user-side work, scheduled separately
- Build-pipeline change to STOP rendering Elexon templated pages once all 33 are Claude-Designed — deferred until all 33 land in authored-pages/
</deferred>
