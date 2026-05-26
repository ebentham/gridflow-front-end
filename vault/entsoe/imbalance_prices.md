---
source: entsoe
dataset_key: imbalance_prices
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Imbalance Prices (A85)

## Overview

Imbalance settlement prices in EUR/MWh per control area, broken into the
"long" (system surplus, businessType A19) and "short" (system deficit, A20)
directions. Article 12.3.A_G (`IMBALANCE_PRICES_R3`). Document type `A85`,
returned in a `Balancing_MarketDocument` envelope. Resolution typically
PT15M for continental control areas. The TSO-charged price for the side
of imbalance.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../20-domain/markets/imbalance-price.md)
  [Balancing settlement](../../20-domain/markets/balancing-settlement.md)

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
| Historical depth | Vendor-bounded; varies by control area |
| Publication lag  | ~T+1 hour after settlement period |
| Response format  | XML (Balancing_MarketDocument); large windows returned as ZIP-of-XML |
| Document type    | `A85` |
| Process type     | n/a |
| Domain param name | `controlArea_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | yes | API key | `<your-entsoe-api-key>` |
| `documentType` | str | yes | `A85` | `A85` |
| `controlArea_Domain` | str (EIC) | yes | Control area EIC mRID | `10YFR-RTE------C` |
| `periodStart` | str | yes | `yyyyMMddHHmm` UTC | `202605060000` |
| `periodEnd` | str | yes | `yyyyMMddHHmm` UTC | `202605070000` |

### Working curl example

```bash
curl -X GET --ssl-no-revoke \
  "https://web-api.tp.entsoe.eu/api?securityToken=<your-entsoe-api-key>&documentType=A85&controlArea_Domain=10YFR-RTE------C&periodStart=202504010000&periodEnd=202504020000" \
  -H "Accept: application/xml"
```

GB (`10YGB----------A`) returns code 999 (`IMBALANCE_PRICES_R3 [17.1.G]`).
Use Elexon `system_prices` for GB imbalance settlement.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/imbalance_prices/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML (or ZIP-of-XML, unpacked by the connector before storage).
**Granularity**: One file per (control area, query window) — the connector unpacks ZIP envelopes per inner XML entry.

### Bronze sample

(First ~500 bytes of FR 2025-04-01 imbalance prices, unpacked from ZIP.)

```json
{
  "envelope": "Balancing_MarketDocument xmlns='urn:iec62325.351:tc57wg16:451-6:balancingdocument:4:4'",
  "type": "A85",
  "process.processType": "A16",
  "area_Domain.mRID": "10YFR-RTE------C",
  "TimeSeries": [
    {
      "businessType": "A19",
      "currency_Unit.name": "EUR",
      "price_Measure_Unit.name": "MWH",
      "Period": {
        "resolution": "PT15M",
        "Point": [{"position": 1, "imbalance_Price.amount": 31.11}]
      }
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/imbalance_prices/year=YYYY/month=MM/imbalance_prices_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.imbalance_prices.ImbalancePricesTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeImbalancePrices`
**Dedup key**: `(timestamp_utc, area_code, direction)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` (tz-aware UTC) | No | derived | |
| `area_code` | `str` | No | `area_Domain.mRID` (parser remaps to `control_area_domain`) | EIC control area |
| `direction` | `str` | No | `businessType` mapped via `replace_strict` | `A19→long`, `A20→short` |
| `price_eur_mwh` | `float` | No | `Point/imbalance_Price.amount` (parser matches `*_Price.amount`) | EUR/MWh |
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
        "price_eur_mwh": 31.11,
        "resolution": "PT15M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 5, 16, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2025, 4, 1, 0, 0, tzinfo=UTC),
        "area_code": "10YFR-RTE------C",
        "direction": "short",
        "price_eur_mwh": 35.40,
        "resolution": "PT15M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 5, 16, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB empty post-Brexit** — for GB imbalance settlement use Elexon
  `system_prices` (run-type-aware).
- **ZIP-of-XML responses** for multi-day windows — auto-unpacked by the
  connector.
- **`Balancing_MarketDocument`** envelope, not `Publication_MarketDocument`
  — namespace differs (`451-6:balancingdocument:4:4` vs.
  `451-3:publicationdocument`).
- **Value tag** is `imbalance_Price.amount`, not `price.amount`. The parser
  matches via `_matches_value_tag` which accepts any `*_Price.amount` tag
  when `value_tag="price.amount"` is requested — confirmed working on the
  live response.
- **`area_Domain.mRID`** in some envelopes (root level) and `controlArea_Domain.mRID`
  in others — the parser handles both.
- **Direction mapping**: `A19→"long"` (system surplus, TSO sells imbalance)
  and `A20→"short"` (system deficit, TSO buys). `replace_strict` will
  raise on any unknown businessType — silver fails fast on unknowns.

---

## Implementation delta

- Code-tuple: `(A85, None, None — direction encoded by businessType A19/A20 in response, controlArea_Domain)`.
  Guide PDF unfetchable; tuple `unverified - PDF fetch failed` against
  canonical docs. Live FR response (older window 2025-04-01) confirms
  the API accepts the request and returns `Balancing_MarketDocument` with
  `type=A85` and per-direction `<TimeSeries businessType=A19/A20>`. The
  default 2026-05-06 window is too recent for FR balancing settlement
  (publication lag) — use older windows for backfill validation.

---

## Modelling notes

- Used as a feature in cross-zone imbalance correlation studies. For UK
  imbalance modelling, the canonical source is Elexon `system_prices`
  (which has GB-specific run types — initial vs. settlement).
- Build the imbalance spread as `(short - long)` per (timestamp, area) for
  a system-stress signal.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoints](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/imbalance_prices.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
- [Domain: imbalance pricing](../../20-domain/markets/imbalance-price.md)
