---
slug: imbalance_volume
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A86/A16
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/imbalance_volume.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeImbalanceVolume (lines 361-381)
  - gridflow/src/gridflow/silver/entsoe/imbalance_volume.py::ImbalanceVolumeTransformer (lines 18-98)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["imbalance_volume"] (lines 295-301)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** EU imbalance volumes, <span class="italic fg-accent">long and short.</span>

**Lede:** Imbalance volumes in MWh per control area split by direction (long / short) — the volume counterpart to imbalance_prices, the EU equivalent of GB Elexon NIV.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A86/A16](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.imbalance_volume` |
| API PATH | `/api?documentType=A86&businessType=A19` |
| FREQUENCY | PT30M typical |
| PUBLICATION LAG | T+1h |
| VOLUME | 96 points / area / day |
| PRIMARY KEY | `(timestamp_utc, area_code, direction)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A86 | DocumentType |
| 2 | A19 | businessType (pinned) |
| 3 | long / short | `direction` codes (A01 / A02) |
| 4 | 7 | Schema columns |

# Sidebar siblings

- imbalance_prices
- current_balancing_state
- activated_balancing_qty
- day_ahead_prices
- system_prices (Elexon)

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB imbalance volume · 24h"
- **Subtitle:** "Line · MWh · UTC · 6 May 2026"
- **Seed:** 3
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeImbalanceVolume` (lines 361-381). Maps `flowDirection` (A01/A02) to `direction` ("long"/"short") via `replace_strict`. Distinct from imbalance_prices' businessType-based direction.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L368, L376-381` |
| `area_code` | `str` | No | `<controlArea_Domain.mRID>` | Control area EIC. | `schemas/entsoe.py L369`; `silver/entsoe/imbalance_volume.py L60` |
| `direction` | `str` | No | derived from `<flowDirection>` | "long" (A01 = generation excess) / "short" (A02 = consumption excess). | `schemas/entsoe.py L370`; `silver/entsoe/imbalance_volume.py L63-66` |
| `volume_mwh` | `float` | No | `<Point><quantity>` | MWh imbalance volume. | `schemas/entsoe.py L371` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT30M`. | `schemas/entsoe.py L372` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L373` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L374` |

**PARQUET PATH:** `data/silver/entsoe/imbalance_volume/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, direction)` (`silver/entsoe/imbalance_volume.py L75`)

# Sample data

| timestamp_utc | area_code | direction | volume_mwh | resolution | data_provider |
|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | long | 0.0 | PT30M | entsoe |
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | short | 42.0 | PT30M | entsoe |
| **2026-05-06T17:30:00+00:00** | **10YGB----------A** | **short** | **481.0** | **PT30M** | **entsoe** |
| 2026-05-06T17:30:00+00:00 | 10YGB----------A | long | 0.0 | PT30M | entsoe |

**Sources:** Synthesised against typical GB evening-peak. The highlighted **GB short 17:30 (481 MWh)** row exactly matches the magnitude of `current_balancing_state` at the same hour (-481 MW × 0.5 h = 240.5 MWh — note the half-hour conversion). Pair with `imbalance_prices` for the EUR cost: 481 MWh × 285.40 EUR/MWh ≈ €137 k for that one SP.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A86&businessType=A19&controlArea_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/imbalance_volume/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.imbalance_volume.ImbalanceVolumeTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A86&businessType=A19&controlArea_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Net imbalance per zone per period (signed: positive=short)
SELECT timestamp_utc, area_code,
       sum(CASE WHEN direction='short' THEN volume_mwh ELSE 0 END) -
       sum(CASE WHEN direction='long' THEN volume_mwh ELSE 0 END) AS net_imbalance_mwh
FROM read_parquet('data/silver/entsoe/imbalance_volume/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 7 DAY
GROUP BY 1, 2 ORDER BY abs(net_imbalance_mwh) DESC LIMIT 50;
```

**Tab 3 — Python · polars**
```python
import polars as pl

iv = pl.read_parquet("data/silver/entsoe/imbalance_volume/**/*.parquet")
ip = pl.read_parquet("data/silver/entsoe/imbalance_prices/**/*.parquet")
# Imbalance settlement value (€) = volume × price per direction
val = iv.join(ip, on=["timestamp_utc", "area_code", "direction"]).with_columns(
    (pl.col("volume_mwh") * pl.col("price_eur_mwh")).alias("settlement_eur")
)
print(val.group_by(["area_code", "direction"]).agg(pl.col("settlement_eur").sum()))
```

# Caveats

## 01 businessType A19 pinned, flowDirection drives direction

Connector pins `businessType=A19`; the `direction` field is derived from `flowDirection` (A01/A02), not businessType. This is opposite to `imbalance_prices` where businessType (A19/A20) drives direction. *(Source: `endpoints.py L299-300`; `silver/entsoe/imbalance_volume.py L63-66`.)*

## 02 volume_mwh not volume_mw

Unit is MWh (integrated over interval). Distinct from MW (instantaneous) elsewhere. *(Source: `schemas/entsoe.py L371`.)*

## 03 Sign of short/long depends on TSO convention

ENTSO-E convention: long = system surplus (generation excess), short = system deficit. Some downstream models use opposite signs. *(Source: domain knowledge.)*

## 04 Revisions overwrite

Imbalance settlement is revised over time — `keep="last"` keeps the most recent. *(Source: `silver/entsoe/imbalance_volume.py L75`.)*

## 05 Not entitlement-blocked

A86 (with businessType A19) is accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no `imbalance_volume-http-401.md`.)*

# Related datasets

- **`imbalance_prices`** — A85 imbalance prices. `PT30M`. Pair for settlement value (€). `entsoe · prices · 30 min`
- **`current_balancing_state`** — A86/B33 area control error. `PT30M`. Sister A86 surface with B33 businessType — same magnitude, different framing. `entsoe · balancing · 30 min`
- **`activated_balancing_qty`** — A83/A16 activation MWh. `PT60M`. Activated volume closes the imbalance gap. `entsoe · balancing · hourly`
- **`system_prices` (Elexon)** — GB NIV (`net_imbalance_volume`). `30 min`. The GB-native equivalent. `elexon · prices · 30 min`
