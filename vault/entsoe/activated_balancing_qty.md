---
source: entsoe
dataset_key: activated_balancing_qty
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-11
layer_coverage: silver
status: silver-only
---

# ENTSO-E - Activated Balancing Energy Quantity

## Overview

Registered Silver transformer for activated balancing energy quantities in MWh
by control area, reserve type, and activation direction.

Important status: this dataset is **Silver-only** in the current codebase.
`gridflow.silver.entsoe.activated_balancing_qty.ActivatedBalancingQtyTransformer`
is registered, and `gridflow.schemas.entsoe.EntsoeActivatedBalancingQty`
defines the schema, but the dataset is not present in
`gridflow.connectors.entsoe.endpoints.DOC_TYPES` or `config/sources.yaml`.
The CLI will not fetch this dataset from ENTSO-E until connector wiring is
added. The transformer can process matching bronze XML files when they
already exist.

## API endpoint

> **Silver-only status.** This dataset is not wired into `gridflow.connectors.entsoe.endpoints.DOC_TYPES`; the API tuple below is the *expected* call shape once connector wiring lands. Surfaced as a known discrepancy in the rendered page caveats.

| Property | Value |
|---|---|
| Base URL | `https://web-api.tp.entsoe.eu/api` |
| Document type | `A83` |
| Process type | `A16` |
| Business type | `A95`, `A96`, `A97`, or `A98` in source XML |
| Domain param | `controlArea_Domain` |
| Value tag | `quantity` |
| Response format | XML (`Balancing_MarketDocument`) |

The transformer maps reserve `businessType` values as `A95 -> fcr`,
`A96 -> afrr`, `A97 -> mfrr`, and `A98 -> rr`. It maps
`flowDirection.direction` values as `A01 -> up` and `A02 -> down`.

## Bronze layer

Expected path:
`data/bronze/entsoe/activated_balancing_qty/YYYY/MM/DD/raw_<uuid>.xml`

`read_bronze()` uses the base transformer's exact-date lookup with
covering-partition fallback, then parses every `raw_*.xml` file with
`parse_timeseries_xml(..., value_tag="quantity")`.

## Silver layer

Path:
`data/silver/entsoe/activated_balancing_qty/year=YYYY/month=MM/activated_balancing_qty_YYYYMMDD.parquet`

Transformer class:
`gridflow.silver.entsoe.activated_balancing_qty.ActivatedBalancingQtyTransformer`

Pydantic schema:
`gridflow.schemas.entsoe.EntsoeActivatedBalancingQty`

Dedup key:
`(timestamp_utc, area_code, reserve_type, direction)`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|---|---|---|---|---|
| `timestamp_utc` | `datetime` UTC | No | parsed period start + point position | UTC-aware |
| `area_code` | `str` | No | `control_area_domain` | Control area EIC |
| `reserve_type` | `str` | No | `business_type` | `fcr`, `afrr`, `mfrr`, or `rr` |
| `direction` | `str` | No | `flow_direction` | `up` or `down` |
| `quantity_mwh` | `float` | No | `value` | Activated quantity in MWh |
| `resolution` | `str` | No | `resolution` | Source interval resolution |
| `data_provider` | `str` | No | derived | Constant `entsoe` |
| `ingested_at` | `datetime` UTC or `None` | Yes | derived | Transformer run time |
| `event_time` | `datetime` UTC | No | base transformer | Added at write time |
| `available_at` | `datetime` UTC | No | base transformer | Added at write time |
| `source_run_id` | `str` | No | base transformer | Added at write time |
| `dataset_version` | `str` | No | base transformer | Added at write time |

## Implementation notes

- `replace_strict` is used for reserve type and direction mappings.
- The shape mirrors `activated_balancing_prices`, replacing
  `price_eur_mwh` with `quantity_mwh`.
- Connector work needed before live fetches: add a `DOC_TYPES` entry, add a
  `config/sources.yaml` dataset entry, then validate the live ENTSO-E tuple.

## Links

- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/entsoe/activated_balancing_qty.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Fixture](../../../../../../Python/gridflow/tests/fixtures/entsoe/activated_balancing_qty_gb.xml)
- [Design spec](../../../10-projects/energy-pipeline/specs/entsoe-connector-extension.md)
