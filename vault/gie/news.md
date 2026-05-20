---
source: gie_agsi
dataset_key: news
vendor: GIE AGSI+ (Gas Storage)
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# GIE AGSI+ — News (service-announcement listing)

## Overview

`news` returns the AGSI service-announcement / news listing — operator
notices about reporting issues, planned data outages, and corrections.
Each entry carries a numeric `url` (announcement ID), `start_at` /
`end_at` window, `title`, `summary`, `details` (HTML), and an
`entities` array describing affected companies / facilities.

The dataset answers: "What operator advisories or data caveats apply
right now to AGSI gas-storage data?" — used to flag suspect periods in
storage time-series, attribute outages, and explain anomalous trends.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://agsi.gie.eu` |
| Path             | `/api/news` |
| Method           | GET |
| Auth             | header `x-key` (lowercase), key from env `GIE_API_KEY` |
| Rate limit       | 60 calls/minute. Connector throttles to 1 req/s. |
| Pagination       | Catalog YAML declares `last_page`/`total` pagination, but live response (2026-05-08) returns a single envelope with 299 records and **no `last_page` or `total` fields**. See Implementation delta. |
| Historical depth | All visible AGSI announcements (~2-3 years rolling). |
| Publication lag  | Real-time when AGSI staff publish. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `page` | int | No | Page number, 1-indexed. Default 1. Honoured per catalog; live response did not paginate. | `page=2` |
| `size` | int | No | Page size. Default 30, max 300. | `size=300` |

### Working curl example

```bash
# Replace <KEY> with $GIE_API_KEY
curl --ssl-no-revoke -X GET \
  "https://agsi.gie.eu/api/news" \
  -H "x-key: <KEY>"
```

Live response: HTTP 200, ~2.6 MB, `{"data": [299 records]}`.

---

## Bronze layer

**Path pattern**: `data/bronze/gie_agsi/news/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON. Immutable.
**Granularity**: One file per fetch.

### Bronze sample

```json
{
  "data": [
    {
      "url": 1713470,
      "start_at": "2026-05-05 11:00:00",
      "end_at": null,
      "title": "Enovos Storage GmbH - Status update UGS Frankenthal",
      "summary": "<p>Missing reporting expected since 01/04/2026 - zero values confirmed</p>",
      "details": "<p>Enovos Storage GmbH confirms the zero values (storage empty) since 1 April 2026. ...</p>",
      "entities": [
        {
          "name": "Enovos Storage GmbH",
          "logo": "iVBORw0K... (base64 PNG)",
          "country": "DE",
          "eic": "21X-ENOVOS-STG"
        }
      ]
    }
  ]
}
```

Note the live response has **no `last_page` / `total`** keys at the top
level — only `data`. The fixture
(`tests/fixtures/gie/agsi_news_response.json`) does include them.

---

## Silver layer

**Path pattern**: `data/silver/gie_agsi/news/year=YYYY/month=MM/news_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.gie.agsi.NewsTransformer`
**Pydantic schema**: (no dedicated schema — `AgsiJsonTransformer` produces dynamic columns)
**Dedup key**: `(url,)` — falls back to `(id, turl, entity_code, eic)` per `AgsiJsonTransformer.unique` logic.
**Point-in-time field**: `updated_at` if present, else `start_at`.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `url` | `str` | No | `url` | Numeric announcement ID, stored as text. |
| `start_at` | `datetime[UTC]` | Yes | `start_at` | Event start. Format `YYYY-MM-DD HH:MM:SS` UTC. |
| `end_at` | `datetime[UTC]` | Yes | `end_at` | Often null. |
| `title` | `str` | Yes | `title` | |
| `summary` | `str` | Yes | `summary` | HTML-tagged. |
| `details` | `str` | Yes | `details` | HTML-tagged. |
| `entities` | `str` | Yes | `entities` | JSON-encoded list of affected entity dicts. |
| `data_provider` | `str` | No | derived | Always `gie_agsi`. |
| `ingested_at` | `datetime[UTC]` | No | derived | |

### Silver sample

```python
[
    {
        "url": "1713470",
        "start_at": datetime(2026, 5, 5, 11, 0, tzinfo=UTC),
        "end_at": None,
        "title": "Enovos Storage GmbH - Status update UGS Frankenthal",
        "summary": "<p>Missing reporting expected since 01/04/2026 - zero values confirmed</p>",
        "details": "<p>Enovos Storage GmbH confirms the zero values (storage empty) ...</p>",
        "entities": '[{"name": "Enovos Storage GmbH", "country": "DE"}]',
        "data_provider": "gie_agsi",
        "ingested_at": datetime(2026, 5, 8, 17, 40, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- Lowercase `x-key` header. Capitalised `X-Key` returns 401.
- `last_page` and `total` are documented as the pagination source of
  truth, but the **live `/api/news` response (2026-05-08) returns
  neither** — the entire 299-record listing comes back in a single body
  (~2.6 MB). The fallback `_last_page` returns 1, so the connector
  does not loop. Effectively a single-page response in practice.
- Values in **GWh** elsewhere; news carries no numeric values.
- Rate limit: 60 calls/min (1 req/s).
- Each `entities` element may contain a base64 logo (`logo` field) —
  silver JSON-encodes the array, which inflates parquet size if not
  trimmed.
- `end_at` is frequently null for ongoing events (e.g. ongoing reporting
  outages with no scheduled resumption).
- The implementation phase is `deferred` in the catalog (not part of
  the v0.7 storage delivery), but the endpoint is documented and
  live-served.
- `url` is a numeric ID, not a URL. Use it as a `turl` to fetch one
  item via `/api/news?turl=<url>` (but see `news_item` page —
  `turl` filtering is silently ignored on the live endpoint).

---

## Implementation delta

- **Pagination metadata absent on live**: catalog YAML declares
  `authoritative_total_pages: last_page` and `per_page_count: total`.
  Live response (2026-05-08) contains neither — only `data`. Connector
  `_last_page` falls through to default 1, so behaviour is correct
  (single page), but the docs claim is unverifiable from this snapshot.
- **No `turl` field**: catalog YAML and code `_news_item_turls` look for
  `turl`, `url`, or `id`. Live response has only `url` (numeric). The
  fallback to `url` already covers this.
- **Fixture vs live**: fixture wraps the same record set in
  `{"last_page": 1, "total": 1, "data": [1 record]}`. Live has no
  `last_page` / `total`. Fixture is structurally compatible with the
  parser but does not match live behaviour.

No discrepancies found in connector behaviour.

---

## Modelling notes

- **Use**: data-quality flags. Join storage time-series on
  `entities[].eic` and the `start_at` / `end_at` window to mask
  affected periods.
- **Filters**: drop rows older than the storage window of interest;
  drop entries with no `entities` (general AGSI announcements).
- **Joins**: `storage_reports.entity_code` ↔ `news.entities[].eic`
  for facility-level data masking.

---

## Links

- [Official API docs](https://agsi.gie.eu/api)
- [Connector source](../../../../../Python/gridflow/src/gridflow/connectors/gie/client.py)
- [Endpoint registry](../../../../../Python/gridflow/src/gridflow/connectors/gie/endpoints.py)
- [Silver transformer](../../../../../Python/gridflow/src/gridflow/silver/gie/agsi.py)
- [Domain: gas day](../../../20-domain/concepts/gas-day.md)
