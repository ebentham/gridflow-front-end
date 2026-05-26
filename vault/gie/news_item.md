---
source: gie_agsi
dataset_key: news_item
vendor: GIE AGSI+ (Gas Storage)
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# GIE AGSI+ — News item (announcement detail by id)

## Overview

`news_item` is conceptually one AGSI announcement at a time, fetched
via `/api/news?turl=<id>`. The connector accepts a `turl` (or `id`)
param and is expected to return a single-record detail payload similar
to the fixture
(`tests/fixtures/gie/agsi_news_item_response.json`):
`{"data": {"turl": "...", "title": "...", ...}}`.

In live behaviour (2026-05-08), the AGSI endpoint silently **ignores**
the `turl` filter and returns the full news listing — see
Implementation delta. The connector's `_is_news_item_detail` filter
discards the listing-shaped response, so the dataset effectively yields
zero rows in practice, despite returning HTTP 200.

The dataset answers: "What is the full HTML / metadata of one
announcement, by ID?" — used to enrich `news` rows with the full
`details` body (e.g. for downstream parsing or UI rendering).

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://agsi.gie.eu` |
| Path             | `/api/news` (with `turl=<id>` param) |
| Method           | GET |
| Auth             | header `x-key` (lowercase), key from env `GIE_API_KEY` |
| Rate limit       | 60 calls/minute. Connector throttles to 1 req/s. |
| Pagination       | None expected (single-record detail). Live returns full listing — see delta. |
| Historical depth | All visible AGSI announcements. |
| Publication lag  | Real-time. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `turl` | str/int | Yes | Announcement ID (the numeric `url` value from the news listing). | `turl=1713470` |
| `id` | str/int | No | Connector alias for `turl` (`fetch(news_item, id=...)`). | `id=1713470` |

### Working curl example

```bash
# Replace <KEY> with $GIE_API_KEY
curl --ssl-no-revoke -X GET \
  "https://agsi.gie.eu/api/news?turl=1713470" \
  -H "x-key: <KEY>"
```

Live response (2026-05-08): HTTP 200, body identical to `/api/news`
(same 2.6 MB listing, 299 records). The `turl` filter is silently
ignored.

---

## Bronze layer

**Path pattern**: `data/bronze/gie_agsi/news_item/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON. Immutable.
**Granularity**: One file per announcement ID requested.

### Bronze sample

Fixture-shape (expected, from
`tests/fixtures/gie/agsi_news_item_response.json`):

```json
{
  "data": {
    "turl": "demo-maintenance",
    "title": "Planned maintenance detail",
    "summary": "Storage maintenance announcement",
    "details": "Detailed sanitized announcement body.",
    "start_at": "2026-05-01T00:00:00Z",
    "end_at": "2026-05-02T00:00:00Z",
    "entities": [{"code": "21W-DEMO-ALPHA-1", "name": "Alpha One"}]
  }
}
```

Live behaviour (observed): the response is `{"data": [299 records]}`
— a list, not a single record. The connector's
`_is_news_item_detail()` returns `False` for this shape and the
response is discarded with a `Discarded listing-shaped AGSI news_item
response` warning.

---

## Silver layer

**Path pattern**: `data/silver/gie_agsi/news_item/year=YYYY/month=MM/news_item_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.gie.agsi.NewsItemTransformer`
**Pydantic schema**: (no dedicated schema — dynamic columns from `AgsiJsonTransformer`)
**Dedup key**: `(turl,)` — falls back to `(id, url, entity_code)` if `turl` is absent.
**Point-in-time field**: `updated_at` if present, else `start_at`.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `turl` | `str` | No | `turl` | Announcement ID. |
| `title` | `str` | Yes | `title` | |
| `summary` | `str` | Yes | `summary` | HTML-tagged. |
| `details` | `str` | Yes | `details` | HTML-tagged. |
| `start_at` | `datetime[UTC]` | Yes | `start_at` | |
| `end_at` | `datetime[UTC]` | Yes | `end_at` | |
| `entities` | `str` | Yes | `entities` | JSON-encoded list. |
| `data_provider` | `str` | No | derived | Always `gie_agsi`. |
| `ingested_at` | `datetime[UTC]` | No | derived | |

### Silver sample

```python
[
    {
        "turl": "demo-maintenance",
        "title": "Planned maintenance detail",
        "summary": "Storage maintenance announcement",
        "details": "Detailed sanitized announcement body.",
        "start_at": datetime(2026, 5, 1, 0, 0, tzinfo=UTC),
        "end_at": datetime(2026, 5, 2, 0, 0, tzinfo=UTC),
        "entities": '[{"code": "21W-DEMO-ALPHA-1", "name": "Alpha One"}]',
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
- **Live `turl` filter is ignored** — `/api/news?turl=<id>` returns the
  full listing identical to `/api/news` (verified 2026-05-08, body
  size 2.6 MB, 299 records, byte-for-byte equal). The connector's
  `_is_news_item_detail` discards the listing shape, so the silver row
  count for this dataset is effectively zero against the current API
  build.
- The catalog YAML and registry default-params still use
  `default_params={"turl": "{id}"}`. This is the documented form, even
  though it has no effect on the live response.
- `last_page` is the pagination source of truth (not `total`) — but
  this endpoint is single-record by design, so pagination is N/A.
- Values in **GWh** elsewhere; news_item carries no numeric values.
- Rate limit: 60 calls/min (1 req/s).
- The implementation phase is `deferred` in the catalog (not part of
  v0.7 storage delivery), but the endpoint is documented and live-served.

---

## Implementation delta

- **`turl` filter ignored upstream**: live `/api/news?turl=1713470`
  returns the full listing, not the single item. Documentation is
  ambiguous about whether `turl` is the correct param. Connector
  defends against this via `_is_news_item_detail` shape filter — but
  the result is a zero-row silver output.
- **Path documented as `/api/news?turl={id}` in catalog YAML**;
  registry uses `default_params = {"turl": "{id}"}` and same path
  `/api/news`. Equivalent. No discrepancy.
- **Single-record vs list shape**: fixture is single-record;
  live is list. Connector treats list as "not a detail" and drops it,
  which is the correct conservative behaviour but means the dataset
  produces no silver rows currently.

No discrepancies found in connector behaviour. Live-API behaviour
discrepancy logged in this delta.

---

## Modelling notes

- **Use**: enrichment for `news` rows when full HTML body is needed
  for parsing (e.g. extracting structured outage windows from free
  text). Currently effectively unused since `turl` filter is broken.
- **Filters**: would join `news.url` ↔ `news_item.turl` once the
  upstream filter behaves.

---

## Links

- [Official API docs](https://agsi.gie.eu/api)
- [Connector source](../../../../../Python/gridflow/src/gridflow/connectors/gie/client.py)
- [Endpoint registry](../../../../../Python/gridflow/src/gridflow/connectors/gie/endpoints.py)
- [Silver transformer](../../../../../Python/gridflow/src/gridflow/silver/gie/agsi.py)
- [Domain: gas day](../../../20-domain/concepts/gas-day.md)
