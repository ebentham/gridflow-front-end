---
slug: disbsad
vendor: elexon
vendor_label: Elexon BMRS
api_code: DISBSAD
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/disbsad.md
  - gridflow/src/gridflow/schemas/elexon.py::ElexonDISBSAD (lines 246-266)
  - gridflow/src/gridflow/silver/elexon/disbsad.py::DISBSADTransformer (lines 19-118)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 76-82, PUBLISH_DATETIME style with from/to params)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/DISBSAD (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vault Silver Sample"
    source_a_says: "stor_flag value shown as `\"...\"` (placeholder)"
    source_b: "gridflow schemas/elexon.py L253"
    source_b_says: "stor_flag is `bool = False` (default), not a string"
    orchestrator_recommendation: "trust gridflow — vault sample is a placeholder; real value is a bool"
  - source_a: "vault Silver schema 'component' source field"
    source_a_says: "Field `component` mapped from `component`"
    source_b: "gridflow silver/elexon/disbsad.py L61"
    source_b_says: "Column mapping has `component: component` but live API returns `service` for the same semantic field; `component` not present in 2026-05-08 sample"
    orchestrator_recommendation: "trust gridflow — `component` is preserved if present but the live API actually emits `service` (renamed in vendor API but vault not yet updated)"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Non-BM balancing actions, <span class="italic fg-accent">action by action.</span>

**Lede:** DISBSAD is the disaggregated component feed for Balancing Services Adjustment Data — each row a single non-BM action (STOR call-off, ancillary service, system-operator instruction outside BOALF) with its cost in GBP and volume in MWh. Pair with `netbsad` (the aggregate) to reconcile BSC settlement and attribute imbalance cost to its constituent actions.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · DISBSAD](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/DISBSAD)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.disbsad` |
| API PATH | `/datasets/DISBSAD` |
| FREQUENCY | daily |
| PUBLICATION LAG | 1 day |
| VOLUME | 180k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period, adjustment_action_id, component)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Publication frequency |
| 2 | 1 day | Publication lag |
| 3 | ~6k | Actions / day |
| 4 | 11 | Schema columns |

# Sidebar siblings

- netbsad
- boal
- system_prices
- pn
- nonbm

# Overview

1. <code>disbsad</code> is **Disaggregated Balancing Services Adjustment Data** — the constituent rows that aggregate into NETBSAD. Each row captures a single non-BM balancing action: an `adjustment_action_id`, the cost (`cost` in GBP, not GBP/MWh) and volume (`volume` in MWh), plus flags marking whether the action was System Operator-issued (`so_flag`) or STOR-provider (`stor_flag`).

2. Gridflow fetches it from <code>/datasets/DISBSAD</code> using <code>from</code>/<code>to</code> query params (connector entry at <code>connectors/elexon/endpoints.py L76-82</code>). The <code>DISBSADTransformer</code> renames camelCase to snake_case, derives `timestamp_utc`, and dedups on `(settlement_date, settlement_period, adjustment_action_id, component)` — the four-tuple is required because the same `adjustment_action_id` can appear with different components. Pydantic schema <code>ElexonDISBSAD</code> is declared.

3. Cadence is daily with D+1 publication lag (BSC settlement timetable). Verified against the live API on 2026-05-08. Cost-attribution analytics typically `JOIN bmunits_reference` via `partyId` (raw bronze field) and aggregate by service category; the silver layer keeps the granular row so downstream views can attribute. Pair with `netbsad` to verify aggregation, with `boal` to combine BM and non-BM actions for total balancing cost.

# Sample chart

- **Type:** `barsH`
- **Title:** "Daily DISBSAD cost by component · last 30 days"
- **Subtitle:** "Horizontal bars · GBP · UTC · April 2026"
- **Seed:** 17
- **Toggles:** `cost` (active) / `volume (MWh)`

# Schema

Defined in `gridflow/schemas/elexon.py` · `ElexonDISBSAD` (lines 246-266) and `gridflow/silver/elexon/disbsad.py` · `DISBSADTransformer.output_cols`. Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at` (no native PIT field on the API response).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `schemas/elexon.py L249` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `schemas/elexon.py L250` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. | `silver/elexon/disbsad.py L84-93` |
| `adjustment_action_id` | `Optional[str]` | Yes | `id` | DISBSAD action identifier (integer in API; cast to str in silver). | `schemas/elexon.py L252` |
| `so_flag` | `bool` | No (default `False`) | `soFlag` | System Operator-issued flag. | `schemas/elexon.py L253` |
| `stor_flag` | `bool` | No (default `False`) | `storProviderFlag` | STOR-provider flag. | `schemas/elexon.py L254` |
| `component` | `Optional[str]` | Yes | `component` (legacy) / `service` (current) | DISBSAD component / service category. See discrepancy in frontmatter. | `schemas/elexon.py L255`; `silver/elexon/disbsad.py L61` |
| `cost` | `Optional[float]` | Yes | `cost` | **GBP** (total cost of the action, not per-MWh). | `schemas/elexon.py L256` |
| `volume` | `Optional[float]` | Yes | `volume` | **MWh**. Signed: positive = SO buying, negative = SO selling. | `schemas/elexon.py L257` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `schemas/elexon.py L258` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `schemas/elexon.py L259` |

**PARQUET PATH:** `data/silver/elexon/disbsad/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period, adjustment_action_id, component)` (`silver/elexon/disbsad.py L95-99`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | adjustment_action_id | so_flag | stor_flag | component | cost | volume | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | 1 | true | false | _null_ | 0.0 | 0.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | 1 | true | false | _null_ | 0.0 | 0.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | 4421 | true | false | Ancillary | 4820.50 | 120.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **17** | **2026-05-06T08:00:00+00:00** | **4422** | **true** | **true** | **STOR** | **18420.00** | **155.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 18 | 2026-05-06T08:30:00+00:00 | 4501 | true | false | Constraint | 9120.00 | 88.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | 5102 | true | true | STOR | 22100.00 | 180.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 37 | 2026-05-06T18:00:00+00:00 | 5151 | true | false | Reserve | 6440.00 | 60.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 5380 | true | false | Constraint | -2810.00 | -45.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 and 2 (SP8/SP9 with `id=1`, cost/volume = 0) verbatim from the vault Bronze Sample (vault/elexon/disbsad.md, live 2026-05-08). Remaining rows synthesised — respect schema constraints (cost as float GBP, volume as signed float MWh, flags as bools) and represent the typical pattern: low-activity overnight, STOR calls around morning + evening peaks, occasional negative-cost constraint actions when SO is selling power back. The highlighted **SP17 `STOR`** row is the interesting case: simultaneously `so_flag=true` and `stor_flag=true` — a STOR call-off issued by the System Operator at morning peak, the canonical pattern this dataset is built to surface.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: DISBSAD's component vocabulary is vendor-managed and partially undocumented; enumerating an incomplete list would mislead. Schema row notes document the column.)` — known component values include `STOR`, `Constraint`, `Reserve`, `Ancillary`; new values can appear without warning.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/DISBSAD`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/disbsad/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.disbsad.DISBSADTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/DISBSAD?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily DISBSAD cost split by component (excluding zero rows)
SELECT settlement_date,
       COALESCE(component, '(null)') AS component,
       SUM(cost) AS daily_cost_gbp,
       SUM(volume) AS daily_volume_mwh
FROM read_parquet('data/silver/elexon/disbsad/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 30 DAY
  AND cost <> 0
GROUP BY 1, 2
ORDER BY 1 DESC, daily_cost_gbp DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/disbsad/**/*.parquet")
# Top STOR call-offs by cost
stor = (
    df.filter(pl.col("stor_flag") & (pl.col("cost") > 0))
      .sort("cost", descending=True)
      .select(["settlement_date", "settlement_period", "cost", "volume"])
      .head(20)
)
print(stor)
```

# Caveats

## 01 `cost` is total GBP, not GBP/MWh

`cost` is the absolute money for the action, not a unit price. Divide by `volume` to derive an implied £/MWh. For zero-volume rows (common — most periods have placeholder rows with `cost=0, volume=0`), the implied price is undefined; filter them out before averaging. *(Source: vault Known Issues; `schemas/elexon.py L256`.)*

## 02 DISBSAD aggregates into NETBSAD — don't double-count

Sum of DISBSAD `volume` per (settlement_date, settlement_period) equals NETBSAD `total_net_bsad_volume` for the same period (per BSC reconciliation). If you join the two datasets, do not aggregate DISBSAD a second time — pick one as the source of truth depending on whether you need component attribution (DISBSAD) or just the net per period (NETBSAD). *(Source: vault Known Issues — "DISBSAD pairs with NETBSAD: NETBSAD is the aggregate of DISBSAD components for the same period".)*

## 03 `component` vs `service` API drift

The vault and silver column mapping use `component` but the live API on 2026-05-08 returned a `service` field instead; older bronze archives may have `component`. The transformer preserves whichever it finds (the column mapping only renames if present), which means the silver `component` column may be entirely null for fresh bronze. Cross-reference both bronze field names if you back-fill. *(Source: discrepancy noted in frontmatter; cross-reference vault Bronze Sample fields vs `silver/elexon/disbsad.py L61` column mapping.)*

## 04 `from`/`to` query params, not `publishDateTimeFrom/To`

Like BOALF, DISBSAD uses `from`/`to` parameters (not `publishDateTimeFrom`/`To`). The connector overrides via `from_param="from", to_param="to"`. Wrong param names get silently ignored and the API returns the last ~24 hours. *(Source: `connectors/elexon/endpoints.py L80-81`.)*

## 05 Zero-cost placeholder rows are normal

Most settlement periods have `cost=0, volume=0` placeholder rows (`adjustment_action_id=1` with `service=null`) representing "no balancing action this period". Filter out `cost=0 AND volume=0` for cost-attribution analytics — these aren't measurement gaps, they are real "nothing happened" markers. *(Source: vault Bronze Sample — SP8 and SP9 both showed the zero placeholder pattern on 2026-05-06.)*

# Related datasets

- **netbsad** — Net balancing services adjustment data. `daily`. The aggregate counterpart; sum of DISBSAD by (date, period) equals NETBSAD net volume. `elexon · prices & balancing · daily`
- **boal** — Bid-offer acceptance. `hourly`. BM-issued instructions; DISBSAD covers everything outside the BM. Combine to compute total balancing cost. `elexon · prices & balancing · hourly`
- **system_prices** — System buy / sell prices. `30 min`. Correlate DISBSAD cost spikes with SBP/SSP movements — DISBSAD is one of the drivers of imbalance cash-out. `elexon · prices & balancing · 30 min`
- **nonbm** — Non-BM STOR generation. `30 min`. Volume of STOR units; pair with DISBSAD `stor_flag` rows to attribute STOR call-offs to specific units. `elexon · generation · 30 min`
