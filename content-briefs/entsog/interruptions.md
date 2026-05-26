---
slug: interruptions
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: interruptions
last_verified: 2026-05-08
endpoint_removed: 2026-05-19
sources_consulted:
  - vault/entsog/interruptions.md (vault `removed: 2026-05-19` — vendor took endpoint down)
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["interruptions"] (lines 155-166) — still registered for historical bronze
  - .planning/reconciliation/entsog/02-interruptions-http-404.md (closed 2026-05-19 — endpoint withdrawn by vendor; vault flagged `removed`)
discrepancies_found:
  - source_a: "live ENTSO-G API"
    source_a_says: "HTTP 404 from current endpoint /interruptions"
    source_b: "vault/entsog/interruptions.md frontmatter `removed: 2026-05-19`"
    source_b_says: "Vendor withdrew the endpoint; historic bronze remains queryable but no new rows"
    orchestrator_recommendation: "Surface in lede + Caveats #01. Historic data still useful for backtests; the connector registration is retained for replay."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Pipeline interruption events, <span class="italic fg-accent">historic-only.</span>

**Lede:** Planned and unplanned capacity interruption events per point — historically the canonical record for outage attribution. Endpoint withdrawn by vendor in 2026; archived data only.

**Verified line:** Vault verified 2026-05-08 · endpoint withdrawn 2026-05-19 · [ENTSO-G Transparency · /interruptions](https://transparency.entsog.eu/) (404)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.interruptions` (historic) |
| API PATH | `/api/v1/interruptions` (404 — withdrawn) |
| FREQUENCY | event-driven (when interruptions occur) |
| PUBLICATION LAG | as published |
| VOLUME | varies (event-driven) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | event-driven | Cadence |
| 2 | 404 | Live HTTP status (withdrawn) |
| 3 | historic | Replay-only |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- physical_flows
- urgent_market_messages
- nominations
- firm_available
- interruptible_available

# Sample chart

- **Type:** `barsH`
- **Title:** "Interruption events per point · last 12 months (historic)"
- **Subtitle:** "Horizontal bars · count · pre-2026-05 archive"
- **Seed:** 31
- **Toggles:** `1y` (active) / `3y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derived columns from the live response when the endpoint was alive. Schema below reflects the vault-documented shape from pre-removal data.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `eventStart` (derived) | Event start, set via `_TIMESTAMP_PRIORITY` (`silver/entsog/generic.py L45-53`). | `silver/entsog/generic.py L118-120` |
| `event_start` / `event_stop` | `datetime[UTC]` | Yes | `eventStart` / `eventStop` | Outage window. | `silver/entsog/generic.py L114-116` |
| `operator_key` / `operator_label` | `str` | Yes | `operatorKey` / `operatorLabel` | TSO. | dynamic |
| `point_key` / `point_label` | `str` | Yes | `pointKey` / `pointLabel` | Connection-point. | dynamic |
| `direction_key` | `str` | Yes | `directionKey` | `"entry"` / `"exit"`. | dynamic |
| `interruption_type` | `str` | Yes | `interruptionType` | Planned / Unplanned / etc. | dynamic |
| `restoration_information` | `str` | Yes | `restorationInformation` | Free-text vendor field. | dynamic |
| `unavailable_capacity` | `float` | Yes | `unavailableCapacity` | Lost capacity in vendor unit. | `silver/entsog/generic.py L65-77` (`_NUMERIC_NAMES`) |
| `unit` | `str` | Yes | `unit` | Capacity unit (typically `"kWh/d"`). | dynamic |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/interruptions/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| event_start | event_stop | point_key | direction_key | interruption_type | unavailable_capacity | unit |
|---|---|---|---|---|---|---|
| 2025-12-10T06:00:00+00:00 | 2025-12-10T14:00:00+00:00 | ITP-00005 | exit | Planned | 50,000,000 | kWh/d |
| 2025-11-22T04:00:00+00:00 | 2025-11-23T04:00:00+00:00 | ITP-00207 | exit | Unplanned | 80,000,000 | kWh/d |
| **2025-10-15T06:00:00+00:00** | **2025-10-15T18:00:00+00:00** | **ITP-00207** | **entry** | **Planned** | **35,000,000** | **kWh/d** |
| 2025-09-08T06:00:00+00:00 | 2025-09-08T22:00:00+00:00 | ITP-00495 | entry | Planned | 20,000,000 | kWh/d |
| 2025-08-19T04:00:00+00:00 | 2025-08-20T04:00:00+00:00 | ITP-00005 | exit | Unplanned | 60,000,000 | kWh/d |
| 2025-07-03T06:00:00+00:00 | 2025-07-03T14:00:00+00:00 | ITP-00090 | entry | Planned | 15,000,000 | kWh/d |
| 2025-06-12T04:00:00+00:00 | 2025-06-12T08:00:00+00:00 | ITP-00005 | exit | Unplanned | 40,000,000 | kWh/d |
| 2025-04-25T06:00:00+00:00 | 2025-04-25T18:00:00+00:00 | ITP-00207 | exit | Planned | 70,000,000 | kWh/d |

**Sources:** Synthesised from the pre-2026-05 archive shape documented in vault `interruptions.md`. All rows are illustrative — the live endpoint returns 404 since 2026-05-19. Highlighted row is a BBL entry interruption — note the rare `entry` direction (most interruptions are at the dominant flow direction). Use historic bronze for backtests; do not attempt live fetches.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/interruptions` (HTTP 404 since 2026-05-19)
- AUTH: None (public — when endpoint was alive).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/interruptions/<year>/<month>/<day>/raw_<uuid>.json` (historic)
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `InterruptionsTransformer`)

**Tab 1 — Example URL**
```
# Historic only — returns HTTP 404 after 2026-05-19
https://transparency.entsog.eu/api/v1/interruptions?from=2025-01-01&to=2025-12-31&timeZone=UCT&periodType=day&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Most-interrupted points in 2025 (replay from historic bronze)
SELECT point_key, point_label,
       COUNT(*) AS events,
       SUM(unavailable_capacity) / 1e6 AS total_lost_gwh
FROM read_parquet('data/silver/entsog/interruptions/**/*.parquet')
WHERE event_start >= '2025-01-01'
  AND event_start <  '2026-01-01'
GROUP BY 1, 2
ORDER BY events DESC
LIMIT 10;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/interruptions/**/*.parquet")
# Planned vs Unplanned breakdown
breakdown = (
    df.group_by("interruption_type")
      .agg(pl.len().alias("events"))
      .sort("events", descending=True)
)
print(breakdown)
```

# Caveats

## 01 Endpoint withdrawn by vendor (2026-05-19)

Live API returns HTTP 404. Historic data remains queryable from bronze archive. Use `urgent_market_messages` as a partial replacement for unplanned-outage notifications. *(Source: `.planning/reconciliation/entsog/02-interruptions-http-404.md` closed 2026-05-19; vault frontmatter `removed: 2026-05-19`.)*

## 02 `timeZone=UCT` (vendor typo, intentional)

When the endpoint was live, connector sent `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17` `ENTSOG_TIMEZONE`.)*

## 03 Event-driven cadence

A `(point_key, direction_key)` may have 0 or many interruptions per gas day. Dedup on `id` (vendor concatenation). *(Source: `silver/entsog/generic.py L126-130`.)*

## 04 `interruption_type` is free-text-ish

Vendor values include `Planned`, `Unplanned`, and operator-specific variants. Map to a canonical taxonomy before aggregating. *(Source: vault Bronze sample field reference.)*

## 05 Historic replay is the canonical use

The connector entry remains in `ENDPOINTS` for replay/backtest workflows; live fetches will now bronze the 404 response (empty) via the standard short-circuit. *(Source: `connectors/entsog/endpoints.py L155-166`; `connectors/entsog/client.py L109-115`.)*

# Related datasets

- **`urgent_market_messages`** — UMM bulletins covering unplanned outages. `as published`. Closest live replacement for the withdrawn interruptions endpoint. *entsog · UMM · real-time*
- **`physical_flows`** — Flow at the same point. `daily`. Cross-check interruption windows against observed flow drops. *entsog · operational · daily*
- **`firm_available`** — Available firm capacity. `daily`. Interruptions reduce `firm_available` until restored. *entsog · capacity · daily*
- **`interruptible_available`** — Capacity offered as interruptible. `daily`. Pair with this dataset's events for interruption-rate analysis. *entsog · capacity · daily*
