---
source: gie_agsi
dataset_key: unavailability
vendor: GIE AGSI+ (Gas Storage)
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# GIE AGSI+ — Unavailability (storage outage and maintenance reports)

## Overview

`unavailability` returns AGSI's storage-outage / planned-maintenance
records — per-event entries with `start` / `end` windows, affected
country / company / facility, the reduced `volume`, an `injection` /
`withdrawal` capacity reduction, a free-text `description`, and a
`type` (`Planned`, `Unplanned`, ...).

The dataset answers: "Which AGSI storage facilities are out, when, and
how much capacity is missing?" — a critical input for short-term
withdrawal-capacity forecasts, fundamental gas-spread trades, and
explaining sudden capacity reductions in `storage_reports` /
`storage`.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://agsi.gie.eu` |
| Path             | `/api/unavailability` |
| Method           | GET |
| Auth             | header `x-key` (lowercase), key from env `GIE_API_KEY` |
| Rate limit       | 60 calls/minute. Connector throttles to 1 req/s. |
| Pagination       | `last_page` is the source of truth; `total` is the per-page row count. Iterate `page=1..last_page`. |
| Historical depth | All visible AGSI unavailability records (typically multi-year). |
| Publication lag  | Real-time when operators report. `published` field per record. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `country` | str | No | ISO-2 country code. Filters by affected country. | `country=DE` |
| `company` | str | No | Company EIC. | `company=21X0000000011756` |
| `facility` | str | No | Facility EIC. | `facility=37W000000000002O` |
| `start` | str (YYYY-MM-DD) | No | Range start. **Used by the connector and registry**. | `start=2026-04-01` |
| `end` | str (YYYY-MM-DD) | No | Range end (inclusive). | `end=2026-05-07` |
| `from` | str (YYYY-MM-DD) | No | Alternate range start. Live API also accepts this — produces a different `last_page`. | `from=2026-04-01` |
| `to` | str (YYYY-MM-DD) | No | Alternate range end. | `to=2026-05-07` |
| `page` | int | No | Page number, 1-indexed. | `page=2` |
| `size` | int | No | Page size. Default 30, max 300. | `size=300` |

### Working curl example

```bash
# Replace <KEY> with $GIE_API_KEY
curl --ssl-no-revoke -X GET \
  "https://agsi.gie.eu/api/unavailability?country=DE&start=2026-04-01&end=2026-05-07" \
  -H "x-key: <KEY>"
```

Live response (DE, 2026-05-08): HTTP 200, ~14 KB,
`{"last_page": 7, "total": 30, "data": [30 records]}`.

GB returned `{"last_page": 1, "total": 0, "data": []}` — empty by
design (no UK storage outages reported on AGSI).

---

## Bronze layer

**Path pattern**: `data/bronze/gie_agsi/unavailability/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON. Immutable.
**Granularity**: One file per (page, country, window) call.

### Bronze sample

Live (DE, page 1):

```json
{
  "last_page": 7,
  "total": 30,
  "dataset": "<a href=\"/unavailability/gantt/DE\">Germany</a>",
  "data": [
    {
      "published": "2026-05-08 10:40:07",
      "country": {"name": "Germany", "code": "DE"},
      "company": {"name": "EWE Gasspeicher", "eic": "21X0000000011756"},
      "facility": {"name": "EWE H-Gas Zone", "eic": "37W000000000002O"},
      "start": "2026-05-04 06:00:00",
      "end": "2026-05-08 12:00:00",
      "volume": "3.004",
      "injection": "41.4",
      "withdrawal": "82.8",
      "description": "safety test / maintenance work (only Huntorf is influenced)",
      "end_flag": "Confirmed",
      "type": "Planned"
    }
  ]
}
```

GB (empty):

```json
{
  "last_page": 1,
  "total": 0,
  "dataset": "<a href=\"/unavailability/gantt/GB\">United Kingdom (Pre-Brexit)</a>",
  "data": []
}
```

Note that the docs (v007 PDF) are ambiguous about whether
`unavailability` is part of the AGSI API surface — the catalog YAML
notes "documentation wording is ambiguous about unavailability API
coverage." The endpoint is live-served and well-formed.

---

## Silver layer

**Path pattern**: `data/silver/gie_agsi/unavailability/year=YYYY/month=MM/unavailability_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.gie.agsi.UnavailabilityTransformer`
**Pydantic schema**: (no dedicated schema — dynamic columns from `AgsiJsonTransformer`)
**Dedup key**: `(facility_eic, start, end)` — falls back to `(id, url, entity_code, eic)` per `AgsiJsonTransformer.unique` logic.
**Point-in-time field**: `published` (parsed to UTC datetime).

### Silver schema

(Dynamic — derived from live JSON keys via `_normalise_row` /
`_camel_to_snake` / `_safe_*` helpers.)

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `published` | `datetime[UTC]` | Yes | `published` | Vendor publish timestamp. |
| `country` | `str` | Yes | `country` | JSON-encoded `{"name", "code"}` dict. |
| `company` | `str` | Yes | `company` | JSON-encoded `{"name", "eic"}` dict. |
| `facility` | `str` | Yes | `facility` | JSON-encoded `{"name", "eic"}` dict. |
| `start` | `datetime[UTC]` | Yes | `start` | Outage window start. |
| `end` | `datetime[UTC]` | Yes | `end` | Outage window end (`end_flag` says whether confirmed or estimated). |
| `volume` | `float` | Yes | `volume` | GWh (per docs). |
| `injection` | `float` | Yes | `injection` | GWh/day capacity reduction. |
| `withdrawal` | `float` | Yes | `withdrawal` | GWh/day capacity reduction. |
| `description` | `str` | Yes | `description` | Free-text note. |
| `end_flag` | `str` | Yes | `end_flag` | `Confirmed`, `Estimate`. |
| `type` | `str` | Yes | `type` | `Planned`, `Unplanned`, ... |
| `data_provider` | `str` | No | derived | Always `gie_agsi`. |
| `ingested_at` | `datetime[UTC]` | No | derived | |

### Silver sample

```python
[
    {
        "published": datetime(2026, 5, 8, 10, 40, 7, tzinfo=UTC),
        "country": '{"name": "Germany", "code": "DE"}',
        "company": '{"name": "EWE Gasspeicher", "eic": "21X0000000011756"}',
        "facility": '{"name": "EWE H-Gas Zone", "eic": "37W000000000002O"}',
        "start": datetime(2026, 5, 4, 6, 0, tzinfo=UTC),
        "end": datetime(2026, 5, 8, 12, 0, tzinfo=UTC),
        "volume": 3.004,
        "injection": 41.4,
        "withdrawal": 82.8,
        "description": "safety test / maintenance work (only Huntorf is influenced)",
        "end_flag": "Confirmed",
        "type": "Planned",
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
- `last_page` is the pagination source of truth (not `total`).
  `total` is the per-page row count.
- Values in **GWh** (volume) and **GWh/day** (injection / withdrawal
  reductions). The fixture has `unavailableCapacity` and
  `workingGasVolume` keys — those are not present in the live response.
- Rate limit: 60 calls/min (1 req/s).
- GB returns zero rows by design (no UK storage outages reported on
  AGSI). Only post-Brexit GB rows are sparse anyway.
- `country`, `company`, `facility` arrive as nested dicts
  (`{"name": ..., "code": ...}` or `{"name": ..., "eic": ...}`) —
  the silver transformer JSON-encodes them at column level.
- `start` / `end` arrive as `YYYY-MM-DD HH:MM:SS` (naïve local) —
  silver `_safe_datetime` parses with UTC fallback.
- The catalog YAML notes documentation ambiguity (v007 PDF wording
  about whether `unavailability` is part of the AGSI API).

---

## Implementation delta

- **v007 documentation ambiguity**: the GIE
  `GIE_API_documentation_v007.pdf` reviewer-cross-check (per
  `docs/gie_agsi_endpoint_catalog.yaml`) leaves it unclear whether
  `/api/unavailability` is fully part of the AGSI API or a separate
  legacy/portal-only feature. The endpoint is live-served and returns
  well-formed JSON; the catalog YAML says: "Marked active because the
  endpoint is documented and live-served, though documentation wording
  is ambiguous about unavailability API coverage." This dataset page
  treats it as active per the live-validation pass on 2026-05-08.
- **Date param naming**: registry uses `start` / `end` for the date
  range (matches catalog `date_params.range: [start, end]`). The
  live API **also** accepts `from` / `to` and produces a slightly
  different filter result (different `last_page`). The connector's
  registry choice (`start` / `end`) returns matching data — no fix
  needed, but the alternative form exists.
- **Field shapes vs fixture**: live records include
  `country`/`company`/`facility` as nested dicts. The fixture
  (`tests/fixtures/gie/agsi_unavailability_response.json`) uses flat
  `country: "DE"`, `company: "21X-..."`, `facility: "21W-..."` strings.
  The silver transformer handles both via dynamic typing — fixture is
  out of date relative to live shape (logged here, NOT regenerated in
  V1 — fixture regeneration is out of scope).
- **`event_start`/`event_end` vs `start`/`end`**: fixture uses
  `eventStart` / `eventEnd`; live uses `start` / `end`. The
  `_unavailability_record_overlaps` helper checks both shapes.
- **`unavailableCapacity` / `workingGasVolume` not in live**: fixture
  has these keys; live has `volume`, `injection`, `withdrawal`. The
  `AgsiJsonTransformer` numeric heuristic captures `volume` and
  `*_capacity` suffixes regardless.

No connector-behaviour discrepancies found.

---

## Modelling notes

- **Models**: short-term withdrawal-capacity forecasts, fundamental
  gas-spread trades, explanatory features for sudden country-level
  capacity drops.
- **Targets**: `withdrawal` (GWh/day reduction during outage),
  `volume` (energy not stored).
- **Features**: type (planned vs unplanned), end_flag (confirmed vs
  estimate), event duration.
- **Joins**: `storage_reports.entity_code` ↔ `unavailability.facility.eic`
  for facility-level capacity adjustment;
  `unavailability.country.code` ↔ `storage.country_code` for country
  rollup.

---

## Links

- [Official API docs](https://agsi.gie.eu/api)
- [Connector source](../../../../../Python/gridflow/src/gridflow/connectors/gie/client.py)
- [Endpoint registry](../../../../../Python/gridflow/src/gridflow/connectors/gie/endpoints.py)
- [Silver transformer](../../../../../Python/gridflow/src/gridflow/silver/gie/agsi.py)
- [Domain: gas day](../../../20-domain/concepts/gas-day.md)
