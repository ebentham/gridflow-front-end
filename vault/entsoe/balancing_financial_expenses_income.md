---
source: entsoe
dataset_key: balancing_financial_expenses_income
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-09
layer_coverage: bronze, silver
---

# ENTSO-E — Financial expenses and income for balancing (A87)

## Overview

Monthly / yearly financial expenses and income that a TSO incurs from
balancing market activity, in EUR. Aggregates the monetary side of
balancing operations: payments to BSPs for activated balancing energy
and reserved capacity, minus revenues from imbalance-charging settlement.
Useful for: cost-of-balancing benchmarking across TSOs, modelling
imbalance-pricing-margin shadow prices, and understanding regulatory
exposure.

A87 is unusual within the H8 family — it carries `<price.amount>`
(monetary EUR amounts) rather than `<quantity>` (MW), and the response
is published as `Publication_MarketDocument` (not `Balancing_MarketDocument`).
TSOs that publish this to ENTSOE do so on a long cadence (monthly
batches typical), so high-frequency queries are expected to return
EMPTY for most timestamps.

A87 uses the older `controlArea_Domain` parameter style (consistent with
its publication-document lineage), distinguishing it from the H8-
balancing-extension siblings that use `area_Domain` /
`connecting_Domain` / `Acquiring_Domain+Connecting_Domain`.

→ Domain concepts:
  [Imbalance pricing](../../20-domain/markets/imbalance-price.md)
  [TSO economics](../../20-domain/concepts/tso-economics.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken=<ENTSOE_API_KEY>` |
| Rate limit       | Vendor-published: not documented. Project default: 1 req/s. |
| Pagination       | None — A87 is sparse, low-cardinality. |
| Historical depth | TODO — A87 catalogue dates listed in the API guide; varies by TSO. GB has no published data. |
| Publication lag  | Months — TSOs typically publish A87 retrospectively in monthly or yearly batches per Reg 17.1.I. |
| Response format  | XML (`Publication_MarketDocument` urn:iec62325.351:tc57wg16:451-3) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | string | Yes | `A87` | `A87` |
| `controlArea_Domain` | string (EIC) | Yes | Control area EIC (NOT `area_Domain`). | `10YGB----------A` |
| `periodStart` | string | Yes | UTC `yyyyMMddHHmm` | `202605070000` |
| `periodEnd` | string | Yes | UTC `yyyyMMddHHmm` | `202605080000` |
| `securityToken` | string | Yes | API key | `<UUID>` |

ENTSOE tuple: `(documentType=A87, processType=n/a, businessType=n/a, area-param-name=controlArea_Domain)`. **A87 has no required `processType` or `businessType` at query level** — the response uses `<Reason.code>` to classify the document semantically (per ENTSOE API guide Section 17.1.I), distinct from the typed-time-series classification used by other H8 datasets. Each `<TimeSeries>` carries its own `<businessType>` (e.g. `B10`) describing what the EUR amount means.

### Working curl example

```bash
curl --ssl-no-revoke -fsS -H "Accept: application/xml" \
  "https://web-api.tp.entsoe.eu/api?documentType=A87&controlArea_Domain=10YGB----------A&periodStart=202605070000&periodEnd=202605080000&securityToken=${ENTSOE_API_KEY}" \
  -o /tmp/entsoe-balancing_financial_expenses_income.xml \
  -w "HTTP %{http_code} | %{size_download} bytes\n"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/balancing_financial_expenses_income/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML (`Publication_MarketDocument`, **not** `Balancing_MarketDocument`).
**Granularity**: One file per (control_area, fetch window).

### Bronze sample

From `tests/fixtures/entsoe/balancing_financial_expenses_income_gb.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Publication_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3">
  <mRID>fixture-balancing-financial-expenses-income-gb-20240115</mRID>
  <revisionNumber>1</revisionNumber>
  <type>A87</type>
  <TimeSeries>
    <mRID>financial-1</mRID>
    <businessType>B10</businessType>
    <controlArea_Domain.mRID codingScheme="A01">10YGB----------A</controlArea_Domain.mRID>
    <Period>
      <timeInterval>
        <start>2024-01-15T00:00Z</start>
        <end>2024-01-15T02:00Z</end>
      </timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><price.amount>35.5</price.amount></Point>
      <Point><position>2</position><price.amount>37.25</price.amount></Point>
    </Period>
  </TimeSeries>
</Publication_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/balancing_financial_expenses_income/year=YYYY/month=MM/balancing_financial_expenses_income_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h8_balancing.BalancingFinancialExpensesIncomeTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeBalancingFinancial`
**Dedup key**: `(timestamp_utc, area_code, business_type)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | derived | UTC-aware. |
| `area_code` | `str` | No | `controlArea_Domain.mRID` | Renamed from `control_area_domain`. |
| `amount_eur` | `float` | No | `<*_Price.amount>` (parser uses `_matches_value_tag` with `value_tag="price.amount"`) | EUR; sign convention is TSO-local. |
| `business_type` | `str` | No | `<businessType>` per TimeSeries | Default "" in canonical. Examples: `B10`, `B11` (TSO-classified expense category). |
| `resolution` | `str` | No | `<resolution>` | Default "" in canonical. |
| `data_provider` | `str` | No | derived | Default "entsoe" in canonical. |
| `ingested_at` | `datetime` | Yes | derived | Nullable (datetime or None). |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2024, 1, 15, 0, 0, tzinfo=UTC),
        "area_code": "10YGB----------A",
        "amount_eur": 35.5,
        "business_type": "B10",
        "resolution": "1:00:00",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 3, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2024, 1, 15, 1, 0, tzinfo=UTC),
        "area_code": "10YGB----------A",
        "amount_eur": 37.25,
        "business_type": "B10",
        "resolution": "1:00:00",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 3, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB returns EMPTY.** Live curl on 2026-05-08 returned reason 999: `No matching data found for Data item FINANCIAL_EXPENSES_AND_INCOME_FOR_BALANCING_R3 [17.1.I] (10YGB----------A)...`.
- **Reason.code semantic classification.** A87 is documented via `Reason.code` rather than typed time series. The publishing TSO encodes the type of expense/income via the `Reason.code` element on the document (or via `<businessType>` per TimeSeries). When ingesting, prefer `businessType` per TimeSeries — it is more granular and present in the fixture.
- **`Publication_MarketDocument`, not `Balancing_MarketDocument`.** Unique within H8: A87 is published under the older Publication document namespace. The transformer uses `value_tag="price.amount"` and `value_column="amount_eur"` to pick this up. The parser's `_matches_value_tag` accepts both `price.amount` and any `*_Price.amount`-suffixed tag.
- **Schema mismatch hint:** The connector's `endpoints.py` registers `domain_style="control_area"` for A87 (which the helper translates to `controlArea_Domain` query param); the silver transformer's `area_columns = ("control_area_domain",)` matches the parser key. Both consistent.
- **Sparse cadence.** Most calendar dates will return EMPTY even for active publishing TSOs. Schedule `daily` is over-zealous — monthly is more realistic. Tracked as a follow-up.

### Control-area vs cross-zonal

A87 is single-area only. There is no cross-zonal financial-expense
counterpart in the ENTSOE catalogue.

---

## Implementation delta

- **A87 uses `controlArea_Domain` (older style) — the lone H8 dataset that does so.** The other H8 balancing datasets (A86/A24/A15/A37/A38) use `area_Domain` / `connecting_Domain` / `Acquiring_Domain` per the H8 spec, but A87 reverts to the legacy `controlArea_Domain` convention. The orchestrator instructions stated *all* four of A37/A24/A15/A38 use `controlArea_Domain` — that is incorrect for A24/A15/A37 (they use `area_Domain` / `connecting_Domain`) but correct only by coincidence for A87.
- **Schedule cadence — RESOLVED in V2 (2026-05-09).** `config/sources.yaml` now registers A87 as `schedule: monthly, max_query_days: 31`. See gridflow commit `fix(V2-D):`.
- **`Reason.code`-based classification not yet exposed in silver — DEFERRED.** Requires base-class refactor of `_H8BalancingTransformer` to extract `<Reason><code>` from the MarketDocument header, plus a new `reason_code` schema column on `EntsoeBalancingFinancial`. Recorded as a backlog item; will land in a follow-up phase.

---

## Changelog

- **2026-05-09 — V2-FIX-06 (5b).** Schedule cadence corrected to monthly (`max_query_days: 31`).
- **2026-05-08 — V1.** Live-validated; cadence + Reason.code gaps surfaced.

---

## Modelling notes

- Use as a **macro-level cost benchmark** rather than a high-frequency feature. Monthly A87 amounts let you compute per-MWh cost-of-balancing for a TSO.
- Useful for: TSO benchmarking studies, regulatory-impact-assessment models, and as a covariate when comparing balancing-market price formation across countries.
- Pair with [imbalance_volume.md](./imbalance_volume.md) and `aggregated_balancing_energy_bids` to compute implied per-MWh balancing cost.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf) — Section 17.1.I
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoint registry](../../../../src/gridflow/connectors/entsoe/endpoints.py) — `balancing_financial_expenses_income`
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h8_balancing.py) — `BalancingFinancialExpensesIncomeTransformer`
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py) — `EntsoeBalancingFinancial`
- [Fixture](../../../../tests/fixtures/entsoe/balancing_financial_expenses_income_gb.xml)
