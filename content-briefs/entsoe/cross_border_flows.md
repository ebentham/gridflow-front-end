---
slug: cross_border_flows
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A11
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/10-cross-border-flows-http-401.md)"
sources_consulted:
  - vault/entsoe/cross_border_flows.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeCrossborderFlow (lines 64-84)
  - gridflow/src/gridflow/silver/entsoe/cross_border_flows.py::CrossBorderFlowsTransformer (lines 18-88)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["cross_border_flows"] (lines 47-49)
  - .planning/reconciliation/entsoe/10-cross-border-flows-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/48-cross-border-flows-extra-resolution.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Physical flows between zones, <span class="italic fg-accent">directional.</span>

**Lede:** Hourly physical cross-border flows in MW per zone-pair direction — the canonical input for interconnector utilisation, congestion analysis, and cross-border price-spread modelling.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.cross_border_flows` |
| API PATH | `/api?documentType=A11` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | T+1h |
| VOLUME | 24 points / border-direction / day |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A11 | DocumentType |
| 2 | T+1h | Best-case lag |
| 3 | zone-pair | `domain_style` |
| 4 | 7 | Schema columns |

# Sidebar siblings

- net_transfer_capacity
- commercial_schedules
- net_positions
- transfer_capacity_use
- offered_transfer_capacity_implicit

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB → FR physical flow · 24-hour"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 41
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeCrossborderFlow` (lines 64-84). G5-W3 (2026-05) added `resolution` and `ingested_at` to align with transformer output. Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L71, L79-84` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L72` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L73` |
| `flow_mw` | `float` | No | `<Point><quantity>` | MW physical flow (directional, positive = in → out). | `schemas/entsoe.py L74` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. Added in G5-W3 to match transformer output. | `schemas/entsoe.py L75` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L76` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. Added in G5-W3. | `schemas/entsoe.py L77` |

**PARQUET PATH:** `data/silver/entsoe/cross_border_flows/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code)` (`silver/entsoe/cross_border_flows.py L68-70`)

# Sample data

| timestamp_utc | in_area_code | out_area_code | flow_mw | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 1840.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T06:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 2410.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T19:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **3920.0** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T19:00:00+00:00 | 10YFR-RTE------C | 10YGB----------A | 0.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T11:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | -180.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T11:00:00+00:00 | 10YFR-RTE------C | 10YGB----------A | 180.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised against typical GB ↔ FR flow shape (export to FR in evenings via IFA/ElecLink, low or reverse mid-day). The highlighted **GB → FR 19:00 (3.92 GW)** row is the canonical winter-evening export peak via the GB-FR interconnectors (IFA + IFA2 + ElecLink ≈ 4 GW combined capacity). Note the SP11 (11:00) rows: GB → FR is -180 MW (recorded as -180) and FR → GB is +180 MW — many TSOs publish both directions; pair them to compute the signed net flow.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A11&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/cross_border_flows/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.cross_border_flows.CrossBorderFlowsTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A11&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Signed net flow per border per hour (GB perspective)
SELECT timestamp_utc,
       CASE WHEN in_area_code='10YGB----------A' THEN flow_mw
            ELSE -flow_mw END AS gb_export_mw,
       CASE WHEN in_area_code='10YGB----------A' THEN out_area_code
            ELSE in_area_code END AS counterparty
FROM read_parquet('data/silver/entsoe/cross_border_flows/**/*.parquet')
WHERE '10YGB----------A' IN (in_area_code, out_area_code)
ORDER BY timestamp_utc DESC LIMIT 100;
```

**Tab 3 — Python · polars**
```python
import polars as pl

flows = pl.read_parquet("data/silver/entsoe/cross_border_flows/**/*.parquet")
prices = pl.read_parquet("data/silver/entsoe/day_ahead_prices/**/*.parquet")
# Spread-flow correlation: do flows track day-ahead spread?
gb_fr = flows.filter(
    (pl.col("in_area_code") == "10YGB----------A") &
    (pl.col("out_area_code") == "10YFR-RTE------C")
)
print(gb_fr.tail())
```

# Caveats

## 01 Directional — pair both halves for net flow

Each border requires two requests (one per direction). True net flow = `flow(GB→FR) - flow(FR→GB)`. *(Source: vault Known Issues; `endpoints.py L47-49`.)*

## 02 GB borders still publish post-Brexit

Unlike `actual_generation`, GB cross-border flows continue to publish via ENTSO-E (the flows are physical and reported by the European-side TSO). *(Source: vault Known Issues.)*

## 03 Resolution typically PT60M

Most borders publish `PT60M`. The G5-W3 schema update (2026-05) added `resolution` to the Pydantic class to match transformer output. *(Source: `schemas/entsoe.py L66-69`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code)` re-publication overwrites silently on dedup. No `published_at` for PIT. *(Source: `silver/entsoe/cross_border_flows.py L68-70`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/10-cross-border-flows-http-401.md`.)*

# Related datasets

- **`net_transfer_capacity`** — Forecasted capacity per border. `PT60M`. The denominator for interconnector utilisation calculations (`flow / NTC`). `entsoe · transmission · hourly`
- **`commercial_schedules`** — Nominated commercial flows per border. `PT60M`. Compare commercial schedule to physical flow to identify intraday adjustment. `entsoe · transmission · hourly`
- **`transfer_capacity_use`** — Use of transfer capacity (A25/B05). `PT60M`. The settlement-side view of border utilisation. `entsoe · transmission · hourly`
- **`day_ahead_prices`** — Cross-border price spreads drive cross-border flows. `PT60M`. Pair to compute flow-vs-spread correlation. `entsoe · prices · hourly`
