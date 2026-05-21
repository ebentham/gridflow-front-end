---
source: gie_agsi
dataset_key: storage_reports
vendor: GIE AGSI+ (Gas Storage)
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# GIE AGSI+ — Storage reports (catalog-aligned aggregate / country / company / facility)

## Overview

`storage_reports` is the catalog-aligned form of the AGSI gas-storage
time-series. Same `/api` endpoint and shape as `storage`, but the
connector exercises the full set of query scopes documented in
`docs/gie_agsi_endpoint_catalog.yaml`: `aggregate_type` (`type=EU`),
`country`, `company`, and `facility`. It returns one record per
gas-day per entity, with stocks (`gasInStorage`), flow components
(`injection`, `withdrawal`, `netWithdrawal`), capacity figures
(`workingGasVolume`, `injectionCapacity`, `withdrawalCapacity`,
`contractedCapacity`, `availableCapacity`, `coveredCapacity`),
percent-full and trend.

The dataset answers: "How much gas is stored in EU underground storage,
who operates it, and how is it changing day-by-day?" — the foundational
input for any winter-season tightness, fuel-switching, or storage-spread
trade idea on EU gas.

→ [Gas day](../../../20-domain/concepts/gas-day.md) — gas day starts at
  06:00 UTC, not at midnight.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://agsi.gie.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | header `x-key` (lowercase), key from env `GIE_API_KEY` |
| Rate limit       | 60 calls/minute (vendor-published). Connector throttles to 1 req/s. |
| Pagination       | `last_page` is the source of truth; `total` is the per-page row count. Iterate `page=1..last_page`. |
| Historical depth | 2011-01-01 (per facility records in `about?show=listing`) |
| Publication lag  | Daily, ~16:00 CET refresh. `updatedAt` field per record. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `type` | str | Conditional | Aggregate type (`EU`, `non_eu`). Used when scope = aggregate. | `type=EU` |
| `country` | str | Conditional | ISO-2 country code. Used for country, company, facility scopes. | `country=GB` |
| `company` | str | Conditional | Company EIC. Used for company and facility scopes. | `company=21X-DEMO-ALPHA` |
| `facility` | str | Conditional | Facility EIC. Used for facility scope. | `facility=21W-DEMO-ALPHA-1` |
| `date` | str (YYYY-MM-DD) | Conditional | Single gas day. Mutually exclusive with `from`/`to`. | `date=2026-05-06` |
| `from` | str (YYYY-MM-DD) | Conditional | Range start gas day. | `from=2026-05-01` |
| `to` | str (YYYY-MM-DD) | Conditional | Range end gas day (inclusive). | `to=2026-05-07` |
| `page` | int | No | Page number, 1-indexed. Default 1. | `page=2` |
| `size` | int | No | Page size. Default 30, max 300. Connector uses 300. | `size=300` |

### Working curl example

```bash
# Replace <KEY> with $GIE_API_KEY
curl --ssl-no-revoke -X GET \
  "https://agsi.gie.eu/api?country=GB&from=2026-05-01&to=2026-05-07" \
  -H "x-key: <KEY>"
```

---

## Bronze layer

**Path pattern**: `data/bronze/gie_agsi/storage_reports/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per (entity, gas day) call after pagination is unrolled.

### Bronze sample

```json
{
  "last_page": 1,
  "total": 6,
  "dataset": "<a href=\"/historical/GB\">United Kingdom (Pre-Brexit)</a>",
  "gas_day": "2026-05-06",
  "data": [
    {
      "name": "United Kingdom (Pre-Brexit)",
      "code": "GB",
      "url": "GB",
      "updatedAt": "2026-05-08 17:36:56",
      "gasDayStart": "2026-05-06",
      "gasDayEnd": "2026-05-07",
      "gasInStorage": "-",
      "consumption": "-",
      "consumptionFull": "0",
      "injection": "-",
      "withdrawal": "-",
      "netWithdrawal": "-",
      "workingGasVolume": "-",
      "status": "N",
      "trend": "-",
      "full": "-",
      "info": []
    }
  ]
}
```

GB rows return `-` placeholders post-Brexit. Substituting `country=DE`
returns numeric values:

```json
{
  "name": "Germany",
  "code": "DE",
  "gasInStorage": "65.9608",
  "consumption": "903.9000",
  "consumptionFull": "7.3",
  "injection": "182.43",
  "withdrawal": "60.3",
  "netWithdrawal": "-122.1",
  "workingGasVolume": "247.7476",
  "full": "26.62",
  "trend": "-0.57",
  "status": "E"
}
```

---

## Silver layer

**Path pattern**: `data/silver/gie_agsi/storage_reports/year=YYYY/month=MM/storage_reports_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.gie.agsi.StorageReportsTransformer`
**Pydantic schema**: `gridflow.schemas.gie.GasStorage`
**Dedup key**: `(gas_day, entity_level, entity_code, entity_url)`
**Point-in-time field**: `updated_at` — vendor `updatedAt`. Use for as-of filtering.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `gas_day` | `date` | No | `gasDayStart` | Required. Gas day starts 06:00 UTC. |
| `gas_day_end` | `datetime[UTC]` | Yes | `gasDayEnd` | |
| `updated_at` | `datetime[UTC]` | Yes | `updatedAt` | Vendor revision timestamp. |
| `entity_level` | `str` | No | derived | One of `aggregate_type`, `country`, `company`, `facility`. Inferred from request params. |
| `entity_code` | `str` | No | `code` (or request param) | EIC for company/facility, ISO-2 for country, `EU` for aggregate. |
| `entity_name` | `str` | No | `name` | |
| `entity_url` | `str` | Yes | `url` | |
| `country_code` | `str` | No | request `country` or `code` | |
| `country_name` | `str` | No | derived | |
| `gas_in_storage_gwh` | `float` | Yes | `gasInStorage` | GWh. `-` placeholder → null. |
| `consumption_gwh` | `float` | Yes | `consumption` | GWh. |
| `consumption_full_pct` | `float` | Yes | `consumptionFull` | %. |
| `injection_gwh` | `float` | Yes | `injection` | GWh. |
| `withdrawal_gwh` | `float` | Yes | `withdrawal` | GWh. |
| `net_withdrawal_gwh` | `float` | Yes | `netWithdrawal` | GWh. Signed. |
| `working_gas_volume_gwh` | `float` | Yes | `workingGasVolume` | GWh. |
| `injection_capacity_gwh_per_day` | `float` | Yes | `injectionCapacity` | GWh/day. |
| `withdrawal_capacity_gwh_per_day` | `float` | Yes | `withdrawalCapacity` | GWh/day. |
| `contracted_capacity_gwh_per_day` | `float` | Yes | `contractedCapacity` | GWh/day. |
| `available_capacity_gwh_per_day` | `float` | Yes | `availableCapacity` | GWh/day. |
| `covered_capacity_gwh_per_day` | `float` | Yes | `coveredCapacity` | GWh/day. |
| `storage_pct_full` | `float` | Yes | `full` | 0-100, clamped at schema. |
| `trend` | `float` | Yes | `trend` | Signed daily delta (sign convention TODO confirm). |
| `status` | `str` | Yes | `status` | `E` estimate, `C` confirmed, `N` no value. |
| `info` | `str` | Yes | `info` | JSON-encoded freeform info object. |
| `data_provider` | `str` | No | derived | Always `gie_agsi`. |
| `ingested_at` | `datetime[UTC]` | No | derived | Silver write timestamp. |

### Silver sample

```python
[
    {
        "gas_day": date(2026, 5, 6),
        "gas_day_end": datetime(2026, 5, 7, 0, 0, tzinfo=UTC),
        "updated_at": datetime(2026, 5, 8, 10, 0, 24, tzinfo=UTC),
        "entity_level": "country",
        "entity_code": "DE",
        "entity_name": "Germany",
        "entity_url": "DE",
        "country_code": "DE",
        "country_name": "Germany",
        "gas_in_storage_gwh": 65.9608,
        "consumption_gwh": 903.9,
        "consumption_full_pct": 7.3,
        "injection_gwh": 182.43,
        "withdrawal_gwh": 60.3,
        "net_withdrawal_gwh": -122.1,
        "working_gas_volume_gwh": 247.7476,
        "injection_capacity_gwh_per_day": 4286.25,
        "withdrawal_capacity_gwh_per_day": 7081.16,
        "contracted_capacity_gwh_per_day": 188.3776,
        "available_capacity_gwh_per_day": 63.0975,
        "covered_capacity_gwh_per_day": 100.0,
        "storage_pct_full": 26.62,
        "trend": -0.57,
        "status": "E",
        "info": None,
        "data_provider": "gie_agsi",
        "ingested_at": datetime(2026, 5, 8, 17, 40, 0, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- Lowercase `x-key` header. Capitalised `X-Key` returns 401.
- `last_page` field is the pagination source of truth. `total` is the
  current-page row count, NOT the global record count.
- All values in **GWh** (and capacities in GWh/day). Vendor docs
  historically called this `working_volume`/`gas_in_storage_mwh` but the
  live response key is `gasInStorage` and the units are GWh.
- Rate limit: 60 calls/min (1 req/s).
- GB returns "United Kingdom (Pre-Brexit)" with `-` placeholders for
  numeric values post-Brexit; only historical pre-Oct-2019 GB rows have
  numeric data. Convert `-` to null at the silver-transformer boundary
  (`_safe_float` already does this).
- Gas day starts at 06:00 UTC. The `gas_day` field is a `date`, not a
  timestamp; do not synthesise a UTC midnight timestamp without applying
  the 06:00 offset.
- `trend` sign convention not formally documented; observed values match
  the daily change of `full` percent (negative for net withdrawal).
- Aggregate `EU` row co-exists with country rows in the same response —
  do not double-count when summing.
- `info` is occasionally a non-empty object (e.g. `{"service": "maintenance"}`)
  but in the live GB and DE responses it was an empty list. JSON-encode at
  silver level so the column type is stable.

---

## Implementation delta

- **Endpoint path**: registry uses `/api` and adds query params to select
  scope; live API agrees. No discrepancy.
- **Pagination**: registry uses `last_page` correctly. No discrepancy.
- **`gas_day` envelope field**: live response includes a top-level
  `gas_day` key alongside per-record `gasDayStart`. The connector reads
  per-record `gasDayStart` (correct).
- **`-` placeholder handling**: vendor returns `"-"` strings for missing
  numeric fields (observed for GB after Brexit). The silver
  `_safe_float` helper converts these to `None` — verified in code path.
- **`code` field in Pre-Brexit GB**: still returned as `"GB"` even though
  numeric fields are dashes. `entity_code` will resolve to `"GB"` —
  correct.

No discrepancies found.

---

## Modelling notes

- **Models**: EU gas balance, storage-trajectory forecast,
  storage-spread (summer-vs-winter) trade signals, security-of-supply
  stress tests.
- **Targets**: `storage_pct_full` (% full), `gas_in_storage_gwh`
  (absolute level), `net_withdrawal_gwh` (daily flow).
- **Features**: lag of `full` and `trend`, capacity utilisation
  (`gas_in_storage_gwh / working_gas_volume_gwh`), interaction with
  weather (HDD).
- **Filters**: drop rows where `status = N` (no value); guard against
  EU aggregate rows leaking into country sums.
- **Joins**: ENTSOG physical flows (interconnect import vs storage
  withdrawal), Open-Meteo HDD, NESO / Elexon power demand.

---

## Links

- [Official API docs](https://agsi.gie.eu/api)
- [Connector source](../../../../../Python/gridflow/src/gridflow/connectors/gie/client.py)
- [Endpoint registry](../../../../../Python/gridflow/src/gridflow/connectors/gie/endpoints.py)
- [Silver transformer](../../../../../Python/gridflow/src/gridflow/silver/gie/agsi.py)
- [Pydantic schema](../../../../../Python/gridflow/src/gridflow/schemas/gie.py)
- [Domain: gas day](../../../20-domain/concepts/gas-day.md)
