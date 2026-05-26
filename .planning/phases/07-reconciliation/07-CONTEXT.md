# Phase 7: Reconciliation - Context

**Gathered:** 2026-05-19
**Status:** Ready for planning

<domain>
## Phase Boundary

A verified Vault layer trusted as the input for content phases. After Phase 7, content phases (8 — bug fix, 9 — ENTSO-E, 10 — four-vendor batch) build pages from a Vault we trust. Phase 7 is the new gating phase inserted at the start of v2 per ADR-0001, overriding the v1 "no upfront audit phase" decision.

In scope:
- Wrap `quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py` as the `gridflow-drift-check` console script. Rename file to `gridflow_drift_check.py`; fix the two Windows-specific portability blockers identified by drift research (the `args[0] = "curl.exe"` line at L180 and the hardcoded `C:\Users\Bobbo\...` default at L20-26).
- Run Verification across **all 6 Vendors** (Elexon · ENTSO-E · ENTSO-G · GIE · NESO · Open-Meteo). Emit a JSON report (machine) and a markdown report (human) and finding files under `.planning/reconciliation/<vendor>/<NN>-<slug>.md`.
- Triage every Drift finding into one of three buckets:
  - `status: open` → fixable in v2 via Vault edits.
  - `status: wontfix`, `reason: v3-candidate` → requires `gridflow` code changes (e.g. declaring new Pydantic classes), explicitly out of scope per PROJECT.md.
  - `status: needs-info`, `reason: defer-entitlement` → blocked on external (e.g. ENTSO-E API token entitlement); revisit at the affected content phase's discuss step.
- Land Vault edits for the `open` bucket in the upstream Vault (now version-controlled — see ADR-0002 and Component 4 below) and re-vendor into `gridflow-front-end/vault/<vendor>/`.
- Commit the upstream Vault to a new **private** GitHub repo: `EBentham/quant-vault`. No GitHub App auth; cross-repo CI integration explicitly deferred (ADR-0002).

Out of scope:
- Any content-phase work (Phase 8 — bug fix · Phase 9 — ENTSO-E full coverage · Phase 10 — four-vendor batch). Phase 7 only prepares the Vault layer.
- Closing the `manual_transformer_schema` cases — 58 ecosystem-wide, 22 of them Elexon — by declaring new Pydantic classes in `gridflow.schemas`. Triaged as `wontfix-v3` per PROJECT.md § Out of Scope and ADR-0001 Consequences.
- ENTSO-E entitlement procurement. The 33 ENTSO-E HTTP 401 cases are triaged as `needs-info` / `defer-entitlement`. The actual decision (extend access vs `skip-with-warn`) is deferred to Phase 9's discuss-phase, where it lands on content shape.
- Cross-repo automated drift CI (the "Day-7-caught vs Day-21-caught" benefit from drift-research worst-case scenario). Requires GitHub App auth which ADR-0002 explicitly rejects for v2.
- Pocock-style exploratory triage on the bug-fix phase: bug-fix (Phase 8) is now independent of Reconciliation per grill decision #3, so the GSD pre-planned flow runs on it as scheduled.

</domain>

<decisions>
## Implementation Decisions

### Vault is derivative; Reconciliation only edits derivative layers

- **D-01:** The Vault is a **derivative** documentation layer; the Canonical wins every disagreement. Drift always flows Canonical → Vault → Site. Reconciliation **only ever** fixes the derivative direction (Vault edits) — it never modifies `gridflow/src/gridflow/schemas/*.py`, `silver/**/*.py`, or `connectors/**/*.py`. Trust chain at verification time: `Live API → Canonical → Vault → Site`. Vendor docs are an authoring input upstream of Canonical, not in the trust hierarchy.
  - **Why:** Locked by `CONTEXT.md § Language` (project root) and `PROJECT.md § Source-of-truth hierarchy`; restated as binding decision #1 from the 2026-05-19 grill-with-docs session.
  - **How to apply:** Every Phase 7 finding produces a Vault edit (or a `wontfix-v3` deferral); zero `gridflow` repo edits are produced. If a finding's only resolution is a Canonical change, triage as `wontfix`, `reason: v3-candidate`.

### Reconciliation scope = the drift-detection research package, brought forward

- **D-02:** Phase 7 IS the drift-detection research package being executed, not a fresh design exercise. The MVP architecture from `.planning/research/post-v1/drift-detection/SUMMARY.md` and the concrete Drift instances in `DRIFT-SURFACES.md` are inputs, not suggestions.
  - **Why:** Binding decision #2 from the grill. The research was originally scoped for post-v2; ADR-0001 brings it forward because the alternative ("rely on `gridflow-build --check`") was found to be a category error — `--check` is an idempotence check, not a content-accuracy check.
  - **How to apply:** The planner reads `SUMMARY.md` and `DRIFT-SURFACES.md` before drafting plans. The verifier-wrap (`SUMMARY.md § Tooling Reality`), drift taxonomy (`DRIFT-SURFACES.md § 3`), and the existing in-tree examples (`DRIFT-SURFACES.md § 4`) are load-bearing. Q-DD-01 through Q-DD-17 in the research's "Open Decisions" section are **largely answered** by the grill and this CONTEXT.md (see Q-DD mapping in `<canonical_refs>` below); the planner only needs to resolve the residual ones.

### Per-Vendor gating; bug-fix is independent of Reconciliation

- **D-03:** Drift gates **per-Vendor**. The bug-fix phase (now Phase 8) does NOT depend on Reconciliation completing for any specific Vendor; it operates on the Jinja2 template / shared CSS / build script, none of which Phase 7 modifies.
  - **Why:** Binding decision #3 from the grill. The bug is a layout/typography issue in the rendering layer; Reconciliation is a content-accuracy issue in the Vault layer.
  - **How to apply:** ROADMAP dependency graph after renumber: `Phase 7 (Reconciliation) → Phase 9 (ENTSO-E) → Phase 10 (4-vendor batch)`. Phase 8 (bug fix) sits parallel to Phase 7 — could ship independently. Sequential 7 → 8 → 9 → 10 is still **recommended** to avoid merge churn on `vault/<vendor>/` snapshot vendoring, but only `Phase 7 → Phase 9` and `Phase 7 → Phase 10` are hard dependencies.

### All-Vendor Reconciliation done upfront, not interleaved per-Vendor

- **D-04:** Phase 7 verifies **all 6 Vendors at once**, not interleaved before each Vendor's content phase. Verify everything → triage everything → fix the open bucket → push Vault, in that order.
  - **Why:** Binding decision #4 from the grill (user revision over the originally-considered interleaved option in ADR-0001 Considered Options). User preference for a clean "verify everything → then build everything" split over a per-Vendor cadence.
  - **How to apply:** The verifier runs against all 6 Vendors in one execution; finding files for all 6 Vendors land under `.planning/reconciliation/<vendor>/` before any Vault fix is applied. The planner does not produce a Phase 7 sub-plan that runs Verification on just one Vendor.

### Sub-plans per logical step

- **D-05:** Phase 7 is decomposed into **four sub-plans** along logical step boundaries, not per-Vendor.
  - `07a` — Verifier wrap: rename `verify_curl_and_silver_schema.py` → `gridflow_drift_check.py`, fix the two Windows-specific blockers, expose as the `gridflow-drift-check` console script, add a `[drift]` extra in `pyproject.toml`.
  - `07b` — Run Verification across all 6 Vendors and triage: produce JSON + markdown reports; write finding files under `.planning/reconciliation/<vendor>/<NN>-<slug>.md`; classify each as `open` / `wontfix-v3` / `needs-info`/`defer-entitlement`.
  - `07c` — Fix the `open` bucket: land Vault edits for the load-bearing fixable findings (see `<specifics>` for the catalogue), re-vendor into `gridflow-front-end/vault/<vendor>/`, re-run `gridflow-drift-check` to confirm "no new Drift".
  - `07d` — Push Vault to private GitHub: create `EBentham/quant-vault`, push the reconciled Vault as the initial commit set, document the workflow in upstream Vault's `README.md`.
  - **Why:** Resolved during this discuss-phase. Sub-plans per logical step preserve focused commit history and let `07c` ship one Vendor at a time inside the plan without forcing a Vendor-level sub-plan boundary. Rejected alternatives: one monolithic plan (loses rollback granularity); per-Vendor sub-plans (creates near-empty plans for NESO / Open-Meteo if they have no findings).
  - **How to apply:** The planner produces `07a-PLAN.md`, `07b-PLAN.md`, `07c-PLAN.md`, `07d-PLAN.md` (or equivalent suffixes). Each sub-plan is an atomic commit-able unit. `07a` must complete before `07b`; `07b` must complete before `07c`; `07c` and `07d` can run in either order, though `07d` after `07c` is more natural (push the reconciled state, not the pre-fix state).

### ENTSO-E entitlement deferred to Phase 9

- **D-06:** The 33 ENTSO-E HTTP 401 cases are triaged in `07b` as `status: needs-info`, `reason: defer-entitlement`. The actual decision (extend ENTSO-E API access vs accept `skip-with-warn` for the affected datasets) is deferred to Phase 9's discuss-phase.
  - **Why:** Resolved during this discuss-phase. The entitlement question only binds on content shape, which Phase 9 owns. Pulling it forward into Phase 7 risks blocking Phase 7 completion on unbounded vendor lead-time (ENTSO-E entitlement requests are not 24-hour turnarounds). Drift research's Q-DD-04 default lean ("fix the API token first then enable fail-loud") was implicitly assuming entitlement could be acquired on demand; reality is unknown.
  - **How to apply:** Phase 7 emits 33 `needs-info` finding files for the ENTSO-E datasets currently returning 401, each pointing at Q-DD-04 / DRIFT-SURFACES § 4.4 as the source of analysis. Phase 9's discuss-phase reads those files and chooses the resolution path then. Phase 7 itself does **not** apply for additional ENTSO-E entitlement.

### Pocock skills for exploratory Reconciliation; GSD for pre-planned

- **D-07:** Phase 7's exploratory work uses the **Pocock skill set** — specifically `to-issues` (capture findings as local markdown) and `triage` (state-machine through finding classification). The pre-planned phases (8 — bug fix, 9 — ENTSO-E, 10 — 4-vendor batch) continue to use the standard GSD flow (`/gsd-plan-phase` → `/gsd-execute-phase`).
  - **Why:** Binding decision #5 from the grill. Phase 7 has an inherent open-endedness — we don't know exactly what the Verification will surface until we run it — so the Pocock skills' exploratory shape (capture → triage → act, with bucket-revision allowed) is a better fit than GSD's task-list-and-execute shape.
  - **How to apply:** The `07a` and `07d` plans use GSD execute (mechanical engineering tasks). The `07b` triage step uses the `triage` skill to walk findings through `needs-triage` → (`ready-for-agent` | `ready-for-human` | `wontfix`) state transitions. The `07c` fix step uses `to-issues` to capture per-finding context that wasn't pre-known.

### Issues live as local markdown, not GitHub Issues

- **D-08:** Reconciliation findings live as markdown under `.planning/reconciliation/<vendor>/<NN>-<slug>.md` (per-Vendor sub-directories), not as GitHub Issues. Same surface as the rest of the GSD planning state.
  - **Why:** Binding decision #6 from the grill (`docs/agents/issue-tracker.md` re-pointed at local markdown after Q5). Avoids splitting workflow context across two systems (planning in `.planning/`, findings in GitHub) and matches the user's existing single-context discipline (one `CONTEXT.md`, no Jira, no separate trackers).
  - **How to apply:** Every Verification finding produces a `.planning/reconciliation/<vendor>/<NN>-<slug>.md` file. The `<NN>` is a per-Vendor sequence number; `<slug>` describes the finding (e.g. `01-fuelhh-schema-table-missing-published-at.md`). Canonical labels per `docs/agents/triage-labels.md`: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. The `triage` skill's state machine drives transitions.

### Vault on private GitHub repo; no GitHub App auth

- **D-09:** The upstream Vault is committed to a new private GitHub repo: `EBentham/quant-vault`. No GitHub App auth is configured. Cross-repo automated drift CI is explicitly **not** a v2 deliverable.
  - **Why:** Binding decision #7 from the grill, locked in ADR-0002. Repo name resolved during this discuss-phase (default lean confirmed). The privacy choice keeps half-finished modelling notes off the recruiter visibility surface; skipping App auth saves the one-time setup cost the user judged not yet load-bearing.
  - **How to apply:** Plan `07d` creates the repo (gh CLI: `gh repo create EBentham/quant-vault --private --source=. --remote=origin`), pushes the reconciled Vault as the initial commits, and updates the vendoring workflow in `gridflow-front-end` to document that the snapshot under `vault/<vendor>/` is now sourced from this repo (the snapshot pattern from v1 is **preserved** — content phases still consume the vendored snapshot, not the upstream Vault directly).

### Vendor count stays at 6

- **D-10:** Vendor count remains **6** for Phase 7 scope: Elexon · ENTSO-E · ENTSO-G · GIE · NESO · Open-Meteo. The Site occasionally splits GIE into AGSI + ALSI as two sub-hubs, but the upstream Vendor count is unchanged; Phase 7 runs Verification against 6 Vendors. The AGSI/ALSI split is a Site-rendering decision owned by Phase 10.
  - **Why:** Drawn from `CONTEXT.md § Language` (Vendor entry) and the handoff's "7 vs 6 Vendor count" open item. No re-litigation needed — the answer is a no-op for Phase 7 (the split only affects UI in Phase 10).
  - **How to apply:** Verification iterates over 6 Vendor directories in `quant-vault/30-vendors/`. Finding files live under `.planning/reconciliation/elexon/`, `entsoe/`, `entsog/`, `gie/`, `neso/`, `openmeteo/`. If GIE has internal AGSI/ALSI organisation in the Vault, Verification respects it; Phase 7 does not normalise the split direction.

### Claude's Discretion

- Exact filenames for the four sub-plans (`07a-verifier-wrap-PLAN.md` vs `07-01-verifier-wrap-PLAN.md` vs other) — planner picks per project convention. The v1 archive uses `00-01-PLAN.md` numbering; consistent.
- Exact JSON schema for the Verification report. The existing `vault-curl-schema-validation.json` produced by `verify_curl_and_silver_schema.py` is the starting shape; the planner may extend keys (per-Vendor totals, run timestamp, version stamp) but should not refactor the existing keys downstream consumers rely on. See drift research Q-DD-17 for the precedent.
- Exact format of finding `.md` files under `.planning/reconciliation/<vendor>/`. Mandatory fields: `status:` (one of the five labels), `reason:` (free text, but uses canonical labels `v3-candidate` / `defer-entitlement` where applicable), and a body explaining the Drift instance with a reference back to a DRIFT-SURFACES § N.M example or a verifier finding ID. Optional fields: `assignee:`, `linked-pr:`, `closed-at:`. The planner finalises the template; the `to-issues` skill output is the natural source.
- Exact dependency-extras location for `[drift]` (Q-DD-16). The drift research default lean ("vault if vault has a `pyproject.toml`; else `gridflow-front-end`") applies; the planner verifies whether `quant-vault` has a `pyproject.toml` and picks accordingly. Either location is acceptable.
- Whether `07d` adds a `LICENSE` file to the new `quant-vault` repo. Likely yes (matches the personal-portfolio pattern); planner decides whether MIT (matches `gridflow-front-end`) or a CC license is more appropriate for a docs-heavy repo.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase rescope authority (NEW — start here)

- `.planning/V2-PHASE-7-HANDOFF.md` — the handoff from the 2026-05-19 grill session. Decisions to honour table; load-bearing Drift findings to triage; open items left from the grill (all three resolved in this CONTEXT.md).
- `docs/adr/0001-reconciliation-phase-added-to-v2.md` — the override of the v1 "no upfront audit" decision. ADR Status: accepted (2026-05-19). Read the Context section to understand WHY the override was warranted.
- `docs/adr/0002-vault-hosted-private-github-repo.md` — Vault-on-GitHub decision. ADR Status: accepted (2026-05-19). Read the Decision + Consequences sections; the option-2 (private + GitHub App auth) rejection is load-bearing for Phase 7d.

### Domain language and source-of-truth (essential)

- `CONTEXT.md` (project root) — domain glossary. Required reading: **Canonical**, **Vault**, **Live API response**, **Vendor docs**, **Drift**, **Verification**, **Reconciliation**, **Vendor**, **Dataset** terms; § Relationships; § Flagged ambiguities.
- `.planning/PROJECT.md` § "Source-of-truth hierarchy" — the locked four-layer chain (`code > live API > vault > site`).
- `.planning/PROJECT.md` § "Constraints" — the **accuracy** constraint ("loses all credibility if a recruiter spot-checks against the real Elexon API and finds drift") is the load-bearing constraint that ADR-0001 cites.

### Drift research (the MVP being executed)

- `.planning/research/post-v1/drift-detection/SUMMARY.md` — Executive summary, MVP scope, recommended architecture, anti-pattern catalogue. Read in full.
- `.planning/research/post-v1/drift-detection/DRIFT-SURFACES.md` § 1 (Inventory of artefacts) — 11 artefact types Verification covers.
- `.planning/research/post-v1/drift-detection/DRIFT-SURFACES.md` § 3 (Drift taxonomy) — Structural, Semantic, Referential, Temporal, Volumetric. Use these category labels in finding files.
- `.planning/research/post-v1/drift-detection/DRIFT-SURFACES.md` § 4 (Existing in-tree examples) — load-bearing for `07b` triage. §§ 4.1 (ndf/ndfd `published_at`), 4.2 (fuelhh intra-file Drift), 4.4 (33 ENTSO-E 401s), 4.5 (4 ENTSO-G 404s), 4.6 (`physical_flows` 35-field mismatch). Each `<specifics>` entry maps to one of these.
- `.planning/research/post-v1/drift-detection/CI-ARCHITECTURE.md` § 2 — MVP architecture (verifier in vault, snapshot diff in gridflow CI, scheduled artifact in front-end CI). § 9 — "Open Decisions for v2 Plan-Phase" (Q-DD-01..17); see Q-DD mapping below.
- `.planning/research/post-v1/drift-detection/TOOLING-AUDIT.md` — what exists, what's missing, the two Windows-specific blockers in the verifier.
- `.planning/research/post-v1/drift-detection/INDUSTRY-PATTERNS.md` — adoption list (schemathesis, `model_json_schema()` snapshot, `verified:` micro-line) and anti-pattern catalogue (snapshot fatigue, auto-bump theatre, secret-less forked PRs).

### Q-DD mapping (research questions ↔ this CONTEXT.md decisions)

| Q-DD | Subject | Status |
|------|---------|--------|
| Q-DD-01 | Repo placement of drift-check script | Resolved by D-05/07a: vault (rename to `gridflow_drift_check.py`, expose as console script) |
| Q-DD-02 | Daily cron vs PR-triggered | Out of v2 scope (ADR-0002 defers cross-repo CI) — defer to v2.1+ |
| Q-DD-03 | Freshness policy for `verified:` micro-line | Resolved by D-02: 30 days warn / 90 days fail (research default lean) |
| Q-DD-04 | ENTSO-E 401 resolution path | Resolved by D-06: defer to Phase 9 discuss |
| Q-DD-05 | Pydantic `model_json_schema()` snapshot location | Out of v2 scope — defer to v2.1 |
| Q-DD-06 | Cross-repo PR auto-creation | Out of v2 scope — defer to v2.2+ |
| Q-DD-07 | Failure mode for ENTSO-E 401s when token absent | Resolved by D-06: skip-with-warn semantic preserved |
| Q-DD-08 | `EXCLUDED_ENDPOINTS` handling | Default lean (flag as Referential); planner may keep current behaviour |
| Q-DD-09 | Manual-transformer schemas | Resolved by D-01: `wontfix`, `reason: v3-candidate` (PROJECT.md out-of-scope) |
| Q-DD-10 | Vault `Pydantic schema:` vs `.model_json_schema()` snapshot disagreement | Resolved by D-01: code wins; vault must update |
| Q-DD-11 | `gridflow-build --drift-check` flag | Out of v2 scope — defer to v2.1 |
| Q-DD-12 | Cross-repo auth | Resolved by D-09 / ADR-0002: no App auth; manual Verification cadence |
| Q-DD-13 | Where drift reports live | Resolved by D-08: local markdown under `.planning/reconciliation/<vendor>/` (NOT PR comments / NOT GitHub Issues / NOT artefacts-only) |
| Q-DD-14 | Patito for runtime validation | Out of v2 scope — defer to v2.2+ |
| Q-DD-15 | `schemathesis` in MVP | Out of v2 scope — defer to v2.1 |
| Q-DD-16 | `[drift]` extras location | Planner's discretion (vault or front-end) |
| Q-DD-17 | Existing vault validation outputs | Default lean: keep in vault as historical record; planner picks the report path |

### Working agreements (overrides defaults)

- `CLAUDE.md` (project root) § "Working agreements" — Conventional Commits required; one concern per commit; never commit to `main`; never auto-commit unless asked.
- `CLAUDE.md` (project root) § "Tech stack (post-Phase-3)" — confirms `gridflow-build` is Python + Jinja2, generated HTML gitignored, CI runs build before `upload-pages-artifact`. Phase 7 must not modify the deploy contract; it operates on the Vault layer that the build consumes.
- `~/.claude/CLAUDE.md` § "Universal preferences" — `uv` for Python; Polars (not pandas); ruff + mypy --strict; `pytest -x -q`. Apply to any Python work in `07a`.

### Existing tooling (what to wrap, not rewrite)

- `quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py` — the ~765-line verifier; `07a` wraps and renames it, doesn't rewrite. Specific lines to fix: L180 (`args[0] = "curl.exe"`); L20-26 (hardcoded `C:\Users\Bobbo\...` default).
- `quant-vault/30-vendors/scripts/derive_machine_catalog.py` — complementary catalog deriver; not in scope to modify but its output is informative.
- `quant-vault/30-vendors/vault-curl-schema-validation.md` / `.json` — the most-recent Verification outputs (latest run: 2026-05-16T15:34:03.495442Z). The starting state Phase 7 reconciles from.
- `quant-vault/30-vendors/vault-amendment-plan.md` — the existing Vault-author working document on what to fix; informative for `07c`.

### Sibling repo paths (for cross-repo work)

- `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\` — upstream Vault location (to be pushed to `EBentham/quant-vault` in `07d`).
- `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\` — gridflow main repo (read-only for Phase 7 per D-01).
- `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\vault\<vendor>\` — vendored snapshot location (target for re-vendoring after Vault edits in `07c`).

### Agent-skill protocols

- `docs/agents/issue-tracker.md` — local-markdown issue tracker convention. Phase 7 findings use this.
- `docs/agents/triage-labels.md` — canonical labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. Used by the `triage` skill in `07b`.
- `docs/agents/domain.md` — single-context discipline (`CONTEXT.md` + `docs/adr/` at repo root). Sibling repos keep their own.
- Pocock skill set: `to-issues` (capture findings as local md), `triage` (state-machine through finding classification). Both invoked in `07b`/`07c`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`verify_curl_and_silver_schema.py`** (in `quant-vault`) — the ~765-line existing verifier. `07a` renames and wraps it as `gridflow-drift-check`; does **not** rewrite. The script already does the structural work Phase 7 needs (curl example execution, silver-schema field-by-field comparison, JSON + markdown output emission).
- **`derive_machine_catalog.py`** — complementary catalog deriver. Output (`vault-config-vs-connector` path warnings, frontmatter mismatches, placeholder/TODO counts) is informative for triage but Phase 7 does not modify the script.
- **Existing `pyproject.toml`** at `gridflow-front-end` root with a `[build]` extras pattern — `[drift]` mirrors it if Q-DD-16's decision lands here.
- **Existing `[data-tabs]` / `[scroll-spy]` / template / `theme.css` infrastructure** — untouched by Phase 7; Reconciliation operates on Vault content, not the rendering pipeline.
- **Existing `vault/<vendor>/` vendored-snapshot directory** — `07c` re-vendors edited files into the same structure. v1's vendoring pattern is preserved (ADR-0002 explicitly notes this).
- **Existing `.planning/research/post-v1/drift-detection/` package** — entirely the input. The planner extracts Q-DD answers and MVP architecture from these files rather than re-deriving.

### Established Patterns

- **Conventional Commits** — already in use across all phases. `feat(07a):` for the verifier-wrap commit, `fix(07c):` for individual Vault edits, etc.
- **Vendored vault snapshot pattern** — `gridflow-front-end/vault/<vendor>/` mirrors `quant-vault/30-vendors/<vendor>/datasets/`. ADR-0002 preserves this; `07c`'s re-vendoring step copies edited files between the two locations.
- **Python + Jinja2 build pipeline (gridflow-build)** — not modified by Phase 7. The build consumes Vault state; Phase 7 changes that state. The build does not need to know Verification ran.
- **Single-context discipline** — one `CONTEXT.md` + `docs/adr/` at repo root, per `docs/agents/domain.md`. Phase 7 emits ADR-0001 and ADR-0002 (already done); no new ADRs needed for the resolved open items.
- **Issue tracker = local markdown** — `.planning/issues/<feature>/` for general issues, `.planning/reconciliation/<vendor>/` for Phase 7 findings. Both follow the same per-feature subdirectory convention.

### Integration Points

- **`07a` lands in the `quant-vault` upstream repo** — once `07d` has pushed the Vault to GitHub, the verifier rename + Windows-fix commits live in `EBentham/quant-vault`. Sequence: `07a` makes the changes locally in the upstream Vault; `07d` initialises the GitHub repo and pushes including those changes. Alternative: `07d` first, `07a` second — both work; planner picks.
- **`07c` produces commits in TWO repositories** — the upstream Vault (where the edit semantically belongs) AND the `gridflow-front-end/vault/<vendor>/` snapshot (where CI consumes it). Cross-repo coordination: planner decides whether to use git submodule, manual `cp -r`, or a Python helper. v1 used manual copy (per ADR-0002 "The vendoring pattern is preserved"); inertia recommends keeping that.
- **No `.github/workflows/` changes** — Phase 7 does NOT add a drift-check.yml workflow. Per ADR-0002, automated cross-repo drift CI is out of scope for v2; the verifier runs manually (or via a workflow scheduled inside the Vault repo with its own secrets, but that's not Phase 7 work).
- **Phase 8 (bug fix) inherits a Vault state where `published_at` / `issue_time` Drift is fixed** — the rendered `fuelhh.html` after Phase 8's template/CSS work will reflect the corrected schema table. Phase 8 still owns the layout fix; Phase 7 just ensures the data flowing through that layout is accurate.
- **Phase 9 (ENTSO-E) inherits 33 `needs-info` finding files** — the ENTSO-E content build cannot ship the 33 affected datasets at `fuelhh` fidelity until those finding files are resolved (extend access OR skip-with-warn). Phase 9's discuss-phase reads `.planning/reconciliation/entsoe/*.md` and chooses.

</code_context>

<specifics>
## Specific Ideas

### Load-bearing Drift findings the Verification MUST surface

From `DRIFT-SURFACES.md` § 4 — these are the concrete instances Phase 7 must triage. Failing to surface any of these means the wiring is wrong (per drift research SUMMARY.md "load-bearing acceptance test"):

**Elexon — fixable in v2 (`open` bucket, addressed in `07c`):**

- `ndf` / `ndfd` schema table omits `published_at`. Canonical: `ElexonDemandForecast.published_at: datetime | None` declared at `gridflow/src/gridflow/schemas/elexon.py:194`. Vault: `ndf.md:99` and `ndf.md:111` reference `issue_time` instead. Site: `site/hifi/data-sources/elexon/ndf.html:213` renders `Point-in-time field: issue_time` — **deployed-and-wrong**. Category: Structural + Semantic. Fix: edit `quant-vault/30-vendors/elexon/datasets/ndf.md` (and `ndfd.md`) to use `published_at`; re-vendor; rebuild.
- `fuelhh` schema table omits `published_at`. Canonical: `ElexonFuelHH.published_at: datetime | None = None` declared at `gridflow/src/gridflow/schemas/elexon.py:87`. Vault: `fuelhh.md:103` metadata block correctly names `published_at` but the schema table at `fuelhh.md:107-115` omits the row. **Intra-file Drift**, neither verifier nor build catches it. Category: Structural. Fix: add the `published_at` row to the schema table.
- 18 ENTSO-E `resolution` field nullability mismatches across Vault tables. Canonical: `Field(default=None, ...)` (nullable). Vault tables omit the nullability flag. Category: Semantic. Fix: add Nullable=Yes to the 18 affected tables. (Note: these 18 are Vault edits, not entitlement-blocked — distinct from the 33 ENTSO-E 401s.)

**ENTSO-E — needs-info, defer-entitlement (33 findings, addressed in Phase 9):**

- 33 ENTSO-E datasets return HTTP 401 from the current `.env` API token (`DRIFT-SURFACES.md` § 4.4). Token works for 11 endpoints, not these 33. Category: Temporal × Referential entitlement drift. Each finding produced in `07b` cites Q-DD-04 / DRIFT-SURFACES § 4.4 as the source of analysis. Phase 9's discuss-phase decides resolution.

**ENTSO-G — fixable in v2 (`open` bucket, addressed in `07c`):**

- 4 endpoints return HTTP 404: `hydrogen_content`, `interruptions`, `methane_content`, `oxygen_content` (`DRIFT-SURFACES.md` § 4.5). The vendor took these down; the Vault still describes them. Category: Referential. Fix: either delete the `.md` files (preferred if no other Vault content references them) or mark them with a `removed:` frontmatter flag the template knows to render distinctly. Planner picks.
- `physical_flows` 35-field mismatch in one `.md` file (`DRIFT-SURFACES.md` § 4.6). The worst single-file Drift in the ecosystem — the Vault has been used as a place to dump raw response keys; silver-layer consolidated them into two derived columns (`flow_gwh_per_day`, `timestamp_utc`). Category: Structural. Fix: rewrite the schema table in `entsog/datasets/physical_flows.md` to match the Pydantic shape; preserve the raw-keys discussion in a prose `## Bronze response keys` section if useful for the Site narrative.

**Wontfix-v3 (deferred per PROJECT.md):**

- 58 ecosystem-wide `manual_transformer_schema` cases (22 Elexon: `agpt`, `agws`, `atl`, `fou2t14d`, `fuelinst`, `imbalngc`, `inddem`, `indgen`, `indo`, `indod`, `itsdo`, `lolpdrm`, `market_depth`, `melngc`, `netbsad`, `nonbm`, `remit`, `soso`, `temp`, `tsdf`, `tsdfd`, `uou2t14d`). Closing the gap requires declaring `ElexonAGPT`, `ElexonAGWS`, etc. in `gridflow.schemas.elexon` — cross-repo work explicitly out of scope per PROJECT.md § Out of Scope. Each `07b` finding for these is triaged as `status: wontfix`, `reason: v3-candidate` and references PROJECT.md § Out of Scope.

### Specific behaviours wanted

- **Verification output format consistency** — preserve the JSON keys the existing `vault-curl-schema-validation.json` already emits, so any historical analysis still works. Extensions (per-Vendor counts, run timestamp, version stamp) are additive.
- **Triage labels** — exact strings: `open` / `wontfix` / `needs-info` (lowercase; matches `docs/agents/triage-labels.md` convention). Status transitions follow the `triage` skill's state machine.
- **Finding file naming** — `.planning/reconciliation/<vendor>/<NN>-<slug>.md` where `<NN>` is a per-Vendor sequence (zero-padded) and `<slug>` is kebab-case. E.g. `.planning/reconciliation/elexon/01-ndf-schema-table-missing-published-at.md`.
- **Re-vendor verification** — after each `07c` Vault edit, the re-vendored snapshot in `gridflow-front-end/vault/<vendor>/` must match the upstream Vault byte-equivalently. Planner picks the verification mechanism (`diff -r`, `git diff --no-index`, custom Python).
- **GitHub repo creation in `07d`** — repo name `EBentham/quant-vault`, private, no GitHub App. `.gitignore` should at minimum exclude `vault-curl-schema-validation.md`/`.json` if those are kept (drift research Q-DD-17 default lean preserves them) — or include them; planner picks. `LICENSE` likely yes (planner picks MIT vs CC).

</specifics>

<deferred>
## Deferred Ideas

### Within the v2 milestone (next phases)

- **ENTSO-E entitlement resolution path** — Phase 7 only triages as `needs-info`/`defer-entitlement`. The actual choice (extend ENTSO-E API access vs accept `skip-with-warn`) lands in Phase 9's discuss-phase.
- **GIE AGSI/ALSI Site split direction** — Vendor count stays at 6; the Site rendering split is a Phase 10 (4-vendor batch) decision, owned by `vendor-hub.html.j2` and the manifest shape in `data/gie.json` vs `data/gie_agsi.json` + `data/gie_alsi.json`.

### v2.1 / v2.2+ (post-v2, before v3)

- **Cross-repo automated drift CI** — the "Day-7-caught vs Day-21-caught" worst-case scenario from `DRIFT-SURFACES.md § 5`. Requires GitHub App auth (or scheduled workflow inside the Vault repo with its own secrets). ADR-0002 explicitly defers; revisit triggers listed there.
- **`gridflow-build --drift-check` flag** (Q-DD-11) — consume the JSON artefact and fail build if not all in-scope datasets pass. v2.1 work.
- **`model_json_schema()` snapshot diff in gridflow CI** (Q-DD-05) — the canonical structural-drift mechanism. v2.1 work; requires gridflow repo CI changes.
- **schemathesis against Elexon's published OpenAPI** (Q-DD-15) — vendor-API drift detection for the only ecosystem vendor that publishes an OpenAPI spec. v2.1 work.
- **`pytest-examples` against vault Python code blocks** (drift research INDUSTRY-PATTERNS § 4) — cross-repo path-reference drift. v2.1 work.

### v3 candidates (carried from PROJECT.md and ADR-0001)

- **Pydantic schema drift closure** — declaring `ElexonAGPT`, `ElexonAGWS`, `ElexonFOU2T14D`, etc. in `gridflow.schemas.elexon` for the 22 Elexon manual-transformer cases. Cross-repo work in the gridflow repo. Each `07b` `wontfix-v3` finding references this.
- **Patito for silver-layer runtime validation** (Q-DD-14) — Pydantic + Polars; collapses double-declaration (Pydantic + Vault markdown table) to one source. Requires gridflow code changes.
- **Per-dataset related-card blurbs** — `related_blurbs:` Vault frontmatter field; PROJECT.md § Out of Scope.
- **`fuelhh` fuel-pill grid** — `fuel_types: [...]` Vault frontmatter field; PROJECT.md § Out of Scope.

### Discussion artefacts

- **Pocock vs GSD skill boundary** — Pocock for Phase 7's exploratory `07b`/`07c` work; GSD for the pre-planned phases (8/9/10). Captured in D-07; not relitigable.
- **No GitHub Issues** — D-08 makes this binding for Phase 7. If a future phase wants GitHub Issues, that's a fresh decision in its own discuss-phase; document why the local-markdown discipline would break.

</deferred>

---

*Phase: 7-reconciliation*
*Context gathered: 2026-05-19*
