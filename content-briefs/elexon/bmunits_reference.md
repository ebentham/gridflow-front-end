---
slug: bmunits_reference
vendor: elexon
vendor_label: Elexon BMRS
api_code: BMUNITS
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/bmunits_reference.md
  - gridflow/src/gridflow/schemas/elexon.py::ElexonBMUnit (lines 269-280)
  - gridflow/src/gridflow/silver/elexon/bmunits.py::BMUnitsTransformer (lines 19-116)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 266-271, NO_PARAMS style, no pagination)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/reference/bmunits/all (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vault Silver schema table"
    source_a_says: "bm_unit_id sourced from bmUnit or elexonBmUnit"
    source_b: "gridflow silver/elexon/bmunits.py L62-64"
    source_b_says: "Column mapping prefers elexonBmUnit then bmUnit (live API returns elexonBmUnit)"
    orchestrator_recommendation: "trust gridflow — live API returns elexonBmUnit; vault description is correct but order of preference is implementation-defined"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Every registered BM unit, the <span class="italic fg-accent">join key.</span>

**Lede:** GB BM-unit registry — the canonical lookup for unit metadata in every per-BMU dataset (`boal`, `pn`, `uou2t14d`).

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · BMUNITS](https://bmrs.elexon.co.uk/api-documentation/endpoint/reference/bmunits/all)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.bmunits_reference` |
| API PATH | `/reference/bmunits/all` |
| FREQUENCY | weekly |
| PUBLICATION LAG | 0 |
| VOLUME | 1 snapshot |
| PRIMARY KEY | `(bm_unit_id)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | weekly | Refresh cadence |
| 2 | ~3000 | Active BM units |
| 3 | 8 | Fuel categories |
| 4 | 9 | Schema columns |

# Sidebar siblings

- boal
- pn
- uou2t14d
- fuelhh
- agpt

# Sample chart

- **Type:** `barsH`
- **Title:** "BM units by fuel type · current snapshot"
- **Subtitle:** "Horizontal bars · count of registered units · 2026-05-08"
- **Seed:** 5
- **Toggles:** `count` (active) / `capacity (MW)`

# Schema

Defined in `gridflow/schemas/elexon.py` · `ElexonBMUnit` (lines 269-280) and `gridflow/silver/elexon/bmunits.py` · `BMUnitsTransformer.output_cols`. The silver table is **not partitioned** — single reference file. Point-in-time field: `ingested_at` (no native PIT field; snapshot semantics).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `bm_unit_id` | `str` | No | `elexonBmUnit` / `bmUnit` | Canonical BM Unit identifier (e.g. `T_DRAXX-1`). Preserve raw casing. | `schemas/elexon.py L272` |
| `bm_unit_name` | `Optional[str]` | Yes | `bmUnitName` / `name` | Friendly name (e.g. `Drax Power Station 1`). | `schemas/elexon.py L273` |
| `fuel_type` | `Optional[str]` | Yes | `fuelType` | Fuel category (CCGT, WIND, NUCLEAR, ...). Null for some unit types. | `schemas/elexon.py L274` |
| `registered_capacity_mw` | `Optional[float]` | Yes | `generationCapacity` / `registeredCapacity` | MW. Cast to `Float64`. Note `demandCapacity` is a separate API field, not folded in. | `schemas/elexon.py L275`; `silver/elexon/bmunits.py L86` |
| `company_name` | `Optional[str]` | Yes | `leadPartyName` / `companyName` | Lead party / operator. | `schemas/elexon.py L276` |
| `gsp_group_id` | `Optional[str]` | Yes | `gspGroupId` | GSP group code (e.g. `_K`, `_A`). | `schemas/elexon.py L277` |
| `national_grid_bm_unit` | `Optional[str]` | Yes | `nationalGridBmUnit` | ENTSO-E EIC / National Grid BMU ID (e.g. `ABERU-1`). | `schemas/elexon.py L278` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `schemas/elexon.py L279` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Snapshot ingestion time. | `schemas/elexon.py L280` |

**PARQUET PATH:** `data/silver/elexon/bmunits_reference/bmunits_reference.parquet` (single file, NOT partitioned)
**PARTITION BY:** _none — reference snapshot_
**DEDUP KEY:** `(bm_unit_id)`

# Sample data

| bm_unit_id | bm_unit_name | fuel_type | registered_capacity_mw | company_name | gsp_group_id | national_grid_bm_unit | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|
| E_ABERDARE | Aberdare Power Station | _null_ | 15.4 | UK Power Reserve Limited | _K | ABERU-1 | elexon | 2026-05-08T12:00:00Z |
| **T_ABRBO-1** | **ABRBO-1** | **WIND** | **99.0** | **Aberdeen Offshore Wind Farm** | **_null_** | **ABRBO-1** | **elexon** | **2026-05-08T12:00:00Z** |
| T_DRAXX-1 | Drax Power Station 1 | BIOMASS | 645.0 | Drax Power Limited | _D | DRAXX-1 | elexon | 2026-05-08T12:00:00Z |
| T_HEYM27 | Heysham 2 (Reactor 7) | NUCLEAR | 605.0 | EDF Energy Nuclear Generation Ltd | _N | HEYM27 | elexon | 2026-05-08T12:00:00Z |
| T_HOWAO-2 | Hornsea 2 Offshore Wind Farm | WIND | 1320.0 | Ørsted Hornsea Project Two Ltd | _null_ | HOWAO-2 | elexon | 2026-05-08T12:00:00Z |
| I_IFA1 | IFA Interconnector | INTFR | 2000.0 | NGV (IFA) Limited | _null_ | IFA1 | elexon | 2026-05-08T12:00:00Z |
| T_PEHE-1 | Pembroke 1 (CCGT) | CCGT | 540.0 | RWE Generation UK plc | _null_ | PEHE-1 | elexon | 2026-05-08T12:00:00Z |
| T_GRMO-1 | Greater Gabbard Offshore Wind Farm | WIND | 504.0 | Greater Gabbard Offshore Winds Ltd | _null_ | GRMO-1 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (`E_ABERDARE`) and 2 (`T_ABRBO-1`) verbatim from the vault Bronze Sample (vault/elexon/bmunits_reference.md, live 2026-05-08). Remaining rows synthesised — respect schema constraints (`registered_capacity_mw` as float, fuel codes from observed BMRS list) and represent the major BM-unit categories (biomass, nuclear, wind, interconnector, CCGT). The highlighted **T_ABRBO-1** row is the interesting case: a wind unit with `gspGroupId: null` (offshore units are not tied to a GSP group) and a non-trivial `national_grid_bm_unit` mapping.

# Dataset-specific section: BM-unit categories

BM-unit categorisation observable from the live snapshot. The `fuel_type` column is one of:

- `CCGT` — Combined Cycle Gas Turbine
- `WIND` — Wind (onshore and offshore both labelled `WIND` here; split via `agpt`)
- `NUCLEAR` — Nuclear
- `BIOMASS` — Biomass
- `NPSHYD` — Non-pumped-storage hydro
- `PS` — Pumped storage
- `COAL` — Coal (rare post-2024)
- `OCGT` — Open Cycle Gas Turbine
- `OIL` — Oil (emergency reserve)
- `INTFR` / `INTIRL` / `INTNED` / `INTEW` / `INTEM` — Interconnectors
- _null_ — Some unit types (e.g. supplier units, embedded BMUs) carry no fuel

`bm_unit_id` prefix conventions (read first letter):

- `T_` — Transmission-connected unit (`T_DRAXX-1`)
- `E_` — Embedded/distribution-connected unit (`E_ABERDARE`)
- `I_` — Interconnector unit (`I_IFA1`)
- `2__`, `S_`, etc. — Supplier and other BMU types

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/reference/bmunits/all`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/bmunits_reference/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.bmunits.BMUnitsTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/reference/bmunits/all?format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- BM-unit count by fuel type
SELECT COALESCE(fuel_type, '(null)') AS fuel,
       COUNT(*) AS units,
       SUM(registered_capacity_mw) AS total_capacity_mw
FROM read_parquet('data/silver/elexon/bmunits_reference/bmunits_reference.parquet')
GROUP BY 1
ORDER BY units DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

bmu = pl.read_parquet("data/silver/elexon/bmunits_reference/bmunits_reference.parquet")
# Join example: attach fuel_type + name to a BOAL extract
boal = pl.read_parquet("data/silver/elexon/boal/**/*.parquet")
enriched = boal.join(
    bmu.select(["bm_unit_id", "bm_unit_name", "fuel_type"]),
    on="bm_unit_id",
    how="left",
)
print(enriched.head())
```

# Caveats

## 01 Snapshot semantics — no history

Each refresh overwrites the single parquet at `bmunits_reference.parquet`; registration history is not preserved. For PIT queries, archive bronze. *(Source: `silver/elexon/bmunits.py L105-113`.)*

## 02 Response is a bare JSON array, not `{data: [...]}`

`/reference/bmunits/all` returns a bare array; transformer handles both via `data.get("data", []) if isinstance(data, dict) else data`. *(Source: `silver/elexon/bmunits.py L47`.)*

## 03 No pagination — single 3000-row snapshot per call

Connector sets `supports_pagination=False`; the entire register returns in one call. Fetch weekly, not per-job. *(Source: `connectors/elexon/endpoints.py L268-271`.)*

## 04 `bm_unit_id` casing must be preserved

Prefixed identifiers (`T_DRAXX-1`, `E_ABERDARE`, `2__DUKPR008`) are cast to `Utf8` without normalisation. Lower-casing breaks joins. *(Source: `silver/elexon/bmunits.py L83`.)*

## 05 `registered_capacity_mw` source preference

Maps `registeredCapacity` and `generationCapacity` to the same column; the parallel `demandCapacity` field is dropped. Demand-side capacity needs bronze. *(Source: `silver/elexon/bmunits.py L68-69`.)*

# Related datasets

- **boal** — Bid-offer acceptance. `hourly`. Joins on `bm_unit_id` to attach unit-level dispatch instructions to the reference register. `elexon · prices & balancing · hourly`
- **pn** — Physical notifications. `hourly`. Joins on `bm_unit_id` for BMU-level pre-gate-closure intentions. `elexon · prices & balancing · hourly`
- **uou2t14d** — 2-14 day availability by BM unit. `daily`. Joins on `bm_unit_id` for forward availability declarations. `elexon · demand & forecasts · daily`
- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. Not a unit-level join target, but lookup the `fuel_type` column to derive top-N BMU contribution to each fuel category. `elexon · generation · 30 min`
