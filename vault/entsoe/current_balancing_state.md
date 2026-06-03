---
source: entsoe
dataset_key: current_balancing_state
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Current balancing state (A86 / B33)

## Overview

Real-time imbalance position of a control area, reported as the
instantaneous net regulating MW required by the TSO to keep system
frequency at nominal. Positive values indicate the system is short
(generation deficit, requiring upward regulation); negative values
indicate the system is long (generation surplus, requiring downward
regulation). Published intra-day at high frequency (typically minute /
quarter-hour resolution) so that operators and balance responsible
parties can anticipate imbalance settlement exposure before period
close.

Document type **A86** is shared with `imbalance_volume`. The two
datasets distinguish themselves only by the `businessType` query
parameter — `B33` (this dataset, regulating reserve / balancing state)
versus `A19` (settled imbalance volumes, see
[imbalance_volume.md](./imbalance_volume.md)). Always specify
`businessType` when calling A86 or you will get an `Acknowledgement`
back with reason 999.

This is the dataset to use for: short-horizon imbalance forecasts,
real-time alerting on system stress, and as a feature in BM activation
likelihood models. Use [imbalance_volume.md](./imbalance_volume.md)
when you need the settled (after-the-fact) volume per settlement period.

→ Domain concepts:
  [Imbalance pricing](../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken=<ENTSOE_API_KEY>` (header auth NOT supported) |
| Rate limit       | Vendor-published: not documented. Project default: 1 req/s. ENTSOE rejects bursts even when calls are sequential — see `_throttle_request`. |
| Pagination       | None for A86. The endpoint returns one Balancing_MarketDocument per call. |
| Historical depth | TODO — H8 balancing extension catalogue went live progressively from 2022. GB control area has no published data (see EMPTY note below). |
| Publication lag  | Near real-time (intra-day) for control areas that publish — minute-to-quarter-hour resolution. |
| Response format  | XML (`Balancing_MarketDocument` urn:iec62325.351:tc57wg16:451-6) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | string (A-code) | Yes | Fixed `A86` | `A86` |
| `businessType` | string (B-code) | Yes | Fixed `B33` (current balancing state). Without this you get reason-999 even on data-rich areas — A86 is shared with imbalance_volume which uses `A19`. | `B33` |
| `area_Domain` | string (EIC) | Yes | Control area EIC. H8 spec uses `area_Domain` here, not `controlArea_Domain`. | `10YGB----------A` |
| `periodStart` | string (yyyyMMddHHmm UTC) | Yes | Window start, intra-day resolution. | `202605070000` |
| `periodEnd` | string (yyyyMMddHHmm UTC) | Yes | Window end. Plan recommends an intra-day window, typically `<= 14h`. | `202605071400` |
| `securityToken` | string (UUID) | Yes | API key from `ENTSOE_API_KEY`. | `<UUID>` |

ENTSOE tuple: `(documentType=A86, processType=n/a, businessType=B33, area-param-name=area_Domain)`.

### Working curl example

```bash
curl --ssl-no-revoke -fsS -H "Accept: application/xml" \
  "https://web-api.tp.entsoe.eu/api?documentType=A86&businessType=B33&area_Domain=10YGB----------A&periodStart=202605070000&periodEnd=202605071400&securityToken=${ENTSOE_API_KEY}" \
  -o /tmp/entsoe-current_balancing_state.xml \
  -w "HTTP %{http_code} | %{size_download} bytes\n"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/current_balancing_state/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML (`Balancing_MarketDocument`), as-received. Immutable — never modified after write.
**Granularity**: One file per (control_area, fetch window) — typically one file per day per area.

### Bronze sample

From `tests/fixtures/entsoe/current_balancing_state_gb.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Balancing_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:balancingdocument:4:0">
  <mRID>fixture-current-balancing-state-gb-20240115</mRID>
  <revisionNumber>1</revisionNumber>
  <type>A86</type>
  <createdDateTime>2024-01-14T12:00:00Z</createdDateTime>
  <TimeSeries>
    <mRID>state-1</mRID>
    <businessType>B33</businessType>
    <area_Domain.mRID codingScheme="A01">10YGB----------A</area_Domain.mRID>
    <Period>
      <timeInterval>
        <start>2024-01-15T00:00Z</start>
        <end>2024-01-15T02:00Z</end>
      </timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>125</quantity></Point>
      <Point><position>2</position><quantity>-75</quantity></Point>
    </Period>
  </TimeSeries>
</Balancing_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/current_balancing_state/year=YYYY/month=MM/current_balancing_state_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h8_balancing.CurrentBalancingStateTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeBalancingState`
**Dedup key**: `(timestamp_utc, area_code, business_type)`
**Point-in-time field**: none (this is a real-time state, not a published-revisions feed)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | derived (Period.timeInterval.start + position * resolution) | Validator rejects naive datetimes. |
| `area_code` | `str` | No | `area_Domain.mRID` | Renamed from `area_domain` by the transformer. |
| `quantity_mw` | `float` | No | `<quantity>` per Point | Sign convention: positive = system short. |
| `business_type` | `str` | No | `<businessType>` | Default "B33" in canonical. Always `B33` for this dataset. |
| `resolution` | `str` | No | `<resolution>` (raw ISO duration) | Default "" in canonical. Emitted verbatim as the ISO-8601 duration code, e.g. `PT60M` / `PT15M`. |
| `data_provider` | `str` | No | derived | Default "entsoe" in canonical. |
| `ingested_at` | `datetime` | Yes | derived (now(UTC) at transform) | Nullable (datetime or None). |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2024, 1, 15, 0, 0, tzinfo=UTC),
        "area_code": "10YGB----------A",
        "quantity_mw": 125.0,
        "business_type": "B33",
        "resolution": "PT60M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 3, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2024, 1, 15, 1, 0, tzinfo=UTC),
        "area_code": "10YGB----------A",
        "quantity_mw": -75.0,
        "business_type": "B33",
        "resolution": "PT60M",
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

- **GB returns EMPTY.** Live curl on 2026-05-08 with `area_Domain=10YGB----------A` and a 14h window returns HTTP 200 with `Acknowledgement_MarketDocument` reason 999: `No matching data found for Data item CURRENT_BALANCING_STATE_R3 [12.3.A] (10YGB----------A)...`. ENTSOE has reduced GB-area coverage post-Brexit; National Grid ESO publishes equivalent data via Elexon BMRS instead.
- **A86 + businessType is mandatory.** Submitting A86 without `businessType` returns reason 999. This is the same documentType used by `imbalance_volume` (with `businessType=A19`). Cross-link: see [imbalance_volume.md](./imbalance_volume.md).
- **Intra-day window required.** This is a real-time state feed, not historical. The plan specifies an intra-day window (e.g. 00:00-14:00) rather than a full day. Long windows (e.g. multi-day) tend to error or return EMPTY for areas that do publish.
- **No DocStatus / mRID on TimeSeries.** Unlike outage feeds, A86 carries no per-TimeSeries status — the document `mRID` and `revisionNumber` at the root are the only versioning artefacts.
- **Sign convention is TSO-local.** Positive vs negative quantity does not have a uniform pan-EU meaning — confirm against the publishing TSO's data dictionary before using as a feature.

---

## Implementation delta

- **Area parameter:** docs/code use `area_Domain`, **not** `controlArea_Domain` as suggested in the V1-PLAN-B4 orchestrator instructions. The H8 balancing extension spec (Article 12.3 of GL EB) uses `area_Domain` for A86/A24/A15. The fixture file at `tests/fixtures/entsoe/current_balancing_state_gb.xml` confirms this — the response carries `<area_Domain.mRID>`. The orchestrator instruction was incorrect; code is right.
- **A86 dual mapping:** This dataset shares documentType A86 with `imbalance_volume` — they differ only by `businessType` (B33 here, A19 there). See [imbalance_volume.md](./imbalance_volume.md) for the settled-volume counterpart.
- **`processType` not specified:** A86/B33 has no `processType` in `endpoints.py` (`process_type=None`). The ENTSOE API guide does not list a process type for B33. Confirmed by successful live (HTTP 200) call without `processType`.
- **`controlArea_Domain` mention in entsoe README:** The current vendor README does not yet document the H8 area_Domain pattern. Will be addressed by the V1-PLAN-B5 aggregate plan.

---

## Modelling notes

- Useful as a **leading indicator** for imbalance price direction. Models that predict period-end imbalance volume / price benefit from A86 features sampled at minute resolution within the period.
- Use as a feature for: BM activation likelihood, imbalance price short-horizon regression, NIV (Net Imbalance Volume) nowcast.
- Caveat for GB: since GB returns EMPTY here, equivalent data must be sourced from Elexon (`freq`, `disbsad`, `imbalngc` family). Cross-area comparisons require pulling from EU-country control areas where A86/B33 is published (e.g. DE-LU, FR).

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf) — Section 17 (Balancing) and 12.3.A
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoint registry](../../../../src/gridflow/connectors/entsoe/endpoints.py) — see `current_balancing_state` entry
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h8_balancing.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py) — `EntsoeBalancingState`
- [Fixture](../../../../tests/fixtures/entsoe/current_balancing_state_gb.xml)
- [Imbalance volume (A86 / A19)](./imbalance_volume.md)
