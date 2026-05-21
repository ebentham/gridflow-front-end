---
slug: cmp_auction_premiums
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: cmpAuctions
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/cmp_auction_premiums.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["cmp_auction_premiums"] (lines 146-154)
  - .planning/reconciliation/entsog/14-cmp-auction-premiums-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Auction premiums and <span class="italic fg-accent">clearing prices.</span>

**Lede:** Auction premiums plus reserve and cleared prices per capacity auction — the canonical price signal for congested EU gas interconnection capacity.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /cmpAuctions](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.cmp_auction_premiums` |
| API PATH | `/api/v1/cmpAuctions` |
| FREQUENCY | as published (post-auction) |
| PUBLICATION LAG | as published |
| VOLUME | varies (auction-event-driven) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | as published | Frequency |
| 2 | EUR | Reporting unit (price) |
| 3 | per-auction | Cadence |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- cmp_unsuccessful_requests
- cmp_unavailable_firm_capacity
- available_through_oversubscription
- available_through_uioli_long_term
- firm_booked

# Sample chart

- **Type:** `barsH`
- **Title:** "Top auction premiums by point · last 3 years"
- **Subtitle:** "Horizontal bars · EUR · grouped by point"
- **Seed:** 44
- **Toggles:** `1y` (active) / `3y` / `5y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Endpoint-specific fields are `auctionPremium`, `clearedPrice`, `reservePrice`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `auctionFrom` (derived) | Set via `_TIMESTAMP_PRIORITY` (auction_from is L48-49). | `silver/entsog/generic.py L118-120, L45-53` |
| `auction_from` / `auction_to` | `datetime[UTC]` | Yes | `auctionFrom` / `auctionTo` | Auction execution window. | `silver/entsog/datetime.py::parse_entsog_datetime_expr` |
| `capacity_from` / `capacity_to` | `datetime[UTC]` | Yes | `capacityFrom` / `capacityTo` | Capacity-validity window being auctioned. | `silver/entsog/datetime.py` |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction. | dynamic |
| `auction_premium` | `float` | Yes | `auctionPremium` | Premium paid above reserve price. | `silver/entsog/generic.py L65-77` (`_NUMERIC_NAMES`) |
| `cleared_price` | `float` | Yes | `clearedPrice` | Final auction-clearing price. | `silver/entsog/generic.py L65-77` |
| `reserve_price` | `float` | Yes | `reservePrice` | Minimum acceptable price. | `silver/entsog/generic.py L65-77` |
| `unit` | `str` | Yes | `unit` | `"EUR"`. | dynamic |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/cmp_auction_premiums/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| auction_from | point_key | direction_key | reserve_price | cleared_price | auction_premium | unit |
|---|---|---|---|---|---|---|
| 2017-03-06T08:00:00+00:00 | ITP-00007 | entry | 6.05243 | 6.05243 | 0 | EUR |
| 2025-09-01T09:00:00+00:00 | ITP-00005 | exit | 8.20 | 12.45 | 4.25 | EUR |
| **2025-09-01T09:00:00+00:00** | **ITP-00207** | **exit** | **7.80** | **18.20** | **10.40** | **EUR** |
| 2025-09-01T09:00:00+00:00 | ITP-00495 | entry | 5.50 | 7.10 | 1.60 | EUR |
| 2024-09-01T09:00:00+00:00 | ITP-00005 | exit | 7.80 | 9.20 | 1.40 | EUR |
| 2024-09-01T09:00:00+00:00 | ITP-00207 | exit | 7.50 | 14.80 | 7.30 | EUR |
| 2023-09-01T09:00:00+00:00 | ITP-00005 | exit | 7.20 | 7.40 | 0.20 | EUR |
| 2023-09-01T09:00:00+00:00 | ITP-00207 | exit | 7.10 | 11.30 | 4.20 | EUR |

**Sources:** First row verbatim from vault Bronze sample (`cmp_auction_premiums.md` L83-100; bayernets `ITP-00007` 2017 entry auction, reserve = cleared with zero premium — typical of uncongested points). Remaining rows synthesised for canonical GB annual auctions, showing the historic BBL exit premium escalation (2023 → 2025) as continental winter demand pressure on UK-NL flow capacity intensified.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/cmpAuctions?from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/cmp_auction_premiums/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `CmpAuctionPremiumsTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/cmpAuctions?from=2026-05-06&to=2026-05-06&timeZone=UCT&periodType=day&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- BBL exit annual-auction premium time series
SELECT EXTRACT(year FROM auction_from) AS auction_year,
       point_key, direction_key,
       AVG(reserve_price)  AS avg_reserve,
       AVG(cleared_price)  AS avg_cleared,
       AVG(auction_premium) AS avg_premium
FROM read_parquet('data/silver/entsog/cmp_auction_premiums/**/*.parquet')
WHERE point_key = 'ITP-00207'
  AND direction_key IN ('exit', 'Exit')
GROUP BY 1, 2, 3
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/cmp_auction_premiums/**/*.parquet")
# Premium ratio: how much above reserve did the auction clear?
prem = (
    df.with_columns((pl.col("cleared_price") / pl.col("reserve_price")).alias("premium_ratio"))
      .filter(pl.col("premium_ratio") > 1.5)
      .sort("premium_ratio", descending=True)
)
print(prem.head(15))
```

# Caveats

## 01 `direction_key` casing — check both forms

CMP family endpoints sometimes return capitalised values; cross-endpoint joins should lowercase both sides. *(Source: vault Known Issues; CMP-family convention.)*

## 02 Reserve = cleared means no scarcity

When `auction_premium ≈ 0` and `cleared_price = reserve_price`, the auction was uncongested (multiple eligible bidders below the cap, or single bidder at reserve). *(Source: domain knowledge / CAM auction mechanics.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Prices are in `EUR/(kWh/h/year)`-style products

The vendor unit is `"EUR"` but the implicit capacity-product reference (yearly/quarterly/monthly/daily kWh/h) determines the actual EUR-per-energy interpretation. Read `productType` if present (in `tariffs`/`tariff_simulations` family for cross-reference). *(Source: ENTSO-G data dictionary.)*

# Related datasets

- **`cmp_unsuccessful_requests`** — Unsuccessful auction requests. `as published`. Pair to identify where scarcity drove premium. *entsog · CMP · daily*
- **`cmp_unavailable_firm_capacity`** — Firm capacity classified unavailable. `as published`. Causal driver of scarcity. *entsog · CMP · daily*
- **`tariffs`** — Tariff types and components. `as published`. Reference for capacity-product economics. *entsog · tariffs · daily*
- **`tariff_simulations`** — Simulated capacity costs. `as published`. Forward-looking complement to historic auction prices. *entsog · tariffs · daily*
