# Handoff: v2 grill-with-docs session 2026-05-19 → /gsd-discuss-phase 7

Context for the agent picking up the newly-inserted v2 Phase 7 (Reconciliation). This handoff supersedes the assumptions baked into the original v2 ROADMAP for Phases 7-9 (which renumber to 8-10).

## TL;DR of the rescope

The v2 milestone was rescoped in a `/grill-with-docs` interview on 2026-05-19. The locked v1 decision "assume vault content complete; no upfront audit phase" was overridden (see ADR-0001). A new Phase 7 (Reconciliation) is inserted at the start of v2; existing Phase 7 (bug fix), Phase 8 (ENTSO-E), and Phase 9 (4-vendor batch) renumber to 8, 9, 10. The Vault will be committed to a new private GitHub repo (see ADR-0002).

## Decisions to honour during planning

| # | Decision | Source |
|---|---|---|
| 1 | Vault is **derivative** — fix lands in Vault, never overrides Canonical | CONTEXT.md, grill Q1 |
| 2 | Reconciliation = the drift-detection research package, brought forward from post-v2 | grill Q3 |
| 3 | Drift gates per-Vendor — bug fix phase is independent of Reconciliation | grill Q4 |
| 4 | All-Vendor Reconciliation done upfront in Phase 7, not interleaved per-Vendor | grill Q6 user revision |
| 5 | Pocock skills for exploratory Reconciliation work (`to-issues` + `triage`); GSD for pre-planned phases | grill Q5 |
| 6 | Issues live as local markdown under `.planning/issues/<feature>/` and `.planning/reconciliation/<vendor>/`, **not** GitHub Issues | user direction after Q5 |
| 7 | Vault on **private** GitHub repo; **no GitHub App auth** — accept the cross-repo CI limitation | ADR-0002 |

## New Phase 7 scope (Reconciliation)

**Goal:** a verified Vault layer trusted as the input for content phases. After Phase 7, content phases (8-10) build pages from a Vault we trust.

### Components

1. **Wrap the verifier.** Rename `quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py` → `gridflow_drift_check.py`; expose as `gridflow-drift-check` console script. Fix the two Windows-specific blockers (`args[0] = "curl.exe"` at L180; hardcoded `C:\Users\Bobbo\...` default at L20-26). Per drift research SUMMARY.md § "Tooling Reality" and CI-ARCHITECTURE.md § 2.
2. **Run Verification across all 6 Vendors.** Outputs: JSON report (machine) + markdown report (human) + finding files under `.planning/reconciliation/<vendor>/<NN>-<slug>.md`.
3. **Triage each finding into one of three buckets.**
   - `status: open` → fixable in v2 (Vault edits)
   - `status: wontfix` with reason `v3-candidate` → needs gridflow code changes (e.g. new Pydantic classes)
   - `status: needs-info` with reason `defer-entitlement` → blocked on external (e.g. ENTSO-E API token entitlement)
4. **Fix the open bucket.** Land Vault edits in the upstream Vault (now on GitHub, see component 5) and re-vendor into `gridflow-front-end/vault/<vendor>/`.
5. **Commit upstream Vault to private GitHub.** Repo name TBD by user; default lean `EBentham/quant-vault`. Per ADR-0002 this is a plain private repo with no GitHub App auth.

### Acceptance criteria

- `gridflow-drift-check` exists as a console script on path; portable to Linux CI (the two Windows-specific blockers are parameterised).
- Every Vendor under `.planning/reconciliation/<vendor>/` has either a closed finding or a documented `wontfix-v3` / `defer-entitlement` status for every Drift instance the Verification surfaces.
- Re-running `gridflow-drift-check` returns "no new Drift" (or only documented-deferred Drift).
- The upstream Vault is committed to a private GitHub repo.
- The vendored snapshot in `gridflow-front-end/vault/<vendor>/` matches the reconciled upstream Vault.

## Load-bearing Drift findings (from drift research)

These are the concrete cases Phase 7 must surface and triage. References are to `.planning/research/post-v1/drift-detection/DRIFT-SURFACES.md` examples.

### Elexon — fixable (open)

- `ndf` and `ndfd` schema table omits `published_at` (DRIFT-SURFACES § 4.1) — Canonical has it (`elexon.py:194`); Vault names `issue_time` instead in metadata block. Deployed-wrong on the live Site.
- `fuelhh` schema table omits `published_at` (DRIFT-SURFACES § 4.2) — Canonical has it (`elexon.py:87`); Vault metadata says `published_at` but schema table doesn't list the row. Intra-file Drift.
- 18 ENTSO-E `resolution` field nullability mismatches across Vault tables.

### ENTSO-E — defer-entitlement

- 33 datasets return HTTP 401 from the current `.env` API token (DRIFT-SURFACES § 4.4). Token works for 11 endpoints, not these 33. Resolution path is **Q-DD-04** in the drift research: either obtain extended ENTSO-E API entitlement, or accept `skip-with-warn` semantics and ship the affected pages with a "requires additional entitlement" caveat. Decision must be taken before Phase 9 (ENTSO-E content build) can ship those 33 datasets.

### ENTSO-G — fixable (open)

- 4 endpoints return HTTP 404 (DRIFT-SURFACES § 4.5): `hydrogen_content`, `interruptions`, `methane_content`, `oxygen_content`. Vault entries describe endpoints the vendor took down; Vault edits should either delete or mark them `removed`.
- `physical_flows` 35-field mismatch in one .md file (DRIFT-SURFACES § 4.6) — the worst single-file Drift in the ecosystem. Vault has been used to dump raw response keys; the silver-layer consolidated them into two derived columns.

### Wontfix-v3 (out of scope per PROJECT.md)

- 58 ecosystem-wide `manual_transformer_schema` cases (22 of which are Elexon) — closing the gap means declaring `ElexonAGPT`, `ElexonAGWS`, `ElexonFOU2T14D`, etc. in `gridflow.schemas.elexon` (cross-repo work in the gridflow repo). PROJECT.md § Out of Scope explicitly defers this to v3.

## Open items left from the grill (decide during discuss-phase)

- **Repo name for the private Vault repo.** User to confirm. Default lean: `EBentham/quant-vault` matching the local directory name.
- **ENTSO-E entitlement resolution path.** Two options:
  - Secure additional API access (cost: time + possibly money + vendor lead time)
  - Accept skip-with-warn policy and ship 33 ENTSO-E dataset pages with a caveat
  - Decision must be taken before Phase 9; can be deferred to that phase's discuss step if desired.
- **7 vs 6 Vendor count.** Site splits GIE into AGSI + ALSI as two sub-hubs; PROJECT.md counts as 6 Vendors. Decide whether to keep the visible split. Likely a no-op (visible split is a UI choice, doesn't affect Phase 7).
- **Phase 7 task granularity.** Should this be one large plan or multiple sub-plans (e.g. one per Vendor)? Reasonable to split: `7a verifier-wrapping`, `7b run-verification-and-triage`, `7c fix-elexon`, `7d fix-entsog`, etc. Decide during plan-phase.

## Artifacts produced this session

- [CONTEXT.md](../CONTEXT.md) — domain glossary; new term **Vendor docs** added, SoT ambiguity flagged.
- [docs/adr/0001-reconciliation-phase-added-to-v2.md](../docs/adr/0001-reconciliation-phase-added-to-v2.md)
- [docs/adr/0002-vault-hosted-private-github-repo.md](../docs/adr/0002-vault-hosted-private-github-repo.md)
- [docs/agents/issue-tracker.md](../docs/agents/issue-tracker.md) — re-pointed at local markdown (`.planning/issues/`, `.planning/reconciliation/<vendor>/`)
- [docs/agents/triage-labels.md](../docs/agents/triage-labels.md)
- [docs/agents/domain.md](../docs/agents/domain.md)

## Recommended next action

Invoke `/gsd-discuss-phase 7` with the prompt at the end of this handoff. The discuss-phase agent should:

1. Read `CONTEXT.md`, ADR-0001, ADR-0002, this handoff, and the drift-detection research at `.planning/research/post-v1/drift-detection/` (start with SUMMARY.md, then DRIFT-SURFACES.md and CI-ARCHITECTURE.md).
2. Resolve the open items above via the standard discuss-phase questioning.
3. Update `PROJECT.md` § Active + § Key Decisions to reflect the rescope, renumber phases in `ROADMAP.md`, and update `STATE.md`.
4. Proceed to `/gsd-plan-phase 7`.

The grill produced decisions; this handoff hands them off. The discuss-phase agent is expected to honour decisions 1-7 above without re-litigating them.
