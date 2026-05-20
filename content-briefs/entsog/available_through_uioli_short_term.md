---
slug: available_through_uioli_short_term
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/AvailableThroughUioliShortTerm
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/available_through_uioli_short_term.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["available_through_uioli_short_term"] (line 114) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/12-available-through-uioli-short-term-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Short-term use-it-or-lose-it <span class="italic fg-accent">capacity.</span>

**Lede:** Day-ahead capacity recovered via the UIOLI short-term mechanism — the canonical signal for capacity reclaimed when nominated firm-booked capacity is not used.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.available_through_uioli_short_term` |
| API PATH | `/api/v1/operationalData?indicator=Available%20through%20UIOLI%20short-term` |
| FREQUENCY | daily |
| PUBLICATION LAG | day-ahead (T-1) |
| VOLUME | ~9 GB points/day (default filter); often 0 rows |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | day-ahead | UIOLI window |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- available_through_uioli_long_term
- available_through_oversubscription
- available_through_surrender
- interruptible_available
- firm_booked

# Sample chart

- **Type:** `sparkline`
- **Title:** "UIOLI short-term capacity at Bacton (IUK) · 90-day window"
- **Subtitle:** "Sparkline · GWh/day · last 90 days"
- **Seed:** 37
- **Toggles:** `30d` (active) / `90d`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same canonical operational-data shape; differentiator is `indicator="Available through UIOLI short-term"` (note hyphen).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Validity window (day-ahead). | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Available through UIOLI short-term"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction. | dynamic |
| `is_cmp_relevant` | `bool` | Yes | `isCmpRelevant` | `true` for this indicator. | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"`. | dynamic |
| `value` | `float` | Yes | `value` | UIOLI-recovered short-term capacity. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/available_through_uioli_short_term/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | period_to | point_key | direction_key | unit | value | last_update_date_time |
|---|---|---|---|---|---|---|
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 8,000,000 | 2026-05-05T16:00:00+00:00 |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 3,500,000 | 2026-05-05T16:00:00+00:00 |
| **2026-05-05T04:00:00+00:00** | **2026-05-06T04:00:00+00:00** | **ITP-00005** | **exit** | **kWh/d** | **12,000,000** | **2026-05-04T16:00:00+00:00** |
| 2026-05-05T04:00:00+00:00 | 2026-05-06T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 2,000,000 | 2026-05-04T16:00:00+00:00 |
| 2026-05-04T04:00:00+00:00 | 2026-05-05T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 6,000,000 | 2026-05-03T16:00:00+00:00 |
| 2026-05-03T04:00:00+00:00 | 2026-05-04T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 0 | 2026-05-02T16:00:00+00:00 |
| 2026-05-02T04:00:00+00:00 | 2026-05-03T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 4,500,000 | 2026-05-01T16:00:00+00:00 |
| 2026-05-01T04:00:00+00:00 | 2026-05-02T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 3,000,000 | 2026-04-30T16:00:00+00:00 |

**Sources:** Synthesised — UIOLI short-term has daily cadence and reflects what shippers under-nominated the previous gas day. Highlighted row is the largest UIOLI-short release of the sample week (12 GWh/d at Bacton IUK on 2026-05-05) — typical pattern is a 1-day window with significant variability.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Available through UIOLI short-term&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/available_through_uioli_short_term/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `AvailableThroughUioliShortTermTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Available%20through%20UIOLI%20short-term&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily UIOLI short-term recovered (last 30 days)
SELECT period_from::date AS gas_day,
       point_key, direction_key,
       value / 1e6 AS recovered_gwh
FROM read_parquet('data/silver/entsog/available_through_uioli_short_term/**/*.parquet')
WHERE period_from >= current_date - INTERVAL 30 DAY
  AND value > 0
ORDER BY 1 DESC, recovered_gwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/available_through_uioli_short_term/**/*.parquet")
# Daily total UIOLI-short across GB points
gb_total = (
    df.filter(pl.col("operator_key").str.starts_with("UK-TSO-"))
      .group_by("period_from")
      .agg((pl.col("value").sum() / 1e6).alias("uioli_short_gwh"))
      .sort("period_from")
)
print(gb_total.tail(14))
```

# Caveats

## 01 Indicator string is exact-case (with hyphen)

Connector sends literal `"Available through UIOLI short-term"`. *(Source: `OPERATIONAL_INDICATORS["available_through_uioli_short_term"]` `connectors/entsog/endpoints.py L114`.)*

## 02 Daily-cadence, day-ahead window

UIOLI short-term is the day-ahead version of UIOLI long-term — recovered capacity is offered for one gas day only. Pair with `firm_booked` to see what triggered the reclamation. *(Source: ENTSO-G CMP Network Code.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Different cadence from UIOLI long-term

Long-term is annual; short-term is daily — the two report different mechanisms despite naming similarity. *(Source: ENTSO-G Network Code on CAM/CMP.)*

# Related datasets

- **`available_through_uioli_long_term`** — Annual UIOLI mechanism. `daily`. Sister mechanism with longer look-back. *entsog · capacity · daily*
- **`available_through_oversubscription`** — Oversubscription mechanism. `daily`. Sister CMP procedure. *entsog · capacity · daily*
- **`available_through_surrender`** — Voluntary surrender. `daily`. Voluntary alternative. *entsog · capacity · daily*
- **`interruptible_available`** — Interruptible capacity. `daily`. Adjacent supply of short-term capacity. *entsog · capacity · daily*
