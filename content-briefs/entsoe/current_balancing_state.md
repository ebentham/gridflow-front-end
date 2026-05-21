---
slug: current_balancing_state
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A86/B33
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/12-current-balancing-state-http-401.md)"
sources_consulted:
  - vault/entsoe/current_balancing_state.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeBalancingState (lines 597-613)
  - gridflow/src/gridflow/silver/entsoe/h8_balancing.py::CurrentBalancingStateTransformer (lines 113-117)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["current_balancing_state"] (lines 319-325)
  - .planning/reconciliation/entsoe/12-current-balancing-state-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/50-current-balancing-state-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Current balancing state, <span class="italic fg-accent">A86/B33.</span>

**Lede:** Near-real-time balancing-state quantity in MW per control area — signed net activation reflecting whether the TSO is buying or selling balancing energy at the current settlement period.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.current_balancing_state` |
| API PATH | `/api?documentType=A86&businessType=B33` |
| FREQUENCY | PT30M typical |
| PUBLICATION LAG | T+1h |
| VOLUME | 48 points / area / day |
| PRIMARY KEY | `(timestamp_utc, area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A86 | DocumentType |
| 2 | B33 | businessType (pinned) |
| 3 | H8 | Shared transformer family |
| 4 | 7 | Schema columns |

# Sidebar siblings

- imbalance_prices
- imbalance_volume
- activated_balancing_prices
- activated_balancing_qty
- balancing_energy_bids

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB current balancing state · 24h"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 81
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeBalancingState` (lines 597-613). H8-family transformer; uses `area_Domain` (single control area).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L600, L608-613` |
| `area_code` | `str` | No | `<area_Domain.mRID>` | Control area EIC (renamed by H8 transformer from area_domain). | `schemas/entsoe.py L601`; `silver/entsoe/h8_balancing.py L107` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Signed balancing state MW. | `schemas/entsoe.py L602` |
| `business_type` | `str` | No (default `"B33"`) | `<businessType>` | Pinned to `B33` ("Area control error"). | `schemas/entsoe.py L603` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT30M`. | `schemas/entsoe.py L604` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L605` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L606` |

**PARQUET PATH:** `data/silver/entsoe/current_balancing_state/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, business_type)` (`silver/entsoe/h8_balancing.py L41`)

# Sample data

| timestamp_utc | area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | -42.0 | B33 | PT30M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T08:00:00+00:00 | 10YGB----------A | 124.0 | B33 | PT30M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T17:30:00+00:00** | **10YGB----------A** | **-481.0** | **B33** | **PT30M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T18:00:00+00:00 | 10YGB----------A | -312.0 | B33 | PT30M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **GB 17:30 (-481 MW)** row reflects a typical evening-peak short-system condition — the area control error is negative, indicating the system is short and the TSO must activate upward balancing. Combined with `imbalance_prices`, this is the canonical signal driving short-term price formation in the GB balancing mechanism.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A86&businessType=B33&area_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/current_balancing_state/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h8_balancing.CurrentBalancingStateTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A86&businessType=B33&area_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily mean balancing-state and absolute deviation per zone (last 30 days)
SELECT date_trunc('day', timestamp_utc) AS day, area_code,
       avg(quantity_mw) AS mean_state_mw,
       avg(abs(quantity_mw)) AS mean_abs_state_mw
FROM read_parquet('data/silver/entsoe/current_balancing_state/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2 ORDER BY 1, mean_abs_state_mw DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

state = pl.read_parquet("data/silver/entsoe/current_balancing_state/**/*.parquet")
prices = pl.read_parquet("data/silver/entsoe/imbalance_prices/**/*.parquet")
# Negative state (short) should correlate with elevated imbalance price
print(state.join(prices, on=["timestamp_utc", "area_code"]).select([
    "timestamp_utc", "quantity_mw", "price_eur_mwh"
]).tail())
```

# Caveats

## 01 businessType B33 pinned

Connector pins `businessType=B33` (Area control error). Other A86 businessType variants surface in `imbalance_volume`. *(Source: `endpoints.py L319-325`.)*

## 02 H8 transformer family

Uses shared `_H8BalancingTransformer` base. `area_domain` renamed to `area_code` during transform. *(Source: `silver/entsoe/h8_balancing.py L25-110`.)*

## 03 Sign convention

Negative quantity = system short (TSO buying upward balancing); positive = system long. Domain convention may vary by TSO — verify with local market documentation. *(Source: domain knowledge.)*

## 04 Revisions overwrite

Same `(timestamp_utc, area_code, business_type)` re-publication overwrites silently on dedup. *(Source: `silver/entsoe/h8_balancing.py L41`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/12-current-balancing-state-http-401.md`.)*

# Related datasets

- **`imbalance_volume`** — A86 imbalance volumes per direction. `PT30M`. Sister A86 surface with businessType A19 (long/short split). `entsoe · prices · 30 min`
- **`imbalance_prices`** — A85 imbalance prices. `PT30M`. Pair to map state → price. `entsoe · prices · 30 min`
- **`activated_balancing_qty`** — A83/A16 activated reserve MWh. `PT60M`. Identifies which reserves the TSO used to close the gap. `entsoe · balancing · hourly`
- **`balancing_energy_bids`** — A37/A47 bid stack. `PT60M`. The bid stack against which the activations are matched. `entsoe · balancing · hourly`
