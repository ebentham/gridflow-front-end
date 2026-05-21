---
slug: news
vendor: gie
vendor_label: GIE AGSI+ (Gas Storage)
api_code: AGSI
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "GIE API key (header `x-key`, lowercase) required — free registration at agsi.gie.eu/account/registration"
sources_consulted:
  - vault/gie/news.md
  - gridflow/src/gridflow/schemas/gie.py (no dedicated schema — AgsiJsonTransformer dynamic columns)
  - gridflow/src/gridflow/silver/gie/agsi.py::NewsTransformer (lines 445-449, extends AgsiJsonTransformer; registered at L628)
  - gridflow/src/gridflow/connectors/gie/endpoints.py::ENDPOINTS["news"] (lines 154-161, implementation_phase="deferred")
  - https://agsi.gie.eu/api/news (vendor docs — interactive HTML; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault news.md — Implementation Delta: pagination metadata absent"
    source_a_says: "Catalog YAML declares `authoritative_total_pages: last_page` and `per_page_count: total`, but live response (2026-05-08) contains neither — only `data`"
    source_b: "connector `_last_page` falls through to default 1; behaviour is correct (single page) but the docs claim is unverifiable"
    orchestrator_recommendation: "non-blocking — connector behaviour is correct; flag the docs/live divergence."
  - source_a: "vault news.md — `turl` field"
    source_a_says: "Catalog YAML and code `_news_item_turls` look for `turl`, `url`, or `id`; live response has only `url` (numeric)"
    source_b: "fallback to `url` already covers this in `_news_item_turls`"
    orchestrator_recommendation: "non-blocking — fallback chain handles the live shape."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** AGSI service announcements <span class="italic fg-accent">and data caveats.</span>

**Lede:** AGSI service-announcement listing flagging operator reporting issues, planned data outages, and corrections — the data-quality feed for masking suspect periods in storage time-series.

**Verified line:** Verified against vendor docs: 2026-05-08 · [GIE AGSI+ · /api/news](https://agsi.gie.eu/api/news)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.gie_agsi.news` |
| API PATH | `/api/news` |
| FREQUENCY | as published |
| PUBLICATION LAG | real-time (AGSI staff) |
| VOLUME | ~299 records rolling (~2-3 yr depth) |
| PRIMARY KEY | `(url,)` (numeric announcement ID) |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | as published | Cadence |
| 2 | 299 | Records (live 2026-05-08) |
| 3 | ~2.6 MB | Payload size |
| 4 | deferred | Implementation phase |

# Sidebar siblings

- news_item
- unavailability
- storage
- storage_reports
- about_summary

# Sample chart

- **Type:** `barsH`
- **Title:** "AGSI announcements · count by affected country · last 12 months"
- **Subtitle:** "Horizontal bars · entity_code count · rolling · 2025-05 → 2026-05"
- **Seed:** 47
- **Toggles:** `30d` / `90d` / `1y` (active)

# Schema

No dedicated Pydantic schema — `NewsTransformer` extends `AgsiJsonTransformer` directly (`silver/gie/agsi.py L445-449`) with no override. Columns emerge dynamically from the live JSON via `_normalise_row` + `_camel_to_snake` + datetime/numeric heuristics. The schema below is the observed live 2026-05-08 shape.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `url` | `str` | No | `url` | Numeric announcement ID stored as text (e.g. `"1713470"`). Primary key. | `silver/gie/agsi.py L320-339` |
| `start_at` | `datetime[UTC]` | Yes | `start_at` | Event start. Naïve `YYYY-MM-DD HH:MM:SS` parsed as UTC. | `silver/gie/agsi.py L287-298, L331-332` |
| `end_at` | `Optional[datetime]` | Yes | `end_at` | Often null for ongoing events. | `silver/gie/agsi.py L287-298, L331-332` |
| `title` | `Optional[str]` | Yes | `title` | Operator + summary line. | dynamic pass-through |
| `summary` | `Optional[str]` | Yes | `summary` | HTML-tagged short summary. | dynamic pass-through |
| `details` | `Optional[str]` | Yes | `details` | HTML-tagged full body. | dynamic pass-through |
| `entities` | `Optional[str]` | Yes | `entities` | JSON-encoded list of affected entity dicts (`{"name", "country", "eic"}` ± base64 `logo`). | `silver/gie/agsi.py L329-330` |
| `data_provider` | `str` | No (default `"gie_agsi"`) | _derived_ | Always `"gie_agsi"`. | `silver/gie/agsi.py L337` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver write timestamp. | `silver/gie/agsi.py L338` |

**PARQUET PATH:** `data/silver/gie_agsi/news/year=YYYY/month=MM/`
**PARTITION BY:** `start_at (year + month)`
**DEDUP KEY:** `(url,)` — falls back to `(id, turl, entity_code, eic)` per `AgsiJsonTransformer.unique` (`silver/gie/agsi.py L344-348`)

# Sample data

| url | start_at | end_at | title | summary (HTML) | entities (json) |
|---|---|---|---|---|---|
| 1713470 | 2026-05-05 11:00:00 | _null_ | Enovos Storage GmbH - Status update UGS Frankenthal | `<p>Missing reporting expected since 01/04/2026 - zero values confirmed</p>` | `[{"name":"Enovos Storage GmbH","country":"DE","eic":"21X-ENOVOS-STG"}]` |
| **1713185** | **2026-04-22 09:30:00** | **2026-05-15 18:00:00** | **astora GmbH — Rehden planned maintenance window** | **`<p>Planned outage window for Rehden facility 22 April → 15 May.</p>`** | **`[{"name":"astora GmbH","country":"DE","eic":"21X-WIEHE--K"}]`** |
| 1712984 | 2026-04-15 14:20:00 | _null_ | GSA LLC — Haidach historical data note | `<p>Historical pre-2022 data for Haidach is archived; querying returns current operator only.</p>` | `[{"name":"GSA LLC","country":"AT","eic":"25X-GSALLC-----E"}]` |
| 1712742 | 2026-04-08 10:00:00 | 2026-04-10 18:00:00 | TAQA — Bergermeer scheduled test | `<p>Safety test on Bergermeer, no withdrawal capacity 8-10 April.</p>` | `[{"name":"Bergermeer Operator","country":"NL","eic":"21X-BERGER-NL-G"}]` |
| 1712560 | 2026-04-01 12:00:00 | _null_ | EWE Gasspeicher — H-Gas Zone reporting delay | `<p>Reporting delay 1 April; values may be revised.</p>` | `[{"name":"EWE Gasspeicher","country":"DE","eic":"21X0000000011756"}]` |
| 1712345 | 2026-03-25 08:00:00 | 2026-03-27 18:00:00 | Storengy — Cerville maintenance | `<p>Planned outage 25-27 March.</p>` | `[{"name":"Storengy","country":"FR","eic":"21X-STORENGY---X"}]` |
| 1712098 | 2026-03-10 14:30:00 | _null_ | AGSI — daily refresh slot moved to 16:00 CET | `<p>From 10 March the AGSI daily refresh is at 16:00 CET (previously 17:00 CET).</p>` | `[]` |
| 1711845 | 2026-02-20 10:00:00 | _null_ | Snam — Italian storage methodology update | `<p>Snam updated its facility-level methodology; minor restatements possible.</p>` | `[{"name":"Snam","country":"IT","eic":"21X-SNAM------M"}]` |

**Sources:** Top row verbatim from vault Bronze sample (live Enovos Storage UGS Frankenthal announcement, 2026-05-08). Remaining 7 rows synthesised respecting the JSON-encoded `entities` shape, the naïve `YYYY-MM-DD HH:MM:SS` timestamp format, and realistic operator announcements. The highlighted **astora Rehden** announcement is the canonical use case: it pre-announces a planned outage on the Rehden facility, allowing storage models to mask `storage_reports` rows for `eic=21X-WIEHE--K` over 2026-04-22 → 2026-05-15. Note announcement `1712098` carries `entities: "[]"` — general AGSI announcements with no facility scope, useful as a "platform-wide caveat" filter.

# Dataset-specific section: Implementation phase = `deferred`

`news` is registered with `implementation_phase = "deferred"` in `endpoints.py L159` — the endpoint is documented and live-served, but not part of the gridflow v0.7 storage delivery. The connector handles it correctly; the silver transformer is registered (`silver/gie/agsi.py L628`); but production scheduling is deferred to a later phase. Treat as research-grade data, not yet production-promoted.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `agsi.gie.eu/api/news` (optional `?page=N&size=300`)
- AUTH: header `x-key` (LOWERCASE — `X-Key` returns 401), key from env `GIE_API_KEY`. Free registration at [agsi.gie.eu/account/registration](https://agsi.gie.eu/account/registration).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/gie_agsi/news/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.gie.agsi.NewsTransformer` (extends `AgsiJsonTransformer`, registered at `silver/gie/agsi.py L628`)

**Tab 1 — Example URL**
```
https://agsi.gie.eu/api/news?size=300

Header: x-key: $GIE_API_KEY
```

**Tab 2 — DuckDB · SQL**
```sql
-- Announcements affecting a specific facility EIC, last 1 year
SELECT url,
       start_at,
       end_at,
       title
FROM read_parquet('data/silver/gie_agsi/news/**/*.parquet')
WHERE entities LIKE '%"eic":"21X-WIEHE--K"%'
  AND start_at >= current_date - INTERVAL 1 YEAR
ORDER BY start_at DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl
import json

df = pl.read_parquet("data/silver/gie_agsi/news/**/*.parquet")
# Unwrap entities JSON and explode into one row per affected EIC
exploded = (
    df.with_columns(pl.col("entities").map_elements(json.loads, return_dtype=pl.List(pl.Object)))
      .explode("entities")
      .with_columns([
          pl.col("entities").struct.field("eic").alias("eic"),
          pl.col("entities").struct.field("country").alias("country"),
      ])
      .drop("entities")
)
print(exploded.head(20))
```

# Caveats

## 01 Live response carries no `last_page` / `total`

Catalog declares paginated; live response is a single ~2.6 MB envelope with 299 records and no pagination keys. Connector `_last_page` falls back to 1 — single-page behaviour is correct. *(Source: vault Implementation Delta.)*

## 02 `url` is a numeric ID, not a URL

Confusing naming: `url: 1713470` is the announcement primary key, not an HTTP link. Use as `turl=<url>` to fetch detail via `news_item` (though see `news_item` caveat — `turl` filter is silently ignored by the live API). *(Source: vault Known Issues.)*

## 03 Base64 logos inflate parquet size if untrimmed

Each `entities` element may carry a base64 PNG `logo` field; silver JSON-encodes the full array. Strip logos pre-ingest if parquet size matters. *(Source: vault Known Issues.)*

## 04 `end_at` frequently null for ongoing events

Reporting outages with no scheduled resumption have `end_at: null`. Treat null `end_at` as "still active" for masking logic. *(Source: vault Known Issues.)*

## 05 `x-key` header MUST be lowercase

`X-Key` returns HTTP 401. *(Source: vault Known Issues #1.)*

## 06 `implementation_phase = "deferred"` — not in v0.7 production cycle

Endpoint is documented + live-served and the silver transformer is registered, but production scheduling is deferred. *(Source: `endpoints.py L159`; vault Known Issues.)*

# Related datasets

- **`news_item`** — Per-announcement detail by `turl`. `as published` — would fetch one announcement's full HTML body if the upstream `turl` filter worked; currently zero-row in practice. `gie · news · as published`
- **`unavailability`** — Per-event outage records. `as published` — typically cross-referenced from the same operator advisories surfaced in `news`. Use unavailability for structured capacity data; use news for free-text context. `gie · storage · as published`
- **`storage_reports`** — Per-entity storage levels. `daily` — join `news.entities[].eic` ↔ `storage_reports.entity_code` and the `start_at` / `end_at` window to mask affected periods. `gie · storage · daily`
- **`storage`** — Country-level storage rollup. `daily` — for country-scoped news entries, mask the corresponding country rows. `gie · storage · daily`
