---
source: gie_agsi
dataset_key: about_summary
vendor: GIE AGSI+ (Gas Storage)
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# GIE AGSI+ — About summary (operator and facility reference, hierarchical)

## Overview

`about_summary` is the AGSI reference / discovery payload returned by
`/api/about` (no `show` parameter). It enumerates AGSI Storage System
Operators (SSOs) and their facilities organised by region and country in
a nested object: `SSO → Europe → <Country> → [companies...]`. Each
company carries metadata (EIC, type, image logo) and a `facilities`
array with operational start / end dates.

The dataset answers: "What companies and facilities exist on the AGSI
platform, with what EICs, in which countries?" It is the entity master
file for storage. Used at silver level to enrich
`storage`/`storage_reports` with company / facility names and to plan
expected bronze counts.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://agsi.gie.eu` |
| Path             | `/api/about` |
| Method           | GET |
| Auth             | header `x-key` (lowercase), key from env `GIE_API_KEY` |
| Rate limit       | 60 calls/minute. Connector throttles to 1 req/s. |
| Pagination       | None — single response. (No `last_page` / `total` fields.) |
| Historical depth | Snapshot of current state. |
| Publication lag  | Refreshed when GIE updates the operator inventory. |
| Response format  | JSON (nested object) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| (none) | — | — | The default `about` payload requires no query params. | — |

### Working curl example

```bash
# Replace <KEY> with $GIE_API_KEY
curl --ssl-no-revoke -X GET \
  "https://agsi.gie.eu/api/about" \
  -H "x-key: <KEY>"
```

Live response is ~558 KB JSON.

---

## Bronze layer

**Path pattern**: `data/bronze/gie_agsi/about_summary/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON. Immutable.
**Granularity**: One file per fetch (weekly schedule per `config/sources.yaml`).

### Bronze sample

Top-level keys: `["SSO"]`. The `SSO` key holds a region tree. Truncated
sample:

```json
{
  "SSO": {
    "Europe": {
      "Austria": [
        {
          "image": "iVBORw0K... (base64 PNG)",
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
              "operational_start_date": "2011-01-01",
              "operational_end_date": "2022-10-07"
            }
          ]
        }
      ]
    }
  }
}
```

---

## Silver layer

**Path pattern**: `data/silver/gie_agsi/about_summary/year=YYYY/month=MM/about_summary_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.gie.agsi.AboutSummaryTransformer`
**Pydantic schema**: (no dedicated schema — this is reference data; rows are flattened companies + facilities)
**Dedup key**: `(entity_level, entity_code)`
**Point-in-time field**: none — snapshot reference table.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `entity_level` | `str` | No | derived | `company` or `facility`. |
| `entity_code` | `str` | No | `eic` (or `code`) | EIC identifier. |
| `entity_name` | `str` | No | `name` (or `short_name`) | |
| `short_name` | `str` | Yes | `short_name` | |
| `country_code` | `str` | Yes | `country.code` (or string `country`) | |
| `country_name` | `str` | Yes | `country.name` | |
| `entity_type` | `str` | Yes | `type` | `SSO` for company, `DSR` for facility. |
| `operational_start_date` | `str` | Yes | `operational_start_date` | Facility-only. ISO date. |
| `operational_end_date` | `str` | Yes | `operational_end_date` | Facility-only. ISO date. |
| `company_code` | `str` | Yes | `company` | Facility-only. Parent company EIC. |
| `company_name` | `str` | Yes | derived | Facility-only. |
| `aggregate_code` | `str` | Yes | `data.code` | Optional — present if response is shaped as company `data` envelope. |
| `aggregate_name` | `str` | Yes | `data.name` | Optional. |
| `publication_link` | `str` | Yes | `publication_link` | Company-only. |
| `transparency_template` | `str` | Yes | `transparency_template` | Company-only. |
| `operational_information` | `str` | Yes | `operational_information` | Company-only. |
| `available_capacities` | `str` | Yes | `available_capacities` | Company-only. |
| `tariffs` | `str` | Yes | `tariffs` | Company-only. |
| `has_image` | `bool` | No | derived | True if base64 logo present. |
| `data_provider` | `str` | No | derived | Always `gie_agsi`. |
| `ingested_at` | `datetime[UTC]` | No | derived | |

### Silver sample

```python
[
    {
        "entity_level": "company",
        "entity_code": "25X-GSALLC-----E",
        "entity_name": "GSA LLC",
        "short_name": "GSA",
        "country_code": "AT",
        "country_name": None,
        "entity_type": "SSO",
        "has_image": True,
        "data_provider": "gie_agsi",
        "ingested_at": datetime(2026, 5, 8, 17, 40, tzinfo=UTC),
    },
    {
        "entity_level": "facility",
        "entity_code": "25W-SPHAID-GAZ-M",
        "entity_name": "UGS Haidach (GSA) // historical data prior to 6 Oct 2022",
        "country_code": "AT",
        "country_name": None,
        "entity_type": "DSR",
        "operational_start_date": "2011-01-01",
        "operational_end_date": "2022-10-07",
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
- No `last_page` / `total` / pagination fields — `/api/about` is a single
  monolithic response (~558 KB).
- All values in **GWh** at the `storage` endpoints; this dataset is
  reference-only and carries no numeric storage values.
- Rate limit: 60 calls/min (1 req/s).
- The live response shape is `{"SSO": {"Europe": {<Country>: [...]}}}`
  — different from the fixture
  (`tests/fixtures/gie/agsi_about_summary_response.json`), which uses a
  flat envelope with `data.platform`, `data.totalCompanies`, etc. The
  silver transformer (`_about_summary_companies`) recurses into the
  nested object and pulls out any dict with a `facilities` list, so it
  handles both shapes — but the fixture is stale relative to live
  behaviour.
- `image` field carries base64-encoded PNG logos; `has_image` is the
  silver-level summarisation. Bronze keeps the raw bytes.
- Facility `operational_end_date` indicates a facility no longer
  reports — useful filter for storage analyses.

---

## Implementation delta

- **Live response shape**: `{"SSO": {"Europe": {<Country>: [...]}}}`.
  Fixture has `{"data": {"platform": "AGSI", "totalCompanies": "3", ...}}`.
  The silver transformer copes via recursive descent, but the fixture is
  stale and should be regenerated to match live shape (logged here, NOT
  fixed in V1 — fixture regeneration is out of scope).
- **`country` value type**: in the live response `country` is a string
  (e.g. `"AT"`), not a dict with `.code`/`.name` as some `_nested_text`
  paths assume. The transformer handles both via `_nested_text`'s
  `key == "code"` fallback returning `str(value)`.
- **No documented response key**: catalog YAML declares
  `response_key: data` but the live response has no `data` envelope.
  Reading is via the recursive `_about_summary_companies` walker —
  works as long as no `show=` param is passed.

---

## Modelling notes

- **Use**: entity master / dimensional table for joining onto storage
  facts. Not a modelling input on its own.
- **Joins**: `storage_reports` / `storage` on `entity_code` / `eic`
  to attach company-name labels to facility-level rows.
- **Filters**: `operational_end_date` not null → facility decommissioned;
  exclude from forward-looking inventory.

---

## Links

- [Official API docs](https://agsi.gie.eu/api)
- [Connector source](../../../../../Python/gridflow/src/gridflow/connectors/gie/client.py)
- [Endpoint registry](../../../../../Python/gridflow/src/gridflow/connectors/gie/endpoints.py)
- [Silver transformer](../../../../../Python/gridflow/src/gridflow/silver/gie/agsi.py)
- [Domain: gas day](../../../20-domain/concepts/gas-day.md)
