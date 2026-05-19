# gridflow-front-end context

The data-catalog and portfolio site for the gridflow ecosystem. The site is a published view rendered from a derivative documentation layer (the Obsidian vault), itself derived from the canonical code in gridflow + live vendor APIs. This file is the glossary for that ecosystem.

## Language

**Canonical**:
The structural source of truth for a dataset — the Pydantic schema + silver transformer + connector endpoint definition in the `gridflow` repo. Disagreement with anything else is resolved by changing the other thing, not the canonical.
_Avoid_: ground truth (overloaded), gold standard (was previously used for vault — wrong)

**Vault**:
The Obsidian knowledge base at `quant-vault/30-vendors/`. Derivative documentation layer authored from Canonical + Live API. **Never overrides the Canonical** — when they disagree, the Vault is wrong.
_Avoid_: source of truth, gold standard

**Live API response**:
The actual JSON returned by a vendor endpoint. Sits between the Canonical and the Vault: it's what the Canonical code is *meant* to parse. Verified ad-hoc by `quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py`.
_Avoid_: production data (not always production)

**Vendor docs**:
The vendor's own documentation of their API, published on their website (Elexon BMRS docs, ENTSO-E Transparency Platform docs, etc.). An *input* the gridflow author reads when writing the Canonical; itself never authoritative — when Vendor docs and Live API disagree, the Live API wins. Real case: Elexon renamed BOAL → BOALF on the live API; documented in `boal.md:182-186`.
_Avoid_: vendor spec, API spec, golden source — all imply authoritative

**Site**:
The deployed static documentation pages at `https://ebentham.github.io/gridflow-front-end/`. Generated from Vault content by `gridflow-build` (Python + Jinja2). Never authored directly; always a regenerated artefact.
_Avoid_: docs, front-end (ambiguous with the repo name)

**Drift**:
The state where a derivative layer disagrees with the Canonical. Has 5 sub-categories (Structural, Semantic, Referential, Temporal, Volumetric) per `.planning/research/post-v1/drift-detection/DRIFT-SURFACES.md`. Drift is a property of the relationship between layers, not of any single layer.
_Avoid_: bug, stale, out-of-date — all too vague

**Verification**:
The one-shot operation of running the verifier script against current Canonical + Live API + Vault, producing a JSON report. Inputs to Reconciliation but not the same thing — Verification finds Drift, Reconciliation fixes it.
_Avoid_: testing (overloaded), validation (overloaded)

**Reconciliation**:
The operation of identifying Drift and pushing the fix into the *derivative* layer (Vault → match Canonical). For v2, executed via the drift-detection MVP at `.planning/research/post-v1/drift-detection/`. Front-loaded as Phase 7 for all 6 Vendors before any content phase per ADR-001.
_Avoid_: sync (suggests two-way), audit (suggests one-off)

**Vendor**:
A data source upstream of the gridflow ecosystem — Elexon, ENTSO-E, ENTSO-G, GIE, NESO, Open-Meteo. v2 site coverage is 6 Vendors; GIE is occasionally split into AGSI + ALSI on the Site (2 Site sub-hubs), but the upstream Vendor count remains 6.
_Avoid_: provider, source (overloaded)

**Dataset**:
A Vendor-level concept: one named time-series or table available from a Vendor's API. Each Dataset has at most one Pydantic class in the Canonical, one `.md` file in the Vault, one `<dataset>.html` on the Site. v2 target: 163 Datasets across 6 Vendors.
_Avoid_: endpoint (a Dataset can map to multiple endpoints / param shapes), table (loaded with DB connotations)

## Relationships

- **Vendor docs** is an authoring *input* to **Canonical** (gridflow author reads them); can lag the **Live API**
- **Live API response** is the runtime ground truth — what the API actually serves; the **Canonical** code is *meant* to parse it
- **Vault** is derived from **Canonical** + **Live API**; never overrides either
- **Site** is rendered from **Vault** (by `gridflow-build`)
- **Drift** is the relationship state between **Vault** and (**Canonical** + **Live API**)
- **Verification** detects **Drift**; **Reconciliation** removes it (by editing **Vault**, never **Canonical**)
- One **Vendor** owns many **Datasets**; one **Dataset** belongs to exactly one **Vendor**

Trust chain at verification time, in order: **Live API → Canonical → Vault → Site**. Vendor docs are not in the trust chain — they're an authoring input that can itself be wrong.

## Example dialogue

> **Dev:** "The Site shows `published_at` for fuelhh but a recruiter says the parquet doesn't have that column."
> **Domain:** "Which layer has it right? Check the **Canonical** — if `gridflow.schemas.elexon.ElexonFuelHH` declares `published_at`, the **Vault** schema table is the one with **Drift**, and **Reconciliation** means editing `fuelhh.md` to add the row. Never change the schema to match the vault."

## Flagged ambiguities

- "Gold standard" was used for the **Vault** in early discussion; retired — the **Canonical** sits above the Vault, so calling the Vault "gold standard" was a category error.
- "Vendor docs as the actual golden source of truth" — also retired. Vendor docs are an *input* to authoring the Canonical, not the arbiter. Real failure mode: Elexon renamed BOAL → BOALF on the live API; the vendor docs may have lagged. The trust chain at verification is `Live API → Canonical → Vault → Site`. Vendor docs sit upstream of Canonical at authoring time, not in the trust hierarchy.
- "Reconciliation" must not be confused with two-way sync. Drift always flows Canonical → Vault → Site; **Reconciliation** only ever fixes the derivative direction.
- "Source" appears in vault frontmatter (`source: elexon`) as a Vendor key. The word "source" without qualification is ambiguous (Vendor? Canonical?) — prefer "Vendor" or "Canonical" explicitly.
