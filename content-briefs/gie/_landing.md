---
slug: _landing
vendor: gie
vendor_label: GIE Storage
brief_type: landing
vault_dataset_count: 8
last_verified: 2026-05-11
sources_consulted:
  - quant-vault/30-vendors/gie/datasets/ (8 files: about_listing.md, about_summary.md, lng.md, news.md, news_item.md, storage.md, storage_reports.md, unavailability.md)
  - gridflow/src/gridflow/connectors/gie/endpoints.py (AGSI_COUNTRIES L14, ALSI_COUNTRIES L17, GIE_MAX_CALLS_PER_MINUTE L24, ENDPOINTS dict L124–179)
  - gridflow/src/gridflow/connectors/gie/client.py (GieConnector — x-key header auth, dual source_name gie_agsi/gie_alsi, retry policy)
  - gridflow/src/gridflow/schemas/gie.py (2 Pydantic classes: GasStorage, LNGTerminal)
  - "gridflow/src/gridflow/silver/gie/ (2 transformers: agsi.py — 7 classes: GasStorageTransformer, StorageReportsTransformer, AboutListingTransformer, AboutSummaryTransformer, NewsTransformer, NewsItemTransformer, UnavailabilityTransformer; alsi.py — LNGTerminalTransformer)"
  - gridflow-front-end/src/gridflow_front_end/build.py COMING_SOON_VENDORS (two stubs: gie_agsi L134 and gie_alsi L148 — split by sub-product, not yet promoted to REAL_VENDORS)
  - https://agsi.gie.eu (fetched 2026-05-20 — landing page accessible but no machine-readable API docs; vault canonical fallback applied)
  - https://alsi.gie.eu/about (fetched — 404 Not Found; vault canonical fallback applied)
discrepancies_found:
  - source_a: "build.py COMING_SOON_VENDORS (lines 134 + 148)"
    source_a_says: "GIE is represented as two separate COMING_SOON stubs: gie_agsi and gie_alsi — distinct vendor_id entries with separate vendor_label, docs_url, and planned_items"
    source_b: "Phase 8D RECIPE Q-C resolution and CONTEXT D-05"
    source_b_says: "Phase 8D hub is one brief for vendor key `gie` covering both sub-products as two internal groups. The split in COMING_SOON is a build-config artefact; Phase 10 will reconcile."
    orchestrator_recommendation: "Document in caveats — the two COMING_SOON cards will merge into a single REAL_VENDORS['gie'] entry in Phase 10, driven by this brief."
  - source_a: "vault/gie/datasets/lng.md — no Historical depth row"
    source_a_says: "LNG dataset has no explicit earliest-data date in the vault API endpoint table"
    source_b: "vault/gie/datasets/storage.md — Historical depth row"
    source_b_says: "AGSI storage earliest is 2011-01-01 per facility listing records"
    orchestrator_recommendation: "Use 2011-01-01 as the vendor EARLIEST (confirmed for AGSI); annotate LNG earliest as not verified in vault"
  - source_a: "agsi.gie.eu live vendor docs"
    source_a_says: "Landing page is accessible but provides only marketing content — no machine-readable API reference or rate-limit documentation"
    source_b: "vault/gie/datasets/storage.md API endpoint table"
    source_b_says: "Rate limit: 60 calls/minute (vendor-published); Auth: header x-key"
    orchestrator_recommendation: "trust vault — sourced from verified connector implementation"
ready_for_claude_design: true
checked_at: 2026-05-20T12:00:00Z
---

# Editorial layer

**H1 pattern:**

```html
GIE <span class="italic">Storage.</span>
```

**Eyebrow chip:** `GIE · European Union · Gas`

**Illustrative snapshot chip:** yes (standard)

**Lede paragraph (≤60 words):**

Gas Infrastructure Europe — the trade association for European gas storage and LNG operators. AGSI+ publishes daily underground storage levels by country and facility from 2011; ALSI publishes daily LNG terminal inventories and send-out across the same European footprint. Both sub-products share a single `x-key` authentication model on separate hosts.

**CTA 1:** `Browse 8 datasets ↓` (anchors `#datasets`)
**CTA 2:** `Vendor docs ↗` → `https://agsi.gie.eu`

---

# Vendor metadata

| Cell label | Value |
|---|---|
| BASE URL | `agsi.gie.eu` (AGSI+) · `alsi.gie.eu` (ALSI) |
| AUTH | API key · `x-key` request header |
| RATE LIMIT | 1 req/s · project default (60 req/min vendor cap) |
| FORMAT | JSON · ISO-8601 · gas day (06:00 UTC) |
| EARLIEST | 2011-01-01 (AGSI storage) |
| TIMEZONE | UTC · daily gas-day grain |

**Render note for BASE URL cell:** Two hosts — instruct Claude Design to render with `·` separator or `<br/>` between the two values and `font-size: 10px`.

---

# Stats strip

| slot | value | label | source |
|---|---|---|---|
| 1 | `8` | `Datasets` | vault: 8 files in `gie/datasets/` |
| 2 | `2` | `Categories` | 2 groups: AGSI (Storage) + ALSI (LNG) |
| 3 | `9` | `AGSI countries` | AGSI_COUNTRIES in endpoints.py: AT, BE, DE, ES, FR, GB, IT, NL, PL |
| 4 | `2011` | `Storage depth` | Historical depth from vault storage.md: 2011-01-01 |

---

# About section

**Paragraph 1 — Who they are:**

`gie` is Gas Infrastructure Europe, the Brussels-based trade association representing European gas storage operators (AGSI+) and LNG terminal operators (ALSI). The AGSI+ API (`agsi.gie.eu`) publishes Aggregated Gas Storage Inventory data — daily underground storage levels for EU facilities collected directly from member operators. ALSI (`alsi.gie.eu`) publishes the equivalent inventory and send-out figures for LNG import terminals.

**Paragraph 2 — What they publish:**

The eight gridflow datasets span two sub-products. Under AGSI+: `storage` (daily country-level gas-in-storage by GWh and % full), `storage_reports` (the same surface at aggregate/country/company/facility granularity), `unavailability` (outage and maintenance reports), `about_listing` and `about_summary` (operator and facility reference data), and `news` / `news_item` (service announcements). Under ALSI: `lng` (daily LNG terminal inventory, send-out, and injection by country). Both API hosts use the same `/api` path shape and the same `x-key` authentication header.

**Paragraph 3 — Why it matters for energy trading:**

European gas storage levels are the primary structural indicator for gas market tightness. The `storage` % full figure — published daily against a 5-year average benchmark — is the key input for forward gas price modelling over the October–March withdrawal season. Pairing GIE `storage` with ENTSO-G `aggregated_physical_flows` (cross-border nominations) and Elexon `fuelhh` (CCGT dispatch) gives a complete supply-withdrawal-to-power generation chain for GB+EU energy modelling.

---

# Groups

## Group: Storage (AGSI+)

**Blurb:** Daily underground gas storage levels, facility inventory, outages, and operator reference data.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `storage` | Gas storage levels · country · daily | daily | ~16:00 CET same day | ~9 countries / day |
| `storage_reports` | Storage reports · aggregate/country/company/facility | daily | ~16:00 CET same day | varies by scope |
| `unavailability` | Storage unavailability · outage reports | as published | real-time | varies |
| `about_listing` | Operator and facility inventory · flat listing | snapshot | on change | 1 snapshot |
| `about_summary` | Operator and facility reference · hierarchical | snapshot | on change | 1 snapshot |
| `news` | Service announcements · news listing | as published | real-time | rolling ~2-3 yr |
| `news_item` | Announcement detail · by ID | as published | real-time | 1 per ID |

## Group: LNG (ALSI)

**Blurb:** Daily LNG terminal inventory, send-out, and injection by country across EU import terminals.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `lng` | LNG terminal levels · country · daily | daily | daily | ~8 countries / day |

**Row count invariant:** 8 dataset rows across 2 groups == `vault_dataset_count: 8`. ✓

---

# Source map

| Gridflow source | Purpose | Notes |
|---|---|---|
| `connectors/gie/endpoints.py` | AGSI+/ALSI country lists, API path, rate-limit config, ENDPOINTS dict | `AGSI_COUNTRIES` L14 (9 countries); `ALSI_COUNTRIES` L17 (8 countries); `GIE_MAX_CALLS_PER_MINUTE` L24; `ENDPOINTS` dict L124–179 covers 6 AGSI endpoint families |
| `connectors/gie/client.py` | Auth (x-key header), dual source_name routing (gie_agsi vs gie_alsi), pagination, retry policy | `GieConnector` — `source_name = "gie_agsi"` default; ALSI registered separately; auth via `x-key` header from env `GIE_API_KEY` |
| `schemas/gie.py` | 2 Pydantic classes: `GasStorage` (L12) and `LNGTerminal` (L50) | `GasStorage` covers storage + storage_reports paths; `LNGTerminal` covers ALSI lng; reference/news datasets have no dedicated Pydantic schema |
| `silver/gie/agsi.py` | AGSI transformers: `GasStorageTransformer`, `StorageReportsTransformer`, `AboutListingTransformer`, `AboutSummaryTransformer`, `NewsTransformer`, `NewsItemTransformer`, `UnavailabilityTransformer` | 7 transformer classes for 7 AGSI datasets |
| `silver/gie/alsi.py` | ALSI transformer: `LNGTerminalTransformer` | 1 transformer class for `lng` dataset |
| `build.py COMING_SOON_VENDORS` | Two stubs: `gie_agsi` (L134) and `gie_alsi` (L148) — separate entries with different vendor_label and docs_url | Discrepancy: Phase 8D brief treats GIE as one hub (vendor key `gie`); Phase 10 will merge these stubs into `REAL_VENDORS["gie"]` |

---

# Cross-vendor links

- **`entsog` · `aggregated_physical_flows`** — storage withdrawal vs cross-border nominations: AGSI net withdrawal flow vs ENTSO-G point-level interconnection flows. Core supply-side balance check.
- **`elexon` · `fuelhh`** — storage withdrawal vs CCGT dispatch: GIE net withdrawal from GB-connected storage paired with Elexon CCGT fuel half-hourly outturn to trace gas-to-power conversion.
- **`entsoe` · `actual_generation`** — EU-wide gas-burn context: ENTSO-E gas PSR generation aggregated vs GIE EU storage levels for seasonal storage-to-generation attribution.
- **`neso` · `carbon_intensity`** — gas-burn carbon intensity: GIE storage levels drive CCGT dispatch probability, which drives GB grid carbon intensity (gas ≈ 394 gCO2/kWh vs coal ≈ 937 gCO2/kWh in GB).

---

# Caveats

## 01 Two COMING_SOON stubs will merge into one REAL_VENDORS entry in Phase 10

`build.py COMING_SOON_VENDORS` currently has two separate entries for GIE: `gie_agsi` (L134, domain "Gas storage") and `gie_alsi` (L148, domain "LNG"). This is a build-config artefact from earlier planning — the two sub-products were originally considered separate hubs. Phase 8D resolves this: the landing hub for `gie` covers both sub-products as two internal groups (AGSI + ALSI). In Phase 10, both COMING_SOON stubs will be removed and a single `REAL_VENDORS["gie"]` entry added, driven by this brief's `vendor_meta` values.

**Source:** `build.py COMING_SOON_VENDORS` L134 (`gie_agsi`) and L148 (`gie_alsi`); Phase 8D CONTEXT Q-C resolution.

## 02 Authentication required — API key from GIE registration

Unlike ENTSO-G, NESO, and Open-Meteo, GIE requires an API key for all endpoints. The key is passed as an `x-key` request header (lowercase) and sourced from the `GIE_API_KEY` environment variable in gridflow's connector configuration. There is no documented public-access tier — users must register at `agsi.gie.eu/account` to obtain a key. Rate limit is 60 calls/minute (1 per second in gridflow's connector).

**Source:** `connectors/gie/endpoints.py` `GIE_MAX_CALLS_PER_MINUTE`; vault `storage.md` API endpoint table.

## 03 Gas-day convention (06:00 UTC start) differs from calendar day

GIE data uses the European gas-day convention: each gas day starts at 06:00 UTC and ends at 06:00 UTC the following calendar day. The `gasDayStart` field in AGSI responses marks the gas-day open. This differs from calendar-day datasets (e.g. NESO carbon intensity, which runs from 00:00 UTC). When joining GIE daily storage figures with intra-day datasets, align on gas-day open (06:00 UTC) rather than midnight.

**Source:** vault `storage.md` ("Gas day starts 06:00 UTC") and `schemas/gie.py` `GasStorage.gas_day` field.

## 04 Reference datasets (about_listing, about_summary) have no Pydantic schema

Five of the seven AGSI datasets (`about_listing`, `about_summary`, `news`, `news_item`, `unavailability`) have no dedicated Pydantic schema class in `schemas/gie.py`. These datasets use dynamic column materialisation via `AgsiJsonTransformer` in `silver/gie/agsi.py`. Only `storage` and `storage_reports` (both mapping to `GasStorage`) and `lng` (`LNGTerminal`) have typed silver contracts. Downstream consumers of reference and news datasets should not rely on a fixed column schema.

**Source:** `schemas/gie.py` (2 classes only); vault `about_listing.md` Pydantic schema note: "(no dedicated schema — reference data)".

## 05 ALSI earliest data not verified in vault

The AGSI+ `storage` dataset has a confirmed earliest date of 2011-01-01 (from facility listing records). The ALSI `lng` dataset has no explicit earliest-data entry in the vault file. The EARLIEST hero cell in this brief uses 2011-01-01 (the confirmed AGSI bound) as the vendor-level earliest; ALSI earliest should be verified independently when Phase 10 per-dataset briefs are produced.

**Source:** vault `storage.md` ("Historical depth: 2011-01-01"); vault `lng.md` (no Historical depth row present).

---

# Per-vendor cheatsheet

## AGSI country codes

`AT` Austria · `BE` Belgium · `DE` Germany · `ES` Spain · `FR` France · `GB` Great Britain · `IT` Italy · `NL` Netherlands · `PL` Poland

(9 AGSI countries per `AGSI_COUNTRIES` in `connectors/gie/endpoints.py` L14)

## ALSI country codes

`BE` Belgium · `ES` Spain · `FR` France · `GB` Great Britain · `IT` Italy · `NL` Netherlands · `PL` Poland · `PT` Portugal

(8 ALSI countries per `ALSI_COUNTRIES` in `connectors/gie/endpoints.py` L17)

## AGSI endpoint families

| Family | Path | Datasets | Notes |
|---|---|---|---|
| Storage | `/api` | `storage`, `storage_reports` | Paginated; query by aggregate, country, company, or facility |
| Listing | `/api/about` | `about_listing`, `about_summary` | Reference snapshot; use `?show=listing` for flat form |
| News | `/api/news` | `news`, `news_item` | Paginated; item by `turl` param; implementation_phase: deferred |
| Unavailability | `/api/unavailability` | `unavailability` | Paginated; date-windowed |

## GasStorage key fields

`storage_pct_full` (% full, 0-100, clamped by validator) · `net_withdrawal_gwh` (signed daily delta) · `gas_in_storage_gwh` (absolute volume) · `entity_level` (aggregate / country / company / facility) · `gas_day` (date, gas-day grain)

---

# Source-of-truth note

Pages are regenerated from the [gridflow](https://github.com/EBentham/gridflow) ETL pipeline's vault content via `gridflow-build`. Schemas align with `gridflow.schemas.gie` (`GasStorage` for AGSI+ storage data; `LNGTerminal` for ALSI LNG data); values shown in charts are illustrative deterministic snapshots, not live GIE AGSI+ / ALSI responses. The vault's `gie/datasets/` files are the canonical per-dataset reference; this landing brief is the vendor-hub layer above them.
