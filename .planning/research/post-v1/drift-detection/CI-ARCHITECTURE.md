# CI architecture for drift detection v2

Agent D / 4 — synthesis of `DRIFT-SURFACES.md` (Agent A), `TOOLING-AUDIT.md` (Agent B), and `INDUSTRY-PATTERNS.md` (Agent C) into a proposed end-state CI shape and the decision set v2 plan-phase must resolve. This file does **not** answer "should we adopt drift detection" — that question was answered when v1 shipped 33 datasets across three repos with no machinery to keep them aligned, and the verifier in the vault flagged 7 concrete schema diffs (`vault-curl-schema-validation.md:7-9` per TOOLING-AUDIT § 1, Coverage). This file answers "what shape" and "what decisions are pending."

The single most important architectural claim, stated upfront so it cannot be overlooked: **live-vendor-API drift checks must live in a separate scheduled workflow, not in `deploy.yml`.** The existing deploy pipeline runs `gridflow-build` synchronously before `upload-pages-artifact@v3` (`.github/workflows/deploy.yml:34-44`). If a vendor 503 can block a documentation deploy, the drift check has become Industry-Patterns Anti-pattern 1 ("everything blocks deploy"). The cheap, deterministic checks (count parity, verified-date freshness against committed vault data) belong in `deploy.yml`; the expensive, vendor-dependent checks belong in `drift-check.yml`. This separation reads as obvious only after stating it; the whole architecture below pivots on it.

---

## 1. Proposed architecture diagram

```
gridflow code (canonical)
   |
   +-- Pydantic .model_json_schema() snapshot ---> gridflow/schemas-snapshot.json     [v2.1; Structural]
   |                                                       |
   |                                                       v
   |                                          [diff vs prev commit on PR]
   |                                                       |
   |                                                       v
   |                                       breaking-change PR comment / label
   |
   +-- ENDPOINTS dict --> count + path inventory ---+                                 [Volumetric]
                                                    v
quant-vault ---> verify_curl_and_silver_schema.py (existing; rename+wrap)
   |   (29-vendors/scripts/)         |                                                [Structural, Semantic,
   |                                  v                                                 Referential, Temporal]
   |                          drift-report.json + .md
   |                                  |
   |                                  v
   |                  scheduled drift-check.yml (NEW) --> GitHub Actions annotations
   |                                                   --> issue on scheduled run failure
   v                                                   --> PR comment if PR-triggered
gridflow-build (Jinja2) ---> site/hifi/data-sources/<vendor>/<dataset>.html
                                  |
                                  v
                            deploy.yml: htmlhint + lychee (v1 CI-01/02)
                                       + gridflow-build --check  (v1 CI-03)
                                       + count parity check        (NEW; Volumetric)
                                       + verified-date freshness   (NEW; Temporal)
```

Annotations on the right edge map each new arrow to a drift category from `DRIFT-SURFACES.md § 3`. The four NEW arrows are the v2 build scope; the two existing arrows (verifier in vault; deploy.yml in front-end) already exist and are wired in v1.

---

## 2. Repo placement decision matrix

Four candidate homes for the drift-check tooling. The trade-offs:

| Option | Pros | Cons |
|---|---|---|
| (a) **gridflow** main repo | Owns the canonical Pydantic schemas; `.env` with vendor keys already lives here; existing `ci.yml` (`gridflow/.github/workflows/ci.yml`) runs pytest + ruff + mypy in CI; natural home for the `.model_json_schema()` snapshot diff per Industry-Patterns § 1 ("Pydantic v2 schema export") | Drift checks against the *vault* introduce a cross-repo dependency in gridflow's CI; gridflow contributors don't necessarily care about vault state; would expand `ci.yml` scope substantially |
| (b) **quant-vault** | Verifier already lives here (`30-vendors/scripts/verify_curl_and_silver_schema.py`, ~765 lines per TOOLING-AUDIT § 1); the `derive_machine_catalog.py` script (~765 lines, undiscovered in v1 planning per TOOLING-AUDIT § 2) is also vault-resident; `vault-curl-schema-validation.json`/`.md` already write here; inertia is the strongest argument | Vault is "the working notebook" — content + scripts mixed; running CI inside a notebook-repo tightens the Reading Discipline contract; vault privacy may complicate fork PRs |
| (c) **gridflow-front-end** | Front-end CI already orchestrates Python + Jinja2 (`pyproject.toml` `[build]` extra); deploy pipeline is where drift becomes visible; the front-end repo is the natural place to chain both checkouts because it already needs both for `gridflow-build` | Front-end is "downstream of drift" per the SoT hierarchy in `CLAUDE.md § Source-of-truth hierarchy`; running detection here puts it temporally after the drift has been baked into the site; cross-repo checkout setup costs |
| (d) **new 4th repo** (`gridflow-drift-detector`) | Clean separation of concerns; single-purpose repo with focused dependency surface (PyYAML + curl + gridflow + Pydantic); single home for the new `gridflow-drift-check` console script and its tests | Coordination overhead (4 repos to keep in sync); duplicates the cross-repo-checkout cost; one more place a solo maintainer has to remember to push to |

**Recommendation:** **(b) vault remains owner of the script** (rename `verify_curl_and_silver_schema.py` to `gridflow_drift_check.py` and expose it as a Python module + console script `gridflow-drift-check`); **(a) gridflow CI gates the schema-snapshot diff** (cheapest place — the Pydantic class is already imported there); **(c) gridflow-front-end CI consumes the JSON report as a job artefact from a scheduled drift-checker workflow** (where the consequences of drift are visible to recruiters).

The rationale is dual: inertia (the verifier already lives in vault and re-homing it costs more than wrapping it) plus the architectural truth that drift originates in the canonical source (gridflow code) and *manifests* in the front-end (the published artefact). Detection therefore wants to live in the *receiving* side of each edge; the schema-snapshot diff belongs to gridflow because that's where the schema lives; the vault-vs-code verifier belongs to vault because that's where the vault docs live; the site-vs-vault parity check belongs to the front-end because that's where the site lives. Open question Q-DD-01 captures the residual debate.

---

## 3. CI trigger taxonomy

For each GitHub Actions trigger type, recommended use:

- **`on: push: branches: [main]`** — **avoid for drift checks.** Deploy is already running on push to main (`deploy.yml:4-5`). Push-triggered drift detection runs after the merge has already happened; failure cannot block the deploy that's already in flight. Use only as a smoke test that doesn't gate.
- **`on: pull_request`** — **use, with `paths:` filter, for internal-only checks.** PR-triggered drift checks block merges on cheap, deterministic comparisons. Apply to: (i) PRs in gridflow touching `src/gridflow/schemas/*.py` or `src/gridflow/connectors/**/endpoints.py` → schema-snapshot diff + endpoint inventory check; (ii) PRs in vault touching `30-vendors/**/*.md` → run the verifier against committed vault state, not live API. The `paths:` filter avoids the cost on PRs that obviously can't affect drift.
- **`on: schedule:`** — **use for live-vendor-API checks.** Vendor APIs aren't versioned with our commits; their drift is async to our PRs. Recommend **daily 06:00 UTC** for the curl-vs-API verifier (low cost, async signal of vendor change); **weekly Monday 09:00 UTC** for `last_verified:` freshness warnings (no point checking dates more often than human-review can absorb). Industry-Patterns § 5 ("Scheduled-only ... opens issues, never blocks") is the authority.
- **`on: workflow_dispatch`** — **use as a manual re-verifier.** When the author wants to re-run the drift check before tagging a milestone, this is the trigger. Mirror `gridflow/.github/workflows/ci.yml` — no `workflow_dispatch` there today but adding one costs one line.
- **`on: repository_dispatch`** — **defer to v2.2+.** Cross-repo trigger (gridflow → front-end after schema change) is the conda-forge auto-tick pattern from Industry-Patterns § 6 ("conda-forge autotick-bot"). High-value, but it requires a PAT or GitHub App and one of those is the very item Q-DD-12 punts on. Not MVP.
- **`on: workflow_run`** — **avoid for MVP.** Chaining drift-check after gridflow CI succeeds is structurally appealing but couples the two repos' workflows; `repository_dispatch` is the cleaner cross-repo primitive when v2.2+ adds it.

Cited Pitfalls: `PITFALLS.md § Pitfall 8` (cross-repo divergence) argues for *some* automated cross-repo machinery; the scheduled-issue pattern from Industry-Patterns § 7 Anti-pattern 4 (secret-less forked PRs) argues for keeping vendor-key checks in `schedule:`-only contexts, never `pull_request`.

---

## 4. Secret management

Per-vendor inventory of credential requirements:

| Vendor | Auth required | Env var | Status (per verifier 2026-05-16) |
|---|---|---|---|
| Elexon BMRS | No | — | 122 curl examples pass; no key needed |
| ENTSO-E | Yes | `ENTSOE_API_KEY` | 33 `failed_auth` cases per `vault-curl-schema-validation.md` — see Q-DD-04 |
| GIE | Yes | `GIE_API_KEY` | 7 endpoints verified passing per amendment plan |
| ENTSO-G | No | — | Public; 4 endpoints currently 404 (DRIFT-SURFACES § 4.5) |
| Open-Meteo | No | — | Public |
| NESO | No | — | Public |

**Recommendation:** **scope drift secrets to a `drift-detection` GitHub Environment.** Both `ENTSOE_API_KEY` and `GIE_API_KEY` go into this environment scope, not repo-wide. The scheduled `drift-check.yml` is the *only* workflow that selects this environment. Forked PRs cannot trigger that workflow path (the path requires `schedule:` not `pull_request_target:`), so secrets stay safe even if the repo accepts external contributions later. This is the structural mitigation for Industry-Patterns Anti-pattern 4.

A per-vendor graceful-degradation rule: if `ENTSOE_API_KEY` is not present at runtime, the script skips ENTSO-E checks with status `skipped_auth` rather than failing. The existing verifier already emits `skipped_auth` (`verify_curl_and_silver_schema.py:158-173`); preserve that semantic — it's the right shape. The 33 ENTSO-E `failed_auth` cases the latest report carries (DRIFT-SURFACES § 4.4) sit in a third bucket: token is present but vendor returns 401. That's entitlement drift, not missing-key drift; treat it as fail-loud in MVP only *after* Q-DD-04 resolves whether the token is renewable.

OIDC tokens (per Industry-Patterns § 5) are overkill for API-key-based vendors; use only if a future vendor adopts OAuth flows.

---

## 5. Cross-repo checkout strategy

`actions/checkout@v4` supports cross-repo checkout via several auth shapes:

| Method | Strength | Weakness |
|---|---|---|
| Personal Access Token (PAT) | Quick to set up; works immediately | Tied to a user account; rotation calendar burden; scope creep risk |
| GitHub App with installation token | Per-repo permissions; revocable; clean audit trail | More setup; one more credential surface to manage |
| Deploy keys | Per-repo, finer-grained; no app needed | One key per direction per repo pair; combinatorial explosion at 3 repos |
| Public-repo just-clone | Zero auth; no credential management | Requires all involved repos to be public |

The discriminator that this research package cannot resolve from inside the front-end repo is **whether `quant-vault` is public**. `PROJECT.md` confirms `gridflow` is public (`github.com/EBentham/gridflow`). It does not confirm vault privacy. **Q-DD-12 captures this decision.**

**Recommendation (conditional):** if vault is public, just-clone is the right answer — `actions/checkout@v4` with `repository: EBentham/quant-vault` and `path: quant-vault-repo` works without any credential setup, and the v1 brief (`AUTONOMOUS-V1-BRIEF.md`) explicitly notes the vault path will need to be reachable in CI. If vault is private, a GitHub App scoped to `contents: read` on both sibling repos is the proper answer; document the App permissions in the workflow file alongside the checkout step.

The Windows-path concerns from TOOLING-AUDIT § "External dependencies" (the verifier hard-codes `args[0] = "curl.exe"` at `verify_curl_and_silver_schema.py:180`, and defaults `GRIDFLOW` to a literal `C:\Users\...` path at L20-26) are concrete porting tasks the MVP must own. They land alongside the cross-repo-checkout work as the first paragraph of "make this script CI-portable."

---

## 6. Failure-mode design

Per-drift-category recommendations. Default is fail-loud, justified by `PROJECT.md`'s Decision #6 ("Kill all 'live' framing") — the v1 milestone explicitly traded polish for credibility, and silent drift is the credibility-destroying failure mode. Exceptions justified per row.

| Drift category (DRIFT-SURFACES § 3) | Recommended failure mode | Rationale |
|---|---|---|
| **Structural** (Pydantic field set ↔ vault schema table) | **Fail-loud on PR** for PRs touching either side; warn-only on scheduled runs (issue only) | A structural drift caught at PR time is cheap to fix; same drift caught nightly via cron is just async signal. The `published_at`/`issue_time` drift on `ndf`/`ndfd`/`fuelhh` (DRIFT-SURFACES § 4.1, 4.2) is the live example — v2 MVP catches this on the next PR touching those files. |
| **Semantic** (nullable mismatch, type widening) | **Warn-only PR annotation** for nullable downgrades (docs say nullable=Yes, code says non-null — claim is stronger than reality); **fail-loud** for type changes | The downgrade case is misleading-only (the recruiter absorbs a slightly looser invariant than reality); type changes are dangerous (the recruiter writes a query that crashes). Different blast radius, different failure mode. |
| **Referential** (vault claims `gridflow.X.Y.Z` but no importable class) | **Warn-only for `manual_transformer_schema` cases** (preserve verifier's existing semantic); **fail-loud for `schema_import_error`** | 58 `manual_transformer_schema` cases ecosystem-wide (TOOLING-AUDIT § 1, Coverage; 22 of those Elexon). These are by-design today — there's no code to import against. Fail-loud would create CI noise on a known-architectural condition. `schema_import_error` is a true rename event and warrants the block. |
| **Temporal** (`last_verified:` > threshold) | **Warn at 30d, fail at 90d** (subject to Q-DD-03) | The site's whole credibility play is "verified against vendor docs on date X"; if that date is six months stale, the claim is fiction. 30-day warn gives the author lead-time; 90-day fail is the limit. |
| **Volumetric** (count mismatches across manifest / connector / vault / site) | **Fail-loud** on every PR + scheduled run | This is the 22/25/28 v1 recurrence (DRIFT-SURFACES § 4.7); the v1 milestone literally hand-fixed it to 33/33/33/33 with no structural gate. Trivial to check, dangerous to miss, false-positive cost ~zero. |

The vendor-503 flake from Industry-Patterns Anti-pattern 1 is the most important exception to fail-loud. Recommended pattern: retry-with-backoff inside the script (the existing verifier already has a 90s `--max-time` per `run_curl()` L334; add a retry loop); HTTP 5xx is `warn-only`; HTTP 4xx (the response that means "this endpoint changed") is `fail-loud`. The distinction is meaningful — 503 is infrastructure, 404 is contract.

---

## 7. Cadence proposal

Per-drift-edge cadence with explicit cost analysis. Cross-reference the 19 drift edges in `DRIFT-SURFACES § 2`; collapsed here to representative cases.

| Drift edge | Cadence | Why this cadence | Cost of missed detection | Cost of false positive |
|---|---|---|---|---|
| Pydantic schema ↔ vault schema table (edges 1, 2) | **On every PR touching `schemas/`** (gridflow) + on every PR touching `30-vendors/**/*.md` (vault) | Internal, deterministic, cheap; PR-time gating is correct | Drift baked into next deploy (per DRIFT-SURFACES § 5 worst-case scenario, up to 21 days deployed-and-wrong) | Very low — the verifier emits concrete field diffs, easy to triage |
| vault curl ↔ live API (edge 5) | **Scheduled daily 06:00 UTC** + on-PR for PRs touching the curl block | External, vendor-dependent; cannot block deploy on vendor uptime | Recruiter copies a 404'd curl example | Higher — vendor 503s look like drift; mitigation in § 6 |
| Pydantic schema snapshot ↔ previous commit (Industry-Patterns § 1) | **On every gridflow PR touching `schemas/`** | Internal, surfaces breaking changes pre-merge; same workflow that runs pytest | Breaking change merged without coordinating vault update | Very low — diff is deterministic |
| `verified-against-vendor-docs:` freshness (edges 10, 11) | **Scheduled weekly Monday 09:00 UTC** | No value to checking more often than human review can absorb | Site claims credibility against stale date; embarrassment risk if recruiter spot-checks | Near-zero — a date older than threshold *is* the failure |
| Count consistency (edge 13, 16) | **On every gridflow-front-end PR + scheduled weekly** | Trivial cost; the v1 22/25/28 recurrence is the load-bearing example | Manifest claims 33, site renders 32; recruiter notices contradiction | Near-zero |
| Endpoint path renames (edge 4) | **Scheduled daily** + on gridflow PRs touching `endpoints.py` | The BOAL → BOALF rename in DRIFT-SURFACES § 4.3 is the historical reference; trivial check | Recruiter's curl 404s | Low — path comparison is exact |
| Cross-repo path references (edge 15; PITFALLS Pitfall 8) | **Scheduled weekly** | `griffe` resolves Python symbol paths cheaply; no value running per-PR until cross-repo dispatch wired | Site links to dead schema file | Low |
| `EXCLUDED_ENDPOINTS` orphans (edge 12) | **On every gridflow PR touching `endpoints.py`** | Already gated by `gridflow/tests/unit/test_elexon_endpoints.py::TestElexonInventoryContract` per TOOLING-AUDIT § 2 | Vault retains page for an endpoint that's been killed | Near-zero |

The MVP cadence reads: PR-time for internal-deterministic; daily cron for vendor-dependent; weekly cron for human-bandwidth-bound checks. No drift edge runs more frequently than its natural rate-of-change.

---

## 8. MVP scope vs full scope

A v2 milestone need not ship all of the above on day one. Recommended phasing:

**MVP (v2.0) — ship in 1-2 v2 phases.** The smallest delivery that closes the v1 gap:

1. **Wrap the existing verifier as a console script.** Rename `verify_curl_and_silver_schema.py` to a Python module exposed as `gridflow-drift-check` (mirrors `gridflow-build` / `gridflow-serve` pattern in `pyproject.toml:17-19`); port `curl.exe` → `curl` (cross-platform); replace the hardcoded `C:\Users\...` path default with `GRIDFLOW_REPO`/`GRIDFLOW_VAULT_PATH` env-var-first lookup (mirror v1 `VAULT-02`).
2. **Add a `[drift]` optional-dependencies extra** in `pyproject.toml`, mirroring `[build]`: `drift = ["PyYAML>=6.0", "pydantic>=2.0"]` (gridflow is imported as a sibling editable install in CI).
3. **Add `drift-check.yml`** as a separate workflow file from `deploy.yml`, triggered `on: schedule:` (daily 06:00 UTC) and `on: workflow_dispatch:`. Workflow steps: checkout front-end, checkout gridflow (just-clone if public per § 5), checkout vault, run `gridflow-drift-check`, upload JSON report as job artefact, emit GitHub Actions annotations (`::error file=...,line=...::`) on failures.
4. **Extend `deploy.yml`** with two cheap checks before `upload-pages-artifact@v3`:
   - **Count parity check**: `len(json.load("site/hifi/data/elexon.json")['categories'])` set equality with `ENDPOINTS` keys (imported from gridflow) — fail-loud per § 6.
   - **`verified-against-vendor-docs:` freshness check**: parse `last_verified:` frontmatter; warn if >30 days, fail if >90 days (subject to Q-DD-03).
5. **Cross-repo checkout** via just-clone if `quant-vault` is public; else GitHub App per § 5.

The MVP must surface the `ndf`/`ndfd`/`fuelhh` `published_at`/`issue_time` drift (DRIFT-SURFACES § 4.1, 4.2) on its first scheduled run; that's the load-bearing concrete acceptance test. If the MVP doesn't catch what the manual verifier already caught, the wiring is wrong.

**v2.1 expansion** (one v2 phase later):

1. **Schema-snapshot diff in gridflow CI** per Industry-Patterns § 1: `scripts/dump_schemas.py` walks `gridflow.schemas.*`, commits one JSON per dataset to `gridflow/schemas-snapshot/<class>.json`; PR check fails if diff is non-empty without an opt-in `breaking-ok` PR label.
2. **`schemathesis` against Elexon's OpenAPI** (Industry-Patterns § 2): scheduled-only, against the OSUKED-derived YAML if Elexon's own spec URL is hard to find (open question in Industry-Patterns § "Open questions left for execution").
3. **`pytest-examples` against vault Python code blocks** (Industry-Patterns § 4, FastAPI/Pydantic pattern): catches the cross-repo path drift the moment a `gridflow.schemas.X` reference becomes stale.

**v2.2+ expansion** (later v2 phases or v3):

1. **`repository_dispatch` hooks** so gridflow schema changes auto-open vault PRs (conda-forge autotick pattern per Industry-Patterns § 6).
2. **Patito adoption** for runtime Polars-side validation (Industry-Patterns § 3 headline #2): collapses the double-declaration of schema in code+vault to one source. Strictly post-MVP because it requires gridflow code changes, not just CI.
3. **Pact-style consumer-driven contract testing** — *deferred indefinitely* per Industry-Patterns § 2 (assumes provider cooperation; vendors are external).

This phasing keeps the MVP achievable inside a single v2 milestone of 1-2 phases and matches Industry-Patterns § "Cross-section synthesis" three-adoption ordering.

---

## 9. Open questions

These are the decisions v2 plan-phase must resolve. Format is strict per the brief — `Q-DD-NN: <question> · default lean: <best guess with rationale>`. SUMMARY.md will quote these verbatim.

- **Q-DD-01:** Repo placement — vault, gridflow, gridflow-front-end, or new 4th repo for the drift-check script? · default lean: vault (script already lives there at `30-vendors/scripts/verify_curl_and_silver_schema.py`; rename to `gridflow_drift_check.py` and expose as `gridflow-drift-check` console script per § 2)
- **Q-DD-02:** Daily cron vs PR-triggered for live API checks? · default lean: both — `on: schedule:` daily 06:00 UTC for systemic drift, `on: pull_request:` with `paths:` filter for PRs touching curl/schema blocks per § 3
- **Q-DD-03:** How fresh is "fresh" for the `verified-against-vendor-docs:` and `last_verified:` micro-line? · default lean: warn at 30 days, fail at 90 days (the v1 milestone shipped 2026-05-08 and verifier last ran 2026-05-16 — 30/90 gives the author room to absorb without surprise blocks)
- **Q-DD-04:** Should ENTSO-E `failed_auth` blockers (33 cases per `vault-curl-schema-validation.md`) be fixed in v2 or treated as known-unverifiable? · default lean: fix the API token first (config phase of v2), then enable fail-loud on the now-verifiable endpoints; preserves the existing verifier's `failed_auth` triage shape (TOOLING-AUDIT § 1 constants)
- **Q-DD-05:** Pydantic `model_json_schema()` snapshot — committed JSON in gridflow repo, or computed-on-the-fly in CI? · default lean: committed (allows diff in PR review per Industry-Patterns § 1; on-the-fly defeats the diff-in-history purpose)
- **Q-DD-06:** Cross-repo PR auto-creation when gridflow schema changes — yes/no/later? · default lean: later (v2.2+); MVP just annotates "vault PR needed" via GitHub Actions annotation; auto-PR per Industry-Patterns § 6 conda-forge pattern
- **Q-DD-07:** Failure mode for ENTSO-E 401s when token absent — skip-with-warn or fail-loud? · default lean: skip-with-warn (preserve verifier's existing `skipped_auth` semantic per `verify_curl_and_silver_schema.py:158-173`; do not invent a new failure class on day one)
- **Q-DD-08:** How do we handle `EXCLUDED_ENDPOINTS` — flag if documented in vault, ignore, or document as "excluded but informational"? · default lean: flag (Referential drift category per DRIFT-SURFACES § 3); a vault page for `bod`/`generation_by_fuel`/`indicative_imbalance_volumes` (today clean per DRIFT-SURFACES § 4.8) is a future-drift risk worth surfacing
- **Q-DD-09:** Manual-transformer schemas (no Pydantic class) — what verification do we apply? · default lean: status quo for v2 (`manual_transformer_schema` marker on the site; the 58 ecosystem-wide cases per TOOLING-AUDIT § 1 are out of scope for v2 schema-gate)
- **Q-DD-10:** When the vault `Pydantic schema:` reference and the `.model_json_schema()` snapshot disagree, which wins? · default lean: code wins; vault must update (locked by `PROJECT.md § Source-of-truth hierarchy`: `code > live API > vault > site`)
- **Q-DD-11:** Should v2 add a `gridflow-build --drift-check` flag that consumes the verifier report and fails the build if not all in-scope datasets pass? · default lean: yes; keeps the gate at the build step where the user is already running CI in `deploy.yml:38-39`; consumes a JSON artefact produced by the scheduled `drift-check.yml`
- **Q-DD-12:** GitHub App vs PAT vs public-clone for cross-repo checkout? · default lean: public-clone if `quant-vault` stays public; else GitHub App scoped `contents: read` on both sibling repos (vault privacy not verifiable from this research package per § 5)
- **Q-DD-13:** Where do drift reports live for human review — PR comments, GitHub Issues, GitHub Pages site, or artifact downloads only? · default lean: PR comments for fail-loud per-PR runs; weekly summary GitHub Issue for scheduled runs; full JSON artefact uploaded always (Industry-Patterns Anti-pattern 5: artifacts-only is signal-less)
- **Q-DD-14:** Should we add Patito for silver-layer runtime validation in v2 or defer to v3? · default lean: defer to v2.2+ at the earliest; not MVP scope (requires gridflow code changes, not just CI per Industry-Patterns § 3 headline #2)
- **Q-DD-15:** Should `schemathesis` against Elexon's OpenAPI run in MVP or v2.1? · default lean: v2.1 per the phasing in § 8; MVP just runs the existing verifier wrapper. Elexon's OpenAPI URL is itself an open question in Industry-Patterns § "Open questions left for execution"
- **Q-DD-16:** Where does the `[drift]` extra live — `gridflow-front-end/pyproject.toml`, `quant-vault/pyproject.toml` (if it exists), or gridflow's? · default lean: vault if vault has a `pyproject.toml`; else gridflow-front-end mirroring the `[build]` extra pattern at `pyproject.toml:13-15`. Dependencies: PyYAML, pydantic (transitive via gridflow), gridflow itself as an editable sibling install
- **Q-DD-17:** What happens to the existing `vault-curl-schema-validation.md`/`.json` reports in the vault repo? · default lean: keep them committed in vault (they're useful as the human-readable historical record), but rename the workflow's primary output to a CI-artefact path so reports are not double-committed; preserves the `derive_machine_catalog.py` precedent (TOOLING-AUDIT § 2) where vault scripts emit content vault-side

---

*Synthesis of `DRIFT-SURFACES.md`, `TOOLING-AUDIT.md`, `INDUSTRY-PATTERNS.md`; written 2026-05-18 for the v2 drift-detection milestone.*
