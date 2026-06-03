---
source: gie_alsi
dataset_key: lng
vendor: GIE ALSI
last_verified: 2026-05-11
layer_coverage: bronze, silver
---

# GIE ALSI - LNG Terminals

## Overview

Country-level LNG terminal inventory and flow data from GIE ALSI. ALSI shares
the same `x-key` authentication model as AGSI+, but uses the base URL
`https://alsi.gie.eu`. In `gridflow`, the active source is `gie_alsi` and the
active dataset key is `lng`.

## API endpoint

| Property | Value |
|---|---|
| Base URL | `https://alsi.gie.eu` |
| Path | `/api` |
| Method | GET |
| Auth | Header `x-key: <GIE_API_KEY>` |
| Country set | `BE, ES, FR, GB, IT, NL, PL, PT` |
| Response format | JSON |
| Pagination | `page` + `size`; connector stops from `last_page` (the authoritative page count). `total` is the per-page row count; `pageSize` is absent from the live envelope. |

### Query parameters

`country`, `from`, `till`, `page`, `size`.

## Bronze layer

Path:
`data/bronze/gie_alsi/lng/YYYY/MM/DD/raw_<uuid>.json`

The connector stamps `data_date=start.date()`.

## Silver layer

Path:
`data/silver/gie_alsi/lng/year=YYYY/month=MM/lng_YYYYMMDD.parquet`

Transformer:
`gridflow.silver.gie.alsi.LNGTerminalTransformer`

Pydantic schema:
`gridflow.schemas.gie.LNGTerminal`

Dedup key:
`(gas_day, country_code)` when `country_code` is present, otherwise
`gas_day`.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|---|---|---|---|---|
| `gas_day` | `date` | No | `gasDayStart` / `gasDay` / `date` | Gas-day grain |
| `country_code` | `str` or `None` | Yes | `countryCode` / `code` | ISO-like country code |
| `country_name` | `str` or `None` | Yes | `countryName` / `name` | Country display name |
| `lng_in_storage_gwh` | `float` or `None` | Yes | `lngInventory` / `gasInStorage` | Stored LNG volume |
| `send_out_gwh` | `float` or `None` | Yes | `sendOut` / `withdrawal` | LNG send-out |
| `injection_gwh` | `float` or `None` | Yes | `injection` | LNG injection |
| `lng_pct_full` | `float` or `None` | Yes | derived (`lng_in_storage_gwh` / `dtmi_gwh` × 100) | Honest LNG %-full, clamped to [0, 100] in the transformer |
| `dtrs` | `float` or `None` | Yes | `dtrs` | Raw vendor `dtrs`; **unconfirmed non-percentage** metric (live ~724–2132, so not a percent), units not in official ALSI docs |
| `dtmi_lng` | `float` or `None` | Yes | `dtmi.lng` | Raw vendor `dtmi.lng` member; unconfirmed units |
| `dtmi_gwh` | `float` or `None` | Yes | `dtmi.gwh` | Raw vendor `dtmi.gwh` member; unconfirmed units; feeds derived `lng_pct_full` |
| `trend` | `float` or `None` | Yes | `trend` | Daily trend where published |
| `data_provider` | `str` | No | derived | Constant `gie_alsi` |
| `ingested_at` | `datetime` UTC or `None` | Yes | derived | Transformer run time |
| `event_time` | `datetime` UTC | No | base transformer | Added at write time |
| `available_at` | `datetime` UTC | No | base transformer | Added at write time |
| `source_run_id` | `str` | No | base transformer | Added at write time |
| `dataset_version` | `str` | No | base transformer | Added at write time |

## Modelling notes

- Use `gas_day` as the date grain; do not infer an hourly timestamp without an
  explicit gas-day convention.
- Pair this dataset with `gie_agsi/storage` and ENTSO-G physical flows for
  cross-gas-supply views.
- GB coverage may contain null numeric values; treat null as publication
  absence, not zero.

## Links

- [Connector](../../../../../../Python/gridflow/src/gridflow/connectors/gie/client.py)
- [Endpoint constants](../../../../../../Python/gridflow/src/gridflow/connectors/gie/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/gie/alsi.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/gie.py)
