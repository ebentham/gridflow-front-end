---
slug: about_summary
vendor: gie
vendor_label: GIE AGSI+ (Gas Storage)
api_code: AGSI
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "GIE API key (header `x-key`, lowercase) required — free registration at agsi.gie.eu/account/registration"
sources_consulted:
  - vault/gie/about_summary.md
  - gridflow/src/gridflow/schemas/gie.py (no dedicated schema — reference data via AgsiJsonTransformer)
  - gridflow/src/gridflow/silver/gie/agsi.py::AboutSummaryTransformer (lines 402-411) + _about_summary_records (lines 514-561, recursive walker); registered at L626
  - gridflow/src/gridflow/connectors/gie/endpoints.py::ENDPOINTS["about_summary"] (lines 139-145)
  - https://agsi.gie.eu/api/about (vendor docs — interactive HTML; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault about_summary.md — Implementation Delta: live shape vs fixture"
    source_a_says: "Live response shape is `{\"SSO\": {\"Europe\": {<Country>: [...]}}}`; fixture (tests/fixtures/gie/agsi_about_summary_response.json) uses a flat envelope with `data.platform`, `data.totalCompanies`"
    source_b: "silver transformer copes via recursive descent (_about_summary_companies)"
    orchestrator_recommendation: "non-blocking — fixture is stale relative to live shape; transformer handles both via recursion. Fixture regeneration deferred."
  - source_a: "vault — `country` value type"
    source_a_says: "Live `country` is a string (e.g. `\"AT\"`); some `_nested_text` paths assume a dict with `.code` / `.name`"
    source_b: "transformer handles both via `_nested_text` `key == \"code\"` fallback returning `str(value)`"
    orchestrator_recommendation: "non-blocking — covered by `_nested_text` fallback at `silver/gie/agsi.py L582-587`."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** AGSI operators and facilities, <span class="italic fg-accent">hierarchical.</span>

**Lede:** AGSI reference payload organising storage operators by region → country → company → facility — the entity master file used to enrich storage facts with human-readable names and metadata.

**Verified line:** Verified against vendor docs: 2026-05-08 · [GIE AGSI+ · /api/about](https://agsi.gie.eu/api/about)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.gie_agsi.about_summary` |
| API PATH | `/api/about` |
| FREQUENCY | snapshot (on change) |
| PUBLICATION LAG | refreshed on operator inventory update |
| VOLUME | ~71 companies + facilities, ~558 KB payload |
| PRIMARY KEY | `(entity_level, entity_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | snapshot | Cadence |
| 2 | ~558 KB | Payload size |
| 3 | 9 | AGSI countries |
| 4 | SSO/DSR | Entity types |

# Sidebar siblings

- about_listing
- storage_reports
- storage
- unavailability
- news

# Sample chart

- **Type:** `donut`
- **Title:** "AGSI companies by country · current snapshot"
- **Subtitle:** "Donut · company count share · 2026-05-08"
- **Seed:** 12
- **Toggles:** `all` (active)

# Schema

No dedicated Pydantic schema — `AboutSummaryTransformer` extends `AgsiJsonTransformer` and overrides `_records_from_payload` to call `_about_summary_records` (`silver/gie/agsi.py L514-561`), which recurses through the nested `{"SSO": {"Europe": {<Country>: [...]}}}` tree and emits flat company + facility rows. Dynamic columns are added by the `AgsiJsonTransformer` base pass.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `entity_level` | `str` | No | _derived_ | `"company"` or `"facility"`. | `silver/gie/agsi.py L514-561` |
| `entity_code` | `str` | No | `eic` (or `code`) | EIC identifier. | `silver/gie/agsi.py L526-561` |
| `entity_name` | `str` | No | `short_name` / `name` | Falls back to EIC if both blank. | `silver/gie/agsi.py L526-561` |
| `short_name` | `Optional[str]` | Yes | `short_name` | Vendor short label (company only). | dynamic pass-through |
| `country_code` | `Optional[str]` | Yes | `country.code` (or `country` string) | `_nested_text` handles both shapes. | `silver/gie/agsi.py L582-587` |
| `country_name` | `Optional[str]` | Yes | `country.name` | Often null when `country` is a string. | `silver/gie/agsi.py L582-587` |
| `entity_type` | `Optional[str]` | Yes | `type` | `SSO` (company) or `DSR` (facility). | dynamic pass-through |
| `operational_start_date` | `Optional[str]` | Yes | `operational_start_date` | Facility-only. ISO date string. | dynamic pass-through |
| `operational_end_date` | `Optional[str]` | Yes | `operational_end_date` | Facility-only. ISO date string; non-null = decommissioned. | dynamic pass-through |
| `company_code` | `Optional[str]` | Yes | `company` | Facility-only. Parent company EIC. | dynamic pass-through |
| `company_name` | `Optional[str]` | Yes | _derived_ | Facility-only. Filled from parent. | `silver/gie/agsi.py L514-561` |
| `aggregate_code` | `Optional[str]` | Yes | `data.code` | Optional — present if response uses the `data` envelope shape. | dynamic pass-through |
| `aggregate_name` | `Optional[str]` | Yes | `data.name` | Optional. | dynamic pass-through |
| `publication_link` | `Optional[str]` | Yes | `publication_link` | Company-only metadata link. | dynamic pass-through |
| `transparency_template` | `Optional[str]` | Yes | `transparency_template` | Company-only. | dynamic pass-through |
| `operational_information` | `Optional[str]` | Yes | `operational_information` | Company-only. | dynamic pass-through |
| `available_capacities` | `Optional[str]` | Yes | `available_capacities` | Company-only. | dynamic pass-through |
| `tariffs` | `Optional[str]` | Yes | `tariffs` | Company-only metadata link. | dynamic pass-through |
| `has_image` | `bool` | No | _derived_ | True if base64 `image` logo present. | `silver/gie/agsi.py L514-561` |
| `data_provider` | `str` | No (default `"gie_agsi"`) | _derived_ | Always `"gie_agsi"`. | `silver/gie/agsi.py L337` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver write timestamp. | `silver/gie/agsi.py L338` |

**PARQUET PATH:** `data/silver/gie_agsi/about_summary/year=YYYY/month=MM/`
**PARTITION BY:** ingestion date (snapshot reference table)
**DEDUP KEY:** `(entity_level, entity_code)` — falls back via `AgsiJsonTransformer.unique` (`silver/gie/agsi.py L344-348`)

# Sample data

| entity_level | entity_code | entity_name | short_name | country_code | entity_type | company_code | company_name | operational_start_date | operational_end_date | has_image |
|---|---|---|---|---|---|---|---|---|---|---|
| company | 25X-GSALLC-----E | GSA LLC | GSA | AT | SSO | _null_ | _null_ | _null_ | _null_ | True |
| facility | 25W-SPHAID-GAZ-M | UGS Haidach (GSA) // historical data prior to 6 Oct 2022 | _null_ | AT | DSR | 25X-GSALLC-----E | GSA LLC | 2011-01-01 | 2022-10-07 | False |
| **company** | **21X0000000011756** | **EWE Gasspeicher** | **EWE** | **DE** | **SSO** | **_null_** | **_null_** | **_null_** | **_null_** | **True** |
| facility | 37W000000000002O | EWE H-Gas Zone | _null_ | DE | DSR | 21X0000000011756 | EWE Gasspeicher | 2012-04-01 | _null_ | False |
| company | 21X-DEMO-ALPHA | Demo Alpha SSO | Alpha | FR | SSO | _null_ | _null_ | _null_ | _null_ | True |
| facility | 21W-DEMO-ALPHA-1 | Alpha One Storage | _null_ | FR | DSR | 21X-DEMO-ALPHA | Demo Alpha SSO | 2014-06-01 | _null_ | False |
| company | 21X-BERGER-NL-G | Bergermeer Operator | TAQA | NL | SSO | _null_ | _null_ | _null_ | _null_ | True |
| facility | 21W-BERGERMEER-G | Bergermeer | _null_ | NL | DSR | 21X-BERGER-NL-G | Bergermeer Operator | 2014-04-01 | _null_ | False |

**Sources:** First two rows (GSA LLC + UGS Haidach) verbatim from vault Silver sample (live 2026-05-08). Remaining 6 rows synthesised respecting the SSO/DSR taxonomy and the hierarchical-to-flat transform. The highlighted **EWE Gasspeicher** company row demonstrates the company-side enrichment over `about_listing` — `short_name` and `has_image: True` (base64 logo present in bronze, summarised as a bool at silver to keep parquet size manageable). The `Berliner Storage` style company entries also carry `publication_link` / `tariffs` metadata when present in the live payload.

# Dataset-specific section: `about_summary` vs `about_listing`

Both datasets surface the same operator universe (~71 companies, ~140 entity rows) but use different response shapes:

- **`about_listing`** (`?show=listing`) — Top-level list of company objects, each with a nested `facilities` array. ~53 KB. Optimal for query inventory planning (`build_storage_query_plan`). No image data.
- **`about_summary`** (no `show` param) — Nested object `{"SSO": {"Europe": {<Country>: [companies...]}}}`. ~558 KB (10× larger). Includes company `image` (base64 PNG logo), `publication_link`, `tariffs`, `transparency_template`, `operational_information` metadata.

Use `about_listing` for joins / query planning; use `about_summary` for company-metadata enrichment (UI labelling, logo display).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `agsi.gie.eu/api/about` (no query params)
- AUTH: header `x-key` (LOWERCASE — `X-Key` returns 401), key from env `GIE_API_KEY`. Free registration at [agsi.gie.eu/account/registration](https://agsi.gie.eu/account/registration).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/gie_agsi/about_summary/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.gie.agsi.AboutSummaryTransformer` (extends `AgsiJsonTransformer`, registered at `silver/gie/agsi.py L626`)

**Tab 1 — Example URL**
```
https://agsi.gie.eu/api/about

Header: x-key: $GIE_API_KEY
```

**Tab 2 — DuckDB · SQL**
```sql
-- Companies with publication links and current image, by country
SELECT country_code,
       entity_name AS company,
       short_name,
       has_image,
       publication_link
FROM read_parquet('data/silver/gie_agsi/about_summary/**/*.parquet')
WHERE entity_level = 'company'
ORDER BY country_code, company;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/gie_agsi/about_summary/**/*.parquet")
# Build a company-name lookup table for joining onto storage_reports
lookup = (
    df.filter(pl.col("entity_level") == "facility")
      .select("entity_code", "entity_name", "country_code", "company_code", "company_name",
              "operational_start_date", "operational_end_date")
      .sort("country_code", "company_code", "entity_code")
)
print(lookup.head(20))
```

# Caveats

## 01 Live shape is `{"SSO": {"Europe": {<Country>: [...]}}}`, fixture is `{"data": {...}}`

Live response uses a nested `SSO → Europe → Country` tree. The fixture uses a flat `{"data": {"platform": "AGSI", "totalCompanies": "3", ...}}` envelope. `_about_summary_companies` (`silver/gie/agsi.py L563-580`) recurses through both shapes. Fixture is stale but functionally compatible. *(Source: vault Implementation Delta.)*

## 02 No Pydantic schema — reference data via dynamic columns

Unlike `storage` / `storage_reports`, no typed silver contract. Columns derive from recursive walker + `AgsiJsonTransformer` dynamic pass. *(Source: vault Silver layer note; `silver/gie/agsi.py L402-411`.)*

## 03 Base64 `image` logos summarised at silver

Bronze keeps the full base64 PNG bytes; silver replaces with `has_image: bool` to control parquet size. *(Source: vault Known Issues.)*

## 04 `country` value type varies

Live response: `country: "AT"` (string). Some `_nested_text` paths expect a dict with `.code` / `.name`. The fallback at `silver/gie/agsi.py L582-587` returns `str(value)` for the string case. *(Source: vault Implementation Delta.)*

## 05 `x-key` header MUST be lowercase

`X-Key` returns HTTP 401. *(Source: vault Known Issues #1.)*

## 06 No pagination — single ~558 KB response

`/api/about` returns a monolithic JSON object with no `last_page` / `total`. Vendor expectation is one fetch per refresh. *(Source: vault Known Issues.)*

# Related datasets

- **`about_listing`** — Flat list-shaped version of the same inventory. `snapshot` — preferred for query planning; this dataset is preferred for company-metadata enrichment (logos, publication links). `gie · storage · snapshot`
- **`storage_reports`** — Per-entity storage levels. `daily` — join on `entity_code` / `company_code` to attach company names and operational status to storage facts. `gie · storage · daily`
- **`unavailability`** — Per-facility outage records. `as published` — join on facility EIC to attach human-readable facility names and parent-company names. `gie · storage · as published`
- **`storage`** — Country-level storage rollup. `daily` — `about_summary` defines the SSO → country structure used to label country aggregates. `gie · storage · daily`
