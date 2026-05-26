---
source: entsoe
dataset_key: day_ahead_prices
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Day-ahead Prices (A44)

## Overview

Day-ahead market clearing prices in EUR/MWh for each bidding zone, published
by the ENTSO-E Transparency Platform (Article 12.1.D of EU Regulation
543/2013). Each `<TimeSeries>` represents an `(in_Domain, out_Domain)` pair
(typically the same EIC for an internal day-ahead price); `<Point>` elements
carry the cleared price for each settlement interval (typically PT60M or
PT15M for the integrated 15-minute markets).

This is the canonical EU price reference for spread modelling across
interconnected zones — used as the baseline against which UK GB prices,
balancing prices, and intraday prices are compared. Post-Brexit, GB
day-ahead prices are not published on ENTSO-E (returns Acknowledgement code
999 — see Implementation delta below).

→ Link to relevant domain concept notes if they exist, e.g.:
  [Day-ahead market](../../20-domain/markets/day-ahead.md)
  [EIC codes](../../20-domain/concepts/eic-codes.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken` from env var `ENTSOE_API_KEY` |
| Rate limit       | Not vendor-published — codebase configured at 1 req/s; treat 1 req/s as polite |
| Pagination       | None |
| Historical depth | ~5 years on most zones (vendor-bounded) |
| Publication lag  | ~12:55 CET D-1 for D, then revisions |
| Response format  | XML (Publication_MarketDocument); larger windows may be returned as a ZIP-of-XML |
| Document type    | `A44` |
| Process type     | n/a |
| Domain param name | `in_Domain`, `out_Domain` (zone-pair, both set to the bidding zone EIC for an internal day-ahead price) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | yes | API key (UUID) | `<your-entsoe-api-key>` |
| `documentType` | str | yes | Always `A44` | `A44` |
| `in_Domain` | str (EIC mRID) | yes | Bidding zone EIC | `10Y1001A1001A82H` |
| `out_Domain` | str (EIC mRID) | yes | Bidding zone EIC (= `in_Domain` for an intra-zone price) | `10Y1001A1001A82H` |
| `periodStart` | str (`yyyyMMddHHmm` UTC) | yes | Window start | `202605060000` |
| `periodEnd` | str (`yyyyMMddHHmm` UTC) | yes | Window end (max one year, vendor-enforced) | `202605070000` |

### Working curl example

```bash
# Replace <your-entsoe-api-key> with $ENTSOE_API_KEY
curl -X GET --ssl-no-revoke \
  "https://web-api.tp.entsoe.eu/api?securityToken=<your-entsoe-api-key>&documentType=A44&in_Domain=10Y1001A1001A82H&out_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000" \
  -H "Accept: application/xml"
```

Note: GB (`10YGB----------A`) returns Acknowledgement code 999 ("No matching
data found for Data item ENERGY_PRICES [12.1.D]") because GB exited the
EU day-ahead market after Brexit. Use Elexon `system_prices` for GB.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/day_ahead_prices/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, as-received. Immutable — never modified after write.
**Granularity**: One file per (zone, query window). ZIP responses (large windows) are unpacked and each inner XML is stored as a separate raw file.

### Bronze sample

(First ~500 bytes of a DE-LU PT60M day-ahead response, 2026-05-06.)

```json
{
  "envelope": "Publication_MarketDocument xmlns='urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3'",
  "type": "A44",
  "createdDateTime": "2026-05-05T11:00:00Z",
  "TimeSeries": [
    {
      "mRID": "1",
      "businessType": "A62",
      "in_Domain.mRID": "10Y1001A1001A82H",
      "out_Domain.mRID": "10Y1001A1001A82H",
      "currency_Unit.name": "EUR",
      "price_Measure_Unit.name": "MWH",
      "Period": {
        "timeInterval": {"start": "2026-05-06T00:00Z", "end": "2026-05-07T00:00Z"},
        "resolution": "PT60M",
        "Point": [
          {"position": 1, "price.amount": 85.50},
          {"position": 2, "price.amount": 82.30}
        ]
      }
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/day_ahead_prices/year=YYYY/month=MM/day_ahead_prices_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.day_ahead_prices.DayAheadPricesTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeDayAheadPrice`
**Dedup key**: `(timestamp_utc, area_code)` — last write wins
**Point-in-time field**: none (day-ahead prices are not revised — `data_provider` and `ingested_at` are tracking-only)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` (tz-aware UTC) | No | `Period.timeInterval.start + (position-1)*resolution` | Rejected if naive |
| `area_code` | `str` | No | `TimeSeries/in_Domain.mRID` | EIC bidding zone mRID, as-is (no normalisation) |
| `price_eur_mwh` | `float` | No | `Point/price.amount` | EUR/MWh (currency_Unit + price_Measure_Unit) |
| `resolution` | `str` | No (default `""`) | `Period/resolution` | ISO duration: `PT60M` or `PT15M` |
| `data_provider` | `str` | No (default `"entsoe"`) | derived | Constant `"entsoe"` |
| `ingested_at` | `datetime` (tz-aware UTC) | Yes | derived | Set by transformer at silver write |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2026, 5, 6, 0, 0, tzinfo=UTC),
        "area_code": "10Y1001A1001A82H",
        "price_eur_mwh": 85.50,
        "resolution": "PT60M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 4, 28, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2026, 5, 6, 1, 0, tzinfo=UTC),
        "area_code": "10Y1001A1001A82H",
        "price_eur_mwh": 82.30,
        "resolution": "PT60M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 4, 28, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB returns Acknowledgement code 999** — post-Brexit, GB day-ahead prices
  are not published via ENTSO-E. The connector still queries GB by default
  (`DEFAULT_ZONES` includes `GB`); the silver transformer simply produces
  zero rows for GB. Use Elexon `system_prices` for GB market reference.
- **15-minute zones**: DE-LU and a growing list of zones publish PT15M
  resolution. The silver schema preserves `resolution` as a string;
  downstream gold/model layers must aggregate or interpolate as needed.
- **ZIP-of-XML responses**: large windows (multi-day) may be returned as a
  ZIP archive containing day-partitioned XML files. The connector
  auto-detects (`PK\x03\x04` magic bytes) and unpacks before silver parsing.
- **`in_Domain` == `out_Domain`** for intra-zone day-ahead prices. The
  connector sends both with the same EIC; silver maps `in_Domain.mRID`
  to `area_code`.
- **No revisions**: day-ahead prices are not republished post-clearing.
  The dedup `(timestamp_utc, area_code)` is sufficient; no `run_type`
  needed.

---

## Implementation delta

- **Tuple comparison**: code-tuple in `endpoints.py` for `day_ahead_prices`
  is `(documentType=A44, processType=None, businessType=None, domain=in_Domain+out_Domain)`.
  Reference docs (ENTSO-E Static Content Guide PDF) could not be fetched
  directly during this validation pass (`HTTP 400` from
  `transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf`
  — likely CDN protection); the tuple is `unverified - PDF fetch failed`
  against the canonical guide. However the live response on a known-good
  zone (DE-LU) returns a well-formed `<Publication_MarketDocument><type>A44`
  with `<TimeSeries>`, confirming the request shape is accepted by the API.
- No discrepancies between the connector's request shape and the live API's
  accepted shape were observed.

---

## Modelling notes

- Used as the reference EU spot reference for cross-border spread features
  (FR, NL, BE, IE-SEM vs. GB). For UK price modelling, GB clearing comes
  from Elexon (`system_prices`) and the EU side from ENTSO-E here.
- Common derived features: hourly clean-spark spread, peak/off-peak diff,
  rolling daily volatility, day-of-week mean.
- Filter rule: drop rows with `area_code == "10YGB----------A"` for any
  modelling feature (always empty post-Brexit).

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoints](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/day_ahead_prices.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
- [Domain: day-ahead market](../../20-domain/markets/day-ahead.md)
