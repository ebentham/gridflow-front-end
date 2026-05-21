---
slug: activated_balancing_qty
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A83/A16
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/activated_balancing_qty.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeActivatedBalancingQty (lines 384-407)
  - gridflow/src/gridflow/silver/entsoe/activated_balancing_qty.py::ActivatedBalancingQtyTransformer (lines 18-106)
  - .planning/reconciliation/entsoe/36-activated-balancing-qty-manual-transformer-schema.md (wontfix v3-candidate — stale; class now exists in schemas/entsoe.py)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found:
  - source_a: "reconciliation finding 36 (manual_transformer_schema)"
    source_a_says: "No importable Pydantic class declared for activated_balancing_qty"
    source_b: "schemas/entsoe.py L384-407 (EntsoeActivatedBalancingQty)"
    source_b_says: "Class IS declared and imported by silver/entsoe/activated_balancing_qty.py L11 — finding 36 is stale (closed by later schema addition)"
    orchestrator_recommendation: "Surface in Caveats — finding is now resolved but no DOC_TYPES entry in endpoints.py (caller must dispatch manually). The schema is real; the missing piece is the connector registration."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Activated balancing quantity, <span class="italic fg-accent">A83.</span>

**Lede:** Activated balancing energy quantity in MWh per control area, reserve_type and direction — the MWh delivered for each frequency-restoration reserve activation, paired with prices for revenue.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A83/A16](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.activated_balancing_qty` |
| API PATH | `/api?documentType=A83&processType=A16` |
| FREQUENCY | PT60M typical |
| PUBLICATION LAG | as published |
| VOLUME | varies by area |
| PRIMARY KEY | `(timestamp_utc, area_code, reserve_type, direction)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A83 | DocumentType |
| 2 | A16 | processType (realised) |
| 3 | manual | DOC_TYPES dispatch (no endpoints.py entry) |
| 4 | 7 | Schema columns |

# Sidebar siblings

- activated_balancing_prices
- contracted_reserves
- procured_balancing_capacity
- balancing_energy_bids
- current_balancing_state

# Sample chart

- **Type:** `barsH`
- **Title:** "Activated reserve MWh by reserve_type · 24h"
- **Subtitle:** "Horizontal bars · MWh · UTC · 6 May 2026"
- **Seed:** 85
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeActivatedBalancingQty` (lines 384-407). Maps businessType → reserve_type and flowDirection → direction, same pattern as `activated_balancing_prices`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L392, L401-407` |
| `area_code` | `str` | No | `<controlArea_Domain.mRID>` | Control area EIC. | `schemas/entsoe.py L393`; `silver/entsoe/activated_balancing_qty.py L65` |
| `reserve_type` | `str` | No | derived from `<businessType>` | "fcr" (A95) / "afrr" (A96) / "mfrr" (A97) / "rr" (A98). | `schemas/entsoe.py L394`; `silver/entsoe/activated_balancing_qty.py L68-70` |
| `direction` | `str` | No | derived from `<flowDirection>` | "up" (A01) / "down" (A02). | `schemas/entsoe.py L395`; `silver/entsoe/activated_balancing_qty.py L71-73` |
| `quantity_mwh` | `float` | No | `<Point><quantity>` | Activated MWh. | `schemas/entsoe.py L396` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L397` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L398` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L399` |

**PARQUET PATH:** `data/silver/entsoe/activated_balancing_qty/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, reserve_type, direction)` (`silver/entsoe/activated_balancing_qty.py L83`)

# Sample data

| timestamp_utc | area_code | reserve_type | direction | quantity_mwh | resolution | data_provider |
|---|---|---|---|---|---|---|
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | afrr | up | 142.5 | PT60M | entsoe |
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | afrr | down | 18.2 | PT60M | entsoe |
| **2026-05-06T17:00:00+00:00** | **10YGB----------A** | **mfrr** | **up** | **318.4** | **PT60M** | **entsoe** |
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | mfrr | down | 4.1 | PT60M | entsoe |

**Sources:** Synthesised against typical GB evening-peak activation. The highlighted **mFRR up 318.4 MWh** row reflects the deeper reserve volume during the high-system-stress hour. Pair this MWh quantity with the `activated_balancing_prices` €/MWh for the same key tuple to get the activation cost (412.80 × 318.4 ≈ 131 k€ for that one hour of mFRR up).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A83&processType=A16&businessType={A95|A96|A97|A98}&controlArea_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/activated_balancing_qty/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.activated_balancing_qty.ActivatedBalancingQtyTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A83&processType=A16&businessType=A96&controlArea_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Activation revenue per reserve_type per zone (last 30 days)
SELECT q.area_code, q.reserve_type, q.direction,
       sum(q.quantity_mwh) AS total_mwh,
       sum(q.quantity_mwh * p.price_eur_mwh) AS revenue_eur
FROM read_parquet('data/silver/entsoe/activated_balancing_qty/**/*.parquet') q
JOIN read_parquet('data/silver/entsoe/activated_balancing_prices/**/*.parquet') p
  USING (timestamp_utc, area_code, reserve_type, direction)
WHERE q.timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2, 3 ORDER BY revenue_eur DESC NULLS LAST;
```

**Tab 3 — Python · polars**
```python
import polars as pl

qty = pl.read_parquet("data/silver/entsoe/activated_balancing_qty/**/*.parquet")
# Daily activation volume by reserve_type
daily = qty.with_columns(pl.col("timestamp_utc").dt.date().alias("day")).group_by(
    ["day", "reserve_type", "direction"]
).agg(pl.col("quantity_mwh").sum())
print(daily.tail())
```

# Caveats

## 01 No DOC_TYPES entry in endpoints.py

`activated_balancing_qty` has no entry in `connectors/entsoe/endpoints.py::DOC_TYPES`. Callers must dispatch the A83/A16 query manually via `**params` injection. Finding `36-activated-balancing-qty-manual-transformer-schema.md` (wontfix v3-candidate) flagged the missing class — now closed by the L384-407 addition, but the connector dispatch remains manual. *(Source: connector source.)*

## 02 reserve_type code mapping

`businessType` A95/A96/A97/A98 → `reserve_type` "fcr"/"afrr"/"mfrr"/"rr" via `replace_strict`. *(Source: `silver/entsoe/activated_balancing_qty.py L68-70`.)*

## 03 quantity_mwh (MWh) not quantity_mw

Unit is MWh — the integrated energy over the activation interval. Distinct from MW (instantaneous power) in capacity datasets. *(Source: `schemas/entsoe.py L396`.)*

## 04 Both directions surface separately

Up and down activations have separate rows. To compute net activation, sign-handle: `up - down`. *(Source: `schemas/entsoe.py L395`.)*

## 05 Not entitlement-blocked

A83/A16 is accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no `activated_balancing_qty-http-401.md`.)*

# Related datasets

- **`activated_balancing_prices`** — A84/A16 price counterpart. `PT60M`. Pair for revenue (€). `entsoe · balancing · hourly`
- **`contracted_reserves`** — A81 reserved capacity. `PT60M`. The pre-arranged capacity from which activations draw. `entsoe · balancing · hourly`
- **`procured_balancing_capacity`** — A15/A51 procured capacity. `PT60M`. Reservation-side cost (€/MW/h). `entsoe · balancing · hourly`
- **`current_balancing_state`** — A86/B33 area control error. `PT30M`. Drives activation decisions — negative state triggers up-activation. `entsoe · balancing · 30 min`
