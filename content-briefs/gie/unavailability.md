---
slug: unavailability
vendor: gie
vendor_label: GIE AGSI+ (Gas Storage)
api_code: AGSI
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "GIE API key (header `x-key`, lowercase) required — free registration at agsi.gie.eu/account/registration"
sources_consulted:
  - vault/gie/unavailability.md
  - gridflow/src/gridflow/schemas/gie.py (no dedicated schema — dynamic columns via AgsiJsonTransformer)
  - gridflow/src/gridflow/silver/gie/agsi.py::UnavailabilityTransformer (lines 465-473, extends AgsiJsonTransformer; registered at L630)
  - gridflow/src/gridflow/connectors/gie/endpoints.py::ENDPOINTS["unavailability"] (lines 170-178)
  - https://agsi.gie.eu/api (vendor docs — interactive HTML; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault unavailability.md — Implementation Delta: docs ambiguity"
    source_a_says: "GIE v007 PDF wording is ambiguous about whether `/api/unavailability` is part of the AGSI API or a separate legacy/portal feature"
    source_b: "live endpoint returns well-formed JSON (verified 2026-05-08 — DE returned 30 records / 7 pages)"
    orchestrator_recommendation: "treat as active per the live-validation pass; the catalog YAML notes 'Marked active because the endpoint is documented and live-served, though documentation wording is ambiguous'."
  - source_a: "vault — date param naming"
    source_a_says: "Registry uses `start` / `end`; the live API also accepts `from` / `to` and produces a slightly different filter result (different `last_page`)"
    source_b: "gridflow connector uses `start` / `end` per registry"
    orchestrator_recommendation: "no fix needed — connector uses `start`/`end`; the alternative `from`/`to` form is documented for completeness."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Storage outages and <span class="italic fg-accent">planned maintenance.</span>

**Lede:** Per-event AGSI storage outage and maintenance reports — the canonical capacity-reduction feed for short-term withdrawal forecasts, gas-spread trades, and explaining sudden capacity drops in `storage_reports`.

**Verified line:** Verified against vendor docs: 2026-05-08 · [GIE AGSI+ · /api/unavailability](https://agsi.gie.eu/api)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.gie_agsi.unavailability` |
| API PATH | `/api/unavailability?country={ISO2}&start=…&end=…` |
| FREQUENCY | as published |
| PUBLICATION LAG | real-time (operator-reported) |
| VOLUME | ~30 records / country (rolling) |
| PRIMARY KEY | `(facility_eic, start, end)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | as published | Cadence |
| 2 | 9 | AGSI countries |
| 3 | 13 | Dynamic columns |
| 4 | Planned/Unplanned | Event types |

# Sidebar siblings

- storage
- storage_reports
- about_listing
- about_summary
- news

# Sample chart

- **Type:** `barsH`
- **Title:** "DE storage outages · withdrawal capacity reduction · last 12 months"
- **Subtitle:** "Horizontal bars · GWh/day · by facility · 2025-06 → 2026-05"
- **Seed:** 33
- **Toggles:** `30d` / `90d` / `1y` (active)

# Schema

No dedicated Pydantic schema — `UnavailabilityTransformer` extends `AgsiJsonTransformer` (`silver/gie/agsi.py L465`) and emits dynamic columns derived from the live JSON via `_normalise_row` + `_camel_to_snake` + numeric-suffix heuristics (`*_volume`, `*_capacity`, `*_pct`, `*_percentage`). The columns below are the observed schema from the live 2026-05-08 DE response.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `published` | `datetime[UTC]` | Yes | `published` | Vendor publish timestamp; `_safe_datetime` parses naïve `YYYY-MM-DD HH:MM:SS` as UTC. | `silver/gie/agsi.py L46, L287-298, L331-332` |
| `country` | `str` | Yes | `country` | JSON-encoded `{"name", "code"}` dict — live shape is nested. | `silver/gie/agsi.py L329-330` |
| `company` | `str` | Yes | `company` | JSON-encoded `{"name", "eic"}` dict. | `silver/gie/agsi.py L329-330` |
| `facility` | `str` | Yes | `facility` | JSON-encoded `{"name", "eic"}` dict. | `silver/gie/agsi.py L329-330` |
| `start` | `datetime[UTC]` | Yes | `start` | Outage window start. | `silver/gie/agsi.py L46, L331-332` |
| `end` | `datetime[UTC]` | Yes | `end` | Outage window end; check `end_flag` for confirmed-vs-estimate. | `silver/gie/agsi.py L46, L331-332` |
| `volume` | `Optional[float]` | Yes | `volume` | GWh — energy not stored during outage. Captured by `numeric_names` (`silver/gie/agsi.py L300-307`). | `silver/gie/agsi.py L333-334` |
| `injection` | `Optional[float]` | Yes | `injection` | GWh/day capacity reduction. | `silver/gie/agsi.py L333-334` |
| `withdrawal` | `Optional[float]` | Yes | `withdrawal` | GWh/day capacity reduction. | `silver/gie/agsi.py L333-334` |
| `description` | `Optional[str]` | Yes | `description` | Free-text operator note. | `silver/gie/agsi.py L335-336` |
| `end_flag` | `Optional[str]` | Yes | `end_flag` | `Confirmed` or `Estimate`. | `silver/gie/agsi.py L335-336` |
| `type` | `Optional[str]` | Yes | `type` | `Planned` · `Unplanned` · ... | `silver/gie/agsi.py L335-336` |
| `data_provider` | `str` | No (default `"gie_agsi"`) | _derived_ | Always `"gie_agsi"`. | `silver/gie/agsi.py L337` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver write timestamp. | `silver/gie/agsi.py L338` |

**PARQUET PATH:** `data/silver/gie_agsi/unavailability/year=YYYY/month=MM/`
**PARTITION BY:** `published (year + month)`
**DEDUP KEY:** `(facility_eic, start, end)` — falls back to `(id, url, entity_code, eic)` per `AgsiJsonTransformer.unique` (`silver/gie/agsi.py L344-348`)

# Sample data

| published | country (eic-name) | facility (eic-name) | start | end | volume | injection | withdrawal | end_flag | type |
|---|---|---|---|---|---|---|---|---|---|
| 2026-05-08 10:40:07 | `{"name":"Germany","code":"DE"}` | `{"name":"EWE H-Gas Zone","eic":"37W000000000002O"}` | 2026-05-04 06:00:00 | 2026-05-08 12:00:00 | 3.004 | 41.4 | 82.8 | Confirmed | Planned |
| 2026-05-07 14:22:10 | `{"name":"Germany","code":"DE"}` | `{"name":"Etzel ESE","eic":"37W000000000005C"}` | 2026-05-05 06:00:00 | 2026-05-09 06:00:00 | 1.420 | 22.1 | 44.2 | Estimate | Unplanned |
| **2026-05-06 08:11:42** | `{"name":"Germany","code":"DE"}` | **`{"name":"Rehden","eic":"37W000000000001Q"}`** | **2026-04-15 06:00:00** | **2026-06-01 06:00:00** | **18.5** | **125.0** | **210.0** | **Confirmed** | **Planned** |
| 2026-05-06 07:55:21 | `{"name":"France","code":"FR"}` | `{"name":"Storengy Cerville","eic":"21W-CERVILLE---T"}` | 2026-05-04 06:00:00 | 2026-05-07 06:00:00 | 0.420 | 8.4 | 16.8 | Confirmed | Planned |
| 2026-05-05 21:30:00 | `{"name":"Italy","code":"IT"}` | `{"name":"Cortemaggiore","eic":"21W-CORTEMAGG--N"}` | 2026-05-03 06:00:00 | 2026-05-06 06:00:00 | 0.815 | 12.2 | 24.4 | Confirmed | Planned |
| 2026-05-04 11:12:08 | `{"name":"Austria","code":"AT"}` | `{"name":"Haidach (AT)","eic":"25W-HAIDACH----X"}` | 2026-05-01 06:00:00 | 2026-05-15 06:00:00 | 2.110 | 31.5 | 63.0 | Estimate | Planned |
| 2026-05-03 17:48:15 | `{"name":"Netherlands","code":"NL"}` | `{"name":"Bergermeer","eic":"21W-BERGERMEER-G"}` | 2026-05-02 06:00:00 | 2026-05-04 06:00:00 | 0.310 | 6.2 | 12.4 | Confirmed | Unplanned |
| 2026-05-02 09:05:30 | `{"name":"Spain","code":"ES"}` | `{"name":"Yela","eic":"21W-YELA------4J"}` | 2026-05-01 06:00:00 | 2026-05-08 06:00:00 | 1.640 | 24.6 | 49.2 | Estimate | Planned |

**Sources:** Top row verbatim from vault Bronze sample (live DE 2026-05-08, EWE H-Gas Zone planned maintenance). Remaining 7 rows synthesised respecting the JSON-encoded nested-dict shape, the `Planned`/`Unplanned` × `Confirmed`/`Estimate` matrix, and gas-day-aligned `start`/`end` (`06:00:00` UTC). The highlighted **Rehden** row is the most material event in the sample (~18.5 GWh of energy not stored, 210 GWh/day withdrawal reduction over 47 days) — the kind of event a short-term capacity model must surface.

# Dataset-specific section: Event-type taxonomy

The `type` and `end_flag` fields define the 4-quadrant event matrix. Filter accordingly when scoring capacity confidence.

- `type=Planned` · `end_flag=Confirmed` — Scheduled maintenance with firm restoration date. Highest confidence; can be priced into forward curves.
- `type=Planned` · `end_flag=Estimate` — Scheduled maintenance with provisional restoration date. Watch for slippage.
- `type=Unplanned` · `end_flag=Confirmed` — Unexpected outage with restoration confirmed. Treat as a fixed historical input.
- `type=Unplanned` · `end_flag=Estimate` — Unexpected outage with provisional restoration. Highest uncertainty — apply tail risk in capacity forecasts.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `agsi.gie.eu/api/unavailability?country={ISO2}&start={YYYY-MM-DD}&end={YYYY-MM-DD}`
- AUTH: header `x-key` (LOWERCASE — `X-Key` returns 401), key from env `GIE_API_KEY`. Free registration at [agsi.gie.eu/account/registration](https://agsi.gie.eu/account/registration).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/gie_agsi/unavailability/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.gie.agsi.UnavailabilityTransformer` (extends `AgsiJsonTransformer`, registered at `silver/gie/agsi.py L630`)

**Tab 1 — Example URL**
```
https://agsi.gie.eu/api/unavailability?country=DE&start=2026-04-01&end=2026-05-07&size=300

Header: x-key: $GIE_API_KEY
```

**Tab 2 — DuckDB · SQL**
```sql
-- Total withdrawal capacity offline per country, by month
SELECT json_extract_string(country, '$.code') AS country,
       date_trunc('month', start) AS month,
       SUM(withdrawal) AS gwh_per_day_offline
FROM read_parquet('data/silver/gie_agsi/unavailability/**/*.parquet')
WHERE type = 'Planned'
  AND start >= current_date - INTERVAL 1 YEAR
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/gie_agsi/unavailability/**/*.parquet")
# Currently-active outages: window contains today
today = pl.lit(pl.datetime(2026, 5, 8, time_unit="us"))
active = (
    df.filter((pl.col("start") <= today) & (pl.col("end") >= today))
      .select("country", "facility", "start", "end", "withdrawal", "type", "end_flag")
      .sort("withdrawal", descending=True)
)
print(active.head(20))
```

# Caveats

## 01 Nested-dict columns are JSON-encoded at silver

`country`, `company`, `facility` arrive as nested dicts (`{"name": ..., "code": ...}` or `{"name": ..., "eic": ...}`). The `AgsiJsonTransformer` JSON-encodes them at silver (`silver/gie/agsi.py L329-330`). Use `json_extract_string` / `pl.col(...).str.json_path_match(...)` to unwrap. *(Source: vault Known Issues; live 2026-05-08.)*

## 02 GB returns zero rows by design

No UK storage outages are reported on AGSI. `country=GB` returns `{"last_page": 1, "total": 0, "data": []}`. *(Source: vault Known Issues; live 2026-05-08.)*

## 03 Documentation ambiguity (v007 PDF)

The GIE v007 PDF leaves it unclear whether `/api/unavailability` is part of the AGSI API or a legacy/portal feature. Endpoint is live-served and well-formed; treated as active. *(Source: vault Implementation Delta; `docs/gie_agsi_endpoint_catalog.yaml`.)*

## 04 Date-param alternatives produce different filters

Registry uses `start` / `end`; the live API also accepts `from` / `to` and produces a different `last_page` (different filter semantics). Gridflow standardises on `start`/`end`. *(Source: vault Implementation Delta.)*

## 05 `x-key` header MUST be lowercase

`X-Key` returns HTTP 401. *(Source: vault Known Issues #1.)*

## 06 `start` / `end` arrive as naïve local strings

Vendor returns `YYYY-MM-DD HH:MM:SS` without timezone; `_safe_datetime` parses with UTC fallback. *(Source: vault Known Issues; `silver/gie/agsi.py L46-61`.)*

# Related datasets

- **`storage_reports`** — Per-facility storage levels. `daily` — join `unavailability.facility.eic` ↔ `storage_reports.entity_code` to derive effective capacity net of outages. `gie · storage · daily`
- **`storage`** — Country-level storage levels. `daily` — pair with country-rollup `unavailability.country.code` for explanatory features on sudden capacity drops. `gie · storage · daily`
- **`news`** — AGSI service announcements. `as published` — often cross-references the same outage events as free-text operator notices. `gie · news · as published`
- **`about_listing`** — Company + facility EIC inventory. `snapshot` — supplies the facility names for unwrapping the JSON-encoded `facility` column. `gie · storage · snapshot`
