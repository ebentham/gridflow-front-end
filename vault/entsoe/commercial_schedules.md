---
source: entsoe
dataset_key: commercial_schedules
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-11
layer_coverage: bronze, silver
---

# ENTSO-E - Commercial Schedules (A09)

## Overview

Aggregated final commercial schedules per zone pair after capacity allocation.
Article 12.1.E of Regulation (EC) 543/2013. Each TimeSeries records nominated
commercial flow on a directional border for the relevant trading horizon.

Current status: this is the sole active A09 connector dataset. The former
`commercial_schedules_net_positions` key was removed as an identical registry
duplicate and is retained only as a deprecated pointer page.

## API endpoint

| Property | Value |
|---|---|
| Base URL | `https://web-api.tp.entsoe.eu` |
| Path | `/api` |
| Method | GET |
| Auth | Query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit | 1 req/s default |
| Pagination | None |
| Historical depth | 2014-12-05 onward, border-dependent |
| Publication lag | D-1 after gate closure |
| Response format | XML |

### ENTSO-E parameter tuple

| Field | Value |
|---|---|
| `documentType` | `A09` |
| `processType` | omitted |
| `businessType` request parameter | omitted; server returns `A06` on TimeSeries |
| `contract_MarketAgreement.Type` | optional request filter, present in TimeSeries payload |
| Domain params | `in_Domain` + `out_Domain` |

### Query parameters

| Parameter | Required | Description |
|---|---|---|
| `securityToken` | Yes | API key |
| `documentType` | Yes | `A09` |
| `in_Domain` | Yes | Source EIC |
| `out_Domain` | Yes | Destination EIC |
| `contract_MarketAgreement.Type` | No | Filter horizon, e.g. `A01` daily |
| `periodStart` / `periodEnd` | Yes | `yyyymmddHHMM` UTC |

## Bronze layer

Path:
`data/bronze/entsoe/commercial_schedules/YYYY/MM/DD/raw_<uuid>.xml`

Granularity: one file per `(in_Domain, out_Domain, day)` API call.

## Silver layer

Path:
`data/silver/entsoe/commercial_schedules/year=YYYY/month=MM/commercial_schedules_YYYYMMDD.parquet`

Transformer:
`gridflow.silver.entsoe.h6_market.CommercialSchedulesTransformer`

Pydantic schema:
`gridflow.schemas.entsoe.EntsoeTransmissionMarketQuantity`

Dedup key:
`(timestamp_utc, in_area_code, out_area_code, business_type)`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|---|---|---|---|---|
| `timestamp_utc` | `datetime` UTC | No | period + position | Expanded from TimeSeries period |
| `in_area_code` | `str` | No | `in_Domain.mRID` | EIC |
| `out_area_code` | `str` | No | `out_Domain.mRID` | EIC |
| `quantity_mw` | `float` | No | `Point.quantity` | Commercial nomination in MW |
| `business_type` | `str` or `None` | Yes | TimeSeries `businessType` | Usually `A06` |
| `resolution` | `str` or `None` | Yes | `Period.resolution` | e.g. `PT60M` |
| `data_provider` | `str` | No | derived | Constant `entsoe` |
| `ingested_at` | `datetime` UTC or `None` | Yes | derived | Transformer run time |
| `event_time` | `datetime` UTC | No | base transformer | Added at write time |
| `available_at` | `datetime` UTC | No | base transformer | Added at write time |
| `source_run_id` | `str` | No | base transformer | Added at write time |
| `dataset_version` | `str` | No | base transformer | Added at write time |

## Gold layer

None implemented.

## Known issues and gotchas

- A09 is directional. Net commercial position requires both directions.
- Variable-resolution `curveType A03` can compress unchanged intervals; the
  previous value persists until the next point.
- `contract_MarketAgreement.type` in the payload identifies the horizon
  (`A01` daily, `A02` weekly, etc.).
- `commercial_schedules_net_positions` is not active in current `gridflow`
  master.

## Implementation delta

- Live validation 2026-05-08: GB -> FR for 2026-05-06 returned
  `Publication_MarketDocument` with 2 TimeSeries and hourly points. PASS.
- A09 dedup resolved in V2 on 2026-05-09: `commercial_schedules` is now the
  sole active A09 entry. Live re-validation for GB -> FR with
  `contract_MarketAgreement.Type=A01` returned HTTP 200 and 3078 bytes.
- A real signed `net_position_mw` derivation remains a backlog item.

## Changelog

- **2026-05-11.** Reverified against current `gridflow` master docs and
  active counts.
- **2026-05-09.** V2-FIX-05 / ADR-019 A09 registry dedup: dropped
  `commercial_schedules_net_positions`.
- **2026-05-08.** Live-validated; A09 registry duplication surfaced.

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/entsoe.py)
