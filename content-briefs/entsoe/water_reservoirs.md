---
slug: water_reservoirs
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A72/A16
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/34-water-reservoirs-http-401.md)"
sources_consulted:
  - vault/entsoe/water_reservoirs.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeWaterReservoirs (lines 240-255)
  - gridflow/src/gridflow/silver/entsoe/water_reservoirs.py::WaterReservoirsTransformer (lines 18-75)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["water_reservoirs"] (lines 109-114)
  - .planning/reconciliation/entsoe/34-water-reservoirs-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/72-water-reservoirs-resolution-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Weekly hydro storage, <span class="italic fg-accent">MWh in the lakes.</span>

**Lede:** Weekly hydro reservoir filling in MWh per bidding zone — the structural driver of Nordic and Alpine hydro dispatch and a canonical input for scarcity price models.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.water_reservoirs` |
| API PATH | `/api?documentType=A72&processType=A16` |
| FREQUENCY | weekly (P7D) |
| PUBLICATION LAG | weekly |
| VOLUME | 1 reading / zone / week |
| PRIMARY KEY | `(timestamp_utc, area_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | P7D | Resolution |
| 2 | weekly | Cadence |
| 3 | MWh | Unit (energy stored) |
| 4 | 6 | Schema columns |

# Sidebar siblings

- actual_generation
- generation_forecast
- installed_capacity
- forecast_margin
- day_ahead_prices

# Sample chart

- **Type:** `sparkline`
- **Title:** "Nordic reservoir level · 52-week"
- **Subtitle:** "Line · MWh · weekly · NO-1"
- **Seed:** 25
- **Toggles:** `52w` (active) / `26w` / `12w`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeWaterReservoirs` (lines 240-255). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start | Week boundary, tz-aware UTC. | `schemas/entsoe.py L243, L250-255` |
| `area_code` | `str` | No | `<inBiddingZone_Domain.mRID>` | EIC bidding zone — typically Nordic / Alpine. | `schemas/entsoe.py L244` |
| `reservoir_mwh` | `float` | No | `<Point><quantity>` | Stored energy in MWh (potential hydropower if released). | `schemas/entsoe.py L245` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `P7D`. | `schemas/entsoe.py L246` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L247` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L248` |

**PARQUET PATH:** `data/silver/entsoe/water_reservoirs/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code)` (`silver/entsoe/water_reservoirs.py L56`)

# Sample data

| timestamp_utc | area_code | reservoir_mwh | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|
| 2026-04-05T00:00:00+00:00 | 10YNO-1--------2 | 32140000.0 | P7D | entsoe | 2026-05-08T18:00:00Z |
| 2026-04-12T00:00:00+00:00 | 10YNO-1--------2 | 31920000.0 | P7D | entsoe | 2026-05-08T18:00:00Z |
| 2026-04-19T00:00:00+00:00 | 10YNO-1--------2 | 32510000.0 | P7D | entsoe | 2026-05-08T18:00:00Z |
| 2026-04-26T00:00:00+00:00 | 10YNO-1--------2 | 33420000.0 | P7D | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-03T00:00:00+00:00** | **10YNO-1--------2** | **35180000.0** | **P7D** | **entsoe** | **2026-05-08T18:00:00Z** |

**Sources:** Synthesised against typical Norwegian (NO-1) spring filling pattern — snowmelt accelerates fill from ~32 TWh in early April to ~35 TWh in early May. The highlighted **2026-05-03 (35.18 TWh)** row is the seasonal spring-fill peak; combined with `day_ahead_prices`, this is the canonical input for Nordic price modelling (high fill → low prices; drought-low fill → high prices).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A72&processType=A16&in_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/water_reservoirs/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.water_reservoirs.WaterReservoirsTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A72&processType=A16&in_Domain=10YNO-1--------2&periodStart=202604010000&periodEnd=202605010000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Year-over-year reservoir level (Nordic zones)
SELECT timestamp_utc, area_code, reservoir_mwh,
       reservoir_mwh - lag(reservoir_mwh, 52) OVER (
         PARTITION BY area_code ORDER BY timestamp_utc
       ) AS yoy_change_mwh
FROM read_parquet('data/silver/entsoe/water_reservoirs/**/*.parquet')
WHERE area_code IN ('10YNO-1--------2', '10Y1001A1001A44P')
ORDER BY area_code, timestamp_utc;
```

**Tab 3 — Python · polars**
```python
import polars as pl

res = pl.read_parquet("data/silver/entsoe/water_reservoirs/**/*.parquet")
prices = pl.read_parquet("data/silver/entsoe/day_ahead_prices/**/*.parquet")
# Weekly mean price vs reservoir level — the Nordic hydro-scarcity feature
weekly_p = prices.group_by_dynamic("timestamp_utc", every="1w").agg(
    pl.col("price_eur_mwh").mean()
)
joined = res.join(weekly_p, on=["timestamp_utc", "area_code"])
print(joined.tail())
```

# Caveats

## 01 Only Nordic and Alpine zones publish

Most continental and GB zones return EMPTY — only zones with significant reservoir hydro (NO-1, SE-1, AT, CH) publish A72/A16. *(Source: vault Known Issues.)*

## 02 Unit is MWh (energy stored), not %

The value is *potential energy in MWh* if all reservoir water were released through the turbines, not a percentage of nameplate capacity. Compute percentage by joining against the TSO-declared maximum (rarely published — use rolling max). *(Source: ENTSO-E spec.)*

## 03 Weekly cadence (P7D)

Short windows (<1 week) may return EMPTY. Use weekly periods. *(Source: vault Known Issues.)*

## 04 GB EMPTY post-Brexit

No GB hydro reservoir data via ENTSO-E. GB pumped-storage facilities (Dinorwig, Cruachan) are not "reservoirs" in the A72 sense. *(Source: vault Known Issues.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/34-water-reservoirs-http-401.md`.)*

# Related datasets

- **`actual_generation`** — Realised hydro generation by zone. `PT15M-PT60M`. Combine with reservoir level to track hydro dispatch decisions. `entsoe · generation · hourly`
- **`day_ahead_prices`** — Day-ahead clearing prices. `PT60M`. Reservoir level is a canonical price driver in NO-1 / SE-1 / AT — pair for scarcity modelling. `entsoe · prices · hourly`
- **`generation_forecast`** — TSO total generation forecast. `PT60M`. Cross-check whether forecasted hydro dispatch is consistent with reservoir trajectory. `entsoe · forecast · hourly`
- **`storage` (GIE)** — Gas storage analogue. `daily`. Cross-vendor parallel: gas storage drawdown vs hydro reservoir drawdown for joint energy-balance modelling. `gie · storage · daily`
