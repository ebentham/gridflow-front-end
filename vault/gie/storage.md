---
source: gie_agsi
dataset_key: storage
vendor: GIE AGSI+ (Gas Storage)
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# GIE AGSI+ — Storage (country-level gas storage)

## Overview

`storage` is the country-scoped form of the AGSI gas-storage time-series.
Same `/api` endpoint and response shape as `storage_reports`, but the
connector exercises **only** the `country` query scope — one record per
gas-day per country in the AGSI footprint (`AT, BE, DE, ES, FR, GB, IT,
NL, PL`). Stocks (`gasInStorage`), flow components (`injection`,
`withdrawal`, `netWithdrawal`), capacity figures (`workingGasVolume`,
`injectionCapacity`, `withdrawalCapacity`), percent-full and trend.

The dataset answers: "How full is each EU country's underground storage
today, and how is it changing?" — the workhorse country-level view used
in winter-tightness models, fuel-switching signals, and storage-spread
trades.

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
| `country` | str | Yes | ISO-2 country code from the AGSI footprint. | `country=GB` |
| `date` | str (YYYY-MM-DD) | Conditional | Single gas day. Mutually exclusive with `from`/`to`. | `date=2026-05-06` |
| `from` | str (YYYY-MM-DD) | Conditional | Range start gas day. | `from=2026-05-01` |
| `to` | str (YYYY-MM-DD) | Conditional | Range end gas day (inclusive). | `to=2026-05-07` |
| `page` | int | No | Page number, 1-indexed. Default 1. | `page=2` |
| `size` | int | No | Page size. Default 30, max 300. Connector uses 300. | `size=300` |

### Working curl example

```bash
# Replace <KEY> with $GIE_API_KEY
curl --ssl-no-revoke -X GET \
  "https://agsi.gie.eu/api?country=GB&date=2026-05-06" \
  -H "x-key: <KEY>"
```

---

## Bronze layer

**Path pattern**: `data/bronze/gie_agsi/storage/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per (country, gas day) call after pagination is unrolled.

### Bronze sample

```json
{
  "last_page": 1,
  "total": 1,
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

DE returns numeric values:

```json
{
  "name": "Germany", "code": "DE", "gasInStorage": "65.9608",
  "full": "26.62", "trend": "-0.57", "status": "E"
}
```

---

## Silver layer

**Path pattern**: `data/silver/gie_agsi/storage/year=YYYY/month=MM/storage_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.gie.agsi.GasStorageTransformer`
**Pydantic schema**: `gridflow.schemas.gie.GasStorage`
**Dedup key**: `(gas_day, entity_level, entity_code, entity_url)`
**Point-in-time field**: `updated_at` — vendor `updatedAt`. Use for as-of filtering.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `gas_day` | `date` | No | `gasDayStart` | Required. Gas day starts 06:00 UTC. |
| `gas_day_end` | `datetime[UTC]` | Yes | `gasDayEnd` | |
| `updated_at` | `datetime[UTC]` | Yes | `updatedAt` | Vendor revision timestamp. |
| `entity_level` | `str` | No | derived | Always `country` for this dataset. |
| `entity_code` | `str` | No | request `country` / `code` | ISO-2 country code. |
| `entity_name` | `str` | No | `name` | Human-readable country name. |
| `entity_url` | `str` | Yes | `url` | |
| `country_code` | `str` | No | request `country` | |
| `country_name` | `str` | No | `name` | |
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
| `trend` | `float` | Yes | `trend` | Signed daily delta. |
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
- All values in **GWh** (and capacities in GWh/day).
- Rate limit: 60 calls/min (1 req/s).
- GB returns "United Kingdom (Pre-Brexit)" with `-` placeholders for
  numeric values post-Brexit. Convert `-` to null at the silver-transformer
  boundary (`_safe_float` already does this).
- Gas day starts at 06:00 UTC. The `gas_day` field is a `date`, not a
  timestamp; do not synthesise a UTC midnight timestamp without applying
  the 06:00 offset.
- `gas_day_start_validation` is enforced in the connector — a country
  query for `date=2026-05-06` will fail loudly if the response contains
  a different gas day. Helps catch silent vendor caching errors.
- Country footprint (`AGSI_COUNTRIES`): `AT, BE, DE, ES, FR, GB, IT,
  NL, PL`. Other ISO-2 codes return empty data.

---

## Implementation delta

- **Endpoint path**: registry uses `/api`; live API agrees. No discrepancy.
- **Pagination**: registry uses `last_page` correctly. No discrepancy.
- **Legacy fallback**: `connectors/gie/client.py::_fetch_country` (used
  by `gie_alsi`) still uses `till=` instead of `to=` for the range
  parameter. AGSI's `_fetch_agsi_storage` correctly uses `from`/`to`.
  The legacy code path is unused for `gie_agsi` so this is not a live
  bug, but flagged for the eventual ALSI implementation.

No discrepancies found for the active AGSI `storage` code path.

---

## Modelling notes

- **Models**: country-level winter-tightness, EU gas balance,
  storage-spread (S/W) trades, security-of-supply stress tests.
- **Targets**: `storage_pct_full` (% full), `net_withdrawal_gwh` (daily
  flow), `gas_in_storage_gwh` (absolute level).
- **Features**: lag of `full` and `trend`, weather-driven
  consumption (HDD), capacity utilisation
  (`gas_in_storage_gwh / working_gas_volume_gwh`).
- **Filters**: drop rows where `status = N` (no value); GB Pre-Brexit
  rows are effectively unusable post-2020.
- **Joins**: ENTSOG flows (cross-border imports), Open-Meteo HDD,
  Elexon `tsdf` / NESO regional demand for power-sector gas burn.

---

## Links

- [Official API docs](https://agsi.gie.eu/api)
- [Connector source](../../../../../Python/gridflow/src/gridflow/connectors/gie/client.py)
- [Endpoint registry](../../../../../Python/gridflow/src/gridflow/connectors/gie/endpoints.py)
- [Silver transformer](../../../../../Python/gridflow/src/gridflow/silver/gie/agsi.py)
- [Pydantic schema](../../../../../Python/gridflow/src/gridflow/schemas/gie.py)
- [Domain: gas day](../../../20-domain/concepts/gas-day.md)
