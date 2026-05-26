---
slug: available_through_oversubscription
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/AvailableThroughOversubscription
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/available_through_oversubscription.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["available_through_oversubscription"] (line 111) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/09-available-through-oversubscription-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Capacity above firm through <span class="italic fg-accent">oversubscription.</span>

**Lede:** Extra capacity offered through the oversubscription CMP mechanism — the canonical signal for capacity beyond firm-technical limits, made available when historical utilisation justifies it.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.available_through_oversubscription` |
| API PATH | `/api/v1/operationalData?indicator=Available%20through%20Oversubscription` |
| FREQUENCY | daily |
| PUBLICATION LAG | same-day |
| VOLUME | ~9 GB points/day (default filter); often 0 rows |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | CMP | Mechanism (oversubscription) |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- available_through_surrender
- available_through_uioli_long_term
- available_through_uioli_short_term
- cmp_unavailable_firm_capacity
- firm_available

# Sample chart

- **Type:** `sparkline`
- **Title:** "Oversubscription capacity at GB points · 1-year window"
- **Subtitle:** "Sparkline · GWh/day · last 12 months"
- **Seed:** 34
- **Toggles:** `1y` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same canonical operational-data shape; differentiator is `indicator="Available through Oversubscription"`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Validity window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Available through Oversubscription"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction. | dynamic |
| `is_cmp_relevant` | `bool` | Yes | `isCmpRelevant` | `true` for this indicator. | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"`. | dynamic |
| `value` | `float` | Yes | `value` | Oversubscription extra capacity. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/available_through_oversubscription/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | period_to | point_key | direction_key | unit | value | last_update_date_time |
|---|---|---|---|---|---|---|
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 12,000,000 | 2025-09-15T08:00:00+00:00 |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | entry | kWh/d | 8,000,000 | 2025-09-15T08:00:00+00:00 |
| **2025-10-01T04:00:00+00:00** | **2026-10-01T04:00:00+00:00** | **ITP-00207** | **exit** | **kWh/d** | **5,000,000** | **2025-09-15T08:00:00+00:00** |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00207 | entry | kWh/d | 0 | 2025-09-15T08:00:00+00:00 |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00495 | entry | kWh/d | 0 | 2025-09-15T08:00:00+00:00 |
| 2026-04-01T04:00:00+00:00 | 2026-07-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 3,000,000 | 2026-03-15T08:00:00+00:00 |
| 2026-04-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 4,000,000 | 2026-03-15T08:00:00+00:00 |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 0 | 2026-05-05T08:00:00+00:00 |

**Sources:** Synthesised — oversubscription capacity is typically small (single-digit % of technical) and only offered at chronically-congested points. Highlighted row is BBL exit oversubscription at 5 GWh/d, about 2.5% of the 200 GWh/d technical. Zero-rows are common for points without congestion history.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Available through Oversubscription&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/available_through_oversubscription/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `AvailableThroughOversubscriptionTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Available%20through%20Oversubscription&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Points with oversubscription capacity active in the current gas year
SELECT point_key, direction_key,
       MAX_BY(value, period_from) / 1e6 AS extra_gwh
FROM read_parquet('data/silver/entsog/available_through_oversubscription/**/*.parquet')
WHERE period_from <= current_date AND period_to > current_date
  AND value > 0
GROUP BY 1, 2
ORDER BY extra_gwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/available_through_oversubscription/**/*.parquet")
# How often is oversubscription >0?
print(df.group_by("point_key").agg((pl.col("value") > 0).sum().alias("nonzero_rows")).sort("nonzero_rows", descending=True))
```

# Caveats

## 01 Indicator string is exact-case (mixed case)

Connector sends literal `"Available through Oversubscription"` — note the lowercase `through`. *(Source: `OPERATIONAL_INDICATORS["available_through_oversubscription"]` `connectors/entsog/endpoints.py L111`.)*

## 02 Most rows are zero

Oversubscription only kicks in when historical congestion justifies it. Empty (zero-value) rows are the norm at uncongested points. *(Source: domain knowledge / CMP mechanism docs.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Part of CMP — pair with cmp_* datasets

The oversubscription mechanism is one of three CMP procedures (oversubscription, surrender, UIOLI). For full CMP picture, also query `cmp_unsuccessful_requests`, `cmp_unavailable_firm_capacity`, `cmp_auction_premiums`. *(Source: ENTSO-G Network Code on CAM/CMP.)*

# Related datasets

- **`available_through_surrender`** — Capacity surrendered back to the TSO. `daily`. Complementary CMP mechanism. *entsog · capacity · daily*
- **`available_through_uioli_long_term`** — Long-term UIOLI capacity. `daily`. Use-it-or-lose-it long-product. *entsog · capacity · daily*
- **`available_through_uioli_short_term`** — Short-term UIOLI capacity. `daily`. Same mechanism, day-ahead window. *entsog · capacity · daily*
- **`cmp_unavailable_firm_capacity`** — Firm capacity classified as unavailable. `daily`. CMP trigger condition. *entsog · CMP · daily*
