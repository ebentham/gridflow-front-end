---
slug: news_item
vendor: gie
vendor_label: GIE AGSI+ (Gas Storage)
api_code: AGSI
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "GIE API key (header `x-key`, lowercase) required — free registration at agsi.gie.eu/account/registration"
sources_consulted:
  - vault/gie/news_item.md
  - gridflow/src/gridflow/schemas/gie.py (no dedicated schema — AgsiJsonTransformer dynamic columns)
  - gridflow/src/gridflow/silver/gie/agsi.py::NewsItemTransformer (lines 451-462, extends AgsiJsonTransformer with _is_news_item_detail filter; registered at L629)
  - gridflow/src/gridflow/connectors/gie/endpoints.py::ENDPOINTS["news_item"] (lines 162-169, implementation_phase="deferred")
  - https://agsi.gie.eu/api/news (vendor docs — interactive HTML; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault news_item.md — Known Issues: turl filter ignored"
    source_a_says: "Live `/api/news?turl=<id>` returns the full listing identical to `/api/news` (verified 2026-05-08, byte-for-byte equal, 299 records)"
    source_b: "fixture (tests/fixtures/gie/agsi_news_item_response.json) is a single-record `{\"data\": {turl, title, ...}}` shape"
    orchestrator_recommendation: "non-blocking — connector's `_records_from_payload` override discards list-shaped responses (`silver/gie/agsi.py L456-462`); dataset yields zero rows in practice against the current API build. Flag in caveats."
  - source_a: "vault — implementation_phase"
    source_a_says: "Registered as `implementation_phase = \"deferred\"` in endpoints.py L167"
    source_b: "endpoint is live-served and documented"
    orchestrator_recommendation: "treat as research-grade; not yet promoted to v0.7 production."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** One AGSI announcement, <span class="italic fg-accent">fetched by id.</span>

**Lede:** Per-announcement detail endpoint — the (currently broken) per-`turl` lookup for full HTML announcement bodies; effectively zero-row against the live API as of 2026-05-08.

**Verified line:** Verified against vendor docs: 2026-05-08 · [GIE AGSI+ · /api/news?turl=…](https://agsi.gie.eu/api/news)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.gie_agsi.news_item` |
| API PATH | `/api/news?turl={id}` |
| FREQUENCY | as published |
| PUBLICATION LAG | real-time |
| VOLUME | 0 rows / fetch (live API ignores `turl`) |
| PRIMARY KEY | `(turl,)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | as published | Cadence |
| 2 | 0 | Rows / fetch (live) |
| 3 | deferred | Implementation phase |
| 4 | filter ignored | Upstream defect |

# Sidebar siblings

- news
- unavailability
- storage
- storage_reports
- about_summary

# Sample chart

- **Type:** `sparkline`
- **Title:** "AGSI news_item silver row count · last 90 days"
- **Subtitle:** "Sparkline · rows / day · flat at zero — turl filter ignored upstream"
- **Seed:** 99
- **Toggles:** `30d` / `90d` (active)

# Schema

No dedicated Pydantic schema — `NewsItemTransformer` extends `AgsiJsonTransformer` and overrides `_records_from_payload` (`silver/gie/agsi.py L456-462`) to **discard list-shaped responses** (which is what the live API returns). The schema below is the *expected* fixture shape; in practice silver rows are zero against the current API build. Columns mirror `news` but keyed on `turl` instead of `url`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `turl` | `str` | No | `turl` | Announcement ID (the numeric `url` value from the news listing). Primary key. | `silver/gie/agsi.py L344-348` |
| `title` | `Optional[str]` | Yes | `title` | | dynamic pass-through |
| `summary` | `Optional[str]` | Yes | `summary` | HTML-tagged short summary. | dynamic pass-through |
| `details` | `Optional[str]` | Yes | `details` | HTML-tagged full body — the enrichment payload this dataset is intended for. | dynamic pass-through |
| `start_at` | `datetime[UTC]` | Yes | `start_at` | Event start. | `silver/gie/agsi.py L287-298, L331-332` |
| `end_at` | `Optional[datetime]` | Yes | `end_at` | Often null. | `silver/gie/agsi.py L287-298, L331-332` |
| `entities` | `Optional[str]` | Yes | `entities` | JSON-encoded list of affected entity dicts. | `silver/gie/agsi.py L329-330` |
| `data_provider` | `str` | No (default `"gie_agsi"`) | _derived_ | Always `"gie_agsi"`. | `silver/gie/agsi.py L337` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver write timestamp. | `silver/gie/agsi.py L338` |

**PARQUET PATH:** `data/silver/gie_agsi/news_item/year=YYYY/month=MM/`
**PARTITION BY:** `start_at (year + month)` — would partition this way if rows were produced
**DEDUP KEY:** `(turl,)` — falls back to `(id, url, entity_code)` per `AgsiJsonTransformer.unique` (`silver/gie/agsi.py L344-348`)

# Sample data

Live API returns the full news listing (299 records, 2.6 MB) regardless of `turl` param. `NewsItemTransformer._records_from_payload` discards list-shaped responses (`silver/gie/agsi.py L456-458`), so the silver output is empty. The fixture-shape sample below represents the *intended* schema if the upstream `turl` filter behaved as documented.

| turl | title | start_at | end_at | summary | details | entities (json) |
|---|---|---|---|---|---|---|
| demo-maintenance | Planned maintenance detail | 2026-05-01 00:00:00 | 2026-05-02 00:00:00 | `Storage maintenance announcement` | `Detailed sanitized announcement body.` | `[{"code":"21W-DEMO-ALPHA-1","name":"Alpha One"}]` |
| **1713185** | **astora GmbH — Rehden planned maintenance window** | **2026-04-22 09:30:00** | **2026-05-15 18:00:00** | `<p>Planned outage 22 April → 15 May.</p>` | `<p>Detailed methodology and capacity-reduction figures for the Rehden planned maintenance window…</p>` | `[{"name":"astora GmbH","eic":"21X-WIEHE--K"}]` |
| 1713470 | Enovos Storage GmbH - Status update UGS Frankenthal | 2026-05-05 11:00:00 | _null_ | `<p>Missing reporting expected since 01/04/2026 - zero values confirmed</p>` | `<p>Full operator note explaining the zero-value period…</p>` | `[{"name":"Enovos Storage GmbH","eic":"21X-ENOVOS-STG"}]` |
| 1712984 | GSA LLC — Haidach historical data note | 2026-04-15 14:20:00 | _null_ | `<p>Historical pre-2022 data archived</p>` | `<p>Pre-2022 Haidach reporting was operated by a predecessor; queries return current GSA-only data.</p>` | `[{"name":"GSA LLC","eic":"25X-GSALLC-----E"}]` |
| 1712742 | TAQA — Bergermeer scheduled test | 2026-04-08 10:00:00 | 2026-04-10 18:00:00 | `<p>Safety test, no withdrawal capacity 8-10 April</p>` | `<p>Full safety-test methodology and capacity-reduction figures for Bergermeer.</p>` | `[{"name":"Bergermeer Operator","eic":"21X-BERGER-NL-G"}]` |
| 1712560 | EWE Gasspeicher — H-Gas Zone reporting delay | 2026-04-01 12:00:00 | _null_ | `<p>Reporting delay 1 April; values may be revised</p>` | `<p>Detailed note on the reporting-delay cause and estimated revision timing.</p>` | `[{"name":"EWE Gasspeicher","eic":"21X0000000011756"}]` |
| 1712345 | Storengy — Cerville maintenance | 2026-03-25 08:00:00 | 2026-03-27 18:00:00 | `<p>Planned outage 25-27 March</p>` | `<p>Full Cerville maintenance methodology and capacity-reduction figures.</p>` | `[{"name":"Storengy","eic":"21X-STORENGY---X"}]` |
| 1712098 | AGSI — daily refresh slot moved to 16:00 CET | 2026-03-10 14:30:00 | _null_ | `<p>From 10 March daily refresh at 16:00 CET</p>` | `<p>Detailed change note with operational impact.</p>` | `[]` |

**Sources:** First row (`demo-maintenance`) verbatim from vault fixture (`agsi_news_item_response.json`). Remaining 7 rows are the fixture-shape projections of corresponding `news` listing entries — synthesised to show what the dataset *would* contain if the upstream `turl` filter behaved as documented. The highlighted **astora Rehden** row is the canonical enrichment use case: full HTML body parseable for structured outage methodology. Live API yields zero rows for this dataset until the upstream filter is fixed.

# Dataset-specific section: Connector defence against the broken filter

`NewsItemTransformer._records_from_payload` (`silver/gie/agsi.py L456-462`):

```python
def _records_from_payload(self, payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return []
    records = super()._records_from_payload(payload)
    if records:
        return records
    return [payload] if isinstance(payload, dict) else []
```

Logic:
1. If payload's `data` is a list → it's the full `news` listing, not a per-item detail. **Discard with zero rows.**
2. Else delegate to the base `AgsiJsonTransformer._records_from_payload` (`response_key="data"` extraction).
3. If that returns nothing, treat the whole payload as a single-record detail (the fixture shape).

This is the correct conservative behaviour: zero rows is better than 299 duplicates of the listing.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `agsi.gie.eu/api/news?turl={id}` (live API ignores the `turl` filter — see Caveats #01)
- AUTH: header `x-key` (LOWERCASE — `X-Key` returns 401), key from env `GIE_API_KEY`. Free registration at [agsi.gie.eu/account/registration](https://agsi.gie.eu/account/registration).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/gie_agsi/news_item/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.gie.agsi.NewsItemTransformer` (extends `AgsiJsonTransformer`, registered at `silver/gie/agsi.py L629`)

**Tab 1 — Example URL**
```
https://agsi.gie.eu/api/news?turl=1713470

Header: x-key: $GIE_API_KEY
```

**Tab 2 — DuckDB · SQL**
```sql
-- All news_item rows for a specific announcement turl
-- (Currently zero results — live `turl` filter is ignored upstream)
SELECT turl,
       start_at,
       end_at,
       title,
       details
FROM read_parquet('data/silver/gie_agsi/news_item/**/*.parquet')
WHERE turl = '1713470'
ORDER BY start_at DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

# Fallback: until the upstream `turl` filter is fixed, derive news_item-style enrichment
# from the news listing directly. Same primary key (url ↔ turl), same fields available.
news = pl.read_parquet("data/silver/gie_agsi/news/**/*.parquet")
detail = news.filter(pl.col("url") == "1713470").select(
    pl.col("url").alias("turl"),
    "title", "summary", "details", "start_at", "end_at", "entities",
)
print(detail)
```

# Caveats

## 01 Live `turl` filter is silently ignored

`/api/news?turl=<id>` returns the full 299-record listing byte-for-byte identical to `/api/news` (verified 2026-05-08, 2.6 MB). Connector's `_is_news_item_detail` discards the list shape, so silver yields zero rows. *(Source: vault Known Issues; live 2026-05-08.)*

## 02 Implementation phase = `deferred`

Registered as `implementation_phase = "deferred"` (`endpoints.py L167`) — not part of the gridflow v0.7 storage delivery. Endpoint is documented + live-served, but production scheduling is deferred. *(Source: vault Known Issues.)*

## 03 No Pydantic schema — `AgsiJsonTransformer` dynamic columns

Like other AGSI reference / news datasets, no typed silver contract; columns are dynamic. *(Source: vault Silver layer note; `silver/gie/agsi.py L451-462`.)*

## 04 `x-key` header MUST be lowercase

`X-Key` returns HTTP 401. *(Source: vault Known Issues #1.)*

## 05 Workaround: read from `news` directly

Until the upstream `turl` filter behaves, derive `news_item`-style per-announcement enrichment from the `news` dataset on `url` (`url` and `turl` are the same identifier). *(Source: domain knowledge + Tab 3 above.)*

# Related datasets

- **`news`** — Full announcement listing (the same data this dataset would page through if the `turl` filter worked). `as published` — currently the only working source of per-announcement HTML detail. `gie · news · as published`
- **`unavailability`** — Structured outage records. `as published` — many `news` / `news_item` advisories are paraphrases of `unavailability` events; prefer `unavailability` for structured capacity data. `gie · storage · as published`
- **`storage_reports`** — Per-entity storage levels. `daily` — would join on `news_item.entities[].eic` ↔ `storage_reports.entity_code` for facility-level masking once the filter is fixed. `gie · storage · daily`
- **`about_summary`** — Operator inventory. `snapshot` — supplies the company / facility EICs and human-readable names referenced inside `news_item.entities` JSON. `gie · storage · snapshot`
