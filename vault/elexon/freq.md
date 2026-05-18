---
source: elexon
dataset_key: freq
vendor: Elexon BMRS
last_verified: 2026-05-09
layer_coverage: bronze, silver
---

# Elexon - System Frequency (`FREQ`)

## Overview

System frequency measurements — instantaneous samples of the GB transmission system frequency, nominally 50 Hz with a statutory operating range of 49.5–50.5 Hz. The dataset is a high-frequency (sub-minute) telemetry stream used in operational frequency-response models, as a regressor for ancillary services costs, and to validate frequency-keeping performance under the Frequency Response services.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/FREQ` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Several years. |
| Publication lag  | Continuous stream, ~2-second sampling, exposed as 1-minute aggregates. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `measurementDateTimeFrom` | string | No | As per Elexon Swagger spec for freq. | `2026-05-06T00:00Z` |
| `measurementDateTimeTo` | string | No | As per Elexon Swagger spec for freq. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/FREQ?measurementDateTimeFrom=2026-05-06T00:00Z&measurementDateTimeTo=2026-05-06T03:00Z&format=json" \
  -o "/tmp/elexon-freq.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/freq/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/FREQ?measurementDateTimeFrom=2026-05-06T00:00Z&measurementDateTimeTo=2026-05-06T03:00Z&format=json (re-verified with corrected param names 2026-05-09):

```json
{
  "data": [
    {
      "dataset": "FREQ",
      "measurementTime": "2026-05-08T00:00:00Z",
      "frequency": 49.97
    },
    {
      "dataset": "FREQ",
      "measurementTime": "2026-05-07T23:59:45Z",
      "frequency": 50.017
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/freq/year=YYYY/month=MM/freq_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.elexon.freq.FreqTransformer`
**Pydantic schema**: `gridflow.schemas.elexon.ElexonFrequency`
**Dedup key**: `(timestamp_utc)`
**Point-in-time field**: `ingested_at` (no native PIT field)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | `reportDateTime` or `measurementTime` | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `frequency_hz` | `float` | No | `frequency` | Hz; ge=49.0 le=51.0. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-08T00:00:00Z",
        "frequency_hz": 49.97,
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

- **High-frequency stream**: ~5760 samples per 3-hour window. Bronze files can grow large — partition by hour or use a streaming silver pipeline if querying long ranges.
- **Historical bronze re-ingest required**: existing bronze files for `freq` were captured before V2-FIX-01 with the wrong param names — they hold "latest 5761 samples" rather than the requested window. Re-ingest historical FREQ to get correctly-windowed bronze on disk.

---

## Implementation delta

- **Param-name mismatch — RESOLVED in V2 (2026-05-09).** Connector now sends the Swagger-correct `measurementDateTimeFrom`/`measurementDateTimeTo`. See gridflow commit `fix(V2-A):` on `claude/lucid-mccarthy-9ed3e0`. Live re-verification 2026-05-09: `?measurementDateTimeFrom=2026-05-09T00:00Z&measurementDateTimeTo=2026-05-09T01:00Z` returns 241 rows, all within the 1-hour window.

---

## Changelog

- **2026-05-09 — V2-FIX-01.** Connector `from_param`/`to_param` override on `ENDPOINTS["freq"]` now sends `measurementDateTimeFrom`/`measurementDateTimeTo` (per Swagger). API previously silently ignored the wrong-named params and returned latest 5761 samples regardless of window. Regression tests added under `tests/unit/test_elexon_endpoints.py` and `tests/endpoints/test_endpoint_urls.py`.
- **2026-05-08 — V1.** Live-validated; bug surfaced + documented.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/freq.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
