# Phase 7: Reconciliation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `07-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-05-19
**Phase:** 7-reconciliation
**Areas discussed:** Vault repo name · ENTSO-E entitlement resolution path · Phase 7 task granularity

> **Pre-context:** This discuss-phase session ran against a Phase 7 that had already been pre-scoped in a prior `/grill-with-docs` interview on 2026-05-19. See [`.planning/V2-PHASE-7-HANDOFF.md`](../../V2-PHASE-7-HANDOFF.md) for the full grill output, including the 7 binding decisions (Vault-is-derivative, Reconciliation = drift-research-brought-forward, per-Vendor gating, all-Vendor-upfront, Pocock + GSD split, local markdown not GitHub Issues, private repo no GitHub App). Those decisions were honoured here without re-litigation per the handoff contract. Only 3 open items remained for this session to resolve.

---

## Vault repo name

| Option | Description | Selected |
|--------|-------------|----------|
| `EBentham/quant-vault` | Matches the local directory name (`C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\`). Zero rename cost, lowest cognitive friction. Default lean from ADR-0002. | ✓ |
| `EBentham/gridflow-vault` | Names the repo by what it documents rather than by its tool. More discoverable if the Vault is ever made public, but creates a name mismatch with the local directory. | |
| `EBentham/gridflow-knowledge` | Neutral name that doesn't pin the vault to either Obsidian (quant-vault) or gridflow specifically. Useful if scope expands beyond gridflow vendors later. | |

**User's choice:** `EBentham/quant-vault` (the recommended option, matching ADR-0002's default lean).
**Notes:** No rename of the local directory. Captured in `07-CONTEXT.md § D-09` and propagated to ROADMAP.md, REQUIREMENTS.md (RECON-04), and PROJECT.md Key Decisions.

---

## ENTSO-E entitlement resolution path

| Option | Description | Selected |
|--------|-------------|----------|
| Defer to Phase 9 — triage as needs-info now | Mark all 33 as `status: needs-info`, `reason: defer-entitlement`. Don't block Phase 7 on external vendor lead time. Phase 9 (ENTSO-E content build) discuss-phase chooses extend-access vs skip-with-warn when content shape is being decided. | ✓ |
| Try to extend ENTSO-E API access during Phase 7 | Apply for additional ENTSO-E entitlement now. Risk: vendor lead time is unbounded; could block Phase 7 completion. Reward: Phase 9 ships all 49 ENTSO-E pages without skip-with-warn caveat. | |
| Lock skip-with-warn for v2 now | Decide upfront: ship 33 ENTSO-E pages with a 'requires additional entitlement' caveat. Closes the question early; downside is committing to the lesser outcome before Phase 9 needs to. | |

**User's choice:** Defer to Phase 9 — triage as `needs-info` now.
**Notes:** Captured as `07-CONTEXT.md § D-06`. Phase 7's Verification will emit 33 `needs-info` finding files under `.planning/reconciliation/entsoe/` referencing Q-DD-04 / DRIFT-SURFACES § 4.4. Phase 9's discuss-phase reads those finding files and chooses the resolution path then.

---

## Phase 7 task granularity

| Option | Description | Selected |
|--------|-------------|----------|
| Sub-plans per logical step: `07a` verifier wrap · `07b` run+triage · `07c` fix open bucket · `07d` push Vault to GitHub | 4 focused plans, each with its own commit. Matches the handoff's natural breakpoints. Allows partial-PR review and clearer rollback if any sub-plan goes sideways. Larger Phase 7 surface justifies the split. | ✓ |
| Sub-plans per Vendor: `7a` verifier+infra · `7b` elexon · `7c` entsoe-defer · `7d` entsog · `7e` gie · `7f` neso · `7g` openmeteo · `7h` vault-on-github | Maximum granularity. Lets Vendors with no findings (likely NESO, Open-Meteo) close fast. Cost: more plan-overhead boilerplate; some plans will be near-empty. | |
| One large plan covering all of Phase 7 | Single PLAN.md with all tasks. Lowest planning overhead. Risk: monolithic PR review surface; one failed task blocks reverting unrelated work. | |

**User's choice:** 4 sub-plans per logical step.
**Notes:** Captured as `07-CONTEXT.md § D-05`. The `07c` plan still handles per-Vendor fix work; the granularity decision moves the split from Vendor-boundary to step-boundary. Sequencing inside `07c` is planner's discretion (likely Elexon first since the findings are best-understood, then ENTSO-G, then the others as they emerge).

---

## Claude's Discretion

Items handed to the planner for resolution during `/gsd-plan-phase 7`. Captured in `07-CONTEXT.md § Claude's Discretion`:

- Exact sub-plan filenames (`07a-...-PLAN.md` vs `07-01-...-PLAN.md`)
- Exact JSON schema extensions to `vault-curl-schema-validation.json` (preserve existing keys; extensions additive)
- Exact format of `.planning/reconciliation/<vendor>/<NN>-<slug>.md` finding files (mandatory `status:` + `reason:`; other fields planner's discretion; the `to-issues` skill output is the natural starting shape)
- `[drift]` extras location (vault `pyproject.toml` if it has one vs front-end's — Q-DD-16 default lean)
- Sequencing of `07a` vs `07d` (either order works)
- `LICENSE` for the new `EBentham/quant-vault` repo (likely MIT to match `gridflow-front-end`; planner picks)

## Deferred Ideas

- **ENTSO-E entitlement resolution** — deferred from Phase 7 to Phase 9 discuss-phase (D-06 above).
- **GIE AGSI/ALSI Site rendering split direction** — Vendor count stays at 6 for Phase 7; the Site rendering split is a Phase 10 (4-vendor batch) decision.
- **Cross-repo automated drift CI** — out of v2 scope per ADR-0002 (requires GitHub App auth). Revisit triggers listed in ADR-0002.
- **`gridflow-build --drift-check` flag, `model_json_schema()` snapshot diff, schemathesis, `pytest-examples`** — all v2.1+ work per `07-CONTEXT.md § Deferred`.
- **Pydantic class drift closure (22 Elexon `manual_transformer_schema` cases)** — v3 candidate per PROJECT.md. Phase 7 triages each as `wontfix`/`v3-candidate`.

---

*Discussion log written 2026-05-19 at the close of `/gsd-discuss-phase 7`. Source decisions in [07-CONTEXT.md](./07-CONTEXT.md); upstream context in [V2-PHASE-7-HANDOFF.md](../../V2-PHASE-7-HANDOFF.md).*
