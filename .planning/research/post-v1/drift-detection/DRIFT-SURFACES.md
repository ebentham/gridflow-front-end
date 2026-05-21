# Drift surfaces in the gridflow ecosystem

Agent A / 4 — drift detection research package for the v2 milestone.

This file enumerates **what can go out of sync, between which artefacts, with what consequences.** It is the foundation Files 2–4 build on: the inventory drives the taxonomy, the taxonomy drives the failure-mode catalogue, the failure-mode catalogue drives the CI architecture.

## Context (set once)

The gridflow ecosystem is three repos plus one published artefact:

1. `gridflow` (`C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\`) — Python ETL pipeline. Pydantic schemas, silver transforms, vendor-API connectors. **Canonical source of truth.**
2. `quant-vault` (`C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\`) — Obsidian knowledge base. 33 Elexon datasets, plus ENTSO-E / ENTSO-G / GIE / Open-Meteo / NESO. **Derivative documentation layer.** Ships its own validator at `30-vendors/scripts/verify_curl_and_silver_schema.py`.
3. `gridflow-front-end` (this repo) — Static documentation site. Build script at `src/gridflow_front_end/build.py` reads vault `.md` files and renders HTML into `site/hifi/data-sources/<vendor>/<dataset>.html`. v1 shipped on 2026-05-18 (PR #11).
4. **Live vendor API responses** — the ground truth that nothing in the repos directly observes; the verifier in (2) calls them.

The locked source-of-truth hierarchy is `code > live API > vault > site`. v1 baked in a one-time `verified-against-vendor-docs: 2026-05-08` snapshot per dataset. **Ongoing drift detection is deferred to v2.** This file scopes the v2 problem.

---

## 1. Inventory of artefacts

Every place a claim about a dataset can live, plus the surface that emits it.

### 1.1 Pydantic schemas
Path: `gridflow/src/gridflow/schemas/*.py`. Eight files: `__init__.py`, `common.py`, `elexon.py`, `entsoe.py`, `entsog.py`, `gie.py`, `neso.py`, `weather.py` (`C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\src\gridflow\schemas\` glob).

Per file, one Pydantic v2 class per silver-layer dataset. For Elexon: `ElexonSystemPrice` (`elexon.py:25`), `ElexonGenerationByFuel` (`elexon.py:61`), `ElexonFuelHH` (`elexon.py:79`), `ElexonBOAL` (`elexon.py:99`), `ElexonBOD` (`elexon.py:126`), `ElexonMID` (`elexon.py:149`), `ElexonFrequency` (`elexon.py:169`), `ElexonDemandForecast` (`elexon.py:185` — covers both NDF and NDFD via `forecast_type` discriminator), `ElexonWindForecast` (`elexon.py:206`), `ElexonPN` (`elexon.py:226`), `ElexonDISBSAD` (`elexon.py:246`), `ElexonBMUnit` (`elexon.py:269`).

Each class declares: field name (Python identifier), Python type (including `| None` for nullable), value constraints (`Field(ge=..., le=...)`, `pattern=...`), and `field_validator` decorators for cross-field invariants like UTC-aware datetime (`elexon.py:53-58`). **This is the canonical schema. Everything downstream is a derivative claim that must match.**

Who writes it: the gridflow author, during silver-layer development.

### 1.2 Silver-layer transformers
Path: `gridflow/src/gridflow/silver/<vendor>/<dataset>.py`. 73 files under the glob `gridflow/src/gridflow/silver/**/*.py`. For Elexon: 27 files — `freq.py`, `boal.py`, `mid.py`, `fuelhh.py`, etc.

Some datasets get an importable Pydantic class via 1.1 above. Many do not — the verifier classifies these as `manual_transformer_schema`. The validation report at `quant-vault/30-vendors/vault-curl-schema-validation.md:9` records **58 manual_transformer_schema cases across the full ecosystem** (22 of which are Elexon: `agpt`, `agws`, `atl`, `fou2t14d`, `fuelinst`, `imbalngc`, `inddem`, `indgen`, `indo`, `indod`, `itsdo`, `lolpdrm`, `market_depth`, `melngc`, `netbsad`, `nonbm`, `remit`, `soso`, `temp`, `tsdf`, `tsdfd`, `uou2t14d` — listed in `quant-vault/30-vendors/vault-amendment-plan.md:208`). For these, the schema shape is reconstructed from the live response keys; there is no static type to lint against.

Who writes it: the gridflow author. Test fixtures in `gridflow/tests/silver/elexon/test_*.py` (parallel filenames) pin row counts and example outputs.

### 1.3 Connector endpoint registries
Path: `gridflow/src/gridflow/connectors/<vendor>/endpoints.py`. Six files under the glob `gridflow/src/gridflow/connectors/**/endpoints.py`. The Elexon one is the densest.

Key shapes inside `connectors/elexon/endpoints.py`:

- `ParamStyle` enum at lines 13-21 — `SETTLEMENT_DATE`, `SETTLEMENT_DATE_PERIOD`, `PUBLISH_DATETIME`, `DATE_PATH`, `NO_PARAMS`. Five variants.
- `ElexonEndpoint` frozen dataclass at lines 23-39 — `path`, `description`, `param_style`, `date_param`, `period_param`, `supports_pagination`, `from_param`, `to_param`, `stream_path`, `max_chunk_hours`.
- `EXCLUDED_ENDPOINTS` dict at lines 43-52 — three entries (`bod`, `generation_by_fuel`, `indicative_imbalance_volumes`) with prose rationale.
- `ENDPOINTS` dict at lines 57-274 — **33 entries** matching the v1 site scope locked in `PROJECT.md`.
- `build_params()` function at lines 277-312 — switches on `param_style` to build the query dict.

Five Elexon endpoints carry per-endpoint overrides that vault docs must mirror: `boal` has `path="/datasets/BOALF"` with `from_param="from"` / `to_param="to"` (lines 67-73 — the renamed endpoint), `freq` uses `measurementDateTimeFrom/To` (lines 107-114), `lolpdrm` caps at `max_chunk_hours=1` (line 234), `remit` and `soso` cap at `max_chunk_hours=23` (lines 240-254), `uou2t14d` caps at `max_chunk_hours=4` (line 154).

Who writes it: the gridflow author, when adding or evolving a connector.

### 1.4 Vault dataset markdown — frontmatter
Path: `quant-vault/30-vendors/<vendor>/datasets/<slug>.md`. 33 Elexon files under `quant-vault/30-vendors/elexon/datasets/*.md`; many more for `entsoe`, `entsog`, `gie`, `neso`, `open-meteo`.

Frontmatter block at the top of each file. From `fuelhh.md:1-7`:

```
---
source: elexon
dataset_key: fuelhh
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---
```

Five keys: `source` (vendor key, lowercase), `dataset_key` (slug, must match the filename and the connector dict key), `vendor` (display label), `last_verified` (ISO date — temporal anchor), `layer_coverage` (which medallion layers are documented). The `last_verified` value is the load-bearing temporal claim — it is the date stamp the verifier ran successfully.

Who writes it: the vault author, hand-authored per the `gridflow-dataset-spec` skill.

### 1.5 Vault dataset markdown — Silver schema table
Inside each dataset .md file, after the `## Silver layer` header. From `fuelhh.md:107-115`:

```
| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | ... |
| `settlement_period` | `int` | No | `settlementPeriod` | ... |
| ...
```

Five columns: Field (Python identifier), Python type (string label, not parsed), Nullable (`Yes`/`No`), Source field (bronze response key), Notes (prose).

Adjacent to the table, four bullet lines name the transformer class and Pydantic class (`fuelhh.md:100-103`): `**Transformer class**: gridflow.silver.elexon.fuelhh.FuelHHTransformer`, `**Pydantic schema**: gridflow.schemas.elexon.ElexonFuelHH`, `**Dedup key**: (settlement_date, settlement_period, fuel_type)`, `**Point-in-time field**: published_at`.

**Open question:** the `gridflow-build` script reads multiple things from each .md file — the metadata block (transformer / schema / dedup key / point-in-time) at lines 100-103, and the table at lines 107-115, **independently**. The current `fuelhh.md` claims `Point-in-time field: published_at` in the metadata block but the schema table omits `published_at` from the field list. The deployed site at `site/hifi/data-sources/elexon/fuelhh.html:181` shows `published_at` from the metadata, but the schema table on the site (around line 270 of the .html) does not include the field. **This is intra-file drift inside a single vault note** — neither the verifier nor any current CI gate catches it.

Who writes it: the vault author. Verifier at `quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py` checks the **table** against the Pydantic class (if one is importable); it does **not** check the metadata block.

### 1.6 Vault dataset markdown — prose sections
`## Known issues and gotchas`, `## Implementation delta`, `## Modelling notes`. Free-form prose. From `boal.md:182-186`: `**Path rename**: vault endpoints.md (pre-V1) listed path as /datasets/BOAL; docs and code use /datasets/BOALF (vendor renamed BOAL → BOALF). Vault page now corrected.` This is the audit trail for a real drift event that was caught and resolved manually.

Who writes it: the vault author, narrated when fixing drift or documenting gotchas.

### 1.7 Vault validation outputs
`quant-vault/30-vendors/vault-curl-schema-validation.md` (human report) and `vault-curl-schema-validation.json` (machine report). Generated by `quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py`. Last generated `2026-05-16T15:34:03.495442Z` per `vault-curl-schema-validation.md:3`.

Summary at `vault-curl-schema-validation.md:7-9` (most recent run):
- Curl examples: `122` passed, `33` failed_auth, `7` failed
- Authenticated bronze responses: `18` ok, `35` http_failed
- Silver schemas: `56` passed, `33` failed, `58` manual_transformer_schema, `14` no_silver_schema_table, `1` no_silver_section

This **already exists** and **already finds drift**. It does not run in CI for either repo today.

Who writes it: the verifier script, on demand.

### 1.8 Generated site HTML
Path: `site/hifi/data-sources/<vendor>/<dataset>.html`. Per v1 plan (REQ BUILD-07 in `REQUIREMENTS.md:26`), this directory is gitignored post-Phase-3; CI runs `gridflow-build` before `upload-pages-artifact`.

Each rendered page carries:
- A `verified-against-vendor-docs: YYYY-MM-DD` micro-line per REQ ELX-07 (`REQUIREMENTS.md:42`). On `fuelhh.html:44`: `Verified against vendor docs: 2026-05-08`.
- An inline `<code>` Pydantic-class reference per REQ ELX-08 (`REQUIREMENTS.md:43`). On `fuelhh.html` around line 287 (and rendered from the vault metadata block at `fuelhh.md:101`): `Defined in gridflow.schemas.elexon.ElexonFuelHH`.
- A schema table reflecting `fuelhh.md:107-115`.
- A sample JSON block.
- API tabs with the URL + a copyable curl block reflecting `fuelhh.md:48-56`.

Who writes it: `gridflow-build`. Source: `src/gridflow_front_end/build.py`.

### 1.9 Vendor manifests
Paths: `site/hifi/data/elexon.json`, `site/hifi/data/entsoe.json`, `site/hifi/data/vendors.json`.

`elexon.json` enumerates the 33 datasets grouped into 4 categories (Generation, Prices & Balancing, Demand & Forecasts, System & Reference) — read from `site/hifi/data/elexon.json:3-60`. Each dataset entry carries `id`, `title`, `freq`, `lag`, `rows`. Counts are derived from `len(group.datasets)` at build time.

Who writes it: the front-end author, hand-edited. Drift-detection question: does the manifest's `id` list match the vault's `dataset_key` list match the connector's `ENDPOINTS` dict keys?

### 1.10 Jinja2 templates
Path: `templates/*.html.j2` per the build script comment at `src/gridflow_front_end/build.py:49`. Render contracts:
- `dataset.html.j2` — per REQ BUILD-03 (`REQUIREMENTS.md:22`), captures the 7-section anatomy.
- `vendor-hub.html.j2` — REQ BUILD-04 (`REQUIREMENTS.md:23`).
- `vendor-coming-soon.html.j2` — REQ BUILD-05 (`REQUIREMENTS.md:24`).

Drift risk: when the template adds/removes a `{{ x }}` reference, every vault file that doesn't supply `x` either fails to render (StrictUndefined per `build.py:46`) or renders blank.

Who writes it: the front-end author. Template is the bridge that converts intent in (1.4)-(1.6) into committed HTML in (1.8).

### 1.11 Live vendor APIs
Elexon BMRS at `https://data.elexon.co.uk/bmrs/api/v1` (no auth for tested endpoints — `fuelhh.md:28`). ENTSO-E at `https://web-api.tp.entsoe.eu` (API-key required — `build.py:104-105`). ENTSO-G at `https://transparency.entsog.eu/`. GIE at `https://agsi.gie.eu/` and `https://alsi.gie.eu/`. Open-Meteo at `https://open-meteo.com/`. NESO Carbon Intensity at `https://carbonintensity.org.uk/`.

These are the *real* canonical source — what the connectors actually parse. Nothing in the deployed artefact observes them; only the verifier in (1.7) does.

---

## 2. Drift edges

Pairs of artefacts that can fall out of sync. Detection difficulty: **trivial** (regex), **moderate** (parse + compare two files), **hard** (live HTTP call + auth + diff against a model). Blast radius: **cosmetic** (typo, not misleading), **misleading** (recruiter can be misled but nothing crashes), **dangerous** (recruiter copy-pastes example, gets 404/wrong-shape; or build fails).

| # | Edge | Detection | Blast radius | Example failure mode |
|---|------|-----------|--------------|-----------------------|
| 1 | Pydantic field name vs vault `Silver schema` table row | moderate (import class + parse table) | misleading | `ElexonFuelHH.published_at` exists; `fuelhh.md:107-115` table omits it. |
| 2 | Pydantic field nullability vs vault `Nullable` column | moderate | misleading | `ElexonDemandForecast.national_demand_mw: float` (non-nullable in code, `elexon.py:192`) vs `ndf.md:109` Nullable=Yes. |
| 3 | Pydantic schema vs generated site `<table>` schema rows | trivial after build (parse HTML) | dangerous | Site shows obsolete field after gridflow rename; recruiter queries by stale name. |
| 4 | Connector `ENDPOINTS[k].path` vs vault `Path` field | trivial (regex/grep) | dangerous | BOAL → BOALF rename (`endpoints.py:67-73`); vault had to be hand-corrected per `boal.md:184`. |
| 5 | Connector `ENDPOINTS[k].path` vs live API response | hard (live HTTP call) | dangerous | ENTSOG 4 endpoints currently return HTTP 404 (`vault-curl-schema-validation.md:48-51`). |
| 6 | Connector `ParamStyle` / `from_param` / `to_param` vs vault Query Parameters table | moderate | dangerous | `freq` uses `measurementDateTimeFrom` (`endpoints.py:111-112`) — if vault docs `publishDateTimeFrom`, recruiter's curl silently returns wrong window. |
| 7 | Bronze sample JSON in vault vs live API response shape | hard (live HTTP + JSON diff) | misleading | Vendor renames `publishTime` → `publishedAt` mid-cycle; vault sample is from old run. |
| 8 | Bronze response keys vs Pydantic `Source field` claim in vault notes | moderate (live HTTP + parse table) | dangerous | `entsog/datasets/physical_flows.md` vault claims 29 fields that aren't in the silver schema, missing 2 that are (`vault-curl-schema-validation.md:273-276`). |
| 9 | Vault `Pydantic schema: gridflow.schemas...` reference string vs actual importable class | moderate (try import) | misleading | 58 cases ecosystem-wide (`vault-curl-schema-validation.md:9`) where vault names a path with no importable class — `manual_transformer_schema` marker. |
| 10 | Vault `last_verified: YYYY-MM-DD` vs today | trivial (date diff) | misleading | If `last_verified: 2026-05-08` and today is six months later, every claim is suspect. |
| 11 | Site `verified-against-vendor-docs: YYYY-MM-DD` line vs the date the verifier last ran | trivial | misleading | Site bakes in 2026-05-08; verifier ran on 2026-05-16 and found 33 mismatches; site still says verified. |
| 12 | Vault `EXCLUDED_ENDPOINTS` orphans: vault dataset .md for an endpoint that no longer exists in `ENDPOINTS` | trivial (set diff) | misleading | `bod` is excluded (`endpoints.py:43-46`) but a stale vault file could still exist. Currently clean — vault `Glob` on `elexon/datasets/*.md` returns 33, matching `ENDPOINTS`. |
| 13 | Manifest `id` list ↔ vault `dataset_key` list ↔ connector `ENDPOINTS` keys ↔ site filename ↔ rendered count strip | trivial (set diff) | misleading-to-dangerous | v1 shipped with 22/25/28 across three surfaces (`research/SUMMARY.md:92`); fixed to 33 everywhere; nothing structural prevents regression. |
| 14 | ENTSO-E PSR-type taxonomy in vault prose vs the actual `psrType=B*` codes used by the connector | hard | dangerous | New PSR code added by ENTSO-E (e.g. battery storage) silently unmapped; vault claims B25 (`build.py:108`). |
| 15 | Cross-repo path reference: vault `[Silver transformer](.../silver/elexon/fuelhh.py)` ↔ actual file on disk in `gridflow` | trivial (file-exists) | misleading | Silver transform renamed in gridflow; vault link still points to old name. `fuelhh.md:165` references this path. |
| 16 | Site filename slug ↔ vault filename ↔ connector dict key ↔ manifest id | trivial (set diff) | misleading | Casing/underscore drift: `system_prices` keeps underscore from BMRS code (`CLAUDE.md:84`) but everything else is kebab-case. One typo splits the universe. |
| 17 | Vault `Implementation delta` claim about a fixed-drift event vs current code | moderate (parse prose + check code) | cosmetic | `boal.md:182-186` says BOAL→BOALF "now corrected" — if connector reverted, vault would lie. |
| 18 | Build template `{{ x }}` reference vs vault content key | trivial (StrictUndefined raises at build) | dangerous-but-caught | Template adds `{{ silver_dedup_key }}`; vault note omits the metadata line; build fails (loud, good — not silent drift). |
| 19 | `EXCLUDED_ENDPOINTS` dict rationale vs reality | moderate (re-test the endpoint) | misleading | `endpoints.py:48` says `generation_by_fuel` is "Duplicate of fuelhh"; if Elexon split them again, the exclusion becomes stale. |

Total: 19 edges. Some compose (e.g. edge 3 = edge 1 × the template render, edge 11 = edge 10 × the build script). Files 2–4 will collapse compositions into the canonical taxonomy in §3.

---

## 3. Drift taxonomy

Five named categories. Use **exactly** these names so File 4 (CI-ARCHITECTURE) can map failure modes back without ambiguity.

### Structural
**What:** The shape of a contract changed. A field was added or removed on one side; a type widened or narrowed; a new enum variant was introduced.
**Detection signal:** set-diff of field names between two artefacts; or a parsed type-string changing.
**Typical blast radius:** misleading-to-dangerous (recruiter queries by stale field name; pipeline raises ValidationError; new field is silently dropped from silver).
**Example:** `ElexonFuelHH.published_at` exists at `elexon.py:87` but is absent from the schema table at `fuelhh.md:107-115`. Documented in the verifier report (`vault-curl-schema-validation.md:106-107`): `Missing in docs: published_at`. **This drift propagated to the deployed site** — `fuelhh.html` displays the `published_at` mention in the metadata block (rendered from `fuelhh.md:103`) but the rendered schema table omits the field.

### Semantic
**What:** The contract shape is unchanged but the meaning shifted. A nullable flag flipped (Yes ↔ No). Units changed without name change. A range constraint loosened or tightened. The enum is the same length but a value's interpretation changed.
**Detection signal:** parallel-shape comparison where field names agree but constraints differ.
**Typical blast radius:** misleading. Pipeline doesn't crash because the type is the same; the recruiter or modeller absorbs the wrong invariant.
**Example:** `ElexonDemandForecast.national_demand_mw` is non-nullable (`elexon.py:192`, type `float` not `float | None`). `ndf.md:109` claims `Nullable=Yes`. The verifier flags this at `vault-curl-schema-validation.md:131`: `Nullable mismatch: national_demand_mw`. The ENTSO-E `resolution` field is the same drift across 18 datasets (`vault-amendment-plan.md:147-170` enumerates them) — code-side it is `Field(default=None, ...)`; vault tables omit the nullability flag.

### Referential
**What:** A cross-reference name became stale. A file moved or was renamed. A claimed importable Python path no longer resolves. A `[link](path)` points at a deleted file.
**Detection signal:** try-import, file-exists check, regex compile of a `from gridflow.schemas.elexon import X` pattern against the vault's claimed `Pydantic schema: gridflow.schemas.elexon.X` string.
**Typical blast radius:** misleading (recruiter clicks through, hits 404; vault page reads as "fiction").
**Example A — unverifiable reference:** 58 ecosystem-wide cases of `manual_transformer_schema` (`vault-curl-schema-validation.md:9`). 22 of those are Elexon (`vault-amendment-plan.md:208` enumerates). For each, the vault claims an importable Pydantic schema, but the verifier cannot find a class — because no static class exists, only a dynamic transformer. The reference is structurally unfalsifiable until a class is added OR the reference is downgraded per `vault-amendment-plan.md:203-204` to `manual-transformer-reviewed`. **The current site has no machinery to display this distinction.**
**Example B — fixed-then-fragile:** the BOAL → BOALF rename. `endpoints.py:67-73` carries `path="/datasets/BOALF"`; the rename is acknowledged at `boal.md:184` Implementation delta. **The next rename of this class** is the danger — there is no monitoring that would detect Elexon renaming BOALF → BOALG in three months.

### Temporal
**What:** A timestamp claim has expired. The vault's `last_verified:` date is older than the policy threshold. The site's `verified-against-vendor-docs:` micro-line is older than the policy threshold. The verifier has not been re-run.
**Detection signal:** date arithmetic. (today - `last_verified:`) > policy_threshold.
**Typical blast radius:** misleading. The claim was true once; the absence of re-verification means the recruiter cannot tell whether it's still true.
**Example:** `fuelhh.md:5` says `last_verified: 2026-05-08`. Today is 2026-05-18 — ten days old. The verifier last ran 2026-05-16 (`vault-curl-schema-validation.md:3`). Vault sums of these dates is not an automation today; if the v2 milestone is *quarterly* re-verification, every vault page is on a six-month timer that nothing fires.

### Volumetric
**What:** Counts diverged across surfaces. The number of datasets the site claims does not match the number of pages it actually renders does not match the number of vault notes does not match `len(ENDPOINTS)` does not match the manifest length.
**Detection signal:** count-of-files / set-cardinality / parsed-number-on-page diff.
**Typical blast radius:** misleading. The site contradicts itself in a way a recruiter can spot in seconds.
**Example:** v1 inherited 22 dataset pages on disk / 25 IDs in `data/elexon.json` / 28 claimed in the catalogue UI (`research/SUMMARY.md:92`). v1 resolved this to 33 everywhere — `endpoints.py:57-274` has 33 entries; vault has 33 .md files (Glob confirmed); `site/hifi/data/elexon.json:3-60` has 33; site footer/index strip render 33 per REQ ELX-05 (`REQUIREMENTS.md:40`). The structural fix is fragile: adding a new dataset to `ENDPOINTS` and a new vault .md without updating the manifest re-introduces a 34/33/33 split, and nothing today fails to deploy.

---

## 4. Existing in-tree examples

Real drifts that exist today, in order of severity.

### Example 4.1 — Schema → vault → site drift on `ndf`/`ndfd` (Structural + Semantic, deployed)
Canonical: `gridflow/src/gridflow/schemas/elexon.py:185-203` declares `class ElexonDemandForecast` with field `published_at: datetime | None` (line 194). Used by both NDF and NDFD via `forecast_type` discriminator (line 191).

Vault: `quant-vault/30-vendors/elexon/datasets/ndf.md:99` says `**Point-in-time field**: issue_time`. Schema table at `ndf.md:111` lists `issue_time` and omits `published_at`. The companion `ndfd.md` has identical drift.

Verifier finding: `vault-curl-schema-validation.md:128-131` records `failed elexon\datasets\ndf.md: Missing in docs: published_at · Extra in docs: issue_time · Nullable mismatch: national_demand_mw`.

Site impact: `site/hifi/data-sources/elexon/ndf.html:213` renders `Point-in-time field: issue_time` — **the deployed public site is provably wrong against the canonical schema**. A recruiter querying for `issue_time` on the gridflow silver parquet would find no such column.

Truth-source winner: gridflow code. Recovery: fix the vault, rebuild the site.

### Example 4.2 — Schema → vault drift on `fuelhh` (Structural, deployed with intra-file split)
Canonical: `elexon.py:87` declares `published_at: datetime | None = None` on `ElexonFuelHH`.

Vault: `fuelhh.md:103` metadata line says `**Point-in-time field**: published_at` — correct. But the silver schema table at `fuelhh.md:107-115` does NOT list `published_at` as a field row. **Drift within the same vault file.**

Verifier finding: `vault-curl-schema-validation.md:106-107` records `failed elexon\datasets\fuelhh.md: Missing in docs: published_at`.

Site impact: `site/hifi/data-sources/elexon/fuelhh.html:181` displays `Point-in-time field: published_at` (rendered from the metadata block) but the rendered HTML schema table that follows omits the `published_at` row. **A recruiter scanning the schema table cannot find the field they were just told is the point-in-time anchor.**

Worth noting: the build script reads the metadata block at `fuelhh.md:100-103` and the schema table at `fuelhh.md:107-115` as **two independent inputs**. No build-time check verifies they agree. This pattern repeats across `fuelhh`, `windfor`, `ndf`, `ndfd` — every dataset whose canonical schema has `published_at` and whose vault table omits it.

Truth-source winner: gridflow code. Recovery: add the field to the vault schema table.

### Example 4.3 — Path rename caught and resolved on `boal` (Referential, drift-after-fix)
Canonical: `endpoints.py:67-73` declares `boal` with `path="/datasets/BOALF"`. The dict key is still `boal`; only the path was renamed.

Vault: `boal.md:182-186` Implementation delta narrates the event — `**Path rename**: vault endpoints.md (pre-V1) listed path as /datasets/BOAL; docs and code use /datasets/BOALF (vendor renamed BOAL → BOALF). Vault page now corrected.`

Site impact: clean. `site/hifi/data-sources/elexon/boal.html:56` shows `/datasets/BOALF`; `boal.html:45` links to `https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/BOALF`; the curl example at `boal.html:346` uses BOALF.

Why include this: **this is the kind of drift the v2 detection must catch**. It was caught by the verifier and fixed by hand. There is no automation today preventing the same shape of drift on every other Elexon endpoint.

### Example 4.4 — 33 ENTSO-E auth failures (Temporal × Referential)
The verifier report at `vault-curl-schema-validation.md:13-47` lists 33 ENTSO-E datasets returning HTTP 401 from the current `.env` API token. Examples: `actual_generation.md:56`, `cross_border_flows.md:74`, `generation_forecast.md:53`, `wind_solar_forecast.md:53`.

This is **not** missing-key drift — the token works for 11 ENTSO-E endpoints (enumerated at `vault-amendment-plan.md:60-71`). It's entitlement drift: the vendor changed what the token can access. Or the vault examples drifted out of step with the token's entitlements.

Site impact: today, none — the v1 site only ships ONE ENTSO-E dataset (`actual_generation`, the v1 cross-vendor proof per REQ VEND-02). **That one dataset is in the failing list.** The site claims `Verified against vendor docs: 2026-05-08` against an endpoint that returns 401 from the working `.env` key.

Truth-source winner: ambiguous — could be entitlement, token, or example parameters. Recovery: per `vault-amendment-plan.md:117-119`, split ENTSO-E pages into "verified with current token" and "requires additional entitlement", and don't ship the latter as "working curl example."

### Example 4.5 — ENTSOG 404 endpoints (Referential)
`vault-curl-schema-validation.md:48-51` records four ENTSOG endpoints returning HTTP 404:
- `entsog\datasets\hydrogen_content.md:60`
- `entsog\datasets\interruptions.md:46`
- `entsog\datasets\methane_content.md:60`
- `entsog\datasets\oxygen_content.md:60`

Site impact: zero today — v1 ships ENTSOG as a coming-soon stub (`build.py:117-131`). But these vault docs are stale-by-design: they describe endpoints the vendor took down. Without a re-test gate, when the milestone *does* ship these to depth, the curl examples will 404 for any recruiter who tries them.

### Example 4.6 — ENTSOG `physical_flows` massive shape drift (Structural)
`vault-curl-schema-validation.md:273-276` records:
```
failed entsog\datasets\physical_flows.md:
  Missing in docs: flow_gwh_per_day, timestamp_utc
  Extra in docs: booking_platform_key, booking_platform_label, ... (29 extras)
  Nullable mismatch: direction_key, operator_key, operator_label, point_key, point_label, unit
```

The vault has been used as a place to dump raw response keys; the silver-layer schema has consolidated them into two derived columns (`flow_gwh_per_day`, `timestamp_utc`). The silver-vault drift is now 35 field-level mismatches in one file.

This is the worst single-file drift in the ecosystem. v1 doesn't expose it because v1 doesn't render ENTSOG. v2 must close the gap before ENTSOG ships at depth.

### Example 4.7 — 22/25/28 dataset-count discrepancy from v1 (Volumetric, resolved)
Before v1, `site/hifi/data-sources.html` claimed 28 datasets in the catalogue UI; `site/hifi/data/elexon.json` enumerated 25; 22 .html files existed on disk (`research/SUMMARY.md:92`).

v1 resolved this to 33 everywhere per REQ ELX-05 (`REQUIREMENTS.md:40`): connector has 33 (`endpoints.py:57-274`), vault has 33 (Glob on `elexon/datasets/*.md`), manifest has 33 (`elexon.json:3-60`), site footer/index strip renders 33.

Why include: the *resolution* is fragile. Adding a new endpoint to `ENDPOINTS` and a new vault .md without updating `elexon.json` re-introduces a 34/33/33 split. v1 did not introduce a CI gate against this regression.

### Example 4.8 — `EXCLUDED_ENDPOINTS` orphans (Volumetric, currently clean)
`endpoints.py:43-52` declares three exclusions: `bod`, `generation_by_fuel`, `indicative_imbalance_volumes`. Each has a rationale string. Today: the vault has zero `.md` files for any of these three (verified via Glob); the manifest has zero entries for any of these three; the site renders no page for any of these three. **Clean.**

But the exclusion machinery and the rationale strings are not version-bound to anything. If Elexon re-introduces `indicative_imbalance_volumes` and the gridflow author re-adds it to `ENDPOINTS`, the rationale at `endpoints.py:49-51` (`"Removed by Elexon; use active imbalance datasets instead."`) becomes stale and nobody fails to deploy.

---

## 5. Worst-case drift scenario

Concrete sequence walking from gridflow rename to recruiter-facing failure, with current state and proposed v2 state.

**Day 0 (today).** `gridflow/src/gridflow/schemas/elexon.py:87` declares `ElexonFuelHH.published_at: datetime | None = None`. Vault `fuelhh.md:103` says `**Point-in-time field**: published_at`. Site `fuelhh.html:181` displays `Point-in-time field: published_at`. The schema table in all three places technically omits `published_at` from the columns list, but the metadata block claim is consistent. Recruiter who reads the page is told `published_at` is the point-in-time field.

**Day 7.** The gridflow author renames the schema field `published_at` → `publication_time` on `ElexonFuelHH`. The change lands as a commit on gridflow's `main`. The reason: alignment with ENTSO-E's `publicationTime` naming for joinability. Test suite in gridflow passes — `gridflow/tests/silver/elexon/test_fuelhh.py` fixtures are updated in the same PR.

**Day 7 (continued).** No notification reaches the vault. No CI gate in the front-end repo runs the schema-against-vault verifier. The vault still says `published_at`. The site still says `published_at`. The deployed artefact is unchanged.

**Day 14.** The front-end author wants to add a new vault note for a new Elexon endpoint. They edit `fuelhh.md` to add a cross-link in `Modelling notes`. They commit. CI runs `gridflow-build`; the build script doesn't import any gridflow class (it parses vault markdown only — `src/gridflow_front_end/build.py:46`), so the schema drift is invisible to the build. CI deploys. **The deployed site now claims a field name that does not exist in any gridflow parquet.**

**Day 28.** A recruiter at a London energy-trading firm reads the gridflow-front-end. The recruiter pipelines power data themselves. They scan `fuelhh.html`, see `Point-in-time field: published_at`, copy that into a SQL query against their own warehouse. No rows. They check the gridflow GitHub repo for the schema (the site links to it at `fuelhh.html` around line 287 — the cross-repo reference per REQ ELX-08). They find `ElexonFuelHH.publication_time`. **Two truth claims about the same thing disagree.** The recruiter concludes: this site is not maintained.

**Day 35.** The author notices because the recruiter sent a polite email. They hand-fix `fuelhh.md`, rebuild, push. The drift event lasted 21 days. The same hand-fix discipline is required for every renamed field, every endpoint path change, every nullable flip. The author's bandwidth is the rate-limiter.

**What v2 drift CI would change:**
- Day 7: a nightly CI job on the front-end repo (or a pre-deploy step in `deploy.yml`) clones gridflow at HEAD, imports `ElexonFuelHH`, parses `fuelhh.md`'s schema table and metadata block, and compares. The check fails. The deploy doesn't happen. The PR that would have triggered the deploy stays red.
- Day 8: the author sees the red CI status. They check the gridflow commit. They update the vault. They re-run CI. The site deploys with `publication_time` everywhere.
- Drift event reduced from 21 days (deployed-and-wrong) to 24 hours (caught-before-deploy).

This is the v2 story. File 2 (DETECTION-MECHANISMS) enumerates *how* to make the comparison. File 3 (FAILURE-MODES) catalogues *which* shapes of drift this catches and which it misses. File 4 (CI-ARCHITECTURE) wires it into `.github/workflows/deploy.yml` without breaking the build-in-CI / gitignored-output contract from v1's REQ BUILD-07.

---

## Open questions surfaced for File 2–4

1. **Does `gridflow-build` consume the vault metadata block (`**Pydantic schema**: X`) and the silver schema table independently?** Evidence in §1.5: `fuelhh.html` carries both, and they don't agree about `published_at`. If the build is the right place to fail on intra-vault-file disagreement, the CI architecture needs a new check. If the verifier in (1.7) should grow this check, that's a vault-repo change.
2. **Should drift CI run in the front-end repo (vault → site direction, catches "what would deploy")** or **in the vault repo (catches drift earlier in the chain)** or **in both?** v1 deferred this; v2 must answer. The cross-repo coordination shape from `CLAUDE.md:51-57` (vault and gridflow checkouts available at build time) implies the front-end repo is the natural place — it already needs both checkouts.
3. **Temporal threshold:** is the policy "fail if `last_verified` > 90 days" or "warn at 30 days, fail at 180"? File 4 will need a concrete answer for the CI YAML.
4. **`manual_transformer_schema` handling:** these 58 ecosystem-wide cases need a separate UI treatment. The current site does not distinguish "schema-verified" from "manual-transformer-reviewed" per `vault-amendment-plan.md:203-204`. File 3 may want to flag this as a failure-mode the v2 milestone must cover.
5. **ENTSO-E entitlement drift (4.4):** is this a drift the v2 CI should detect, or is it out of scope because the credentials aren't available in CI without secret-management? File 4 must choose.
