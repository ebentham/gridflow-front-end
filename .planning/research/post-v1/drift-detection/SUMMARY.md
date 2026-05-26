# Drift Detection Research Summary

**Project:** gridflow-front-end (post-v1 preparation)
**Domain:** Cross-repo schema + content drift detection
**Researched:** 2026-05-18
**Confidence:** HIGH on the wrap-don't-rewrite recommendation and the drift taxonomy; MEDIUM on the specific repo-placement and snapshot-diff choices (pending Q-DD-01 / Q-DD-05 in plan-phase)

## Executive Summary

The headline finding is that v2 is **integration, not invention** — three drift-detection layers already exist locally (the vault's `verify_curl_and_silver_schema.py`, the vault's `derive_machine_catalog.py`, and gridflow's `TestElexonInventoryContract` pytest suite) and the v2 milestone is mostly a CI-wrapper + reporter task rather than a from-scratch build (per TOOLING-AUDIT.md § 2). The drift problem is real and measurable today: the latest verifier report carries 33 silver-schema failures, 33 ENTSO-E `failed_auth` cases, 4 ENTSOG 404s, plus deployed-and-wrong drift on `ndf` / `ndfd` / `fuelhh` where the public site claims a `Point-in-time field` that doesn't exist in the canonical Pydantic schema (DRIFT-SURFACES.md § 4.1, 4.2). The 5-category taxonomy (Structural / Semantic / Referential / Temporal / Volumetric) maps cleanly onto failure-mode design — fail-loud for structural and volumetric drift, warn-only for nullable downgrades and vendor 5xx flakes, scheduled-issue-only for vendor-API-dependent checks (CI-ARCHITECTURE.md § 6). The recommended architecture: vault remains owner of the renamed script (`gridflow-drift-check`), gridflow CI gates a `model_json_schema()` snapshot diff (v2.1), and front-end CI consumes a scheduled drift-report artefact. The highest single risk is drift CI that becomes flaky noise everyone ignores — snapshot fatigue, secret-less forked PRs, and the auto-bump-timestamp anti-pattern are all explicitly catalogued in INDUSTRY-PATTERNS.md § 7 and the architecture is designed around avoiding them.

## Key Findings

### Recommended Approach

The MVP architectural recommendation is a three-repo placement split. The drift-check script stays in `quant-vault/30-vendors/scripts/` (renamed from `verify_curl_and_silver_schema.py` to `gridflow_drift_check.py` and exposed as a `gridflow-drift-check` console script) because that's where ~765 lines of working code already live; rehoming costs more than wrapping. The Pydantic `model_json_schema()` snapshot diff lives in gridflow CI because that's the cheapest place to import the canonical class. The front-end repo runs a new `drift-check.yml` workflow on `on: schedule:` daily 06:00 UTC plus `on: workflow_dispatch:`, checking out all three repos and consuming the JSON report (CI-ARCHITECTURE.md § 2).

The MVP scope is deliberately small: wrap the existing verifier as a portable console script (fixing the Windows-specific `args[0] = "curl.exe"` and the hardcoded `C:\Users\...\gridflow` default), add a `[drift]` extra in `pyproject.toml`, add `drift-check.yml` as a separate workflow from `deploy.yml`, and extend `deploy.yml` with two cheap deterministic checks before `upload-pages-artifact@v3` (count parity across manifest / connector / vault; `verified-against-vendor-docs:` freshness against committed frontmatter) per CI-ARCHITECTURE.md § 8. The load-bearing acceptance test: the MVP must surface the `ndf` / `ndfd` / `fuelhh` `published_at` / `issue_time` drift on its first scheduled run — if it doesn't catch what the manual verifier already caught, the wiring is wrong.

The v2.1 expansion adds the Pydantic snapshot diff in gridflow CI, schemathesis against Elexon's published OpenAPI spec (Elexon is the only ecosystem vendor that publishes one — ENTSO-E, ENTSO-G, GIE, Open-Meteo do not), and `pytest-examples` against vault Python code blocks for cross-repo path-reference drift (INDUSTRY-PATTERNS.md § 2, § 4).

### Drift Surface Inventory

- 11 artefact types: Pydantic schemas, silver transforms, connector endpoints, vault frontmatter, vault silver-schema tables, vault prose, verifier outputs, generated HTML, manifests, Jinja2 templates, live vendor APIs (DRIFT-SURFACES.md § 1)
- 19 drift edges enumerated with detection-difficulty and blast-radius classification (DRIFT-SURFACES.md § 2). Top 5 by blast-radius: (a) connector path vs live API response — dangerous (ENTSOG 404s); (b) connector ParamStyle vs vault Query Parameters — dangerous (silent wrong-window queries); (c) Pydantic field set vs vault schema table — misleading-to-dangerous (deployed-and-wrong on `ndf` / `fuelhh`); (d) manifest ↔ vault ↔ connector ↔ site count parity — the 22/25/28 v1 recurrence; (e) cross-repo path references (vault → gridflow files) — misleading
- 5-category taxonomy: **Structural** (field added/removed, type widened), **Semantic** (nullable flipped, units changed), **Referential** (vault claims `gridflow.X.Y.Z` that no longer imports), **Temporal** (`last_verified:` stale), **Volumetric** (counts diverged across surfaces)
- Real in-tree examples: `ndf` / `ndfd` / `fuelhh` `published_at` vs `issue_time` (deployed-and-wrong, Structural); BOAL → BOALF path rename (Referential, caught manually and resolved); 33 ENTSO-E `failed_auth` cases (Temporal × Referential entitlement drift); ENTSOG `physical_flows` with 35 field-level mismatches in one file (worst single-file drift); 22/25/28 v1 dataset-count split, resolved to 33 with no structural gate

### Tooling Reality

- **What exists:** the verifier (curl + schema check; latest run covers 122 passed / 33 failed_auth / 7 failed curl examples, plus 56 passed / 33 failed silver schema checks); `derive_machine_catalog.py` (vault-config-vs-connector path warnings, frontmatter mismatches, placeholder/TODO counts); gridflow's `TestElexonInventoryContract` (connector ↔ config equality, runs in CI on every push to gridflow); `test_bronze_silver_contract.py` (silver-output ↔ Pydantic schema, runs in CI) — TOOLING-AUDIT.md § 1-2
- **What's missing:** site HTML never inspected by any tool; `elexon.json` manifest never compared against connector or vault; `last_verified:` freshness never asserted; field type mismatches beyond nullable (the verifier reads column 2 of the vault table but never compares against the Pydantic annotation); cross-repo path-reference checks; renamed-endpoint detection (path-string match against connector value)
- **Two trivial Windows-specific blockers** in the verifier need parameterizing for Linux CI: `args[0] = "curl.exe"` at `verify_curl_and_silver_schema.py:180` and the hardcoded `C:\Users\Bobbo\...` default at L20-26
- **Pydantic v2 introspection has two complementary APIs:** `.model_fields` (what the verifier uses today; produces human-readable field-by-field reports) and `.model_json_schema()` (proposed for v2.1; produces a stable JSON Schema fingerprint that's diffable in PR review and version-controllable as a committed snapshot)

### Industry Pattern Adoption

**Adopt:**
- **`verified: YYYY-MM-DD` micro-line + scheduled re-verifier cron** (already partial in v1 via REQ ELX-07; extend to CI per INDUSTRY-PATTERNS.md § 4 — the Stripe / Read the Docs / MDN pattern)
- **schemathesis against Elexon's published OpenAPI** for vendor-API drift, scheduled-only (Elexon publishes a spec via Swagger-UI at `bmrs.elexon.co.uk/api-documentation` and the OSUKED community project derives a `BMRS_API.yaml` as a fallback source)
- **Pydantic v2 `model_json_schema()` snapshot diff** committed to gridflow per INDUSTRY-PATTERNS.md § 1 — the schema directory's commit history then *is* the schema-drift log

**Skip:**
- **Pact** and consumer-driven contract testing — assumes provider cooperation; vendors are external
- **dredd** — strictly subsumed by schemathesis
- **Great Expectations** — overkill for 33 datasets and aesthetic mismatch (the SaaS-looking HTML data-docs are explicitly anti-goal in PROJECT.md)
- **Soda Core** — re-introduces YAML-vs-Pydantic duplication that Pydantic-native tools eliminate
- **mypy stub diffing** — subsumed by `griffe` for cross-repo symbol resolution
- **dbt tests / Avro Schema Registry** — wrong ecosystems

**Maybe later (v2.2+):**
- **Patito** (Pydantic + Polars) for runtime silver-layer validation, collapsing the double-declaration of schema (Pydantic + vault markdown table) to one source. Strictly post-MVP because it requires gridflow code changes, not just CI.

### Open Decisions for v2 Plan-Phase

Quoted verbatim from CI-ARCHITECTURE.md § 9.

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

### Risks

Mirroring v1 PITFALLS.md structure — the load-bearing risks from across the four files.

1. **Drift CI becomes flaky noise everyone ignores** (the failure mode that destroys all the work; INDUSTRY-PATTERNS.md § 7 Anti-patterns 1, 2, 7). The trap is well-intentioned PR-gating on vendor-dependent checks: first Elexon 503, deploy blocks; author adds `continue-on-error: true`; check becomes theatre. Mitigation: vendor-dependent checks live in scheduled-only workflows that open issues, never block deploy; 5xx is `warn-only`, 4xx is `fail-loud`; the `verified:` date bump happens *only* after a passing verification, never as a side-effect of a failed run.
2. **Cross-repo secret-management gap blocks forked PR CI** (CI-ARCHITECTURE.md § 4; INDUSTRY-PATTERNS.md § 7 Anti-pattern 4). Secrets are isolated from forked PRs by GitHub design; checks that need `ENTSOE_API_KEY` or `GIE_API_KEY` silently skip on external contributions. Mitigation: scope drift secrets to a `drift-detection` GitHub Environment selected only by the scheduled workflow; forked PRs run a no-secret subset.
3. **The 33 ENTSO-E `failed_auth` cases are a known-blocker** that must be resolved before v2 can enable fail-loud on ENTSO-E (DRIFT-SURFACES.md § 4.4). Today's failures are entitlement drift (token works for 11 endpoints, not these 33) — Q-DD-04 captures the resolution path.
4. **Vendor 503s and weekend / holiday cron flakes** (INDUSTRY-PATTERNS.md § 7 Anti-pattern 3). Energy-sector data has degenerate Christmas-day profiles; vendor 5xxs look like drift. Mitigation: retry-with-backoff inside the script (existing 90s `--max-time` plus a retry loop); embed known-low-data-day semantics in the assertion.
5. **Manual-transformer-schema cases (~58 ecosystem-wide; 22 Elexon) can't be drift-checked structurally** because no static Pydantic class exists for them (TOOLING-AUDIT.md § 1 Coverage; DRIFT-SURFACES.md § 3 Referential). Risk that we paper over with a "reviewed" label that becomes theatre. Mitigation: explicit `manual_transformer_schema` status preserved through the report; v2 MVP does not invent verification for them (Q-DD-09).

## Confidence Calibration

| Finding | Confidence | What would change the verdict |
|---------|------------|-------------------------------|
| Verifier is canonical and should be wrapped not replaced | HIGH | Discovering a fundamental bug in the verifier's schema-extraction logic (e.g. it under-reports) |
| 5-category drift taxonomy (Structural / Semantic / Referential / Temporal / Volumetric) | HIGH | A real-world drift example that doesn't fit any category |
| MVP scope (verifier-in-CI + count parity + verified-date freshness) | HIGH | Bandwidth tightens further, or the verifier's CI portability is harder than the two Windows-specific lines suggest |
| Recommendation that vault owns the script (vs new 4th repo) | MEDIUM | If `quant-vault` stays private and the cross-repo checkout cost (GitHub App setup) exceeds the rehoming cost — Q-DD-12 is the deciding factor |
| schemathesis against Elexon recommendation | MEDIUM | If the community OSUKED-derived OpenAPI is too out-of-date or Elexon publishes something more authoritative |
| Pydantic `model_json_schema()` snapshot diff is the right structural-drift mechanism | MEDIUM-HIGH | If a real diff between two Pydantic commits proves noisy/cosmetic in practice (property ordering, `$defs` churn) — the canonical-normalisation mitigation may need refinement |
| Anti-pattern catalogue (snapshot fatigue, auto-bump theatre, secret-less forked PRs) | HIGH | These are well-cited in industry primary sources; unlikely to change |

---
*Research conducted 2026-05-18. Inputs: DRIFT-SURFACES.md, TOOLING-AUDIT.md, INDUSTRY-PATTERNS.md, CI-ARCHITECTURE.md + the reading list specified in RESEARCH-BRIEF.md + cross-repo paths to gridflow + quant-vault + gridflow-front-end.*
