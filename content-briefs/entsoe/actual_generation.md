---
slug: actual_generation
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A75/A16
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/01-actual-generation-http-401.md)"
sources_consulted:
  - vault/entsoe/actual_generation.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeActualGeneration (lines 46-61)
  - gridflow/src/gridflow/silver/entsoe/actual_generation.py::ActualGenerationTransformer (lines 18-90)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["actual_generation"] (lines 37-41)
  - .planning/reconciliation/entsoe/01-actual-generation-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/37-actual-generation-area-name-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found:
  - source_a: "schemas/entsoe.py L51 (EntsoeActualGeneration.area_name)"
    source_a_says: "area_name: str = '' — declared on schema with empty default"
    source_b: "silver/entsoe/actual_generation.py L82-87 (output_cols)"
    source_b_says: "area_name not in output_cols — transformer omits it; silver rows have no area_name column"
    orchestrator_recommendation: "trust gridflow silver — area_name is unfilled; downstream must join an EIC reference to get human-readable zone names. Caveats #04 flags this."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Realised generation, <span class="italic fg-accent">by fuel and zone.</span>

**Lede:** Realised MW generation per EIC bidding zone by PSR production type — the canonical residual-load input for European power-market models and the cross-vendor analogue of GB `fuelhh`.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.actual_generation` |
| API PATH | `/api?documentType=A75&processType=A16` |
| FREQUENCY | PT15M / PT30M / PT60M |
| PUBLICATION LAG | T+1h → T+24h |
| VOLUME | ~17 TimeSeries / zone / day |
| PRIMARY KEY | `(timestamp_utc, area_code, production_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 21 | PSR types (B01..B25) |
| 2 | T+1h | Best-case lag |
| 3 | XML | `GL_MarketDocument` |
| 4 | 6 | Schema columns |

# Sidebar siblings

- actual_load
- day_ahead_prices
- wind_solar_forecast
- cross_border_flows
- actual_generation_units

# Sample chart

- **Type:** `stackedArea`
- **Title:** "DE-LU generation by production type · 24-hour snapshot"
- **Subtitle:** "Stacked area · MW · UTC · 6 May 2026"
- **Seed:** 11
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeActualGeneration` (lines 46-61). Silver transformer drops `area_name` from output despite the schema declaring it (see Caveats #04).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; resolution varies (`PT15M` / `PT30M` / `PT60M`). Validator requires tzinfo. | `schemas/entsoe.py L49, L56-61` |
| `area_code` | `str` | No | `<inBiddingZone_Domain.mRID>` | EIC bidding zone identifier (e.g. `10YGB----------A`, `10Y1001A1001A82H`). | `schemas/entsoe.py L50` |
| `area_name` | `str` (declared) | Yes | _derived_ | **Declared in schema (default `""`) but not in transformer `output_cols`** — silver has no `area_name` column. | `schemas/entsoe.py L51`; `silver/entsoe/actual_generation.py L82-87` |
| `production_type` | `str` | No | `<MktPSRType><psrType>` | EIC PSR code, `B01`..`B25`. Falls back to `"unknown"` if missing. | `schemas/entsoe.py L52`; `silver/entsoe/actual_generation.py L65-70` |
| `generation_mw` | `float` | No | `<Point><quantity>` | MW. XML unit is `MAW` (mega-amp-watt = MW in IEC 62325). | `schemas/entsoe.py L53` |
| `resolution` | `str` | No (default `""`) | parsed from `<Period><resolution>` | ISO duration: `PT15M` / `PT30M` / `PT60M`. | `silver/entsoe/actual_generation.py L82` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L54` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set by transformer at silver write. | `silver/entsoe/actual_generation.py L79` |

**PARQUET PATH:** `data/silver/entsoe/actual_generation/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, production_type)` — keep last on sort (`silver/entsoe/actual_generation.py L72-74`)

# Sample data

| timestamp_utc | area_code | production_type | generation_mw | resolution | data_provider |
|---|---|---|---|---|---|
| 2026-05-05T22:00:00+00:00 | 10Y1001A1001A82H | B19 | 0.0 | PT15M | entsoe |
| 2026-05-05T22:15:00+00:00 | 10Y1001A1001A82H | B16 | 1843.5 | PT15M | entsoe |
| 2026-05-05T22:15:00+00:00 | 10Y1001A1001A82H | B14 | 4280.0 | PT15M | entsoe |
| 2026-05-05T22:15:00+00:00 | 10Y1001A1001A82H | B12 | -340.0 | PT15M | entsoe |
| **2026-05-06T11:00:00+00:00** | **10Y1001A1001A82H** | **B16** | **28940.0** | **PT15M** | **entsoe** |
| 2026-05-06T11:00:00+00:00 | 10Y1001A1001A82H | B05 | 1820.0 | PT15M | entsoe |
| 2026-05-06T11:00:00+00:00 | 10Y1001A1001A82H | B04 | 12450.0 | PT15M | entsoe |
| 2026-05-06T22:00:00+00:00 | 10Y1001A1001A82H | B16 | 0.0 | PT15M | entsoe |

**Sources:** Rows derived from vault Bronze sample (DE-LU, 2026-05-06, captured live 2026-05-08); PSR-type code labels added editorially. The highlighted row is solar midday peak (`B16` = 28.9 GW) — illustrates the diurnal swing the dataset is most useful for. Hydro Pumped Storage (`B12`) shows -340 MW (charging) — note the negative-can-occur semantics for storage classes.

# Production types (PSR codelist — `production_type`)

EIC code list `B01`..`B25` — the canonical taxonomy for European generation.

- `B01` Biomass · `B02` Fossil brown coal / lignite · `B03` Fossil coal-derived gas · `B04` Fossil gas (CCGT / OCGT combined) · `B05` Fossil hard coal · `B06` Fossil oil · `B07` Fossil oil shale · `B08` Fossil peat · `B09` Geothermal · `B10` Hydro pumped storage (negative when charging) · `B11` Hydro run-of-river and poundage · `B12` Hydro water reservoir · `B13` Marine · `B14` Nuclear · `B15` Other renewable · `B16` Solar · `B17` Waste · `B18` Wind offshore · `B19` Wind onshore · `B20` Other · `B25` Energy storage

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A75&processType=A16&in_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — register at [transparency.entsoe.eu](https://transparency.entsoe.eu/). Default key returns HTTP 401; extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/actual_generation/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.actual_generation.ActualGenerationTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A75&processType=A16&in_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily generation mix for DE-LU last 7 days
SELECT date_trunc('day', timestamp_utc) AS day,
       production_type,
       sum(generation_mw) / count(*) AS avg_mw
FROM read_parquet('data/silver/entsoe/actual_generation/**/*.parquet')
WHERE area_code = '10Y1001A1001A82H'
  AND timestamp_utc >= current_timestamp - INTERVAL 7 DAY
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsoe/actual_generation/**/*.parquet")
# Pivot to wide: one column per production type — residual-load feature
mix = df.filter(pl.col("area_code") == "10Y1001A1001A82H").pivot(
    index="timestamp_utc", on="production_type",
    values="generation_mw", aggregate_function="sum",
)
print(mix.select(["timestamp_utc", "B19", "B18", "B16"]).tail())
```

# Caveats

## 01 GB stopped publishing post-Brexit

Calls against GB (`10YGB----------A`) return `Acknowledgement_MarketDocument` reason 999. Use Elexon `fuelhh` / `fuelinst` for GB. *(Source: vault Known Issues #1.)*

## 02 Resolution varies by zone

DE/AT/FR are `PT15M`; others `PT60M`. Don't assume hourly when joining settlement-period datasets. *(Source: vault Known Issues #2.)*

## 03 Revisions silently overwrite

Same `(timestamp_utc, area_code, production_type)` may be republished; transformer dedups on sort-last. No `published_at` surfaced. *(Source: `silver/entsoe/actual_generation.py L72-74`.)*

## 04 `area_name` declared but not emitted

Schema declares `area_name: str = ""` (`schemas/entsoe.py L51`) but transformer `output_cols` omits it. Silver has no `area_name` column. *(Source: frontmatter discrepancy.)*

## 05 Storage units carry both directions

A75 includes generation (`businessType=A03`) and consumption (`A04`) for storage — `B10` / `B12` rows can be negative (charging). Filter or sign-handle for net-generation calculations. *(Source: vault Known Issues #5.)*

## 06 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source; live verification deferred to extended ENTSO-E registration. *(Source: `.planning/reconciliation/entsoe/01-actual-generation-http-401.md`.)*

# Related datasets

- **`actual_load`** — Realised demand per zone. `PT15M/PT30M/PT60M`. Pair to compute residual demand (`actual_load - sum(renewable production_types)`) — canonical EU MEF input. `entsoe · load · hourly`
- **`day_ahead_prices`** — Marginal day-ahead clearing prices per zone. `PT60M`. The price counterpart residual-load models try to predict from this dataset's renewable shares. `entsoe · prices · hourly`
- **`wind_solar_forecast`** — TSO-published wind / solar forecasts. `PT60M`. Compare against this dataset for per-zone forecast skill. `entsoe · forecast · hourly`
- **`fuelhh` (Elexon)** — GB equivalent of this dataset (since GB does not publish to ENTSO-E post-Brexit). `30 min`. Cross-vendor join: stitch GB `fuelhh` to continental `actual_generation`. `elexon · generation · 30 min`
