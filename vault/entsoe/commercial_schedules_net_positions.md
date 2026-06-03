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

## Overview

`commercial_schedules_net_positions` was a registry duplicate of
[`commercial_schedules`](./commercial_schedules.md) — the same A09 `EntsoeDocType`
on the connector side, the same XML payload on the wire, and the same
per-direction Silver rows on the transformer side. The "net positions"
framing implied a single signed value per zone-pair-period, but no
signed-net-position transformer was ever wired; both keys emitted the
identical per-direction shape.

The key was removed in V2 (V2-FIX-05 / ADR-019) once the registry-duplicate
audit surfaced. This vault page remains as a pointer for old links so
external references don't 404; the rendered page on the site is documented
as deprecated and links to `commercial_schedules` for the active surface.

## API endpoint

> **Deprecated.** This dataset was removed in V2 (ADR-019). The API tuple
> below is preserved for historical reference only — at the wire level the
> call shape was identical to [`commercial_schedules`](./commercial_schedules.md),
> which is the active replacement.

| Property | Value |
|---|---|
| Base URL | `https://web-api.tp.entsoe.eu/api` |
| Document type | `A09` (identical to `commercial_schedules`) |
| Status | Deprecated — `DOC_TYPES` entry removed in V2-FIX-05 / ADR-019 |

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
