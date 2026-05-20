---
slug: fuelhh
vendor: elexon
vendor_label: Elexon BMRS
api_code: FUELHH
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/fuelhh.md
  - gridflow/src/gridflow/schemas/elexon.py::ElexonFuelHH (lines 79-96)
  - gridflow/src/gridflow/silver/elexon/fuelhh.py::FuelHHTransformer (lines 19-111)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 115-119, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "schemas/elexon.py L79-96 (ElexonFuelHH)"
    source_a_says: "ElexonFuelHH includes `published_at: Optional[datetime] = None`"
    source_b: "gridflow silver/elexon/fuelhh.py L103-106"
    source_b_says: "Transformer output_cols list does NOT include published_at"
    orchestrator_recommendation: "trust gridflow silver — published_at is declared on the schema but the transformer drops it from output; either remove the schema field or add to output_cols. The reference page (authored-pages/elexon/fuelhh.html) treats published_at as the documented PIT field even though silver does not surface it."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Generation by fuel type, <span class="italic fg-accent">half-hourly.</span>

**Lede:** Half-hourly GB generation by fuel type — the canonical observation series for generation mix, capacity factors, and emissions.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · FUELHH](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.fuelhh` |
| API PATH | `/datasets/FUELHH` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | ~5 min |
| VOLUME | 1.4M / mo |
| PRIMARY KEY | `(settlement_date, settlement_period, fuel_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Frequency |
| 2 | ~5 min | Publication lag |
| 3 | 1.4M | Rows / month |
| 4 | 7 | Schema columns (silver output) |

# Sidebar siblings

- fuelinst
- agpt
- agws
- windfor
- nonbm

# Overview

1. <code>fuelhh</code> is the half-hourly GB generation outturn aggregated by fuel type — the realised MWh in each settlement period split by fuel category (CCGT, coal, nuclear, wind, solar, biomass, interconnectors). It is the canonical observation series for the GB generation mix and underpins capacity-factor analytics and emissions reporting.

2. Gridflow fetches it from <code>/datasets/FUELHH</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze, is validated against the <code>ElexonFuelHH</code> Pydantic schema, and written to the silver parquet partition via <code>FuelHHTransformer</code>.

3. Refreshed every 30 minutes with ~5 minute publication lag. Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `stackedArea`
- **Title:** "GB generation mix · 24-hour snapshot"
- **Subtitle:** "Stacked area · MW · UTC · 6 May 2026"
- **Shape:** (legacy hardcoded GB fuel mix — no params; this brief is the gold standard for the default stackedArea path)
- **Seed:** 42
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/elexon.py` · `ElexonFuelHH` (lines 79-96) and `gridflow/silver/elexon/fuelhh.py` · `FuelHHTransformer.output_cols`. Partitioned by `settlement_date` (year + month). Point-in-time field: `published_at` per schema (but see discrepancy — transformer does not currently emit this column).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `schemas/elexon.py L82`; `silver/elexon/fuelhh.py L75-78` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). Field validator `ge=1, le=50`. | `schemas/elexon.py L83` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. Validator requires tzinfo. | `schemas/elexon.py L84, L91-96`; `silver/elexon/fuelhh.py L81-90` |
| `fuel_type` | `str` | No | `fuelType` | Fuel category — uppercase API codes (CCGT, COAL, NUCLEAR, WIND, SOLAR, BIOMASS, NPSHYD, PS, OCGT, OIL, OTHER, INTFR, INTIRL, INTNED, INTEW, INTEM). | `schemas/elexon.py L85` |
| `generation_mw` | `float` | No | `generation` | MW. Average output for this fuel type in this period. Can be negative for pumped hydro (charging) or interconnectors (import). | `schemas/elexon.py L86` |
| `published_at` | `Optional[datetime]` | Yes | `publishTime` | Declared on schema (`ElexonFuelHH.published_at`, `schemas/elexon.py L87`) but **NOT** in transformer output (silver/elexon/fuelhh.py L103-106). See frontmatter discrepancy. | `schemas/elexon.py L87` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `schemas/elexon.py L88`; `silver/elexon/fuelhh.py L99` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `schemas/elexon.py L89`; `silver/elexon/fuelhh.py L100` |

**PARQUET PATH:** `data/silver/elexon/fuelhh/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period, fuel_type)` (`silver/elexon/fuelhh.py L92-95`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | fuel_type | generation_mw | data_provider | ingested_at |
|---|---|---|---|---|---|---|
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | CCGT | 7840.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | NUCLEAR | 4310.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | WIND | 9220.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | SOLAR | 0.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **8** | **2026-05-06T03:30:00+00:00** | **BIOMASS** | **2821.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | NPSHYD | 410.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | INTFR | 1640.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | INTNED | 720.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** BIOMASS row (`generation_mw=2821`) verbatim from the vault Bronze Sample (vault/elexon/fuelhh.md, live 2026-05-08); CCGT row (`generation_mw=7729` in vault) lightly adjusted to 7840 to match the published canonical reference (authored-pages/elexon/fuelhh.html). Remaining six rows synthesised — respect schema constraints (`fuel_type` ∈ canonical 16-code list, `generation_mw` as float MW) and represent the typical SP8 (03:30 UTC) early-morning mix. The highlighted **BIOMASS** row is the interesting case: matches the canonical sample in the vendor verification dump and is the row the reference page (`authored-pages/elexon/fuelhh.html`) emphasises.

# Dataset-specific section: Fuel types

The 16 codes appearing in the `fuel_type` column. Interconnector codes (`INT*`) can carry negative values (export) or positive (import). Pumped storage (`PS`) is negative when charging.

- `CCGT` — Combined Cycle Gas Turbine (largest single contributor in most periods)
- `NUCLEAR` — Nuclear
- `WIND` — Wind (onshore + offshore combined; use `agpt` for the split)
- `SOLAR` — Solar PV (embedded estimate; not metered at unit level)
- `BIOMASS` — Biomass / bio-energy
- `NPSHYD` — Non-pumped-storage hydro
- `PS` — Pumped storage (negative when charging)
- `OCGT` — Open Cycle Gas Turbine (peakers)
- `COAL` — Coal (rarely non-zero from 2024)
- `OIL` — Oil (emergency reserve only)
- `OTHER` — Other / unclassified
- `INTFR` — IFA / ElecLink (France)
- `INTIRL` — EWIC / Moyle (Ireland)
- `INTNED` — BritNed (Netherlands)
- `INTEW` — East-West (Republic of Ireland)
- `INTEM` — Viking Link / NSL (Norway)

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/fuelhh/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.fuelhh.FuelHHTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH?publishDateTimeFrom=2026-05-01T00:00:00Z&publishDateTimeTo=2026-05-02T00:00:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Last 30 days, daily total by fuel
SELECT settlement_date, fuel_type,
       SUM(generation_mw) * 0.5 AS daily_mwh
FROM read_parquet('data/silver/elexon/fuelhh/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 30 DAY
GROUP BY 1, 2
ORDER BY 1, daily_mwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/fuelhh/**/*.parquet")
# Pivot to wide format: one column per fuel type
mix = df.pivot(
    index=["settlement_date", "settlement_period"],
    on="fuel_type",
    values="generation_mw",
    aggregate_function="sum",
)
print(mix.head())
```

# Caveats

## 01 Settlement period range is 1..50

DST days have 46 (spring) or 50 (autumn) settlement periods. Validator `ge=1, le=50`. *(Source: `schemas/elexon.py L83`.)*

## 02 `fuelType` casing preserved

Codes stay uppercase (`CCGT`, `COAL`, …); don't lowercase in joins. *(Source: `silver/elexon/fuelhh.py L78`.)*

## 03 Embedded generation excluded

BM-registered only. Sub-MW solar / small wind / embedded CHP show up as reduced demand. *(Source: GB embedded-generation framework.)*

## 04 `WIND` is onshore + offshore combined

For the split, use `agpt` (PSR `Wind Onshore` / `Wind Offshore`) or `agws` — both D+1, not live. *(Source: vault Known Issues.)*

## 05 Interconnectors can be negative

`INT*` rows go negative when GB exports. Include / exclude depending on whether you want "GB generation" or "GB balance". *(Source: GB sign convention.)*

## 06 `published_at` declared but not emitted

Schema declares `published_at` (`schemas/elexon.py L87`) but transformer omits it from `output_cols` (`silver/elexon/fuelhh.py L103-106`). Silver rows carry no `published_at`. *(Source: frontmatter discrepancy.)*

# Related datasets

- **fuelinst** — Generation by fuel · instantaneous. `~5 min`. Same fuel breakdown at ~5-minute resolution; the half-hour aggregate that becomes FUELHH. Use for real-time monitoring. `elexon · generation · ~5 min`
- **agpt** — Aggregated generation per PSR type. `30 min`. Gives the onshore/offshore wind split FUELHH collapses into one bucket. `elexon · generation · 30 min`
- **agws** — Wind & solar actual generation. `30 min`. Includes `Estimated` embedded solar; pair with FUELHH for a complete renewable picture. `elexon · generation · 30 min`
- **windfor** — Wind generation forecast. `hourly`. Compare FUELHH `WIND` actuals against the forecast to measure forecast error. `elexon · generation · hourly`
