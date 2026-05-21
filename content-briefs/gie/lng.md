---
slug: lng
vendor: gie
vendor_label: GIE ALSI (LNG)
api_code: ALSI
last_verified: 2026-05-11
entitlement_required: true
entitlement_reason: "GIE API key (header `x-key`, lowercase) required — shared key with AGSI+; free registration at alsi.gie.eu/account/registration"
sources_consulted:
  - vault/gie/lng.md
  - gridflow/src/gridflow/schemas/gie.py::LNGTerminal (lines 50-68)
  - gridflow/src/gridflow/silver/gie/alsi.py::LNGTerminalTransformer (lines 18-119, registered at L122)
  - gridflow/src/gridflow/connectors/gie/endpoints.py::ALSI_COUNTRIES (line 17) + shared GIE_API_PATH (line 11)
  - https://alsi.gie.eu/api (vendor docs — interactive HTML; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault lng.md — API endpoint table"
    source_a_says: "Query params listed as `country, from, till, page, size` — uses `till=` for range end (not `to=`)"
    source_b: "storage.md / storage_reports.md — AGSI uses `from`/`to`"
    orchestrator_recommendation: "trust vault — ALSI legacy convention differs from AGSI. The `storage.md` brief's Implementation Delta flagged this from the AGSI side: `_fetch_country` (used by `gie_alsi`) still uses `till=` instead of `to=`. Documented here as the active ALSI behaviour."
  - source_a: "vault lng.md — no Historical depth row"
    source_a_says: "ALSI `lng` has no explicit earliest-data date in the API endpoint table"
    source_b: "AGSI storage.md — earliest is 2011-01-01"
    orchestrator_recommendation: "annotate ALSI earliest as not verified in vault; treat 2011-01-01 (AGSI bound) as the conservative lower bound for the vendor hub."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** European LNG terminals, <span class="italic fg-accent">country by country.</span>

**Lede:** Country-scoped daily LNG terminal inventory and send-out — the canonical EU LNG-inflow indicator for storage-vs-LNG substitution modelling, security-of-supply analysis, and gas-supply balance.

**Verified line:** Verified against vendor docs: 2026-05-11 · [GIE ALSI · /api](https://alsi.gie.eu/api)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.gie_alsi.lng` |
| API PATH | `/api?country={ISO2}&from=…&till=…` |
| FREQUENCY | daily (gas day) |
| PUBLICATION LAG | daily |
| VOLUME | ~8 rows / day |
| PRIMARY KEY | `(gas_day, country_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Snapshot cadence |
| 2 | 8 | ALSI countries |
| 3 | GWh | Reporting unit |
| 4 | 10 | Silver output cols |

# Sidebar siblings

- storage
- storage_reports
- unavailability
- about_summary
- about_listing

# Sample chart

- **Type:** `sparkline`
- **Title:** "FR LNG terminals · send-out · last 12 months"
- **Subtitle:** "Sparkline · GWh/day · daily · gas-day · 2025-06 → 2026-05"
- **Seed:** 28
- **Toggles:** `1y` (active) / `5y`

# Schema

Defined in `gridflow/schemas/gie.py` · `LNGTerminal` (lines 50-68) and `gridflow/silver/gie/alsi.py` · `LNGTerminalTransformer` (lines 18-119). Partitioned by `gas_day` (year + month). Silver `output_cols` is the source of truth at `silver/gie/alsi.py L109-114` — 10 columns including `data_provider` and `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `gas_day` | `date` | No | `gasDayStart` / `gasDay` / `date` | Gas day, NOT calendar day — starts at 06:00 UTC. Strict parse via `str.to_date("%Y-%m-%d")`. | `schemas/gie.py L53`; `silver/gie/alsi.py L57-61` |
| `country_code` | `str` | No | `countryCode` / `code` | ISO-2 (one of `BE, ES, FR, GB, IT, NL, PL, PT`). **Required** in `LNGTerminal` (no default — distinct from AGSI's `country_code: str = ""`). | `schemas/gie.py L54`; `silver/gie/alsi.py L74, L95-96` |
| `country_name` | `Optional[str]` | Yes (default `""`) | `countryName` / `name` | Human-readable country. | `schemas/gie.py L55`; `silver/gie/alsi.py L75` |
| `lng_in_storage_gwh` | `Optional[float]` | Yes | `lngInventory` / `lngInStorage` / `gasInStorage` | Stored LNG inventory (GWh). Multiple vendor field aliases handled in `field_map`. | `schemas/gie.py L56`; `silver/gie/alsi.py L66-67` |
| `send_out_gwh` | `Optional[float]` | Yes | `sendOut` / `sendOutGwh` / `withdrawal` | LNG send-out (regas) volume (GWh). Fallback to `withdrawal` for legacy shape. | `schemas/gie.py L57`; `silver/gie/alsi.py L68-69` |
| `injection_gwh` | `Optional[float]` | Yes | `injection` / `injectionGwh` | LNG inflow to terminal (GWh). | `schemas/gie.py L58`; `silver/gie/alsi.py L70` |
| `dtrs_pct_full` | `Optional[float]` | Yes | `dtrs` / `dtrsPctFull` / `full` | Declared Technical Regasification Send-out — % of nominal capacity. 0-100, clamped by validator. | `schemas/gie.py L59, L63-68`; `silver/gie/alsi.py L71-72` |
| `trend` | `Optional[float]` | Yes | `trend` | Signed daily delta of `dtrs_pct_full`. | `schemas/gie.py L60`; `silver/gie/alsi.py L73` |
| `data_provider` | `str` | No (default `"gie_alsi"`) | _derived_ | Always `"gie_alsi"` (**NOT** `"gie_agsi"`). | `schemas/gie.py L61`; `silver/gie/alsi.py L105` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Silver write timestamp. | `silver/gie/alsi.py L106` |

**PARQUET PATH:** `data/silver/gie_alsi/lng/year=YYYY/month=MM/`
**PARTITION BY:** `gas_day (year + month)`
**DEDUP KEY:** `(gas_day, country_code)` when `country_code` is present, else `(gas_day,)` (`silver/gie/alsi.py L98-101`)

# Sample data

| gas_day | country_code | country_name | lng_in_storage_gwh | send_out_gwh | injection_gwh | dtrs_pct_full | trend | data_provider |
|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | FR | France | 78.40 | 420.10 | 510.30 | 64.20 | 0.42 | gie_alsi |
| **2026-05-06** | **ES** | **Spain** | **142.80** | **685.30** | **812.40** | **78.50** | **0.61** | **gie_alsi** |
| 2026-05-06 | NL | Netherlands | 56.20 | 312.40 | 380.10 | 51.30 | 0.28 | gie_alsi |
| 2026-05-06 | BE | Belgium | 24.10 | 145.20 | 178.30 | 48.60 | 0.32 | gie_alsi |
| 2026-05-06 | IT | Italy | 41.80 | 215.40 | 258.10 | 42.10 | -0.15 | gie_alsi |
| 2026-05-06 | PT | Portugal | 18.20 | 92.10 | 110.30 | 55.40 | 0.18 | gie_alsi |
| 2026-05-06 | GB | United Kingdom | 35.40 | 198.30 | 240.10 | 39.80 | -0.21 | gie_alsi |
| 2026-05-06 | PL | Poland | 12.10 | 68.40 | 82.20 | 38.50 | 0.10 | gie_alsi |

**Sources:** All 8 rows synthesised respecting `LNGTerminal` schema constraints — vault `lng.md` carries no explicit live Silver Sample, so values are projected from the 2026-05 ALSI footprint and respect the `dtrs_pct_full` clamp validator (0-100) at `schemas/gie.py L63-68`. The highlighted **ES** row is the canonical case: Spain is the largest LNG-import country in the ALSI footprint by send-out volume (Mugardos, Bilbao, Cartagena, Barcelona, Sagunto, Huelva terminals combined). Unlike AGSI's GB Pre-Brexit gap, GB ALSI continues to publish — but `lng_in_storage_gwh` may carry null values during reporting outages; treat null as publication absence, not zero.

# Dataset-specific section: ALSI country footprint

The 8 countries covered by ALSI as of 2026 (`ALSI_COUNTRIES`, `connectors/gie/endpoints.py L17`).

- `BE` — Belgium (Zeebrugge)
- `ES` — Spain (largest ALSI country by inventory + send-out)
- `FR` — France (Dunkerque, Fos, Montoir)
- `GB` — United Kingdom (Isle of Grain, Milford Haven — **still publishes**, unlike AGSI GB which is Pre-Brexit only)
- `IT` — Italy (Panigaglia, Adriatic, Livorno, Piombino)
- `NL` — Netherlands (Gate terminal, Rotterdam)
- `PL` — Poland (Świnoujście)
- `PT` — Portugal (Sines)

**Footprint contrast with AGSI:** ALSI adds `PT` (Portugal) and drops `AT, DE, PL` partial overlap differences — note **PL** is in both. ALSI excludes `AT` and `DE` (no LNG import terminals — DE's Wilhelmshaven FSRU may be added in future releases).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `alsi.gie.eu/api?country={ISO2}&from={YYYY-MM-DD}&till={YYYY-MM-DD}`
- AUTH: header `x-key` (LOWERCASE — `X-Key` returns 401), key from env `GIE_API_KEY` (shared with AGSI+). Free registration at [alsi.gie.eu/account/registration](https://alsi.gie.eu/account/registration).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/gie_alsi/lng/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.gie.alsi.LNGTerminalTransformer` (registered at `silver/gie/alsi.py L122`)

**Tab 1 — Example URL**
```
https://alsi.gie.eu/api?country=ES&from=2026-05-01&till=2026-05-07&size=300

Header: x-key: $GIE_API_KEY

Note: ALSI uses `till=` for range end (NOT `to=` — different from AGSI).
```

**Tab 2 — DuckDB · SQL**
```sql
-- EU-wide LNG send-out trajectory, last 90 days
SELECT gas_day,
       SUM(send_out_gwh) AS eu_send_out_gwh,
       SUM(injection_gwh) AS eu_injection_gwh,
       AVG(dtrs_pct_full) AS avg_pct_full
FROM read_parquet('data/silver/gie_alsi/lng/**/*.parquet')
WHERE send_out_gwh IS NOT NULL
  AND gas_day >= current_date - INTERVAL 90 DAY
GROUP BY gas_day
ORDER BY gas_day;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/gie_alsi/lng/**/*.parquet")
# Spain LNG net contribution: injection - send_out daily, last 30 days
es = (
    df.filter(pl.col("country_code") == "ES")
      .with_columns((pl.col("injection_gwh") - pl.col("send_out_gwh")).alias("net_storage_change_gwh"))
      .select("gas_day", "lng_in_storage_gwh", "send_out_gwh", "injection_gwh",
              "net_storage_change_gwh", "dtrs_pct_full")
      .sort("gas_day")
      .tail(30)
)
print(es)
```

# Caveats

## 01 ALSI uses `till=` for range end, AGSI uses `to=`

ALSI range query is `from=YYYY-MM-DD&till=YYYY-MM-DD`. AGSI uses `from`/`to`. Connector's `_fetch_country` (used by `gie_alsi`) preserves the `till=` legacy form. *(Source: vault `lng.md` query params table; `storage.md` Implementation Delta.)*

## 02 Unit is GWh — NOT MWh

Stocks in `lng_in_storage_gwh`; flows in `send_out_gwh` / `injection_gwh` (GWh per gas day). Same convention as AGSI. *(Source: vault `lng.md` Silver schema.)*

## 03 Gas day starts at 06:00 UTC, NOT midnight

`gas_day` is a `date`. Gas day for `2026-05-06` runs 06:00 UTC → 06:00 UTC next day. *(Source: vault `lng.md` Modelling notes + `20-domain/concepts/gas-day.md`.)*

## 04 `x-key` header MUST be lowercase

`X-Key` returns HTTP 401. Same enforcement as AGSI. *(Source: shared GIE vendor convention.)*

## 05 GB null values are publication absence, not zero

Unlike AGSI GB (Pre-Brexit `"-"` placeholders), ALSI GB still publishes — but `lng_in_storage_gwh` may carry null during reporting outages. Treat null as publication absence, not a zero LNG inventory. *(Source: vault `lng.md` Modelling notes.)*

## 06 `dtrs_pct_full` is clamped 0-100 by validator

`LNGTerminal.dtrs_pct_full` has a `field_validator` clamping to `[0.0, 100.0]` — identical pattern to `GasStorage.storage_pct_full`. *(Source: `schemas/gie.py L63-68`.)*

# Related datasets

- **`storage`** (GIE AGSI) — Country-level gas storage. `daily` — pair LNG send-out (terminal regas) with storage net withdrawal to model the dual gas-supply buffer (storage drawdown vs LNG inflow). `gie · storage · daily`
- **`storage_reports`** (GIE AGSI) — Facility / company / country / aggregate storage. `daily` — finer-grain storage context for the same supply-buffer analysis. `gie · storage · daily`
- **`aggregated_physical_flows`** (ENTSOG) — Cross-border pipeline flows. `daily` — pair ALSI LNG inflow with ENTSOG pipeline imports to model the full EU gas-supply mix. `entsog · transmission · daily`
- **`fuelhh`** (Elexon) — GB half-hourly CCGT generation. `30 min` — pair GB LNG send-out with downstream gas-to-power conversion to trace LNG → grid attribution. `elexon · generation · 30 min`
