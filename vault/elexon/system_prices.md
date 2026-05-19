---
source: elexon
dataset_key: system_prices
vendor: Elexon BMRS
last_verified: 2026-05-09
layer_coverage: bronze, silver
---

# Elexon - System Buy/Sell Prices (`DISEBSP`)

## Overview

System Buy Price (SBP) and System Sell Price (SSP) — the cash-out prices used by the GB electricity Balancing Mechanism to settle imbalance. SBP is what generators pay (or are paid) for being short relative to their physical notifications, and SSP is what suppliers pay for being long. Together with the Net Imbalance Volume, this dataset is the canonical signal for short-term GB power-market value and is the basis of the imbalance price in BSC settlement.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/balancing/settlement/system-prices/{settlementDate}` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years (settlement records back to BMRS launch). |
| Publication lag  | Released as the settlement run progresses: II within ~hours, SF on settlement day, R1/R2/R3/RF over reconciliation timeline. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `settlementDate` | string | Yes | The settlement date to filter. This must be in the format yyyy-MM-dd. | `2026-05-06` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/2026-05-06?format=json" \
  -o "/tmp/elexon-system_prices.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/system_prices/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/2026-05-06?format=json:

```json
{
  "metadata": {
    "datasets": [
      "DISEBSP"
    ]
  },
  "data": [
    {
      "settlementDate": "2026-05-06",
      "settlementPeriod": 1,
      "startTime": "2026-05-05T23:00:00Z",
      "createdDateTime": "2026-05-06T23:44:34Z",
      "systemSellPrice": 96.79,
      "systemBuyPrice": 96.79,
      "bsadDefaulted": false,
      "priceDerivationCode": "N",
      "reserveScarcityPrice": 0.0,
      "netImbalanceVolume": -37.99166666666667,
      "sellPriceAdjustment": 0.0,
      "buyPriceAdjustment": 0.0,
      "replacementPrice": null,
      "replacementPriceReferenceVolume": null,
      "totalAcceptedOfferVolume": 578.0084677419355,
      "totalAcceptedBidVolume": -616.25,
      "totalAdjustmentSellVolume": 0.0,
      "totalAdjustmentBuyVolume": 0.0,
      "totalSystemTaggedAcceptedOfferVolume": 578.0084677419355,
      "totalSystemTaggedAcceptedBidVolume": -615.25,
      "totalSystemTaggedAdjustmentSellVolume": null,
      "totalSystemTaggedAdjustmentBuyVolume": null
    },
    {
      "settlementDate": "2026-05-06",
      "settlementPeriod": 2,
      "startTime": "2026-05-05T23:30:00Z",
      "createdDateTime": "2026-05-07T00:14:29Z",
      "systemSellPrice": 97.02,
      "systemBuyPrice": 97.02,
      "bsadDefaulted": false,
      "priceDerivationCode": "N",
      "reserveScarcityPrice": 0.0,
      "netImbalanceVolume": -35.72121737036261,
      "sellPriceAdjustment": 0.0,
      "buyPriceAdjustment": 0.0,
      "replacementPrice": null,
      "replacementPriceReferenceVolume": null,
      "totalAcceptedOfferVolume": 605.8404121863799,
      "totalAcceptedBidVolume": -641.704550703696,
      "totalAdjustmentSellVolume": 0.0,
      "totalAdjustmentBuyVolume": 0.0,
      "totalSystemTaggedAcceptedOfferVolume": 605.8404121863799,
      "totalSystemTaggedAcceptedBidVolume": -640.704550703696,
      "totalSystemTaggedAdjustmentSellVolume": null,
      "totalSystemTaggedAdjustmentBuyVolume": null
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/system_prices/year=YYYY/month=MM/system_prices_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.system_prices.SystemPriceTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonSystemPrice`
**Dedup key**: `(settlement_date, settlement_period)`
**Point-in-time field**: `run_type` (precedence II<SF<R1<R2<R3<RF<DF)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `system_sell_price` | `float` | No | `systemSellPrice` | GBP/MWh; ge=-500 le=10000. |
| `system_buy_price` | `float` | No | `systemBuyPrice` | GBP/MWh. |
| `net_imbalance_volume` | `float` | No | `netImbalanceVolume` | MWh. |
| `run_type` | `str` | Yes | `settlementRunType` (when present) | II / SF / R1 / R2 / R3 / RF / DF — BSC settlement run precedence. `/balancing/settlement/system-prices/{date}` does not expose this field, so live silver from that endpoint has `run_type = None`. Older fixtures and any future endpoint that surfaces `settlementRunType` will populate it. Nullable (Optional[str] in canonical). |
| `price_derivation_code` | `str` | Yes | `priceDerivationCode` | How the SBP/SSP was derived for the period. Observed values: `N` (normal), `P` (provisional). No regex constraint — vendor-managed value list. Nullable (Optional[str] in canonical). |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "settlement_date": "2026-05-06",
        "settlement_period": 1,
        "timestamp_utc": "2026-05-06T00:00:00+00:00",
        "system_sell_price": 96.79,
        "system_buy_price": 96.79,
        "net_imbalance_volume": -37.99166666666667,
        "run_type": null,
        "price_derivation_code": "N",
        "data_provider": "elexon",
        "ingested_at": "2026-05-09T12:00:00Z"
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **Settlement runs**: same `(settlement_date, settlement_period)` reappears with different `run_type` (II → SF → R1 → R2 → R3 → RF → DF) as reconciliation progresses. The transformer keeps the highest-rank run only — for point-in-time queries, write a custom dedup or filter on `published_at` upstream.
- **Settlement period range 1..50** — DST days (46 spring, 50 autumn) handled by `utils/time.settlement_period_to_utc`.

---

## Implementation delta

- **Path**: docs require `{settlementDate}` in path (`/balancing/settlement/system-prices/{settlementDate}`); code declares `path = "/balancing/settlement/system-prices"` and the date is appended in `_fetch_date_path()` — equivalent at request time, but the registry path string is doc-shape-incomplete. Cosmetic.
- **`priceDerivationCode` vs `run_type` mismapping — RESOLVED in V2 (2026-05-09).** Pre-V2 the silver renamed `priceDerivationCode` → `run_type` and the Pydantic regex `^(II|SF|R[1-3]|RF|DF)$` rejected the live values `N` / `P`. V2-FIX-04: silver now maps `priceDerivationCode` → `price_derivation_code` (a separate column with no regex constraint), and the schema's `run_type` is `Optional[str]` because this endpoint exposes no run-type field. Confirmed live 2026-05-09: 48 rows from `/balancing/settlement/system-prices/2026-05-06` round-trip through `ElexonSystemPrice` with 0 errors. See gridflow commit `fix(V2-C):`.

---

## Changelog

- **2026-05-09 — V2-FIX-04.** Silver maps `priceDerivationCode` to dedicated `price_derivation_code` column. Schema `run_type` made `Optional[str]` (this endpoint doesn't surface BSC run type). New schema field `price_derivation_code: str | None`. Regression tests in `tests/unit/test_schemas.py` and `tests/unit/test_silver_transforms.py`.
- **2026-05-08 — V1.** Live-validated; `priceDerivationCode = "N"` regex-mismatch surfaced.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/system_prices.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
