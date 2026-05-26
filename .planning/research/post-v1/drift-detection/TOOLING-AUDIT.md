# Tooling audit: drift detection across gridflow / vault / front-end

Status as of 2026-05-18. The gridflow ecosystem already contains real drift-detection tooling — three layers of it, plus a handful of contract tests — and the v2 milestone is mostly about wiring what exists into CI and filling the seams between layers, not building from scratch. This file audits the load-bearing script (`verify_curl_and_silver_schema.py`), inventories the other drift-adjacent tools, and produces the gap table that the v2 build scope hangs off.

## 1. `verify_curl_and_silver_schema.py` deep audit

### Header and setup (L1-35)

The script lives at `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\30-vendors\scripts\verify_curl_and_silver_schema.py`. It is stdlib-plus-PyYAML, with one heavy import — it reaches into the gridflow repo at runtime via `sys.path.insert(0, str(GRIDFLOW / "src"))` (`verify_curl_and_silver_schema.py:31`) and imports the connector registry (`gridflow.cli._import_transformers`, L33) and silver registry (`gridflow.silver.registry._REGISTRY`, L34). This means the script is not portable: it requires both repos checked out on the same machine, both importable, and gridflow's full dependency tree installed (Pydantic, Polars, etc).

The two location anchors are environment-driven but fall back to hardcoded Windows paths (`verify_curl_and_silver_schema.py:20-26`):

```
VAULT = Path(os.environ.get("VENDOR_VAULT_DIR", Path(__file__).resolve().parents[1]))
GRIDFLOW = Path(
    os.environ.get(
        "GRIDFLOW_REPO",
        r"C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow",
    )
)
```

The Windows fallback is fine for the author's laptop but breaks immediately on a Linux GitHub Actions runner. The `VENDOR_VAULT_DIR`/`GRIDFLOW_REPO` env-var shape is reusable in CI as long as both repos are checked out into known paths during the workflow.

Report destinations are also hardcoded into VAULT, not into a CI artefacts directory (`verify_curl_and_silver_schema.py:27-28`):

```
REPORT_JSON = VAULT / "vault-curl-schema-validation.json"
REPORT_MD = VAULT / "vault-curl-schema-validation.md"
```

In a CI run we want these published as workflow artefacts AND emitted as GitHub Actions annotations on the offending vault lines; today they sit on disk inside the vault.

`load_env_file()` (`verify_curl_and_silver_schema.py:63-75`) reads `gridflow/.env` if present and never prints values; that pattern is safe for CI as long as the same secrets are mapped into the workflow as repo secrets.

### Constants

The auth-placeholder map is short and explicit (`verify_curl_and_silver_schema.py:37-40`):

```
AUTH_PLACEHOLDERS = {
    "<your-entsoe-api-key>": "ENTSOE_API_KEY",
    "<KEY>": "GIE_API_KEY",
}
```

Two vendors today: ENTSO-E and GIE. Elexon, NESO, ENTSO-G, Open-Meteo are public. For CI, the placeholder map needs a corresponding workflow `env:` block mapping repo secrets to these names.

`SOURCE_SLEEP_SECONDS` (`verify_curl_and_silver_schema.py:42-52`) carries per-vendor rate-limit-respecting pauses (Elexon 0.5s, ENTSO-E 1.0s, GIE 1.05s, NESO 0.05s). These set the lower bound on total CI runtime: ~150 vault curl examples × average ~0.5s pause + ~1-3s per request = ~5-10 minutes minimum if run on every PR. v2 needs a scheduled-run model, not a per-PR run.

`RUNTIME_COLUMNS` is the load-bearing cheat (`verify_curl_and_silver_schema.py:54-60`):

```
RUNTIME_COLUMNS = {
    "available_at",
    "dataset_version",
    "event_time",
    "ingested_at",
    "source_run_id",
}
```

These are columns the BaseSilverTransformer adds after the Pydantic schema validates — bitemporal/provenance metadata. The verifier excludes them from the `extra_in_docs` set comparison on `verify_curl_and_silver_schema.py:505` (`result["extra_in_docs"] = sorted(doc_names - comparable_code)` where `comparable_code = code_names | RUNTIME_COLUMNS`). Without this exclusion every vault page that documents `ingested_at` would show up as `extra_in_docs`. v2 must preserve this constant; it's the reason the existing 56 schema checks pass.

### Curl-extraction pipeline

`markdown_files()` (L86-87) walks every `.md` under VAULT, skipping `.obsidian`. `extract_curl_blocks()` (L98-129) scans fenced code blocks; if the block contains the literal `curl`, `split_curl_commands()` (L132-146) splits multi-curl blocks on `^curl(\.exe)?` line starts.

`replace_auth_placeholders()` (L158-173) does two layered things: detects "this endpoint needs entsoe key but env var unset" and emits `skipped_auth`; otherwise string-replaces the placeholder in the curl command.

`curl_args()` (L176-194) shlex-splits the command, forces `args[0] = "curl.exe"` (L180 — Windows binary name, will break on Linux runners), and strips any `-o`/`--output` argument so the script can supply its own tempfile body destination.

`run_curl()` (L304-391) executes the curl with a 90-second `--max-time` and 100-second outer subprocess timeout (L334, L352), captures HTTP status via the `-w "__HTTP_STATUS__:%{http_code}"` trick (L342-343, parsed L367-369), classifies into `passed`/`failed_auth` (HTTP 401/403, L372)/`failed`/`timeout`/`parse_error`, and conditionally builds a response profile for ENTSO-E and GIE responses (L378-383) to surface vendor-message HTTP-200 responses (i.e. the API returns 200 with an XML `Acknowledgement` saying "no data for window" or "rate limit exceeded").

`response_profile()` (L215-301) is the most semantically interesting check: it parses the response body, classifies as JSON/XML/zip/gzip/text, and surfaces "vendor_message" status when XML has an `<Acknowledgement_MarketDocument>` root tag or `<text>` reason elements. This is precisely the kind of body-shape check the verifier does NOT extend to Elexon (which is the v1 site's only at-depth vendor).

### Schema-extraction pipeline

`dataset_files()` (L90-95) globs `<vault>/*/datasets/*.md`. `extract_silver_section()` (L394-396) splits the markdown on the `## Silver layer` heading and returns the body up to the next H2.

`parse_schema_ref()` (L399-407) looks for `**Pydantic schema**: <something>` in the Silver section, recognizes "no dedicated schema" / "none" / "n/a" as the manual-transformer signal, and extracts the `gridflow.foo.bar` symbol path. If a vault note declares `**Pydantic schema**: manual_transformer` or omits the line, the dataset is classified as `manual_transformer_schema` later.

`parse_silver_schema_table()` (L410-433) finds a `### Silver schema` H3 inside the Silver section and parses its pipe-table rows into `{field, python_type, nullable, raw_cells}` dicts. Critically: only the first three columns are used; column 2 (`python_type`) is read but never compared — that is one of the verifier's loudest blind spots (see § "What it does NOT validate").

`import_symbol()` (L436-439) does `importlib.import_module()` + `getattr()`. `annotation_allows_none()` (L442-446) recursively checks `typing.get_args()` for `type(None)` — handles `int | None`, `Optional[int]`, `Union[int, None]`.

`model_fields()` (L449-458) iterates `cls.model_fields` (Pydantic v2 API), producing `{name: {annotation: str(annotation), nullable: bool, required: bool}}`. This uses Pydantic's `.model_fields` introspection — a different API surface from `.model_json_schema()`, which is also available and which v2 should additionally use (see § 5).

`schema_check()` (L461-522) orchestrates the comparison. The output statuses it emits, in priority order:

- `no_silver_section` (L482) — vault page has no `## Silver layer` H2 at all
- `no_silver_schema_table` (L485) — Silver section present but no `### Silver schema` table
- `manual_transformer_schema` (L488) — Silver section + table present but no importable Pydantic ref
- `schema_import_error` (L495) — Pydantic ref present but `import_symbol()` raised
- `failed` (L519) — one or more of `missing_in_docs`, `extra_in_docs`, `nullable_mismatches` non-empty
- `passed` (L521) — all three sets clean

A `failed` row carries three sub-payloads on the result dict: `missing_in_docs` (code field set minus doc field set), `extra_in_docs` (doc minus `code | RUNTIME_COLUMNS`), and `nullable_mismatches` (per-field `{docs_nullable, code_nullable, code_annotation}`).

### Outputs

`write_markdown()` (L543-595) renders the human report and `main()` (L598-632) writes both `vault-curl-schema-validation.json` and `vault-curl-schema-validation.md` into VAULT. The JSON is rich: it contains the full `curl_examples` list and `silver_schema_checks` list with every dimension. The Markdown is the executive summary plus failure list.

### External dependencies summary

- `curl.exe` binary (L180 — Windows-specific name, blocker for Linux CI)
- `yaml` (PyYAML, runtime)
- `pydantic` (transitive via gridflow imports)
- `gridflow.cli._import_transformers` (L33 — triggers all silver transformer registration so `model_fields()` calls work)
- `gridflow.silver.registry._REGISTRY` (L34 — used implicitly; the import triggers registration)
- `gridflow/.env` (optional, L29) for `ENTSOE_API_KEY` and `GIE_API_KEY`

### What it validates

1. Every vault `.md` containing fenced curl examples — does the curl return HTTP 2xx with the live API key?
2. For ENTSO-E/GIE specifically — does the HTTP-200 body look like data (JSON with `data` key, XML with non-Acknowledgement root) rather than a vendor-message wrapper?
3. For every `<vendor>/datasets/<dataset>.md` — does the `### Silver schema` field set ⊇ the Pydantic class's `model_fields`?
4. — and ⊆ `model_fields ∪ RUNTIME_COLUMNS`?
5. — and does the doc-table `nullable` flag column match the Pydantic annotation's `Optional`/`| None` status?
6. — and is the named Pydantic class actually importable?

### What it does NOT validate — the v2 gap list

- **Site HTML not inspected.** The script never reads `site/hifi/data-sources/elexon/*.html` or any front-end output. The vault → site rendering layer is invisible to it.
- **`elexon.json` manifest not inspected.** The front-end manifest `site/hifi/data/elexon.json` (the "33 everywhere" load-bearing count) is never compared against connector `ENDPOINTS` or vault inventory.
- **Frontmatter `last_verified:` freshness not checked.** Five vault pages carry this YAML key (sampled: `agws.md`, `imbalngc.md`, `windfor.md`, `tsdfd.md`, `tsdf.md`); the verifier reads frontmatter but never asserts `today - last_verified < N days`.
- **Field type mismatches not detected.** The verifier reads `python_type` column 2 of the vault table at `verify_curl_and_silver_schema.py:428` but never compares it to `model_fields[field]["annotation"]`. A vault page documenting `settlement_period: str` against code `int` reports `passed`.
- **`Pydantic schema:` reference can lie.** The check only validates that the named class imports. If `gridflow/schemas/elexon.py · ElexonFuelHH` is documented but the silver transformer actually uses `ElexonGenerationByFuel`, that goes unflagged.
- **`EXCLUDED_ENDPOINTS` not cross-checked.** `gridflow/src/gridflow/connectors/elexon/endpoints.py:43-52` lists `bod`, `generation_by_fuel`, `indicative_imbalance_volumes` as intentionally absent — the verifier would happily process a vault page for any of these.
- **`ParamStyle` consistency not checked.** The vault Query parameter table is not compared against the connector's `ParamStyle.PUBLISH_DATETIME` vs `SETTLEMENT_DATE` vs `DATE_PATH` declaration.
- **Live API body shape not compared to vault Bronze sample JSON.** The HTTP-200 body is only profiled (JSON vs XML, record count); not diffed against the Bronze section sample JSON in the vault page.
- **Renamed endpoints invisible.** `gridflow/src/gridflow/connectors/elexon/endpoints.py:67-73` shows `boal` now points at `/datasets/BOALF` because Elexon renamed it. The verifier just sees the new URL pass HTTP 200; if the vault note says `/datasets/BOAL` in its description, no flag is raised.
- **gridflow path references in vault Links section not checked.** A vault note can claim `[Transformer](gridflow/src/gridflow/silver/elexon/foo.py)` and the file can have moved; no check.
- **Hardcoded Windows path.** `verify_curl_and_silver_schema.py:24` defaults `GRIDFLOW` to a literal `C:\Users\Bobbo\...` path. CI fix: env-var-first, drop the Windows fallback.
- **`curl.exe` binary name.** `verify_curl_and_silver_schema.py:180` hardcodes `args[0] = "curl.exe"`. On Linux this is `curl`. Trivial fix: parameterize.
- **Not invoked by any CI.** The script is run manually from the author's machine; report lands in the vault; no GitHub Action runs it.

### Coverage (latest report)

From `vault-curl-schema-validation.md:7-9`, generated 2026-05-16:

- Curl examples: `passed: 122, failed_auth: 33, failed: 7` across all vendors (162 total)
- Authenticated bronze response checks (ENTSO-E + GIE only): `ok: 18, http_failed: 35`
- Silver schema checks: `passed: 56, failed: 33, manual_transformer_schema: 58, no_silver_schema_table: 14, no_silver_section: 1` (162 total)

Restricted to the 33 active Elexon datasets that are the v1 site's at-depth scope: roughly **7 fail with concrete diffs** (e.g. `boal` missing `bid_offer_acceptance_number`, `fuelhh` missing `published_at`, `ndf`/`ndfd`/`windfor` extra `issue_time` plus nullable mismatches, `system_prices` nullable mismatches on `price_derivation_code`/`run_type`, `bmunits_reference` nullable mismatch on `fuel_type`); **~22 are `manual_transformer_schema`** (vault page declares no Pydantic ref — these include all the manual/dynamic transformer datasets like `agpt`, `atl`, `fuelinst`, `inddem`, `indgen`, `lolpdrm`, `market_depth`, `netbsad`, `nonbm`, `remit`, `soso`, `temp`, `tsdf`, `tsdfd`, `uou2t14d`); the rest pass.

### Invocation

Run manually from the gridflow venv with `python C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\30-vendors\scripts\verify_curl_and_silver_schema.py`. Env vars sourced from `gridflow/.env` automatically. No schedule, no CI hook.

## 2. Other in-tree drift-adjacent tooling

### `quant-vault/30-vendors/scripts/derive_machine_catalog.py`

A second vault script of similar weight (~765 lines). It generates `machine-catalog.json` + `machine-catalog.validation.json` + `machine-catalog.schema.json`. Performs additional drift checks the curl-and-schema verifier doesn't:

- `missing_vault_notes` (`derive_machine_catalog.py:606-607`) — vault `.md` files expected by gridflow config but absent
- `extra_vault_notes` (`derive_machine_catalog.py:653-705`) — vault `.md` files for datasets not in active connector inventory; status-coded as `silver_only_not_in_connector_config` / `deprecated_or_duplicate_pointer` / `editorial_only`
- `path_warnings` via `path_issues()` (`derive_machine_catalog.py:524-534`) — vault `**Path:**` value compared against connector `endpoint.path` and `endpoint.path_template` after normalisation (`comparable_path()`, L264-270, which strips `?from=..` query strings and normalises `{from_dt}` → `{from}`)
- `frontmatter_mismatches` (`derive_machine_catalog.py:622-625`) — vault frontmatter `dataset_key` not matching its filename/folder
- `placeholder_counts_by_source` — counts editorial `TODO`/`TBD`/`unverified`/`placeholder` markers in vault `.md` text (regex at `derive_machine_catalog.py:88-91`)

Like the verifier: writes JSON into VAULT, not consumed by CI. The `path_warnings` mechanism is the structural drift detector the verifier lacks.

### `gridflow/tests/unit/test_elexon_endpoints.py::TestElexonInventoryContract` (L59-108)

This is the contract test that DOES run in gridflow's CI (`gridflow/.github/workflows/ci.yml:29` runs `pytest tests/ -v --tb=short -x -m "not live"`). It enforces:

- `test_configured_datasets_have_endpoint_definitions` (L60-65) — `sources.yaml` ⊆ `ENDPOINTS`
- `test_endpoint_registry_matches_configured_active_datasets` (L67-72) — `ENDPOINTS` ⊆ `sources.yaml`
- `test_configured_paths_match_endpoint_registry` (L74-83) — per-dataset `config.endpoint` path equals `ENDPOINTS[name].path`
- `test_configured_datasets_have_silver_transformers` (L85-91) — every configured Elexon dataset has a registered silver transformer
- `test_endpoint_param_styles_are_known` (L93-100) — every `ENDPOINTS[name].param_style` is a real `ParamStyle` enum member
- `test_intentional_exclusions_are_documented` (L102-107) — `bod`/`generation_by_fuel`/`indicative_imbalance_volumes` are in `EXCLUDED_ENDPOINTS` with reason text and absent from `ENDPOINTS`

Mirror test at `tests/endpoints/test_endpoint_urls.py::TestElexonEndpointDefinitions::test_active_datasets_match_configured_inventory` (L42-48) re-enforces the same equality. Together they cover connector ↔ config drift completely for gridflow's own surface. They do NOT cover front-end manifest (`elexon.json`) or vault inventory.

### `gridflow/tests/contracts/test_bronze_silver_contract.py`

Live contract test (L18-86): writes synthetic bronze data, runs the silver transformer, validates every silver row against the Pydantic schema (`ElexonSystemPrice(**row)` at L46-49), and asserts column set ⊇ required schema columns (L83-86). Runs in CI on every push/PR per `gridflow/.github/workflows/ci.yml`.

### `gridflow/tests/integration/test_canonical_schema_alignment.py`

A third schema-contract layer (L114-147): parametrised over every `list_transformers()` pair, runs the transformer against synthetic bronze, and asserts the emitted column set matches `docs/CANONICAL_SCHEMA.yaml`'s `bitemporal_columns ∪ business_columns ∪ metadata_columns` for that dataset. Currently 155/161 entries are `TODO_HUMAN_FILL_COLUMNS: true` and skip; 6 Open-Meteo entries are wired (per the module-level docstring at L1-13). This is a separate contract surface (silver-output ↔ YAML spec) that the verifier knows nothing about.

### `gridflow/scripts/elexon_audit.py`

Live end-to-end audit harness (179 lines). For each registered Elexon endpoint: fetches a real one-hour window from yesterday, writes to bronze, runs the silver transformer, records `n_silver_rows` and `sample_columns`. Output: `scripts/elexon_audit_results.json`. Not in CI; run manually. This is the closest existing thing to a "the live API has not silently changed shape" check at the gridflow side.

### Other gridflow tests of interest

`tests/unit/test_schemas.py` covers per-class Pydantic schema validation (positive and negative cases — invalid run_type rejected, naive timestamps rejected). `tests/integration/test_elexon_mocked_e2e.py` and `tests/integration/test_elexon_live_e2e.py` exercise the connector against recorded and live data respectively. None of them cross the boundary into vault or front-end.

### Front-end repo

`gridflow-front-end/tests/` is empty. `gridflow-front-end/src/gridflow_front_end/build.py` is the v1 Jinja2 build script — it reads vault `.md`, renders templates, and supports `--check` for idempotence (`build.py:24` docstring). The idempotence check is wired into CI at `gridflow-front-end/.github/workflows/deploy.yml:38-39`. That is structural-output stability, not content-drift detection.

### Front-end CI baseline

`gridflow-front-end/.github/workflows/deploy.yml` already runs three checks before `upload-pages-artifact@v3`:

- L42-44: `htmlhint --config .htmlhintrc 'site/hifi/**/*.html'` (CI-01)
- L47-55: `lycheeverse/lychee-action@v2` with `--offline --include-fragments` over the built site (CI-02)
- L38-39: `gridflow-build --check` idempotence test (CI-03)

These catch HTML breakage, dead internal links, and build instability — but none of them check content fidelity against gridflow code or the vault. The drift-detection v2 milestone extends this pipeline; it does not replace it.

## 3. Gap analysis

This is the table the v2 build scope hangs off. Each row is a drift edge from File 1 (DRIFT-SURFACES.md, sibling document running in parallel). The "tool that catches it today" column is grounded in the audit above; "tool that's missing" is the v2 build target.

| Drift edge | Tool that catches it today | Tool that's missing |
|---|---|---|
| Pydantic `model_fields` set ↔ vault `### Silver schema` table field set | `verify_curl_and_silver_schema.py::schema_check` L461-522 (latest: 56 pass, 33 fail across all vendors; ~7 of 33 Elexon datasets fail with concrete `missing_in_docs`/`extra_in_docs` diffs) | Site `<table class="schema">` rendered HTML vs vault `### Silver schema` post-build — never checked |
| Vault schema `Nullable` column ↔ Pydantic `Optional`/`\| None` annotation | `verify_curl_and_silver_schema.py::schema_check` L506-517 (`nullable_mismatches`) | Type mismatch (e.g. vault `python_type: str` vs code `date`); Enum subclass extension; `Field(pattern=...)` regex change |
| Vault curl example ↔ live API HTTP 200 | `verify_curl_and_silver_schema.py::run_curl` L304-391 (latest: 122 pass, 33 failed_auth, 7 failed across all vendors) | Body shape match against vault Bronze sample JSON; renamed-endpoint detection (BOAL→BOALF) |
| Live API ENTSO-E/GIE body NOT a vendor-message wrapper | `verify_curl_and_silver_schema.py::response_profile` L215-301 (latest: 18 ok, 35 http_failed for authenticated checks) | Same check extended to Elexon (the v1 site's at-depth vendor) |
| Connector `ENDPOINTS` ↔ `config/sources.yaml` configured datasets (gridflow internal) | `gridflow/tests/unit/test_elexon_endpoints.py::TestElexonInventoryContract` L59-91 — runs in CI on every push to gridflow repo | Nothing missing on this edge |
| Connector `ENDPOINTS` ↔ vault `<vendor>/datasets/*.md` inventory | `derive_machine_catalog.py::missing_vault_notes`/`extra_vault_notes` L606-705 — detects but no CI consumes the report | Same check wired into CI as a fail-the-build assertion |
| `gridflow-front-end/site/hifi/data/elexon.json` manifest ↔ connector `ENDPOINTS` ↔ vault count | Nothing checks the front-end manifest. The v1 milestone relied on hand-typing 33 everywhere (per `REQUIREMENTS.md` ELX-05 and PROJECT.md "33 everywhere"). | Front-end manifest count + key set parity check against connector + vault, executed by `gridflow-build --check` or new CI step |
| Vault `**Pydantic schema**:` reference string ↔ importable class | `verify_curl_and_silver_schema.py::schema_check` L492-497 (`schema_import_error`) | Deeper: does the *transformer* actually use the named class? (verifier only checks the name imports) |
| Connector `ParamStyle` ↔ vault Query parameter table rows | Nothing — vault Query table is parsed by `derive_machine_catalog.py::parse_table` L151-167 but not cross-checked against `ENDPOINTS[name].param_style` | Per-vendor parameter parity check |
| Vault Bronze sample JSON ↔ live API response shape | Nothing — verifier reaches HTTP 200 and stops (or runs `response_profile` for non-Elexon vendors) | JSON Schema fingerprint of live response vs vault Bronze sample, with stable-diff (ignore order, ignore values) |
| Vault `**Path:**` row ↔ connector `endpoint.path` / `endpoint.path_template` | `derive_machine_catalog.py::path_issues` L524-534 emits `vault_api_path_differs_from_executable_catalog` — generated into `machine-catalog.validation.json`, never asserted in CI | Same check wired as a fail-the-build assertion |
| Vault `EXCLUDED_ENDPOINTS` (deprecated/duplicate) ↔ no vault page exists | `gridflow/tests/unit/test_elexon_endpoints.py::test_intentional_exclusions_are_documented` L102-107 — gridflow CI; `derive_machine_catalog.py::extra_vault_notes` flags status `deprecated_or_duplicate_pointer` L653-672 | Cross-repo assert: vault `.md` for `bod`/`generation_by_fuel`/`indicative_imbalance_volumes` should not be in `30-vendors/elexon/datasets/` |
| Site `verified-against-vendor-docs: YYYY-MM-DD` micro-line ↔ today minus N days | Nothing — REQ ELX-07 ships the micro-line; nothing checks freshness | Build-time staleness check |
| Vault frontmatter `last_verified:` ↔ today minus N days | Nothing — present on 5+ vault pages (sampled `agws.md`, `imbalngc.md`, `windfor.md`, `tsdf.md`, `tsdfd.md`) | Same staleness check across vault |
| Vault `Links` section gridflow paths ↔ files exist in gridflow repo | Nothing | Path-exists check across vault Links sections |
| Site HTML rendered from vault matches vault content after a vault edit | `gridflow-build --check` idempotence (`deploy.yml:38-39`) catches build-vs-build instability, not vault-vs-current-vault | Vault → site → assertion (e.g., every `<table class="schema">` row maps back to a vault `### Silver schema` row) |
| Silver transformer column output ↔ Pydantic schema | `gridflow/tests/contracts/test_bronze_silver_contract.py` L18-86 — runs in CI | Nothing missing on this edge for Elexon `system_prices`; coverage thin for other Elexon datasets |
| Silver transformer column output ↔ `docs/CANONICAL_SCHEMA.yaml` | `gridflow/tests/integration/test_canonical_schema_alignment.py` L114-147 — runs in CI; 155/161 entries currently `TODO_HUMAN_FILL_COLUMNS` so they skip | Curating the remaining 155 YAML entries is its own piece of work (gridflow-side) |
| `verify_curl_and_silver_schema.py` report consumed by CI | Nothing — report writes into VAULT, no workflow reads it | Workflow that runs the verifier on schedule + on PRs touching vault/, asserts zero new failures, posts annotations |
| `derive_machine_catalog.py` validation report consumed by CI | Nothing — `machine-catalog.validation.json` writes into VAULT, no workflow reads it | Same: workflow that asserts zero new path_warnings / missing_vault_notes / frontmatter_mismatches |

## 4. Reusable pieces

Order of decreasing portability — what can be lifted as-is, what needs light parameterisation, what should be rewritten.

**Lift as-is, wrap in a thin CLI / pytest harness:**

- `parse_silver_schema_table()` (`verify_curl_and_silver_schema.py:410-433`) — pure markdown→list parser, no side effects. Suitable as a vendor-agnostic helper in a new `gridflow_drift` package or kept in the vault.
- `model_fields()` + `annotation_allows_none()` (L442-458) — pure Pydantic-v2 introspection.
- `parse_schema_ref()` (L399-407) — pure regex.
- `extract_silver_section()` (L394-396), `extract_curl_blocks()` (L98-129), `split_curl_commands()` (L132-146) — pure markdown parsing.
- `RUNTIME_COLUMNS` set (L54-60) — load-bearing constant for any field-set diff against silver code.
- `AUTH_PLACEHOLDERS` (L37-40) — small map; CI workflow maps secrets to the same env-var names.
- `response_profile()` (L215-301) — extend to Elexon (currently restricted to ENTSO-E/GIE at L378).

**Lift with parameterisation:**

- `curl_args()` (L176-194) — change `args[0] = "curl.exe"` (L180) to `args[0] = os.environ.get("CURL_BIN", "curl")`. Drop in cross-platform.
- `run_curl()` (L304-391) — keep the logic, add an `extra_headers` parameter so CI can inject a `User-Agent: gridflow-ci`. Keep the 90/100s timeouts.
- `replace_auth_placeholders()` (L158-173) — keep; ensure the workflow `env:` block maps `ENTSOE_API_KEY` and `GIE_API_KEY` from GitHub repo secrets.
- Output writers (`write_markdown`, L543-595; JSON dump in `main`, L628) — wrap to ALSO emit GitHub Actions `::error file=...,line=...::` annotation format alongside, so failures surface as PR-line annotations not just artefacts.

**Rewrite:**

- Hardcoded `VAULT`/`GRIDFLOW` paths with Windows fallback (L20-26) — replace with env-var-first / CLI-flag-fallback (mirror `gridflow-build`'s pattern at `gridflow-front-end/src/gridflow_front_end/build.py:24`: CLI `--vault-path` → `GRIDFLOW_VAULT_PATH` env var → vendored fallback). Drop the `C:\Users\...` literal.
- Report destination (L27-28) — emit to `<cwd>/_drift-report/` by default, configurable. Vault is content; reports are build artefacts.
- `sys.path.insert(0, str(GRIDFLOW / "src"))` (L31) — replace with installing the gridflow package into the CI venv (or rely on `pip install -e <path-to-gridflow>`).

## 5. Schema introspection beyond `.model_fields`

The verifier uses Pydantic v2's `.model_fields` (L452). That API gives field-level info: annotation, default, required. It is good for the field-set comparison the verifier does.

Pydantic v2 also exposes `.model_json_schema()`, which produces a JSON Schema Draft 2020-12 document for the model. This is a different, complementary artefact:

- Field-set comparison via `.model_fields` produces a human-readable "added field X, dropped field Y, nullable mismatch on Z" report — what the verifier emits today.
- `.model_json_schema()` produces a structural fingerprint — types, constraints (`Field(ge=1, le=50)` becomes `{"minimum": 1, "maximum": 50}`), enums (`SettlementRunType.II..DF` becomes a JSON Schema `"enum": ["II","SF","R1",...]` per `gridflow/src/gridflow/schemas/elexon.py:13-21`), and `$defs` for nested models. It is stable, diffable, and version-controllable.

The v2 recommendation is **keep both**:

1. **`.model_fields` introspection** for the human-readable "this is what changed in the Pydantic class since the vault page was last updated" report. This is what `verify_curl_and_silver_schema.py` already does.
2. **`.model_json_schema()` snapshots** for structural-drift detection over time. Export each Pydantic class's JSON Schema to `gridflow/schemas/snapshots/<class_name>.json`, commit them, and diff in CI. Tools like `json-schema-diff` consume these directly; deeper industry tooling coverage (`oasdiff`, contract-test frameworks, Pact-style consumer-driven contracts) is Agent C's scope. The integration point for v2 is: emit the snapshot at build time, diff against the committed version, fail the build on unexplained changes, surface explained changes as PRs.

The snapshot also serves a second purpose: it can be embedded in the rendered site page as a downloadable JSON-Schema fragment for any recruiter or contributor who wants to consume the contract programmatically — a stronger credibility signal than a hand-typed Markdown table.

## Open questions for the milestone planner

- Is the v2 milestone authorised to add the verifier as a new file in `gridflow-front-end/scripts/` (or `gridflow/scripts/`), or does it stay in the vault? The verifier reaches into both repos either way; the question is where the CI workflow file lives.
- Cross-repo checkout in CI: `actions/checkout@v4` only checks out the current repo by default. v2 needs `actions/checkout@v4` with `repository: EBentham/gridflow` and `path: ../gridflow` for the front-end workflow, plus equivalent for the vault. The vault repo's privacy status determines whether this needs a deploy key.
- Should the drift report fail the deploy, or block the PR but allow the deploy from `main`? Latter is gentler for v2 launch; former is the right end state.
