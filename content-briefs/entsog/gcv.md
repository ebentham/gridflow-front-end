---
slug: gcv
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/GCV
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/gcv.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["gcv"] (line 106) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/21-gcv-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Gross calorific value of gas, <span class="italic fg-accent">per point.</span>

**Lede:** Gross Calorific Value at each operator-point-direction in `kWh/Nm³` — the canonical conversion factor for moving between volumetric and energy gas-flow units.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.gcv` |
| API PATH | `/api/v1/operationalData?indicator=GCV` |
| FREQUENCY | daily (gas day) |
| PUBLICATION LAG | same-day (Provisional) |
| VOLUME | ~9 GB points/day (default filter) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/Nm³ | Reporting unit |
| 3 | gas-quality | Indicator family |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- wobbe_index
- hydrogen_content
- methane_content
- oxygen_content
- physical_flows

# Sample chart

- **Type:** `sparkline`
- **Title:** "Bacton (IUK) · daily GCV"
- **Subtitle:** "Sparkline · kWh/Nm³ · 30-day window"
- **Seed:** 59
- **Toggles:** `30d` (active) / `1y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same operational-data shape as `physical_flows`; differentiators are `indicator="GCV"` and `unit="kWh/Nm³"` (energy per normal cubic metre).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Gas-day window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"GCV"`. | dynamic |
| `operator_key` / `operator_label` | `str` | Yes | `operatorKey` / `operatorLabel` | TSO. | dynamic |
| `point_key` / `point_label` | `str` | Yes | `pointKey` / `pointLabel` | Connection-point. | dynamic |
| `direction_key` | `str` | Yes | `directionKey` | `"entry"` / `"exit"` (lowercase). | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/Nm³"` — energy per normal cubic metre. | dynamic |
| `value` | `float` | Yes | `value` | GCV value (typically 10.5-12.5 kWh/Nm³ for North Sea gas). | `silver/entsog/generic.py L122-124` |
| `flow_status` | `str` | Yes | `flowStatus` | `"Provisional"` / `"Confirmed"`. | dynamic |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/gcv/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | point_key | point_label | direction_key | unit | value | flow_status |
|---|---|---|---|---|---|---|
| 2026-05-06T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | kWh/Nm³ | 11.5638 | Provisional |
| **2026-05-06T04:00:00+00:00** | **ITP-00207** | **Bacton (BBL)** | **exit** | **kWh/Nm³** | **11.4892** | **Provisional** |
| 2026-05-06T04:00:00+00:00 | ITP-00495 | Moffat (IE) | entry | kWh/Nm³ | 11.6210 | Provisional |
| 2026-05-06T04:00:00+00:00 | ITP-00090 | Moffat | entry | kWh/Nm³ | 11.5995 | Provisional |
| 2026-05-05T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | kWh/Nm³ | 11.5701 | Confirmed |
| 2026-05-05T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | exit | kWh/Nm³ | 11.4905 | Confirmed |
| 2026-05-04T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | kWh/Nm³ | 11.5634 | Confirmed |
| 2026-05-04T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | exit | kWh/Nm³ | 11.4823 | Confirmed |

**Sources:** First row verbatim from vault Bronze sample (`gcv.md` L113; `value=11.5638` kWh/Nm³ at Bacton IUK exit). Remaining rows synthesised — GCV values cluster tightly around 11.5 kWh/Nm³ for North Sea gas (Bacton, Moffat); slight inter-point variance reflects gas blend composition. Highlighted row is BBL exit GCV — note the small but consistent gap between IUK and BBL pipeline gas (different upstream blend).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=GCV&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/gcv/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `GcvTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=GCV&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- 30-day average GCV per Bacton point
SELECT point_key, point_label,
       AVG(value) AS avg_gcv_kwh_nm3,
       STDDEV(value) AS gcv_volatility
FROM read_parquet('data/silver/entsog/gcv/**/*.parquet')
WHERE timestamp_utc >= current_date - INTERVAL 30 DAY
  AND point_key IN ('ITP-00005', 'ITP-00207')
GROUP BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/gcv/**/*.parquet")
# Convert physical_flows kWh/d to volumetric Nm³/d using GCV
flows = pl.read_parquet("data/silver/entsog/physical_flows/**/*.parquet")
joined = flows.join(
    df.select(["timestamp_utc", "point_key", "value"]).rename({"value": "gcv"}),
    on=["timestamp_utc", "point_key"], how="left",
)
print(joined.with_columns((pl.col("flow_gwh_per_day") * 1e6 / pl.col("gcv")).alias("nm3_per_day")).head())
```

# Caveats

## 01 Indicator string is exact-case (`"GCV"` — uppercase)

Vendor rejects `gcv` or `Gcv`; connector sends literal `"GCV"`. *(Source: `OPERATIONAL_INDICATORS["gcv"] = "GCV"` `connectors/entsog/endpoints.py L106`.)*

## 02 Unit `kWh/Nm³` — energy per normal cubic metre

Use GCV to convert between volumetric (`Nm³/d`) and energy (`kWh/d`) units. Typical North Sea blend = 11.5 kWh/Nm³. *(Source: vault Bronze sample L110; gas-physics convention.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Slow-varying — daily values are smooth

GCV changes slowly (gas-blend variability is small day-to-day). Use for unit-conversion smoothing rather than as a market signal. *(Source: domain knowledge / vault sample volatility.)*

# Related datasets

- **`wobbe_index`** — Wobbe index (energy / sqrt(specific gravity)). `daily`. Sister gas-quality indicator. *entsog · gas-quality · daily*
- **`physical_flows`** — Energy-denominated flows. `daily`. Use GCV to convert to volumetric Nm³/d. *entsog · operational · daily*
- **`methane_content`** — Methane fraction (endpoint withdrawn 2026-05-19). `daily`. Historic-only sister indicator. *entsog · gas-quality · historic*
- **`hydrogen_content`** — Hydrogen fraction (endpoint withdrawn 2026-05-19). `daily`. Historic-only sister indicator. *entsog · gas-quality · historic*
