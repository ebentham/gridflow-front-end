---
slug: methane_content
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/MethaneContent
last_verified: 2026-05-08
endpoint_removed: 2026-05-19
sources_consulted:
  - vault/entsog/methane_content.md (vault `removed: 2026-05-19`)
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["methane_content"] (line 108) — still registered for historical bronze
  - .planning/reconciliation/entsog/03-methane-content-http-404.md (closed 2026-05-19 — endpoint withdrawn)
discrepancies_found:
  - source_a: "live ENTSO-G API"
    source_a_says: "HTTP 404 from current endpoint /operationalData?indicator=Methane%20Content"
    source_b: "vault/entsog/methane_content.md frontmatter `removed: 2026-05-19`"
    source_b_says: "Vendor withdrew the endpoint; historic bronze remains queryable"
    orchestrator_recommendation: "Surface in lede + Caveats #01. Use historic data for backtests."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Methane volume fraction, <span class="italic fg-accent">historic-only.</span>

**Lede:** Methane volume fraction of delivered gas per operator-point-direction — historically the canonical CH4-purity indicator. Endpoint withdrawn by vendor in 2026; archived data only.

**Verified line:** Vault verified 2026-05-08 · endpoint withdrawn 2026-05-19 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/) (404)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.methane_content` (historic) |
| API PATH | `/api/v1/operationalData?indicator=Methane%20Content` (404 — withdrawn) |
| FREQUENCY | daily (gas day) |
| PUBLICATION LAG | as published |
| VOLUME | historic |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency (historic) |
| 2 | 404 | Live HTTP status (withdrawn) |
| 3 | historic | Replay-only |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- gcv
- wobbe_index
- hydrogen_content
- oxygen_content
- physical_flows

# Sample chart

- **Type:** `sparkline`
- **Title:** "Methane content at GB points · 12-month history"
- **Subtitle:** "Sparkline · volume fraction (%) · pre-2026-05 archive"
- **Seed:** 65
- **Toggles:** `1y` (active) / `3y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derived columns from the live response when the endpoint was alive. Schema below reflects the vault-documented shape from pre-removal data.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Gas-day window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Was `"Methane Content"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction. | dynamic |
| `unit` | `str` | Yes | `unit` | Volume fraction (`"%"` or `"mol%"`). | dynamic |
| `value` | `float` | Yes | `value` | CH4 fraction (typically 85-95% for natural gas; lower for biomethane blends). | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/methane_content/year=YYYY/month=MM/` (historic)
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | point_key | point_label | direction_key | unit | value |
|---|---|---|---|---|---|
| 2025-12-15T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | mol% | 91.34 |
| 2025-11-20T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | exit | mol% | 90.82 |
| **2025-10-15T04:00:00+00:00** | **ITP-00495** | **Moffat (IE)** | **entry** | **mol%** | **92.17** |
| 2025-09-10T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | mol% | 91.55 |
| 2025-08-05T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | exit | mol% | 91.02 |
| 2025-07-22T04:00:00+00:00 | ITP-00007 | Überackern SUDAL | entry | mol% | 95.40 |
| 2025-06-15T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | mol% | 91.30 |
| 2025-05-08T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | mol% | 91.20 |

**Sources:** Synthesised — methane content for North Sea pipeline gas typically clusters 91-92 mol% (the remainder being ethane, propane, nitrogen, CO2). Highlighted row is Moffat IE entry at 92.17 mol% — slightly higher than Bacton reflects different upstream blend composition. Continental gas at Überackern (95.4 mol%) demonstrates the wider range of European gas qualities.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Methane%20Content` (HTTP 404 since 2026-05-19)
- AUTH: None (public — when endpoint was alive).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/methane_content/<year>/<month>/<day>/raw_<uuid>.json` (historic)
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `MethaneContentTransformer`)

**Tab 1 — Example URL**
```
# Historic only — returns HTTP 404 after 2026-05-19
https://transparency.entsog.eu/api/v1/operationalData?from=2025-12-01&to=2025-12-31&timeZone=UCT&indicator=Methane%20Content&periodType=day&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Average methane content per point across 2025
SELECT point_key, point_label,
       AVG(value) AS avg_methane_pct,
       MIN(value) AS min_methane_pct,
       MAX(value) AS max_methane_pct
FROM read_parquet('data/silver/entsog/methane_content/**/*.parquet')
WHERE timestamp_utc BETWEEN '2025-01-01' AND '2026-01-01'
GROUP BY 1, 2
ORDER BY avg_methane_pct DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/methane_content/**/*.parquet")
# Daily GB CH4 spread (interchangeability check across GB entry points)
spread = (
    df.filter(pl.col("operator_key").str.starts_with("UK-TSO-"))
      .group_by("timestamp_utc")
      .agg((pl.col("value").max() - pl.col("value").min()).alias("daily_spread_mol_pct"))
      .sort("timestamp_utc")
      .tail(30)
)
print(spread)
```

# Caveats

## 01 Endpoint withdrawn by vendor (2026-05-19)

Live API returns HTTP 404. Historic data remains queryable from bronze archive. *(Source: `.planning/reconciliation/entsog/03-methane-content-http-404.md` closed 2026-05-19; vault frontmatter `removed: 2026-05-19`.)*

## 02 GCV is the surviving energy-density proxy

Since methane fraction maps directly to energy density, use `gcv` (still live) as the proxy. Methane share can be back-calculated approximately as `gcv / 11.05` for North Sea blends. *(Source: gas-physics convention; vault Modelling notes.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

When the endpoint was live, connector sent `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Historic bronze accessible via connector replay

The connector registration is retained in `OPERATIONAL_INDICATORS` (`endpoints.py L108`) for replay/backtest workflows. *(Source: `connectors/entsog/client.py L109-115`.)*

## 05 Sister gas-quality endpoints also withdrawn

`hydrogen_content` and `oxygen_content` were withdrawn the same day (2026-05-19). *(Source: `.planning/reconciliation/entsog/0[1-4]-*-http-404.md`.)*

# Related datasets

- **`hydrogen_content`** — Hydrogen fraction (also withdrawn 2026-05-19). `daily`. Historic-only sister indicator. *entsog · gas-quality · historic*
- **`oxygen_content`** — Oxygen fraction (also withdrawn 2026-05-19). `daily`. Historic-only sister indicator. *entsog · gas-quality · historic*
- **`gcv`** — Gross calorific value (still live). `daily`. Surviving energy-density proxy. *entsog · gas-quality · daily*
- **`wobbe_index`** — Wobbe index (still live). `daily`. Surviving interchangeability indicator. *entsog · gas-quality · daily*
