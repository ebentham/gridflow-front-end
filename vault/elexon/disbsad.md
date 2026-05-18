---
source: elexon
dataset_key: disbsad
vendor: Elexon BMRS
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# Elexon - Disaggregated Balancing Services Adjustment Data (`DISBSAD`)

## Overview

Disaggregated Balancing Services Adjustment Data (DISBSAD) — the constituent BSAD components used to derive Net BSAD. Each row captures the cost and volume of a single non-BM balancing action (e.g. STOR call-off, ancillary services, system operator instructions outside of BOALF). Together with NETBSAD, DISBSAD is what BSC parties consume to reconcile imbalance settlement.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/DISBSAD` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Same cadence as system prices (per settlement run). |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `from` | string | Yes | The "from" start time or settlement date for the filter. | `2026-05-06T00:00Z` |
| `to` | string | Yes | The "to" start time or settlement date for the filter. | `2026-05-06T03:00Z` |
| `settlementPeriodFrom` | integer | No | The "from" settlement period for the filter. This should be an integer from 1-50 inclusive. | `1` |
| `settlementPeriodTo` | integer | No | The "to" settlement period for the filter. This should be an integer from 1-50 inclusive. | `48` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/DISBSAD?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-disbsad.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/disbsad/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/DISBSAD?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "DISBSAD",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 9,
      "id": 1,
      "cost": 0.0,
      "volume": 0.0,
      "soFlag": true,
      "storFlag": false,
      "partyId": null,
      "assetId": null,
      "isTendered": null,
      "service": null
    },
    {
      "dataset": "DISBSAD",
      "settlementDate": "2026-05-06",
      "settlementPeriod": 8,
      "id": 1,
      "cost": 0.0,
      "volume": 0.0,
      "soFlag": true,
      "storFlag": false,
      "partyId": null,
      "assetId": null,
      "isTendered": null,
      "service": null
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/disbsad/year=YYYY/month=MM/disbsad_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.disbsad.DISBSADTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonDISBSAD`
**Dedup key**: _inline in transformer (see `silver/elexon/disbsad.py`)_
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `adjustment_action_id` | `str` | Yes | `id` | DISBSAD action identifier. |
| `so_flag` | `bool` | No | `soFlag` | System Operator flag. |
| `stor_flag` | `bool` | No | `storProviderFlag` | STOR flag. |
| `component` | `str` | Yes | `component` | DISBSAD component code. |
| `cost` | `float` | Yes | `cost` | GBP. |
| `volume` | `float` | Yes | `volume` | MWh. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-06",
        "settlement_period": 9,
        "timestamp_utc": "2026-05-06T04:00:00+00:00",
        "adjustment_action_id": 1,
        "so_flag": true,
        "stor_flag": "...",
        "component": "...",
        "cost": 0.0,
        "volume": 0.0,
        "data_provider": "elexon",
        "ingested_at": "2026-05-08T12:00:00Z"
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **DISBSAD pairs with NETBSAD**: NETBSAD is the aggregate of DISBSAD components for the same period. Don't sum DISBSAD twice when joining.
- **Cost field unit**: GBP (not GBP/MWh).

---

## Implementation delta

- **Param style**: docs require `from`/`to`; code matches.
- **No Pydantic class** beyond `ElexonDISBSAD` for many fields — schema enforces the core (settlement_date, settlement_period, optional flags); silver transformer enforces full output column set.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/disbsad.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
