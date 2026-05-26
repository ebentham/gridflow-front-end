---
slug: _landing
vendor: entsog
vendor_label: ENTSO-G Transparency
brief_type: landing
vault_dataset_count: 33
last_verified: 2026-05-08
sources_consulted:
  - quant-vault/30-vendors/entsog/datasets/ (33 files: all 33 dataset .md files)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py (ENDPOINTS dict — 33 keys across 7 categories; OPERATIONAL_INDICATORS L95–115; DEFAULT_POINT_DIRECTIONS L24–34)
  - gridflow/src/gridflow/connectors/entsog/client.py (EntsogConnector — no auth, ENTSOG_EMPTY_MESSAGE 404-handling, retry policy)
  - gridflow/src/gridflow/schemas/entsog.py (1 Pydantic class: EntsogPhysicalFlow — only physical_flows is typed)
  - gridflow/src/gridflow/silver/entsog/ (3 files: datetime.py, generic.py, physical_flows.py — PhysicalFlowsTransformer registered at L162)
  - gridflow-front-end/src/gridflow_front_end/build.py COMING_SOON_VENDORS (entsog stub — not yet promoted to REAL_VENDORS)
  - https://transparency.entsog.eu/api/v1 (Swagger/OpenAPI page — attempted WebFetch; surfaced in discrepancies_found)
discrepancies_found:
  - source_a: "schemas/entsog.py"
    source_a_says: "Only 1 Pydantic class (EntsogPhysicalFlow) — covers only the physical_flows dataset"
    source_b: "gridflow/src/gridflow/connectors/entsog/endpoints.py ENDPOINTS dict"
    source_b_says: "33 registered endpoints across 7 categories; only physical_flows has a typed silver schema"
    orchestrator_recommendation: "Surface as stats-strip stat and in Source map. Phase 10 dataset briefs will document the 32 schema-absent datasets individually."
  - source_a: "connectors/entsog/endpoints.py ENTSOG_TIMEZONE = 'UCT'"
    source_a_says: "Timezone constant is 'UCT' (not 'UTC') — this is the value ENTSO-G expects as the timeZone query param"
    source_b: "vault/entsog/datasets/physical_flows.md API endpoint table"
    source_b_says: "timeZone:UCT is documented as a known ENTSO-G API quirk"
    orchestrator_recommendation: "Document in TIMEZONE metadata cell and in Caveats as a known vendor quirk. The API returns timestamps in UCT which is an alias for UTC in most implementations, but the parameter must be sent as 'UCT' or the API returns unexpected offsets."
  - source_a: "https://transparency.entsog.eu/api/v1 (live Swagger page)"
    source_a_says: "Swagger UI page is JavaScript-rendered and could not be extracted as flat API facts via WebFetch"
    source_b: "vault/entsog/datasets/physical_flows.md and connector code"
    source_b_says: "All API facts verified in vault from live curl tests; connector is the canonical implementation reference"
    orchestrator_recommendation: "vendor_docs_unfetchable: JavaScript-rendered Swagger UI; vault canonical fallback applied"
ready_for_claude_design: true
checked_at: 2026-05-20T12:00:00Z
---

# Editorial layer

**H1 pattern:**

```html
ENTSO-G <span class="italic">Transparency.</span>
```

**Eyebrow chip:** `ENTSO-G · European Union · Gas`

**Illustrative snapshot chip:** yes (standard)

**Lede paragraph (≤60 words):**

The European Network of Transmission System Operators for Gas Transparency Platform. Point-level operational flows, nominations, capacities, CMP data, and referential network topology for European gas interconnections. Public API, no authentication. 33 endpoints covering GB interconnection points (Bacton IUK/BBL, Moffat) and zone-level aggregated flows.

**CTA 1:** `Browse 33 datasets ↓` (anchors `#datasets`)
**CTA 2:** `Vendor docs ↗` → `https://transparency.entsog.eu`

---

# Vendor metadata

| Cell label | Value |
|---|---|
| BASE URL | `transparency.entsog.eu/api/v1` |
| AUTH | Public · no key required |
| RATE LIMIT | 5 req/s · project default (vendor undocumented) |
| FORMAT | JSON · ISO-8601 · timeZone:UCT |
| EARLIEST | 2010 (operator-dependent) |
| TIMEZONE | UCT · day periods (vendor quirk — not UTC) |

---

# Stats strip

| slot | value | label | source |
|---|---|---|---|
| 1 | `33` | `Datasets` | vault: 33 files in `entsog/datasets/` |
| 2 | `5` | `Categories` | 5 groups in this brief (Operational + Zone + CMP + Tariff + Reference) |
| 3 | `9` | `GB interconnection points` | DEFAULT_POINT_DIRECTIONS in endpoints.py: Bacton IUK (×3), Bacton BBL (×3), Moffat IE (×2), Moffat (×1) |
| 4 | `1` | `Typed schema` | Only physical_flows has a Pydantic schema (EntsogPhysicalFlow); 32 datasets are schema-absent |

---

# About section

**Paragraph 1 — Who they are:**

`entsog` is the ENTSO-G Transparency Platform, operated by the European Network of Transmission System Operators for Gas. It publishes cross-border gas flow data collected from European transmission system operators under EU Regulation 715/2009 and subsequent network codes. All data is public and free to access — no registration or API key required.

**Paragraph 2 — What they publish:**

33 endpoint surfaces fall into five functional groups. **Operational Data** (19 datasets): point-level physical flows, nominations, allocations, renominations, capacity indicators (firm/interruptible), and gas quality indicators (GCV, Wobbe index, methane/hydrogen/oxygen content). **Zone Data** (1 dataset): aggregated zone-level physical flows for balancing areas. **CMP Data** (3 datasets): Congestion Management Procedure records — unsuccessful requests, unavailable firm capacity, and auction premiums. **Tariff Data** (2 datasets): tariff components and simulations. **Reference Data** (7 datasets — 6 reference + 1 interruptions + 1 UMM): operators, connection points, balancing zones, operator-point-direction combos, interconnections, aggregate interconnections, interruptions, and urgent market messages.

**Paragraph 3 — Why it matters for energy trading:**

ENTSO-G `aggregated_physical_flows` and `physical_flows` are the primary real-time indicators of European gas supply tightness — especially through the GB interconnections at Bacton (IUK pipeline to Netherlands, BBL pipeline to Netherlands) and Moffat (GB-Ireland). Net exit flow from GB storage via these points, combined with GIE `storage` withdrawal data, gives the most direct observable measure of GB gas supply adequacy. Pair with Elexon `fuelhh` to close the gas-to-power conversion chain.

---

# Groups

## Group: Operational · Point Data

**Blurb:** Point-level gas flows, nominations, capacities, and quality indicators at GB interconnection points.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `physical_flows` | Physical flows · all EU points | daily | same day (Provisional) | varies by point |
| `nominations` | Nominations · GB interconnection points | daily | same day | ~9 points / day |
| `allocations` | Allocations · GB interconnection points | daily | ~1 day | ~9 points / day |
| `renominations` | Renominations · GB interconnection points | daily | same day | ~9 points / day |
| `firm_available` | Firm available capacity · GB points | daily | same day | ~9 points / day |
| `firm_booked` | Firm booked capacity · GB points | daily | same day | ~9 points / day |
| `firm_technical` | Firm technical capacity · GB points | daily | same day | ~9 points / day |
| `interruptible_available` | Interruptible available capacity · GB points | daily | same day | ~9 points / day |
| `interruptible_booked` | Interruptible booked capacity · GB points | daily | same day | ~9 points / day |
| `interruptible_total` | Interruptible total capacity · GB points | daily | same day | ~9 points / day |
| `gcv` | Gross calorific value · GB points | daily | same day | ~9 points / day |
| `wobbe_index` | Wobbe index · GB points | daily | same day | ~9 points / day |
| `methane_content` | Methane content · GB points | daily | same day | ~9 points / day |
| `hydrogen_content` | Hydrogen content · GB points | daily | same day | ~9 points / day |
| `oxygen_content` | Oxygen content · GB points | daily | same day | ~9 points / day |
| `available_through_oversubscription` | Available through oversubscription · GB points | daily | same day | ~9 points / day |
| `available_through_surrender` | Available through surrender · GB points | daily | same day | ~9 points / day |
| `available_through_uioli_long_term` | Available through UIOLI long-term · GB points | daily | same day | ~9 points / day |
| `available_through_uioli_short_term` | Available through UIOLI short-term · GB points | daily | same day | ~9 points / day |

## Group: Zone Data

**Blurb:** Aggregated zone-level physical flows for GB and Irish balancing areas.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `aggregated_physical_flows` | Aggregated physical flows · zone level | daily | same day | ~5 zone directions |

## Group: CMP Data

**Blurb:** Congestion Management Procedure records — unsuccessful requests, unavailable firm capacity, auction premiums.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `cmp_unsuccessful_requests` | CMP unsuccessful requests | daily | as published | varies |
| `cmp_unavailable_firm_capacity` | CMP unavailable firm capacity | daily | as published | varies |
| `cmp_auction_premiums` | CMP auction premiums | daily | as published | varies |

## Group: Tariff Data

**Blurb:** Tariff components and simulation costs for UK transmission entry/exit.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `tariffs` | Tariff types and components · UK | as published | — | varies |
| `tariff_simulations` | Tariff simulation costs · UK | as published | — | varies |

## Group: Reference · Network Topology

**Blurb:** Operators, connection points, balancing zones, interruptions, and urgent market messages.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `connection_points` | Connection points · EU network map | snapshot | on change | varies |
| `operators` | Transmission system operators | snapshot | on change | varies |
| `balancing_zones` | European balancing zones | snapshot | on change | varies |
| `operator_point_directions` | Operator-point-direction combos | snapshot | on change | varies |
| `interconnections` | Interconnections from/to UK | snapshot | on change | varies |
| `aggregate_interconnections` | Aggregate interconnections · UK | snapshot | on change | varies |
| `interruptions` | Planned and unplanned interruptions | daily | as published | varies |
| `urgent_market_messages` | Urgent market messages | as published | real-time | varies |

**Row count:** 19 + 1 + 3 + 2 + 8 = 33 dataset rows across 5 groups == `vault_dataset_count: 33`. ✓

---

# Source map

| Gridflow source | Purpose | Notes |
|---|---|---|
| `connectors/entsog/endpoints.py` | 33 endpoint registrations; OPERATIONAL_INDICATORS (L95–115, 19 operational datasets); ENDPOINTS dict (L118–258); DEFAULT_POINT_DIRECTIONS (L24–34, 9 GB/IE interconnection point keys) | `ENTSOG_TIMEZONE = "UCT"` L17 — vendor quirk; `ENTSOG_ALL_RECORDS_LIMIT = -1` L19 for unbounded result sets |
| `connectors/entsog/client.py` | No-auth connector; `_ENTSOG_EMPTY_MESSAGE = "No result found"` — ENTSO-G returns HTTP 404 with body for empty results (not an error); retry policy | `EntsogConnector` — source_name = "entsog"; 404-special-casing documented in module docstring |
| `schemas/entsog.py` | 1 Pydantic class: `EntsogPhysicalFlow` (L12) — typed schema for physical_flows only | Major coverage gap: 32 of 33 datasets have no Pydantic schema. This is a Phase 10 work item. |
| `silver/entsog/physical_flows.py` | `PhysicalFlowsTransformer` (L36) — registered at L162 | One transformer for one dataset; generic.py provides base JSON transform helpers; datetime.py provides UCT→UTC normalisation |
| `silver/entsog/generic.py` | Base transformation helpers shared across ENTSOG datasets | Not a transformer class — shared utility module |
| `silver/entsog/datetime.py` | UCT→UTC timestamp normalisation | Handles ENTSO-G's `UCT` timezone label, which most datetime parsers reject |
| `build.py COMING_SOON_VENDORS` | `entsog` stub — `vendor_label = "ENTSO-G Transparency"`, `vendor_docs_url = "https://transparency.entsog.eu/"` | Not yet promoted to `REAL_VENDORS`; this brief defines the `vendor_meta` block for Phase 10 promotion |

---

# Cross-vendor links

- **`gie` · `storage`** — withdrawal vs nominations: GIE daily net withdrawal from EU storage paired with ENTSO-G nominations at GB interconnection points for gas supply adequacy modelling.
- **`elexon` · `fuelhh`** — gas-to-power conversion chain: ENTSO-G physical flows at Bacton/Moffat → CCGT generation outturn in Elexon fuelhh. The supply side and burn side of the gas market in GB.
- **`entsoe` · `actual_generation`** — EU-wide gas burn: ENTSO-G cross-border flows to power stations aggregated with ENTSO-E generation by PSR type for EU gas-to-generation attribution.
- **`neso` · `carbon_intensity`** — gas nominations → carbon signal: ENTSO-G net import nominations predict CCGT dispatch likelihood 1–3 days ahead, which leads the NESO carbon intensity forecast.

---

# Caveats

## 01 UCT timezone quirk — not a typo

ENTSO-G's API expects `timeZone=UCT` (not `UTC`) as a query parameter. Sending `UTC` returns timestamps offset by the difference between UCT and the local time zone. The gridflow connector encodes `ENTSOG_TIMEZONE = "UCT"` in `endpoints.py` L17 and always passes it explicitly. The `silver/entsog/datetime.py` module normalises the resulting "UCT"-labelled timestamps to proper UTC datetimes at silver write time.

**Source:** `connectors/entsog/endpoints.py` L17; vault `physical_flows.md` API endpoint table.

## 02 Only 1 of 33 datasets has a Pydantic schema

`schemas/entsog.py` defines a single class (`EntsogPhysicalFlow`) covering the `physical_flows` dataset. The remaining 32 datasets — including nominations, capacities, CMP, tariffs, and all reference datasets — have no typed silver schema. Downstream consumers of these datasets receive raw Polars DataFrames with no Pydantic validation layer. Phase 10 per-dataset briefs will expand schema coverage as part of the silver-layer maturation work.

**Source:** `schemas/entsog.py` (1 class); `silver/entsog/physical_flows.py` L162 (only transformer registered to date).

## 03 ENTSO-G returns HTTP 404 for empty result windows — not an error

When no data exists for a requested date range and point combination, the ENTSO-G API returns HTTP 404 with a body `{"message": "No result found"}`. This is not an error — it is the API's documented empty-set convention. The gridflow connector (`client.py`) special-cases this response to emit an empty bronze file rather than raising an HTTP error. Consumers that bypass the connector and call the API directly must implement this 404-handling.

**Source:** `connectors/entsog/client.py` module docstring; `_ENTSOG_EMPTY_MESSAGE = "No result found"`.

## 04 Operational data historical depth is operator-dependent (~2010)

Unlike ENTSO-E (which has a well-defined historical API going back to 2015 for most surfaces), ENTSO-G's historical depth varies by operator and point. The physical_flows surface goes back approximately to 2010 for the main GB interconnection points (Bacton IUK, Bacton BBL, Moffat). Capacity and quality indicator surfaces may have shallower history. The vault notes "approx. 2010 onwards (operator-dependent)" as the canonical depth estimate.

**Source:** vault `physical_flows.md` Historical depth: "Approx. 2010 onwards (operator-dependent)".

## 05 Vendor API docs (Swagger UI) not WebFetch-parseable

The ENTSO-G API documentation at `https://transparency.entsog.eu/api/v1` is a JavaScript-rendered Swagger UI. WebFetch cannot extract the full OpenAPI spec. All API facts in this brief are sourced from the vault's curl-verified dataset files and from the gridflow connector implementation, which represents the ground-truth implementation of the ENTSO-G surface.

**Source:** attempted WebFetch `https://transparency.entsog.eu/api/v1` — JavaScript-rendered; vault canonical fallback applied.

---

# Per-vendor cheatsheet

## Endpoint categories

| Category | Count | Representative keys |
|---|---|---|
| Point Operational Data | 19 | `physical_flows`, `nominations`, `firm_available`, `gcv`, `hydrogen_content` |
| Zone Data | 1 | `aggregated_physical_flows` |
| CMP Data | 3 | `cmp_unsuccessful_requests`, `cmp_unavailable_firm_capacity`, `cmp_auction_premiums` |
| Tariff Data | 2 | `tariffs`, `tariff_simulations` |
| Referential Data | 6 | `connection_points`, `operators`, `balancing_zones`, `operator_point_directions`, `interconnections`, `aggregate_interconnections` |
| Interruptions | 1 | `interruptions` |
| UMM Data | 1 | `urgent_market_messages` |

## DEFAULT_POINT_DIRECTIONS (GB/IE interconnection points)

| Key | Description |
|---|---|
| `UK-TSO-0001ITP-00005exit` | Bacton (IUK) — UK exit |
| `UK-TSO-0003ITP-00005entry` | Bacton (IUK) — UK entry |
| `UK-TSO-0003ITP-00005exit` | Bacton (IUK) — UK exit |
| `UK-TSO-0001ITP-00207exit` | Bacton (BBL) — UK exit |
| `UK-TSO-0004ITP-00063entry` | Julianadorp/Balgzand (BBL) — entry |
| `UK-TSO-0004ITP-00063exit` | Julianadorp/Balgzand (BBL) — exit |
| `IE-TSO-0002ITP-00495entry` | Moffat (IE) — entry |
| `IE-TSO-0002ITP-00495exit` | Moffat (IE) — exit |
| `UK-TSO-0001ITP-00090entry` | Moffat — UK entry |

## OPERATIONAL_INDICATORS mapping

`physical_flows` → `Physical Flow` · `nominations` → `Nomination` · `allocations` → `Allocation` · `renominations` → `Renomination` · `firm_available` → `Firm Available` · `firm_booked` → `Firm Booked` · `firm_technical` → `Firm Technical` · `interruptible_available` → `Interruptible Available` · `interruptible_booked` → `Interruptible Booked` · `interruptible_total` → `Interruptible Total` · `gcv` → `GCV` · `wobbe_index` → `Wobbe Index` · `methane_content` → `Methane Content` · `hydrogen_content` → `Hydrogen Content` · `oxygen_content` → `Oxygen Content` · `available_through_oversubscription` → `Available through Oversubscription` · `available_through_surrender` → `Available through Surrender` · `available_through_uioli_long_term` → `Available through UIOLI long-term` · `available_through_uioli_short_term` → `Available through UIOLI short-term`

---

# Source-of-truth note

Pages are regenerated from the [gridflow](https://github.com/EBentham/gridflow) ETL pipeline's vault content via `gridflow-build`. Schemas align with `gridflow.schemas.entsog` (`EntsogPhysicalFlow` for physical flow data; other datasets have no Pydantic schema yet); values shown in charts are illustrative deterministic snapshots, not live ENTSO-G Transparency Platform responses. The vault's `entsog/datasets/` files are the canonical per-dataset reference; this landing brief is the vendor-hub layer above them.
