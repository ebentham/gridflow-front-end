---
slug: storage_reports
vendor: gie
vendor_label: GIE AGSI+ (Gas Storage)
api_code: AGSI
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "GIE API key (header `x-key`, lowercase) required — free registration at agsi.gie.eu/account/registration"
sources_consulted:
  - vault/gie/storage_reports.md
  - gridflow/src/gridflow/schemas/gie.py::GasStorage (lines 12-47, shared with storage)
  - gridflow/src/gridflow/silver/gie/agsi.py::StorageReportsTransformer (lines 274-277, subclass of GasStorageTransformer; registered at L625)
  - gridflow/src/gridflow/connectors/gie/endpoints.py::ENDPOINTS["storage_reports"] (lines 125-138, full 4-scope query plan)
  - https://agsi.gie.eu/api (vendor docs — interactive HTML, no machine-readable static page; vault canonical fallback applied)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** AGSI storage at every <span class="italic fg-accent">level of granularity.</span>

**Lede:** Gas storage at aggregate, country, company, and facility grain — the catalog-aligned full-scope feed for granular EU gas balance, operator attribution, and stress-test modelling.

**Verified line:** Verified against vendor docs: 2026-05-08 · [GIE AGSI+ · /api](https://agsi.gie.eu/api)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.gie_agsi.storage_reports` |
| API PATH | `/api?type=EU` · `?country={ISO2}` · `?company={EIC}` · `?facility={EIC}` |
| FREQUENCY | daily (gas day) |
| PUBLICATION LAG | ~16:00 CET refresh |
| VOLUME | ~150-200 rows / day (all scopes) |
| PRIMARY KEY | `(gas_day, entity_level, entity_code, entity_url)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Snapshot cadence |
| 2 | 4 | Entity-level scopes |
| 3 | 71 | Companies (live 2026-05-08) |
| 4 | 26 | Schema columns |

# Sidebar siblings

- storage
- unavailability
- about_listing
- about_summary
- lng

# Sample chart

- **Type:** `stackedArea`
- **Title:** "DE storage · facility-level stock · last 90 days"
- **Subtitle:** "Stacked area · GWh · gas-day · 2026-02-06 → 2026-05-06"
- **Seed:** 21
- **Toggles:** `30d` / `90d` (active) / `1y`

# Schema

Defined in `gridflow/schemas/gie.py` · `GasStorage` (lines 12-47, shared with `storage`) and `gridflow/silver/gie/agsi.py` · `StorageReportsTransformer` (line 274 — `GasStorageTransformer` subclass). Partitioned by `gas_day` (year + month). The dataset extends `storage` by exercising all four query scopes; `entity_level` is the discriminator.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `gas_day` | `date` | No | `gasDayStart` | Gas day, NOT calendar day — starts at 06:00 UTC. | `schemas/gie.py L15`; `silver/gie/agsi.py L184` |
| `country_code` | `str` | No (default `""`) | request `country` / `code` | ISO-2; `EU` for aggregate rows. | `schemas/gie.py L16`; `silver/gie/agsi.py L175-177` |
| `country_name` | `str` | No (default `""`) | `name` | Human-readable country. | `schemas/gie.py L17` |
| `gas_day_end` | `Optional[datetime]` | Yes | `gasDayEnd` | End of gas-day window. | `schemas/gie.py L18` |
| `updated_at` | `Optional[datetime]` | Yes | `updatedAt` | Vendor revision timestamp. | `schemas/gie.py L19` |
| `entity_level` | `str` | No (default `"country"`) | _derived from request params_ | One of `aggregate_type` · `country` · `company` · `facility`. Inferred via `_storage_entity_level` from `__request_*` keys. | `schemas/gie.py L20`; `silver/gie/agsi.py L160-165, L496-512` |
| `entity_code` | `str` | No (default `""`) | `code` / request param | EIC (company/facility), ISO-2 (country), `"EU"` (aggregate). | `schemas/gie.py L21`; `silver/gie/agsi.py L166-173` |
| `entity_name` | `str` | No (default `""`) | `name` | | `schemas/gie.py L22` |
| `entity_url` | `Optional[str]` | Yes | `url` | Vendor URL slug. | `schemas/gie.py L23` |
| `gas_in_storage_gwh` | `Optional[float]` | Yes | `gasInStorage` | **GWh**. `"-"` → null. | `schemas/gie.py L24`; `silver/gie/agsi.py L193` |
| `consumption_gwh` | `Optional[float]` | Yes | `consumption` | GWh. | `schemas/gie.py L25` |
| `consumption_full_pct` | `Optional[float]` | Yes | `consumptionFull` | %. | `schemas/gie.py L26` |
| `withdrawal_gwh` | `Optional[float]` | Yes | `withdrawal` | GWh. | `schemas/gie.py L27` |
| `injection_gwh` | `Optional[float]` | Yes | `injection` | GWh. | `schemas/gie.py L28` |
| `net_withdrawal_gwh` | `Optional[float]` | Yes | `netWithdrawal` | GWh, signed. | `schemas/gie.py L29` |
| `working_gas_volume_gwh` | `Optional[float]` | Yes | `workingGasVolume` | GWh. | `schemas/gie.py L30` |
| `injection_capacity_gwh_per_day` | `Optional[float]` | Yes | `injectionCapacity` | GWh/day. | `schemas/gie.py L31` |
| `withdrawal_capacity_gwh_per_day` | `Optional[float]` | Yes | `withdrawalCapacity` | GWh/day. | `schemas/gie.py L32` |
| `contracted_capacity_gwh_per_day` | `Optional[float]` | Yes | `contractedCapacity` | GWh/day. | `schemas/gie.py L33` |
| `available_capacity_gwh_per_day` | `Optional[float]` | Yes | `availableCapacity` | GWh/day. | `schemas/gie.py L34` |
| `covered_capacity_gwh_per_day` | `Optional[float]` | Yes | `coveredCapacity` | GWh/day. | `schemas/gie.py L35` |
| `storage_pct_full` | `Optional[float]` | Yes | `full` | 0-100, clamped by validator. | `schemas/gie.py L36, L42-47` |
| `trend` | `Optional[float]` | Yes | `trend` | Signed daily delta of `storage_pct_full`. | `schemas/gie.py L37` |
| `status` | `Optional[str]` | Yes | `status` | `E` · `C` · `N`. | `schemas/gie.py L38` |
| `info` | `Optional[str]` | Yes | `info` | JSON-encoded freeform object. | `schemas/gie.py L39` |
| `data_provider` | `str` | No (default `"gie_agsi"`) | _derived_ | Always `"gie_agsi"`. | `schemas/gie.py L40` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver write timestamp. | `silver/gie/agsi.py L210` |

**PARQUET PATH:** `data/silver/gie_agsi/storage_reports/year=YYYY/month=MM/`
**PARTITION BY:** `gas_day (year + month)`
**DEDUP KEY:** `(gas_day, entity_level, entity_code, entity_url)` — keep last (`silver/gie/agsi.py L216-224`)

# Sample data

| gas_day | entity_level | entity_code | entity_name | country_code | gas_in_storage_gwh | storage_pct_full | trend | status |
|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | aggregate_type | EU | European Union | EU | 642.30 | 31.45 | -0.42 | E |
| 2026-05-06 | country | DE | Germany | DE | 65.9608 | 26.62 | -0.57 | E |
| 2026-05-06 | country | FR | France | FR | 84.20 | 33.45 | -0.40 | E |
| 2026-05-06 | company | 25X-GSALLC-----E | GSA LLC | AT | 2.18 | 28.10 | -0.31 | E |
| **2026-05-06** | **facility** | **25W-SPHAID-GAZ-M** | **UGS Haidach (GSA)** | **AT** | **0.92** | **23.40** | **-0.45** | **E** |
| 2026-05-06 | company | 21X0000000011756 | EWE Gasspeicher | DE | 3.45 | 19.20 | -0.51 | E |
| 2026-05-06 | facility | 37W000000000002O | EWE H-Gas Zone | DE | 1.84 | 17.80 | -0.49 | E |
| 2026-05-06 | country | GB | United Kingdom (Pre-Brexit) | GB | _null_ | _null_ | _null_ | N |

**Sources:** DE country row verbatim from vault Silver sample (live 2026-05-08); remaining rows synthesised respecting schema constraints and the entity-level taxonomy. The highlighted **facility** row demonstrates the catalog-aligned shape (`entity_level: "facility"`, `entity_code` is the facility EIC, `entity_name` carries the human-readable storage name). Aggregate (`EU`) rows co-exist with country / company / facility rows in the same dataset — do not double-count when summing (see Caveats #06).

# Dataset-specific section: AGSI query scopes

The 4 query scopes exercised by `StorageReportsTransformer` — discriminated via `entity_level`:

- **`aggregate_type`** — `?type=EU` (default) returns one row per gas day per aggregate region. Used for top-line EU storage trajectory.
- **`country`** — `?country={ISO2}` returns one row per gas day per AGSI country (9 countries — `AT BE DE ES FR GB IT NL PL`).
- **`company`** — `?country={ISO2}&company={EIC}` returns one row per gas day per company (71 companies live 2026-05-08).
- **`facility`** — `?country={ISO2}&company={EIC}&facility={EIC}` returns one row per gas day per storage facility.

Company and facility EICs are sourced from `about_listing` / `about_summary`. Query planning is implemented in `build_storage_query_plan` (`connectors/gie/endpoints.py L294-372`).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `agsi.gie.eu/api?{scope-params}&date={YYYY-MM-DD}` (single day) or `&from=…&to=…` (range)
- AUTH: header `x-key` (LOWERCASE — `X-Key` returns 401), key from env `GIE_API_KEY`. Free registration at [agsi.gie.eu/account/registration](https://agsi.gie.eu/account/registration).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/gie_agsi/storage_reports/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.gie.agsi.StorageReportsTransformer` (subclass of `GasStorageTransformer`, registered at `silver/gie/agsi.py L625`)

**Tab 1 — Example URL**
```
https://agsi.gie.eu/api?country=DE&company=21X0000000011756&from=2026-05-01&to=2026-05-07&size=300

Header: x-key: $GIE_API_KEY
```

**Tab 2 — DuckDB · SQL**
```sql
-- Facility-level stock for German EWE Gasspeicher, last 30 days
SELECT gas_day,
       entity_name AS facility,
       gas_in_storage_gwh,
       working_gas_volume_gwh,
       storage_pct_full
FROM read_parquet('data/silver/gie_agsi/storage_reports/**/*.parquet')
WHERE entity_level = 'facility'
  AND country_code = 'DE'
  AND status IN ('E', 'C')
  AND gas_day >= current_date - INTERVAL 30 DAY
ORDER BY entity_name, gas_day;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/gie_agsi/storage_reports/**/*.parquet")
# Country-vs-facility consistency check: country total should ~match facility sum
country = df.filter(pl.col("entity_level") == "country").select(
    "gas_day", "country_code", pl.col("gas_in_storage_gwh").alias("country_gwh")
)
facility = (
    df.filter(pl.col("entity_level") == "facility")
      .group_by(["gas_day", "country_code"])
      .agg(pl.col("gas_in_storage_gwh").sum().alias("facility_sum_gwh"))
)
check = country.join(facility, on=["gas_day", "country_code"], how="inner")
print(check.tail())
```

# Caveats

## 01 `entity_level` discriminator must be filtered

Aggregate, country, company, and facility rows co-exist in the same parquet. Summing without filtering double-counts (aggregate row + country rows for same gas day). Always filter `WHERE entity_level = 'country'` (or your chosen scope). *(Source: vault Known Issues; `silver/gie/agsi.py L160-165, L496-512`.)*

## 02 Unit is GWh — NOT MWh

Stocks in `gas_in_storage_gwh`; capacities in `*_gwh_per_day`. Vendor docs historically called this `gas_in_storage_mwh` but live key is `gasInStorage` and units are GWh. *(Source: vault Known Issues; `schemas/gie.py L24`.)*

## 03 GB post-Brexit returns `"-"` placeholders

`country=GB` returns `"United Kingdom (Pre-Brexit)"` with `status: "N"`; only pre-Oct-2019 historical rows carry numeric data. Filter `WHERE status IN ('E', 'C')`. *(Source: vault Known Issues.)*

## 04 Gas day starts at 06:00 UTC

`gas_day` is a `date`. Gas day for `2026-05-06` runs 06:00 UTC → 06:00 UTC next day. *(Source: vault Known Issues + `20-domain/concepts/gas-day.md`.)*

## 05 `x-key` header MUST be lowercase

Vendor enforces lowercase header naming. `X-Key` (HTTP-library default) returns HTTP 401. *(Source: vault Known Issues #1.)*

## 06 `trend` sign convention undocumented but consistent

Observed `trend` values match the daily change of `storage_pct_full` (negative for net withdrawal). Sign convention not formally documented by vendor. *(Source: vault Implementation Delta.)*

# Related datasets

- **`storage`** — Country-scope-only variant of this dataset. `daily` — same `/api` endpoint but only exercises `QueryScope.COUNTRY`. Use when you want the country roll-up without aggregate / company / facility noise. `gie · storage · daily`
- **`about_listing`** — Flat company + facility EIC inventory. `snapshot` — supplies the `company` and `facility` EICs needed to drive `storage_reports` company / facility scopes. `gie · storage · snapshot`
- **`unavailability`** — Per-facility outage and maintenance records. `as published` — join on `entity_code` (facility EIC) to derive effective-capacity net of outages. `gie · storage · as published`
- **`aggregated_physical_flows`** (ENTSOG) — Cross-border pipeline flows. `daily` — pair facility-level injection / withdrawal with ENTSOG point-level flows to validate gas-network attribution. `entsog · transmission · daily`
