---
slug: storage
vendor: gie
vendor_label: GIE AGSI+ (Gas Storage)
api_code: AGSI
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "GIE API key (header `x-key`, lowercase) required for all endpoints — free registration at agsi.gie.eu/account/registration"
sources_consulted:
  - vault/gie/storage.md
  - gridflow/src/gridflow/schemas/gie.py::GasStorage (lines 12-47)
  - gridflow/src/gridflow/silver/gie/agsi.py::GasStorageTransformer (lines 115-271, registered at L624)
  - gridflow/src/gridflow/connectors/gie/endpoints.py::ENDPOINTS["storage_reports"] (lines 125-138, shared registry with storage)
  - https://agsi.gie.eu/api (vendor docs — interactive HTML, no machine-readable static page; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault Implementation Delta — legacy ALSI fetch path"
    source_a_says: "`connectors/gie/client.py::_fetch_country` (used by `gie_alsi`) still uses `till=` instead of `to=` for range parameter"
    source_b: "vault storage.md — AGSI code path uses `from`/`to` correctly"
    orchestrator_recommendation: "non-blocking for storage — legacy `till=` path is unused for AGSI. Flagged for ALSI brief (`lng.md`)."
  - source_a: "vault dataset_key `storage`"
    source_a_says: "vault frontmatter declares `source: gie_agsi` and `dataset_key: storage`"
    source_b: "Phase 8D landing brief (`_landing.md`) treats GIE as one unified vendor with two internal groups (AGSI + ALSI)"
    orchestrator_recommendation: "documented vendor-namespace split — gridflow silver registers as `(gie_agsi, storage)` but the site-level vendor hub is `gie`. Treat as design intent."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** European gas storage, <span class="italic fg-accent">country by country.</span>

**Lede:** Country-scoped daily gas-storage time-series — the canonical winter-tightness indicator, fuel-switching signal, and storage-spread trade input for European gas modelling.

**Verified line:** Verified against vendor docs: 2026-05-08 · [GIE AGSI+ · /api](https://agsi.gie.eu/api)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.gie_agsi.storage` |
| API PATH | `/api?country={ISO2}&date={YYYY-MM-DD}` |
| FREQUENCY | daily (gas day) |
| PUBLICATION LAG | ~16:00 CET refresh |
| VOLUME | ~9 rows / day |
| PRIMARY KEY | `(gas_day, entity_level, entity_code, entity_url)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Snapshot cadence |
| 2 | ~16:00 CET | Publication refresh |
| 3 | 9 | AGSI countries |
| 4 | 26 | Schema columns |

# Sidebar siblings

- storage_reports
- unavailability
- about_listing
- about_summary
- lng

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE storage · pct_full · last 12 months"
- **Subtitle:** "Sparkline · % full · daily · gas-day · 2025-06 → 2026-05"
- **Seed:** 17
- **Toggles:** `1y` (active) / `5y`

# Schema

Defined in `gridflow/schemas/gie.py` · `GasStorage` (lines 12-47) and `gridflow/silver/gie/agsi.py` · `GasStorageTransformer` (line 115). Partitioned by `gas_day` (year + month). Point-in-time field: `updated_at` (vendor `updatedAt`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `gas_day` | `date` | No | `gasDayStart` | Gas day, NOT calendar day — starts at 06:00 UTC. | `schemas/gie.py L15`; `silver/gie/agsi.py L184` |
| `country_code` | `str` | No (default `""`) | request `country` / `code` | ISO-2 (e.g. `DE`, `FR`, `GB`). | `schemas/gie.py L16`; `silver/gie/agsi.py L175-177` |
| `country_name` | `str` | No (default `""`) | `name` | Human-readable country. | `schemas/gie.py L17`; `silver/gie/agsi.py L179-181` |
| `gas_day_end` | `Optional[datetime]` | Yes | `gasDayEnd` | End of the same gas-day window. | `schemas/gie.py L18`; `silver/gie/agsi.py L185` |
| `updated_at` | `Optional[datetime]` | Yes | `updatedAt` | Vendor revision timestamp; use for as-of filtering. | `schemas/gie.py L19`; `silver/gie/agsi.py L186` |
| `entity_level` | `str` | No (default `"country"`) | _derived_ | Always `"country"` for this dataset. | `schemas/gie.py L20`; `silver/gie/agsi.py L160-165` |
| `entity_code` | `str` | No (default `""`) | `code` / request param | ISO-2 country code. | `schemas/gie.py L21`; `silver/gie/agsi.py L166-173` |
| `entity_name` | `str` | No (default `""`) | `name` | Human-readable country. | `schemas/gie.py L22` |
| `entity_url` | `Optional[str]` | Yes | `url` | Vendor URL slug. | `schemas/gie.py L23` |
| `gas_in_storage_gwh` | `Optional[float]` | Yes | `gasInStorage` | **GWh** (NOT MWh). `"-"` → null via `_safe_float`. | `schemas/gie.py L24`; `silver/gie/agsi.py L193` |
| `consumption_gwh` | `Optional[float]` | Yes | `consumption` | Daily consumption (GWh). | `schemas/gie.py L25`; `silver/gie/agsi.py L194` |
| `consumption_full_pct` | `Optional[float]` | Yes | `consumptionFull` | Consumption as % of working-gas volume. | `schemas/gie.py L26`; `silver/gie/agsi.py L195` |
| `withdrawal_gwh` | `Optional[float]` | Yes | `withdrawal` | Daily withdrawal (GWh). | `schemas/gie.py L27`; `silver/gie/agsi.py L197` |
| `injection_gwh` | `Optional[float]` | Yes | `injection` | Daily injection (GWh). | `schemas/gie.py L28`; `silver/gie/agsi.py L196` |
| `net_withdrawal_gwh` | `Optional[float]` | Yes | `netWithdrawal` | Signed daily delta; positive = withdrawing. | `schemas/gie.py L29`; `silver/gie/agsi.py L198` |
| `working_gas_volume_gwh` | `Optional[float]` | Yes | `workingGasVolume` | Total usable capacity (GWh). | `schemas/gie.py L30`; `silver/gie/agsi.py L199` |
| `injection_capacity_gwh_per_day` | `Optional[float]` | Yes | `injectionCapacity` | GWh/day. | `schemas/gie.py L31` |
| `withdrawal_capacity_gwh_per_day` | `Optional[float]` | Yes | `withdrawalCapacity` | GWh/day. | `schemas/gie.py L32` |
| `contracted_capacity_gwh_per_day` | `Optional[float]` | Yes | `contractedCapacity` | Capacity contracted to shippers. | `schemas/gie.py L33` |
| `available_capacity_gwh_per_day` | `Optional[float]` | Yes | `availableCapacity` | Capacity still available to contract. | `schemas/gie.py L34` |
| `covered_capacity_gwh_per_day` | `Optional[float]` | Yes | `coveredCapacity` | Capacity covered by storage obligations. | `schemas/gie.py L35` |
| `storage_pct_full` | `Optional[float]` | Yes | `full` | 0-100, clamped by validator. Headline indicator. | `schemas/gie.py L36, L42-47`; `silver/gie/agsi.py L205` |
| `trend` | `Optional[float]` | Yes | `trend` | Signed daily delta of `storage_pct_full`. | `schemas/gie.py L37`; `silver/gie/agsi.py L206` |
| `status` | `Optional[str]` | Yes | `status` | `E` estimate · `C` confirmed · `N` no value. | `schemas/gie.py L38`; `silver/gie/agsi.py L207` |
| `info` | `Optional[str]` | Yes | `info` | JSON-encoded freeform object. | `schemas/gie.py L39`; `silver/gie/agsi.py L208` |
| `data_provider` | `str` | No (default `"gie_agsi"`) | _derived_ | Always `"gie_agsi"`. | `schemas/gie.py L40`; `silver/gie/agsi.py L209` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver write timestamp. | `silver/gie/agsi.py L210` |

**PARQUET PATH:** `data/silver/gie_agsi/storage/year=YYYY/month=MM/`
**PARTITION BY:** `gas_day (year + month)`
**DEDUP KEY:** `(gas_day, entity_level, entity_code, entity_url)` — keep last (`silver/gie/agsi.py L216-224`)

# Sample data

| gas_day | entity_code | gas_in_storage_gwh | injection_gwh | withdrawal_gwh | net_withdrawal_gwh | storage_pct_full | trend | status |
|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | DE | 65.9608 | 182.43 | 60.3 | -122.1 | 26.62 | -0.57 | E |
| 2026-05-06 | FR | 84.20 | 95.10 | 12.40 | -82.70 | 33.45 | -0.40 | E |
| **2026-05-06** | **GB** | _null_ | _null_ | _null_ | _null_ | _null_ | _null_ | **N** |
| 2026-05-06 | NL | 41.30 | 78.20 | 8.10 | -70.10 | 29.85 | -0.31 | C |
| 2026-05-06 | IT | 92.40 | 142.60 | 15.30 | -127.30 | 38.20 | -0.49 | E |
| 2026-05-06 | AT | 38.10 | 47.20 | 4.60 | -42.60 | 35.10 | -0.42 | E |
| 2026-05-06 | BE | 4.85 | 6.20 | 0.40 | -5.80 | 28.30 | -0.31 | E |
| 2026-05-06 | ES | 18.40 | 21.10 | 3.50 | -17.60 | 39.60 | -0.34 | E |

**Sources:** DE row verbatim from vault Silver sample (live 2026-05-08); remaining 7 country rows synthesised respecting the schema's GWh-and-% ranges and the early-May shoulder-season injection pattern. The highlighted **GB** row demonstrates the post-Brexit unusability: `"-"` placeholders converted to null by `_safe_float`, `status: "N"`. Always filter `WHERE status IN ('E', 'C')` for GB-inclusive aggregates.

# Dataset-specific section: AGSI country footprint

The 9 countries covered by AGSI as of 2026 (`AGSI_COUNTRIES`, `connectors/gie/endpoints.py L14`).

- `AT` — Austria
- `BE` — Belgium
- `DE` — Germany (largest single-country storage; dominant EU winter buffer)
- `ES` — Spain
- `FR` — France
- `GB` — United Kingdom (**unusable post-Brexit** — see Caveats #02)
- `IT` — Italy
- `NL` — Netherlands (includes Groningen historical, now ~0 since closure)
- `PL` — Poland

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `agsi.gie.eu/api?country={ISO2}&date={YYYY-MM-DD}` (single day) or `&from=…&to=…` (range)
- AUTH: header `x-key` (LOWERCASE — `X-Key` returns 401), key from env `GIE_API_KEY`. Free registration at [agsi.gie.eu/account/registration](https://agsi.gie.eu/account/registration).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/gie_agsi/storage/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.gie.agsi.GasStorageTransformer` (registered at `silver/gie/agsi.py L624`)

**Tab 1 — Example URL**
```
https://agsi.gie.eu/api?country=DE&from=2026-05-01&to=2026-05-07&size=300

Header: x-key: $GIE_API_KEY
```

**Tab 2 — DuckDB · SQL**
```sql
-- European storage trajectory: percent-full per country, last 90 days
SELECT entity_code,
       gas_day,
       storage_pct_full,
       trend
FROM read_parquet('data/silver/gie_agsi/storage/**/*.parquet')
WHERE status IN ('E', 'C')                      -- exclude GB no-value rows
  AND gas_day >= current_date - INTERVAL 90 DAY
ORDER BY entity_code, gas_day;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/gie_agsi/storage/**/*.parquet")
# EU-wide rolling stock — sum country gas_in_storage and convert to TWh
eu = (
    df.filter(pl.col("status").is_in(["E", "C"]))
      .group_by("gas_day")
      .agg((pl.col("gas_in_storage_gwh").sum() / 1000).alias("eu_total_twh"))
      .sort("gas_day")
)
print(eu.tail(30))
```

# Caveats

## 01 Unit is GWh — NOT MWh

GIE reports stocks in `gas_in_storage_gwh` and capacities in `*_gwh_per_day`. Divide by 1000 for TWh; multiply by 1000 to align with MWh power-market datasets. *(Source: vault Known Issues; `schemas/gie.py L24`.)*

## 02 GB is in the footprint but unusable post-Brexit

`country=GB` returns `"United Kingdom (Pre-Brexit)"` with `"-"` placeholders for all numeric fields and `status: "N"`. `_safe_float` converts `"-"` → null. Filter `WHERE status IN ('E', 'C')` for GB-inclusive aggregates. *(Source: vault Known Issues.)*

## 03 Gas day starts at 06:00 UTC, NOT midnight

`gas_day` is a `date`. Gas day for `2026-05-06` runs 2026-05-06 06:00 UTC → 2026-05-07 06:00 UTC. Apply the +06:00 offset when joining intra-day calendar-day datasets. *(Source: vault Known Issues + `20-domain/concepts/gas-day.md`.)*

## 04 `x-key` header MUST be lowercase

Vendor enforces lowercase. Capitalised `X-Key` (default in many HTTP libs) returns HTTP 401. *(Source: vault Known Issues #1.)*

## 05 `last_page` is pagination source of truth

`last_page` is the global page count; `total` is the per-page row count. Iterating on `total` mis-paginates. *(Source: vault Known Issues #2.)*

## 06 `gas_day_start_validation` is enforced by the connector

A `date=YYYY-MM-DD` query that returns a different gas day fails loudly — guards against silent vendor caching errors. *(Source: vault Known Issues.)*

# Related datasets

- **`storage_reports`** — Facility-level (and aggregate/company) version of this dataset. `daily` — same `/api` endpoint, finer `entity_level` granularity (aggregate / country / company / facility). Use when country roll-up hides facility dynamics. `gie · storage · daily`
- **`unavailability`** — Planned outages of storage facilities. `as published` — flag periods where storage capacity is reduced; pair with capacity columns to derive effective net-of-outages capacity. `gie · storage · as published`
- **`aggregated_physical_flows`** (ENTSOG) — Daily cross-border gas flows. `daily` — pair AGSI net withdrawal with ENTSOG pipeline-network attribution to validate gas balance. `entsog · transmission · daily`
- **`lng`** (GIE ALSI) — Daily LNG terminal inventory and send-out. `daily` — combine LNG inflow with AGSI storage trajectory for the full supply-buffer picture. `gie · lng · daily`
