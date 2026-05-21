---
slug: about_listing
vendor: gie
vendor_label: GIE AGSI+ (Gas Storage)
api_code: AGSI
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "GIE API key (header `x-key`, lowercase) required — free registration at agsi.gie.eu/account/registration"
sources_consulted:
  - vault/gie/about_listing.md
  - gridflow/src/gridflow/schemas/gie.py (no dedicated schema — reference data via AgsiJsonTransformer / parse_listing_inventory)
  - gridflow/src/gridflow/silver/gie/agsi.py::AboutListingTransformer (lines 414-442, extends AgsiJsonTransformer; registered at L627)
  - gridflow/src/gridflow/connectors/gie/endpoints.py::ENDPOINTS["about_listing"] (lines 146-153) + parse_listing_inventory (lines 253-291)
  - https://agsi.gie.eu/api/about?show=listing (vendor docs — interactive HTML; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault about_listing.md — Implementation Delta: response shape"
    source_a_says: "Live response is a top-level list of 71 company objects (2026-05-08)"
    source_b: "fixture (tests/fixtures/gie/agsi_listing_response.json) wraps the list in a `{\"data\": [...]}` envelope"
    orchestrator_recommendation: "non-blocking — connector parser `_listing_rows` (`endpoints.py L454-463`) accepts either shape; fixture is functionally compatible but stale."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** AGSI operators and facilities, <span class="italic fg-accent">flat-listed.</span>

**Lede:** Flat listing of AGSI storage companies and facilities with EICs and parent-company linkage — the canonical entity inventory used for query planning across `storage_reports` company and facility scopes.

**Verified line:** Verified against vendor docs: 2026-05-08 · [GIE AGSI+ · /api/about?show=listing](https://agsi.gie.eu/api/about?show=listing)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.gie_agsi.about_listing` |
| API PATH | `/api/about?show=listing` |
| FREQUENCY | snapshot (on change) |
| PUBLICATION LAG | refreshed on operator inventory update |
| VOLUME | 71 companies + facilities (live 2026-05-08) |
| PRIMARY KEY | `(entity_level, entity_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | snapshot | Cadence |
| 2 | 71 | Companies (live) |
| 3 | 9 | AGSI countries |
| 4 | SSO/DSR | Entity types |

# Sidebar siblings

- about_summary
- storage_reports
- storage
- unavailability
- news

# Sample chart

- **Type:** `barsH`
- **Title:** "AGSI storage companies · facility count by country"
- **Subtitle:** "Horizontal bars · facility count · snapshot · 2026-05-08"
- **Seed:** 9
- **Toggles:** `all` (active)

# Schema

No dedicated Pydantic schema — `AboutListingTransformer` extends `AgsiJsonTransformer` and overrides `_records_from_payload` to call `parse_listing_inventory` (`connectors/gie/endpoints.py L253-291`), which emits flat rows for both companies and facilities. The schema below is the deterministic shape produced by the override (`silver/gie/agsi.py L419-442`); the `AgsiJsonTransformer` dynamic-column pass adds any other vendor keys present (e.g. `operational_start_date`, `operational_end_date`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `entity_level` | `str` | No | _derived_ | `"company"` or `"facility"`. | `silver/gie/agsi.py L423, L432` |
| `entity_code` | `str` | No | `eic` (or `code`) | EIC identifier (16-char ISO 17442). | `silver/gie/agsi.py L424, L433`; `endpoints.py L260, L276` |
| `entity_name` | `str` | No | `short_name` / `name` | Falls back to EIC if both blank. | `silver/gie/agsi.py L425, L434`; `endpoints.py L261, L277` |
| `country_code` | `Optional[str]` | Yes | `country` | ISO-2 (live shape is a string, not a nested dict). | `silver/gie/agsi.py L426, L435`; `endpoints.py L262, L283` |
| `entity_type` | `Optional[str]` | Yes | `type` | `"SSO"` for company (Storage System Operator), `"DSR"` for facility. | `silver/gie/agsi.py L427, L436`; `endpoints.py L270, L284` |
| `entity_url` | `Optional[str]` | Yes | `url` | Vendor-managed deep-link URL. | `silver/gie/agsi.py L428, L437`; `endpoints.py L271, L285` |
| `company_code` | `Optional[str]` | Yes (facility only) | `company` | Parent company EIC — facility rows only. | `silver/gie/agsi.py L438`; `endpoints.py L286` |
| `company_name` | `Optional[str]` | Yes (facility only) | _derived_ | Parent company `short_name` / `name` — facility rows only. | `silver/gie/agsi.py L439`; `endpoints.py L287` |
| `data_provider` | `str` | No (default `"gie_agsi"`) | _derived_ | Always `"gie_agsi"`. | `silver/gie/agsi.py L337` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver write timestamp. | `silver/gie/agsi.py L338` |

**Dynamic columns** (pass-through via `AgsiJsonTransformer`): `operational_start_date`, `operational_end_date`, and any other facility metadata fields present in the live payload.

**PARQUET PATH:** `data/silver/gie_agsi/about_listing/year=YYYY/month=MM/`
**PARTITION BY:** ingestion date (snapshot reference table; no time-series partition)
**DEDUP KEY:** `(entity_level, entity_code)` — falls back to `(id, url, entity_code, eic)` per `AgsiJsonTransformer.unique` (`silver/gie/agsi.py L344-348`)

# Sample data

| entity_level | entity_code | entity_name | country_code | entity_type | company_code | company_name | operational_start_date | operational_end_date |
|---|---|---|---|---|---|---|---|---|
| company | 25X-GSALLC-----E | GSA LLC | AT | SSO | _null_ | _null_ | _null_ | _null_ |
| facility | 25W-SPHAID-GAZ-M | UGS Haidach (GSA) // historical data prior to 6 Oct 2022 | AT | DSR | 25X-GSALLC-----E | GSA LLC | 2011-01-01 | 2022-10-07 |
| company | 21X0000000011756 | EWE Gasspeicher | DE | SSO | _null_ | _null_ | _null_ | _null_ |
| **facility** | **37W000000000001Q** | **Rehden** | **DE** | **DSR** | **21X-WIEHE--K** | **astora GmbH** | **2011-01-01** | **_null_** |
| company | 21X-DEMO-ALPHA | Demo Alpha SSO | FR | SSO | _null_ | _null_ | _null_ | _null_ |
| facility | 21W-DEMO-ALPHA-1 | Alpha One Storage | FR | DSR | 21X-DEMO-ALPHA | Demo Alpha SSO | 2014-06-01 | _null_ |
| company | 21X-BERGER-NL-G | Bergermeer Operator | NL | SSO | _null_ | _null_ | _null_ | _null_ |
| facility | 21W-BERGERMEER-G | Bergermeer | NL | DSR | 21X-BERGER-NL-G | Bergermeer Operator | 2014-04-01 | _null_ |

**Sources:** First two rows (GSA LLC company + UGS Haidach facility) verbatim from vault Silver sample (live 2026-05-08). Remaining 6 rows synthesised respecting the SSO/DSR taxonomy and the company / facility EIC linkage. The highlighted **Rehden** facility row is one of the largest German storage sites by working-gas volume (~4.4 bcm; ~50 TWh) — illustrates how `about_listing` links a facility EIC (`37W…`) to its parent company EIC (`21X…`) for query planning.

# Dataset-specific section: AGSI entity types

The `entity_type` discriminator follows ENTSOE-G EIC conventions:

- **`SSO`** — Storage System Operator. The company that operates one or more storage facilities. EIC starts with `21X` / `25X` / `37X` (issuer prefix).
- **`DSR`** — Storage facility. The physical storage asset (depleted reservoir, salt cavern, aquifer). EIC starts with `21W` / `25W` / `37W`.

Some facilities carry an `operational_end_date` indicating the facility no longer reports (decommissioned or transferred). Filter `WHERE operational_end_date IS NULL` for a forward-looking inventory.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `agsi.gie.eu/api/about?show=listing` (or path-concatenated form)
- AUTH: header `x-key` (LOWERCASE — `X-Key` returns 401), key from env `GIE_API_KEY`. Free registration at [agsi.gie.eu/account/registration](https://agsi.gie.eu/account/registration).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/gie_agsi/about_listing/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.gie.agsi.AboutListingTransformer` (extends `AgsiJsonTransformer`, registered at `silver/gie/agsi.py L627`)

**Tab 1 — Example URL**
```
https://agsi.gie.eu/api/about?show=listing

Header: x-key: $GIE_API_KEY
```

**Tab 2 — DuckDB · SQL**
```sql
-- Facility count per company, current snapshot only
SELECT company_code,
       company_name,
       country_code,
       COUNT(*) AS facility_count
FROM read_parquet('data/silver/gie_agsi/about_listing/**/*.parquet')
WHERE entity_level = 'facility'
  AND operational_end_date IS NULL  -- exclude decommissioned
GROUP BY company_code, company_name, country_code
ORDER BY facility_count DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/gie_agsi/about_listing/**/*.parquet")
# Build the company → facility EIC map needed for storage_reports facility queries
inventory = (
    df.filter((pl.col("entity_level") == "facility")
              & pl.col("operational_end_date").is_null())
      .select("country_code", "company_code", "entity_code", "entity_name")
      .sort("country_code", "company_code")
)
print(inventory.head(20))
```

# Caveats

## 01 No `last_page` / `total` — single-response listing

Live response is a top-level list of 71 companies (~53 KB, 2026-05-08). No pagination envelope. The fixture wraps the list in `{"data": [...]}` — parser accepts either via `_listing_rows`. *(Source: vault Known Issues + `endpoints.py L454-463`.)*

## 02 No Pydantic schema — reference data via `AgsiJsonTransformer`

Unlike `storage` / `storage_reports`, this dataset has no typed silver contract. Columns are emitted by `parse_listing_inventory` + `AgsiJsonTransformer` dynamic-column pass. *(Source: vault Silver layer note; `silver/gie/agsi.py L414-442`.)*

## 03 `country` is a string, not a nested dict

Live shape carries `country: "AT"` (ISO-2 string). Some other AGSI endpoints (`unavailability`) return `{"name": ..., "code": ...}` — listing differs. *(Source: vault Known Issues.)*

## 04 `operational_end_date` flags decommissioned facilities

Non-null `operational_end_date` means the facility no longer reports to AGSI. Filter `WHERE operational_end_date IS NULL` for a forward-looking inventory. *(Source: vault Known Issues.)*

## 05 `x-key` header MUST be lowercase

`X-Key` returns HTTP 401. *(Source: vault Known Issues #1.)*

## 06 Live live shape is top-level list, fixture is `{"data": [...]}`

`_listing_rows` (`endpoints.py L454-463`) accepts either shape; fixture is stale but functionally compatible. *(Source: vault Implementation Delta.)*

# Related datasets

- **`about_summary`** — Hierarchical (region → country → company → facility) form of the same operator inventory. `snapshot` — use when you need region grouping or the company `image` / `publication_link` metadata. `gie · storage · snapshot`
- **`storage_reports`** — Per-entity storage levels. `daily` — `about_listing` supplies the company and facility EICs the company/facility scopes need. `gie · storage · daily`
- **`unavailability`** — Per-facility outage records. `as published` — join on facility EIC to attach human-readable facility names. `gie · storage · as published`
- **`storage`** — Country-level storage rollup. `daily` — `about_listing` defines the country footprint via the `country` field. `gie · storage · daily`
