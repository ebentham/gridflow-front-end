---
source: gie_agsi
dataset_key: about_listing
vendor: GIE AGSI+ (Gas Storage)
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# GIE AGSI+ — About listing (flat operator and facility inventory)

## Overview

`about_listing` returns the same operator / facility universe as
`about_summary` but in a flat, list-shaped form via
`/api/about?show=listing`. Each list entry is a company dict carrying
its EIC, country, and a nested `facilities` array. This is the form
gridflow uses to plan expected counts for `storage_reports` queries
across `company` and `facility` scopes (see
`build_storage_query_plan` in `connectors/gie/endpoints.py`).

The dataset answers: "What companies and facilities does AGSI know
about, in machine-readable list form, with one record per row?" — used
for query inventory planning and deduplicating against `about_summary`.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://agsi.gie.eu` |
| Path             | `/api/about?show=listing` |
| Method           | GET |
| Auth             | header `x-key` (lowercase), key from env `GIE_API_KEY` |
| Rate limit       | 60 calls/minute. Connector throttles to 1 req/s. |
| Pagination       | None — single response. (No `last_page` / `total` fields in live response.) |
| Historical depth | Snapshot of current state. |
| Publication lag  | Refreshed when GIE updates the operator inventory. |
| Response format  | JSON (top-level **list** in live behaviour) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `show` | str | Yes | Must be `listing` to switch from the nested `about` form. | `show=listing` |

### Working curl example

```bash
# Replace <KEY> with $GIE_API_KEY
curl --ssl-no-revoke -X GET \
  "https://agsi.gie.eu/api/about?show=listing" \
  -H "x-key: <KEY>"
```

Live response: HTTP 200, ~53 KB, top-level list of 71 company objects.

---

## Bronze layer

**Path pattern**: `data/bronze/gie_agsi/about_listing/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON. Immutable.
**Granularity**: One file per fetch (weekly schedule per `config/sources.yaml`).

### Bronze sample

Live shape — top-level list (no `data` envelope):

```json
[
  {
    "name": "GSA LLC",
    "short_name": "GSA",
    "type": "SSO",
    "eic": "25X-GSALLC-----E",
    "country": "AT",
    "url": "https://agsi.gie.eu/api?country=AT&company=25X-GSALLC-----E",
    "facilities": [
      {
        "name": "UGS Haidach (GSA) // historical data prior to 6 Oct 2022",
        "type": "DSR",
        "eic": "25W-SPHAID-GAZ-M",
        "country": "AT",
        "company": "25X-GSALLC-----E",
        "url": "https://agsi.gie.eu/api?country=AT&company=25X-GSALLC-----E&facility=25W-SPHAID-GAZ-M",
        "operational_start_date": "2011-01-01",
        "operational_end_date": "2022-10-07"
      }
    ]
  }
]
```

The fixture (`tests/fixtures/gie/agsi_listing_response.json`) wraps the
list in a `{"data": [...]}` envelope. The connector parser
(`_listing_rows`) accepts either shape.

---

## Silver layer

**Path pattern**: `data/silver/gie_agsi/about_listing/year=YYYY/month=MM/about_listing_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.gie.agsi.AboutListingTransformer`
**Pydantic schema**: (no dedicated schema — reference data; rows are flattened companies + facilities)
**Dedup key**: `(entity_level, entity_code)`
**Point-in-time field**: none — snapshot reference table.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `entity_level` | `str` | No | derived | `company` or `facility`. |
| `entity_code` | `str` | No | `eic` | EIC identifier. |
| `entity_name` | `str` | No | `name` (or `short_name`) | |
| `country_code` | `str` | Yes | `country` | ISO-2. |
| `entity_type` | `str` | Yes | `type` | `SSO` for company, `DSR` for facility. |
| `entity_url` | `str` | Yes | `url` | |
| `company_code` | `str` | Yes | `company` | Facility-only. Parent company EIC. |
| `company_name` | `str` | Yes | derived | Facility-only. Filled from parent company `name`. |
| `data_provider` | `str` | No | derived | Always `gie_agsi`. |
| `ingested_at` | `datetime[UTC]` | No | derived | |

`AboutListingTransformer` extends `AgsiJsonTransformer`, so dynamic
columns from the live JSON (e.g. `operational_start_date`,
`operational_end_date`) are also passed through where present.

### Silver sample

```python
[
    {
        "entity_level": "company",
        "entity_code": "25X-GSALLC-----E",
        "entity_name": "GSA LLC",
        "country_code": "AT",
        "entity_type": "SSO",
        "entity_url": "https://agsi.gie.eu/api?country=AT&company=25X-GSALLC-----E",
        "data_provider": "gie_agsi",
        "ingested_at": datetime(2026, 5, 8, 17, 40, tzinfo=UTC),
    },
    {
        "entity_level": "facility",
        "entity_code": "25W-SPHAID-GAZ-M",
        "entity_name": "UGS Haidach (GSA) // historical data prior to 6 Oct 2022",
        "country_code": "AT",
        "entity_type": "DSR",
        "entity_url": "https://agsi.gie.eu/api?country=AT&company=25X-GSALLC-----E&facility=25W-SPHAID-GAZ-M",
        "company_code": "25X-GSALLC-----E",
        "company_name": "GSA LLC",
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
- No `last_page` / `total` / pagination fields in live response — single
  list of 71 companies (as of 2026-05-08).
- All values in **GWh** at the `storage` endpoints; this dataset is
  reference-only and carries no numeric storage values.
- Rate limit: 60 calls/min (1 req/s).
- Live response is a top-level **list**, fixture is a `{"data": [...]}`
  envelope. Connector parser `_listing_rows` accepts either.
- Two query-string forms work: `?show=listing` (documented and used by
  registry) and concatenating into the path; both return the same body.
- `operational_end_date` indicates a facility no longer reports —
  useful filter for current-snapshot inventory.
- Some companies have `country` as ISO-2 string (`"AT"`); the connector
  inventory parser treats it as a string. No nested country object in
  this endpoint.

---

## Implementation delta

- **Live shape**: top-level list. Fixture: `{"data": [...]}` envelope.
  Connector handles both via `_listing_rows`. Fixture is technically
  stale relative to live but still functionally compatible (logged here,
  not regenerated in V1).
- **Endpoint path**: registry `path = "/api/about"` with
  `default_params = {"show": "listing"}`. Equivalent to
  `/api/about?show=listing`. No discrepancy.
- **Pagination params**: catalog YAML declares
  `pagination.params: []` and live response has no pagination fields —
  consistent.

No discrepancies found.

---

## Modelling notes

- **Use**: entity inventory for query planning and joining facility-level
  storage data to companies. Not a modelling input on its own.
- **Joins**: `storage_reports` on `entity_code` for facility-level
  attribution; on `company_code` to roll facility data up to companies.
- **Filters**: `operational_end_date` not null → facility decommissioned;
  exclude from forward-looking inventory.

---

## Links

- [Official API docs](https://agsi.gie.eu/api)
- [Connector source](../../../../../Python/gridflow/src/gridflow/connectors/gie/client.py)
- [Endpoint registry](../../../../../Python/gridflow/src/gridflow/connectors/gie/endpoints.py)
- [Silver transformer](../../../../../Python/gridflow/src/gridflow/silver/gie/agsi.py)
- [Domain: gas day](../../../20-domain/concepts/gas-day.md)
