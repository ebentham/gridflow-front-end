---
source: entsoe
dataset_key: commercial_schedules_net_positions
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-11
layer_coverage: deprecated
status: deprecated
---

# ENTSO-E - Commercial Schedules: Net Positions - Deprecated

> **This dataset key was removed in V2 (ADR-019).** It registered an identical
> `EntsoeDocType` to [`commercial_schedules`](./commercial_schedules.md) and
> returned the identical XML payload at the API level. The "net positions"
> interpretation was never actually implemented; both transformers emitted the
> same per-direction Silver rows.
>
> **Use [`commercial_schedules`](./commercial_schedules.md) instead.**

## What was removed

- `connectors/entsoe/endpoints.py::DOC_TYPES["commercial_schedules_net_positions"]`
- `silver/entsoe/h6_market.py::CommercialSchedulesNetPositionsTransformer`
- `config/sources.yaml` `entsoe.commercial_schedules_net_positions` block
- `silver/entsoe/__init__.py` import and `__all__` entry
- Scheduled active dataset counting for the duplicate A09 tuple

## What is preserved

- Historical Parquet under `data/silver/entsoe/commercial_schedules_net_positions/...`
  may still exist in local data directories. No scheduled Gold consumer reads
  it; deleting it would be a separate data cleanup.
- This vault page remains as a deprecation pointer for old links.

## Future net-positions dataset

A real signed `net_position_mw` table would require pairing both zone-pair
directions per period and emitting a single signed value. It should be added
under a new dataset key if a downstream consumer needs it.

## Changelog

- **2026-05-11.** Reverified as a deprecated pointer against current
  `gridflow` master.
- **2026-05-09.** Deprecated in V2-FIX-05 / ADR-019. Use
  [`commercial_schedules`](./commercial_schedules.md) instead.
- **2026-05-08.** Live-validated during V1; A09 registry duplication surfaced.
