---
slug: available_through_uioli_long_term
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/AvailableThroughUioliLongTerm
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/available_through_uioli_long_term.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["available_through_uioli_long_term"] (line 113) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/11-available-through-uioli-long-term-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Long-term use-it-or-lose-it <span class="italic fg-accent">capacity.</span>

**Lede:** Capacity recovered from underused long-term firm bookings via the UIOLI mechanism — the canonical CMP signal for capacity returning to auction.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.available_through_uioli_long_term` |
| API PATH | `/api/v1/operationalData?indicator=Available%20through%20UIOLI%20long-term` |
| FREQUENCY | daily |
| PUBLICATION LAG | same-day |
| VOLUME | ~9 GB points/day (default filter); often 0 rows |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | CMP | Mechanism (UIOLI long-term) |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- available_through_uioli_short_term
- available_through_oversubscription
- available_through_surrender
- cmp_unavailable_firm_capacity
- firm_booked

# Sample chart

- **Type:** `sparkline`
- **Title:** "UIOLI long-term capacity at GB points · 1-year window"
- **Subtitle:** "Sparkline · GWh/day · last 12 months"
- **Seed:** 36
- **Toggles:** `1y` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same canonical operational-data shape; differentiator is `indicator="Available through UIOLI long-term"` (note hyphen).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Validity window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Available through UIOLI long-term"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction. | dynamic |
| `is_cmp_relevant` | `bool` | Yes | `isCmpRelevant` | `true` for this indicator. | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"`. | dynamic |
| `value` | `float` | Yes | `value` | UIOLI-recovered long-term capacity. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/available_through_uioli_long_term/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | period_to | point_key | direction_key | unit | value | last_update_date_time |
|---|---|---|---|---|---|---|
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 0 | 2025-10-01T08:00:00+00:00 |
| **2026-01-15T04:00:00+00:00** | **2026-10-01T04:00:00+00:00** | **ITP-00005** | **exit** | **kWh/d** | **20,000,000** | **2026-01-14T16:30:00+00:00** |
| 2026-01-15T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 6,000,000 | 2026-01-14T16:30:00+00:00 |
| 2026-04-01T04:00:00+00:00 | 2026-07-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 10,000,000 | 2026-03-25T11:00:00+00:00 |
| 2026-04-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 7,000,000 | 2026-03-30T09:00:00+00:00 |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 3,000,000 | 2026-05-05T17:00:00+00:00 |
| 2025-07-01T04:00:00+00:00 | 2025-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 18,000,000 | 2025-06-25T11:00:00+00:00 |
| 2025-10-01T04:00:00+00:00 | 2026-04-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 12,000,000 | 2025-09-15T08:00:00+00:00 |

**Sources:** Synthesised — UIOLI long-term capacity is recovered annually as the TSO assesses utilisation of prior-year firm bookings. Highlighted row is a mid-gas-year UIOLI release at Bacton IUK on 2026-01-14 releasing 20 GWh/d for the remaining ~9 months — typical UIOLI cadence is once per gas-year per point.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Available through UIOLI long-term&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/available_through_uioli_long_term/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `AvailableThroughUioliLongTermTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Available%20through%20UIOLI%20long-term&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Annual UIOLI long-term recovery per point (last 3 gas years)
SELECT EXTRACT(year FROM period_from) AS year_start,
       point_key, direction_key,
       MAX(value) / 1e6 AS max_recovered_gwh
FROM read_parquet('data/silver/entsog/available_through_uioli_long_term/**/*.parquet')
WHERE value > 0
  AND period_from >= current_date - INTERVAL 3 YEAR
GROUP BY 1, 2, 3
ORDER BY 1, max_recovered_gwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/available_through_uioli_long_term/**/*.parquet")
# Show all non-zero UIOLI events
print(df.filter(pl.col("value") > 0).sort("last_update_date_time", descending=True).head(20))
```

# Caveats

## 01 Indicator string is exact-case (with hyphen)

Connector sends literal `"Available through UIOLI long-term"` — lowercase `through`, hyphen `long-term`. *(Source: `OPERATIONAL_INDICATORS["available_through_uioli_long_term"]` `connectors/entsog/endpoints.py L113`.)*

## 02 UIOLI long-term is annual-cadence

The TSO assesses utilisation roughly annually; expect 1-2 release events per gas-year per congested point. *(Source: ENTSO-G CMP Network Code.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Use-It-Or-Lose-It is involuntary

Unlike `available_through_surrender` (voluntary), UIOLI is TSO-initiated capacity reclamation. Track the timing of UIOLI releases as a market-stress signal. *(Source: domain knowledge / CMP mechanism.)*

# Related datasets

- **`available_through_uioli_short_term`** — Short-term UIOLI (day-ahead window). `daily`. Sister mechanism with shorter look-back. *entsog · capacity · daily*
- **`available_through_oversubscription`** — Oversubscription mechanism. `daily`. Sister CMP procedure. *entsog · capacity · daily*
- **`available_through_surrender`** — Voluntary surrender. `daily`. Voluntary alternative to UIOLI. *entsog · capacity · daily*
- **`firm_booked`** — Booked capacity (UIOLI target). `daily`. UIOLI reduces `firm_booked` retrospectively. *entsog · capacity · daily*
