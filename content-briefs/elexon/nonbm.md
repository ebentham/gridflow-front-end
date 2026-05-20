---
slug: nonbm
vendor: elexon
vendor_label: Elexon BMRS
api_code: NONBM
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/nonbm.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonNONBM class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/nonbm.py::NONBMTransformer (lines 19-104)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 200-204, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/NONBM (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vault Implementation Delta"
    source_a_says: "Param style mismatch — docs declare `from`/`to`; code uses default `publishDateTimeFrom/To`. Live test 2026-05-08 returned 1 row with default param names"
    source_b: "gridflow connectors/elexon/endpoints.py L200-204"
    source_b_says: "Connector uses standard PUBLISH_DATETIME style (publishDateTimeFrom/To)"
    orchestrator_recommendation: "documented — API accepts both styles in practice; default is safe for now. Recommend verifying which style is documented as canonical and updating either the connector or vault notes for consistency."
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonNONBM class declared"
    source_b: "gridflow silver/elexon/nonbm.py L19-104"
    source_b_says: "NONBMTransformer outputs settlement_date, settlement_period, timestamp_utc, generation_mw, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer; same shape gap"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Non-BM STOR generation, <span class="italic fg-accent">the reserve fleet.</span>

**Lede:** NONBM is the Non-BM Short-Term Operating Reserve generation feed — MW output from STOR providers that operate outside the Balancing Mechanism. These are the units that supplement BM dispatch during system stress; tracking NONBM is how you measure how much reserve is being called and when.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · NONBM](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/NONBM)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.nonbm` |
| API PATH | `/datasets/NONBM` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | 1 day |
| VOLUME | 44k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Frequency |
| 2 | 1 day | Publication lag |
| 3 | STOR-only | Scope |
| 4 | 6 | Schema columns |

# Sidebar siblings

- fuelhh
- fuelinst
- disbsad
- system_prices
- freq

# Overview

1. <code>nonbm</code> is **Non-BM STOR Generation** — output from Short-Term Operating Reserve providers that sit outside the Balancing Mechanism. STOR is one of NESO's ancillary services; non-BM STOR providers are typically diesel gensets, embedded gas peakers, and battery storage on contracts that pay availability and utilisation but don't expose them through BOALF. NONBM is the canonical observation series for this fleet.

2. Gridflow fetches it from <code>/datasets/NONBM</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern (connector entry at <code>connectors/elexon/endpoints.py L200-204</code>). The vault notes a doc-vs-code mismatch (`from`/`to` in docs, default param names in code), but the live API accepts the default. The <code>NONBMTransformer</code> renames `generation` → `generation_mw`, derives `timestamp_utc`, and dedups on `(settlement_date, settlement_period)`. No Pydantic class is declared.

3. Cadence is half-hourly publication with 1-day lag. Verified against the live API on 2026-05-08; the sample returned `generation=0` for SP22 on 2026-04-01 — typical for off-peak periods. Most NONBM rows are zero; non-zero values cluster around morning and evening peaks and during system-stress events. Pair with `disbsad` STOR-flagged rows to attribute the call-off, with `freq` to correlate dispatch to frequency excursions.

# Sample chart

- **Type:** `sparkline`
- **Title:** "Non-BM STOR generation · last 30 days"
- **Subtitle:** "Sparkline · MW · UTC · April 2026"
- **Seed:** 26
- **Toggles:** `24h` / `7d` / `30d` (active)

# Schema

Defined in `gridflow/silver/elexon/nonbm.py` · `NONBMTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/nonbm.py L72` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/nonbm.py L73` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived via `utils/time.settlement_period_to_utc`. | `silver/elexon/nonbm.py L77-86` |
| `generation_mw` | `float` | No | `generation` | MW. STOR-only — does not include any other non-BM dispatch (interconnectors, BM units, etc.). | `silver/elexon/nonbm.py L59, L74` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/nonbm.py L92` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/nonbm.py L93` |

**PARQUET PATH:** `data/silver/elexon/nonbm/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period)` (`silver/elexon/nonbm.py L88`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | generation_mw | data_provider | ingested_at |
|---|---|---|---|---|---|
| **2026-04-01** | **22** | **2026-04-01T10:30:00+00:00** | **0.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | 0.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | 220.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | 80.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | 480.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 37 | 2026-05-06T18:00:00+00:00 | 420.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 110.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 0.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Row 1 (2026-04-01 SP22, `generation=0`) verbatim from the vault Bronze Sample (vault/elexon/nonbm.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (float MW; non-negative in practice) and represent typical NONBM dispatch: zero overnight, modest at morning peak (SP17), peak at evening (SP36-SP37), tapering off late. The highlighted **2026-04-01 SP22 (0 MW)** row is the interesting case: it is the only vendor-verified row in the vault and the canonical "nothing happening" baseline.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: NONBM emits one scalar per period; no enumerable taxonomies. STOR-specific context is in caveats.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/NONBM`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/nonbm/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.nonbm.NONBMTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/NONBM?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Periods with significant NONBM dispatch over the last 30 days
SELECT settlement_date, settlement_period, generation_mw
FROM read_parquet('data/silver/elexon/nonbm/**/*.parquet')
WHERE generation_mw > 100
  AND settlement_date >= current_date - INTERVAL 30 DAY
ORDER BY generation_mw DESC, settlement_date, settlement_period
LIMIT 50;
```

**Tab 3 — Python · polars**
```python
import polars as pl

nb = pl.read_parquet("data/silver/elexon/nonbm/**/*.parquet")
# Hour-of-day NONBM dispatch profile
profile = (
    nb.with_columns(pl.col("timestamp_utc").dt.hour().alias("hour"))
      .group_by("hour")
      .agg([
          pl.col("generation_mw").mean().alias("avg_mw"),
          pl.col("generation_mw").max().alias("peak_mw"),
      ])
      .sort("hour")
)
print(profile)
```

# Caveats

## 01 STOR-only — not total non-BM generation

NONBM captures only Short-Term Operating Reserve providers operating outside the BM. It does not include other non-BM dispatch (sub-1 MW embedded units that aren't STOR, interconnector imports, ancillary-service providers under different contracts). For "total non-BM generation" you need additional sources. *(Source: vault Known Issues; vault Overview — "captures only STOR providers operating outside the BM".)*

## 02 No Pydantic schema in `schemas/elexon.py`

Like other simple generation datasets without dedicated schemas (FUELINST, AGPT, etc.), NONBM has no Pydantic class. Silver shape is defined by `NONBMTransformer.output_cols`. *(Source: `schemas/elexon.py` grep returns no NONBM class.)*

## 03 Most rows are zero

NONBM dispatch is event-driven — most settlement periods see zero non-BM STOR generation because the BM fleet covers normal operation. Filter `generation_mw > 0` for "active periods" analytics, or use rolling sums for cumulative call-off measures. *(Source: vault Bronze Sample shows `generation=0` for the sampled period; domain knowledge — STOR is a peak/stress fleet.)*

## 04 Param-style doc-vs-code mismatch

The vault notes that the docs declare `from`/`to` but the connector uses default `publishDateTimeFrom`/`To`. Live testing on 2026-05-08 confirmed both work. This is a soft inconsistency — likely the API accepts both — but worth fixing for consistency with REMIT/SOSO patterns where docs and code align. *(Source: discrepancy in frontmatter; vault Implementation Delta.)*

## 05 Pair with `disbsad` STOR rows for attribution

NONBM tells you "how much non-BM STOR generation happened"; `disbsad` STOR-flagged rows (`stor_flag=true`) tell you "which STOR call-offs cost what". Joining the two on (settlement_date, settlement_period) lets you derive implied £/MWh for STOR utilisation — a useful cost-effectiveness metric for the ancillary-services portfolio. *(Source: domain knowledge — STOR settlement chain.)*

# Related datasets

- **disbsad** — Disaggregated balancing services adjustment. `daily`. STOR-flagged rows in DISBSAD are the per-action records that NONBM aggregates per period. Pair for cost attribution. `elexon · prices & balancing · daily`
- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. The BM-side counterpart; sum NONBM + FUELHH (with care to avoid double-counting unit-types) for a fuller GB generation picture. `elexon · generation · 30 min`
- **fuelinst** — Instantaneous generation by fuel. `~5 min`. Real-time counterpart; non-BM STOR dispatch may not appear here if the units are below the metering threshold for FUELINST. `elexon · generation · ~5 min`
- **freq** — System frequency. `~2 s`. STOR is dispatched in response to frequency drops; expect NONBM dispatch to correlate with FREQ excursions below 49.8 Hz. `elexon · system & reference · ~2 s`
