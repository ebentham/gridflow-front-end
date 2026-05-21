---
source: entsoe
dataset_key: imbalance_volume
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Imbalance Volumes (A86)

## Overview

Total imbalance volumes in MWh per control area, by direction. Article
12.3.A_H (`TOTAL_IMBALANCE_VOLUMES_R3`). Document type `A86`, with
`businessType=A19` to denote settlement-imbalance volume; the per-point
`flowDirection` (`A01` long / `A02` short) is what the silver schema maps
to `direction`. Returned in `Balancing_MarketDocument`. Resolution typically
PT15M.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance volume](../../20-domain/markets/imbalance-volume.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken` from env var `ENTSOE_API_KEY` |
| Rate limit       | Not vendor-published; codebase 1 req/s |
| Pagination       | None |
| Historical depth | Vendor-bounded |
| Publication lag  | ~T+1 hour |
| Response format  | XML (Balancing_MarketDocument); ZIP-of-XML for large windows |
| Document type    | `A86` |
| Process type     | n/a |
| Domain param name | `controlArea_Domain` |
| Required businessType | `A19` (codebase fixed) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | yes | API key | `<your-entsoe-api-key>` |
| `documentType` | str | yes | `A86` | `A86` |
| `businessType` | str | yes (codebase-required) | `A19` | `A19` |
| `controlArea_Domain` | str (EIC) | yes | Control area EIC | `10YFR-RTE------C` |
| `periodStart` | str | yes | `yyyyMMddHHmm` UTC | `202605060000` |
| `periodEnd` | str | yes | `yyyyMMddHHmm` UTC | `202605070000` |

### Working curl example

```bash
curl -X GET --ssl-no-revoke \
  "https://web-api.tp.entsoe.eu/api?securityToken=<your-entsoe-api-key>&documentType=A86&businessType=A19&controlArea_Domain=10YFR-RTE------C&periodStart=202504010000&periodEnd=202504020000" \
  -H "Accept: application/xml"
```

GB returns code 999 (`TOTAL_IMBALANCE_VOLUMES_R3 [17.1.H]`).

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/imbalance_volume/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML (or ZIP-of-XML, unpacked).
**Granularity**: One file per (control area, query window).

### Bronze sample

```json
{
  "envelope": "Balancing_MarketDocument xmlns='urn:iec62325.351:tc57wg16:451-6:balancingdocument:3:0'",
  "type": "A86",
  "process.processType": "A16",
  "area_Domain.mRID": "10YFR-RTE------C",
  "TimeSeries": [
    {
      "businessType": "A19",
      "flowDirection.direction": "A01",
      "Period": {
        "resolution": "PT15M",
        "Point": [{"position": 1, "quantity": 12.5}]
      }
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/imbalance_volume/year=YYYY/month=MM/imbalance_volume_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.imbalance_volume.ImbalanceVolumeTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeImbalanceVolume`
**Dedup key**: `(timestamp_utc, area_code, direction)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` (tz-aware UTC) | No | derived | |
| `area_code` | `str` | No | `controlArea_Domain.mRID` / `area_Domain.mRID` | EIC |
| `direction` | `str` | No | `flowDirection.direction` mapped via `replace_strict` | `A01→long`, `A02→short` |
| `volume_mwh` | `float` | No | `Point/quantity` | MWh |
| `resolution` | `str` | No (default `""`) | `Period/resolution` | `PT15M` typical |
| `data_provider` | `str` | No (default `"entsoe"`) | derived | Constant |
| `ingested_at` | `datetime` (tz-aware UTC) | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2025, 4, 1, 0, 0, tzinfo=UTC),
        "area_code": "10YFR-RTE------C",
        "direction": "long",
        "volume_mwh": 12.5,
        "resolution": "PT15M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 6, 0, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB empty post-Brexit**.
- **`businessType=A19` mandatory in the request** — the connector adds it
  via `extra_params`, fixed at A19. Without it, the API rejects with a
  required-parameter error.
- **`replace_strict` direction mapping** raises on any flowDirection not in
  `{A01, A02}` — silent unknowns are not allowed.
- **`Balancing_MarketDocument`** envelope.

---

## Implementation delta

- Code-tuple: `(A86, None, A19, controlArea_Domain)`.
  Guide PDF unfetchable; tuple `unverified - PDF fetch failed` against
  canonical docs. Live FR response (older window 2025-04-01) returns
  `Balancing_MarketDocument` with `type=A86`, `process.processType=A16`
  and 4 `<TimeSeries>` — request shape accepted by the API.
- **Missing `processType=A16`** in the connector's request: the API
  response carries `process.processType=A16` even though the code does not
  send it; this implies the API defaults to `A16` for `A86` requests.
  Worth confirming against canonical docs once accessible.

---

## Modelling notes

- Pair with `imbalance_prices` on `(timestamp_utc, area_code, direction)`
  to derive directional cost-of-imbalance. Useful input for short-term
  market-stress models.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoints](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/imbalance_volume.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
- [Domain: imbalance volume](../../20-domain/markets/imbalance-volume.md)
