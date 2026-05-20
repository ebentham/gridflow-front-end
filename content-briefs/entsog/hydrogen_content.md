---
slug: hydrogen_content
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/HydrogenContent
last_verified: 2026-05-08
endpoint_removed: 2026-05-19
sources_consulted:
  - vault/entsog/hydrogen_content.md (vault `removed: 2026-05-19`)
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["hydrogen_content"] (line 109) — still registered for historical bronze
  - .planning/reconciliation/entsog/01-hydrogen-content-http-404.md (closed 2026-05-19 — endpoint withdrawn)
discrepancies_found:
  - source_a: "live ENTSO-G API"
    source_a_says: "HTTP 404 from current endpoint /operationalData?indicator=Hydrogen%20Content"
    source_b: "vault/entsog/hydrogen_content.md frontmatter `removed: 2026-05-19`"
    source_b_says: "Vendor withdrew the endpoint; historic bronze remains queryable"
    orchestrator_recommendation: "Surface in lede + Caveats #01. Use historic data for backtests; the connector registration is retained for replay."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Hydrogen volume fraction, <span class="italic fg-accent">historic-only.</span>

**Lede:** Hydrogen volume fraction of delivered gas per operator-point-direction — historically the canonical H2-blending indicator. Endpoint withdrawn by vendor in 2026; archived data only.

**Verified line:** Vault verified 2026-05-08 · endpoint withdrawn 2026-05-19 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/) (404)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.hydrogen_content` (historic) |
| API PATH | `/api/v1/operationalData?indicator=Hydrogen%20Content` (404 — withdrawn) |
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
- methane_content
- oxygen_content
- physical_flows

# Sample chart

- **Type:** `sparkline`
- **Title:** "Hydrogen content at GB points · 12-month history"
- **Subtitle:** "Sparkline · volume fraction (%) · pre-2026-05 archive"
- **Seed:** 63
- **Toggles:** `1y` (active) / `3y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derived columns from the live response when the endpoint was alive. Schema below reflects the vault-documented shape from pre-removal data.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Gas-day window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Was `"Hydrogen Content"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction. | dynamic |
| `unit` | `str` | Yes | `unit` | Volume fraction (typically `"%"` or `"mol%"`). | dynamic |
| `value` | `float` | Yes | `value` | H2 fraction (typically 0.0-0.1% for historic data; rising with blending trials). | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/hydrogen_content/year=YYYY/month=MM/` (historic)
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | point_key | point_label | direction_key | unit | value |
|---|---|---|---|---|---|
| 2025-12-15T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | mol% | 0.012 |
| 2025-11-20T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | exit | mol% | 0.018 |
| **2025-10-15T04:00:00+00:00** | **ITP-00007** | **Überackern SUDAL** | **entry** | **mol%** | **0.082** |
| 2025-09-10T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | mol% | 0.015 |
| 2025-08-05T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | exit | mol% | 0.016 |
| 2025-07-22T04:00:00+00:00 | ITP-00495 | Moffat (IE) | entry | mol% | 0.011 |
| 2025-06-15T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | mol% | 0.013 |
| 2025-05-08T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | mol% | 0.014 |

**Sources:** Synthesised from the pre-2026-05 archive shape documented in vault `hydrogen_content.md`. All rows are illustrative — the live endpoint returns 404 since 2026-05-19. Highlighted row is Überackern SUDAL (DE-AT interconnection) at 0.08 mol% — significantly higher than typical North Sea gas, reflecting early continental hydrogen-blending trials. GB-relevant points stayed below 0.02 mol% in the archive window.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Hydrogen%20Content` (HTTP 404 since 2026-05-19)
- AUTH: None (public — when endpoint was alive).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/hydrogen_content/<year>/<month>/<day>/raw_<uuid>.json` (historic)
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `HydrogenContentTransformer`)

**Tab 1 — Example URL**
```
# Historic only — returns HTTP 404 after 2026-05-19
https://transparency.entsog.eu/api/v1/operationalData?from=2025-12-01&to=2025-12-31&timeZone=UCT&indicator=Hydrogen%20Content&periodType=day&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Hydrogen content trend at GB points across the historic archive
SELECT date_trunc('month', timestamp_utc) AS month,
       AVG(value) AS avg_h2_fraction
FROM read_parquet('data/silver/entsog/hydrogen_content/**/*.parquet')
WHERE operator_key LIKE 'UK-TSO%'
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/hydrogen_content/**/*.parquet")
# Year-over-year hydrogen trend per point
yoy = (
    df.with_columns(pl.col("timestamp_utc").dt.year().alias("year"))
      .group_by(["year", "point_key"])
      .agg(pl.col("value").mean().alias("avg_h2"))
      .sort(["point_key", "year"])
)
print(yoy)
```

# Caveats

## 01 Endpoint withdrawn by vendor (2026-05-19)

Live API returns HTTP 404. Historic data remains queryable from bronze archive. *(Source: `.planning/reconciliation/entsog/01-hydrogen-content-http-404.md` closed 2026-05-19; vault frontmatter `removed: 2026-05-19`.)*

## 02 Pre-removal H2 fractions were small

Historic GB values typically <0.02 mol%; the indicator was added in anticipation of blending mandates but never reached production scale in GB. *(Source: vault Modelling notes; domain knowledge.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

When the endpoint was live, connector sent `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Historic bronze accessible via connector replay

The connector registration is retained in `OPERATIONAL_INDICATORS` (`endpoints.py L109`) for replay/backtest workflows; live fetches will now bronze the 404 response (empty) via the standard short-circuit. *(Source: `connectors/entsog/client.py L109-115`.)*

## 05 Sister gas-quality endpoints also withdrawn

`methane_content` and `oxygen_content` were withdrawn the same day (2026-05-19). `gcv` and `wobbe_index` remain the surviving gas-quality surfaces. *(Source: `.planning/reconciliation/entsog/0[1-4]-*-http-404.md`.)*

# Related datasets

- **`methane_content`** — Methane fraction (also withdrawn 2026-05-19). `daily`. Historic-only sister indicator. *entsog · gas-quality · historic*
- **`oxygen_content`** — Oxygen fraction (also withdrawn 2026-05-19). `daily`. Historic-only sister indicator. *entsog · gas-quality · historic*
- **`gcv`** — Gross calorific value (still live). `daily`. Surviving gas-quality surface. *entsog · gas-quality · daily*
- **`wobbe_index`** — Wobbe index (still live). `daily`. Surviving gas-quality surface. *entsog · gas-quality · daily*
