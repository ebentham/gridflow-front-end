# Quant Vault vs GridFlow Implementation Cross-Reference

Date: 2026-05-19

## Direct Answer

The earlier vendor-doc research pass used the vendored snapshot in:

`C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\vault`

It did **not** use the upstream GitHub vault at:

`https://github.com/EBentham/quant-vault`

This follow-up inspected the upstream vault from GitHub and cross-referenced it against the local `gridflow` data pipeline implementation.

## Sources Checked

- Upstream vault: `EBentham/quant-vault`, cloned read-only to a temp checkout at commit `f649e6a7fa6a66f748c22b9c622b2a55aac0f6c1`.
- Frontend vendored snapshot: `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\vault`, repo commit `2884912a3b485abe468a95099dd986e2fd73d980`.
- GridFlow pipeline: `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow`, repo commit `5644682072ee94f275d28001a3a3d07d74331ed1`.
- Pipeline implementation files used:
  - `config/sources.yaml`
  - `src/gridflow/connectors/*/endpoints.py`
  - `src/gridflow/connectors/gie/client.py`
  - `src/gridflow/silver/registry.py`
  - `src/gridflow/silver/*`
  - `docs/*_endpoint_catalog.yaml`
- Vault implementation files used:
  - `30-vendors/machine-catalog.json`
  - `30-vendors/machine-catalog.validation.json`
  - `30-vendors/*/datasets/*.md`
  - `README.md`

## Upstream Vault Shape

`EBentham/quant-vault` is the fuller upstream vault, not the small vendored frontend snapshot. Its README says the frontend consumes a vendored snapshot from `gridflow-front-end/vault/<vendor>/`, while the upstream vault stores per-vendor dataset notes under `30-vendors/<vendor>/datasets/<slug>.md`.

The upstream machine catalog currently contains 162 datasets:

| Source | Upstream vault datasets |
| --- | ---: |
| elexon | 33 |
| entsoe | 49 |
| entsog | 33 |
| gie_agsi | 7 |
| gie_alsi | 1 |
| neso | 33 |
| open_meteo | 6 |
| Total | 162 |

The upstream validation file classifies those 162 entries as:

| Status | Count |
| --- | ---: |
| active_connector_dataset | 160 |
| silver_only_not_in_connector_config | 1 |
| deprecated_or_duplicate_pointer | 1 |

## Frontend Snapshot Gap

The local frontend snapshot is materially behind the upstream vault:

| Vendor snapshot | Local frontend notes | Upstream equivalent |
| --- | ---: | ---: |
| elexon | 33 | 33 |
| entsoe | 25 | 49 |
| entsog | 5 | 33 |
| gie | 0 | 8 |
| neso | 0 | 33 |
| open_meteo | 0 | 6 |

So the frontend-facing vault snapshot is missing 99 upstream dataset notes:

- ENTSO-E: 24 missing from the local snapshot.
- ENTSO-G: 28 missing from the local snapshot.
- GIE: 8 missing from the local snapshot.
- NESO: 33 missing from the local snapshot.
- Open-Meteo: 6 missing from the local snapshot.

Elexon is the only local snapshot vendor that already matches the upstream vault count.

## GridFlow Pipeline Cross-Reference

GridFlow has three relevant implementation layers:

- Bronze source config: `config/sources.yaml`
- Connector endpoint registries: `src/gridflow/connectors/*/endpoints.py`
- Silver transformer registry: populated by `src/gridflow/silver/*`

Dataset-key comparison:

| Source | Upstream vault | GridFlow source config | Connector registry | Silver registry | Assessment |
| --- | ---: | ---: | ---: | ---: | --- |
| elexon | 33 | 33 | 33 | 33 | Matches |
| entsoe | 49 | 47 | 47 | 48 | Two known exceptions |
| entsog | 33 | 33 | 33 | 33 | Matches |
| gie_agsi | 7 | 7 | 6 family endpoints | 7 | Matches after accounting for `storage` alias |
| gie_alsi | 1 | 1 | GIE client family | 1 | Matches |
| neso | 33 | 33 | 33 | 33 | Matches |
| open_meteo | 6 | 6 | 6 | 6 | Matches |

## Dataset-Level Exceptions

### `entsoe/activated_balancing_qty`

Status: present in upstream vault, present in silver, absent from active source config and connector `DOC_TYPES`.

Evidence:

- Upstream vault validation labels it `silver_only_not_in_connector_config`.
- `src/gridflow/silver/entsoe/activated_balancing_qty.py` registers a silver transformer.
- `config/sources.yaml` does not include it as an active `entsoe` source dataset.
- `src/gridflow/connectors/entsoe/endpoints.py` does not include it in `DOC_TYPES`.
- `docs/entsoe_endpoint_catalog.yaml` records the reason: the default GB control area rejects A83 via the service; schema/transformer support remains, but active UK-centric ingestion excludes it until a supported control-area strategy is introduced.

Frontend implication: show this as a documented but inactive/silver-only dataset, not as an ordinary active pipeline dataset.

### `entsoe/commercial_schedules_net_positions`

Status: present in upstream vault, absent from active source config and silver, intentionally removed from connector registry.

Evidence:

- Upstream vault validation labels it `deprecated_or_duplicate_pointer`.
- `config/sources.yaml` comments that `commercial_schedules_net_positions` was removed in V2 under ADR-019.
- `src/gridflow/connectors/entsoe/endpoints.py` says the registry duplicate was removed.
- `docs/entsoe_endpoint_catalog.yaml` keeps the catalog pointer with the duplicate/deferred rationale.

Frontend implication: show this as a duplicate/deprecated pointer to `commercial_schedules`, not as an active ingestable dataset.

### GIE `storage` and `lng`

These are not real gaps.

- `gie_agsi/storage` is configured and has a silver transformer, but it is an alias over the `/api` storage endpoint family rather than a separate key in `GIE ENDPOINTS`.
- `gie_alsi/lng` is configured under the ALSI source and has a silver transformer. The shared GIE connector switches behavior by source name.

Frontend implication: keep `gie_agsi/storage`, `gie_agsi/storage_reports`, and `gie_alsi/lng` as distinct dataset notes, but do not treat the GIE connector endpoint count alone as the source of truth.

## Findings

1. The upstream GitHub vault is already largely cross-referenced to the actual GridFlow pipeline. By dataset key, the only non-1:1 cases are the two ENTSO-E statuses already recorded in the upstream validation output.
2. The local `gridflow-front-end/vault` snapshot is the real gap for the frontend today. It has only 63 dataset notes, while upstream `quant-vault` has 162.
3. GridFlow source config contains 160 active connector datasets. The upstream vault's 160 `active_connector_dataset` entries match that active configured surface.
4. GridFlow silver contains 161 registered transformers because it also retains `entsoe/activated_balancing_qty` as silver-only support.
5. The 162nd upstream vault entry is `entsoe/commercial_schedules_net_positions`, an intentional duplicate/deprecated pointer rather than a pipeline dataset.

## Recommended Next Step

For GridFlow frontend expansion, the next content task is not additional upstream vault invention. It is revendor/reconcile:

1. Pull the upstream `quant-vault/30-vendors/*/datasets/*.md` content into the frontend's `vault/<vendor>/` snapshot layout.
2. Preserve dataset statuses from `machine-catalog.json` so the frontend can distinguish:
   - active connector datasets
   - silver-only datasets
   - deprecated/duplicate pointer datasets
3. Update GridFlow frontend catalog generation to cover all six vendors, not just the currently vendored Elexon/ENTSO-E/ENTSO-G subset.
4. Treat `gridflow` Pydantic schemas and live pipeline registries as canonical where vault text disagrees, consistent with the upstream vault README.

No files under `vault/` were changed during this research pass.
