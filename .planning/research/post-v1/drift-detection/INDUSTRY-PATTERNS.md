# Industry patterns for drift detection

**Subject:** What open-source projects do about schema, API, and documentation drift, and which patterns transfer to the gridflow ecosystem.
**Researched:** 2026-05-18
**Confidence:** HIGH on tool capabilities (verified against current docs); MEDIUM on specific anti-pattern post-mortems (limited primary-source material exists publicly on this exact failure class).

## How to read this

The gridflow ecosystem has four drift surfaces (per the brief): Pydantic schema vs vault markdown · vendor API vs documented curl examples · vault markdown vs rendered HTML · cross-repo path references. The industry has spent ten years building tooling for the first three of those problems under different vocabularies (contract testing, schema diff, snapshot pinning, docs-as-code). This file curates the landscape and lands three concrete adoption recommendations for gridflow.

**Headline recommendations, before the detail:**

1. **Adopt `schemathesis` against Elexon's OpenAPI spec** as a scheduled GitHub Actions job. Elexon publishes machine-readable schemas; schemathesis generates property-based tests from them; a nightly run detects vendor drift before a recruiter spot-checks a 404 URL. (Section 2.)
2. **Adopt Patito (Pydantic + Polars) as the silver-layer schema gate** in gridflow. gridflow is Polars-only; Patito models *are* Pydantic models that double as Polars dataframe validators, so a single `gridflow.schemas.elexon.ElexonFuelHH` declaration serves both API-response validation and silver-dataframe validation. Pandera + `pandera.polars` is the close runner-up; its native Pydantic-v2 row-model engine is currently pandas-only, so adopting it for Polars validation today still leaves the Pydantic-schema-vs-vault drift surface unaddressed. (Section 3.)
3. **Adopt the "verified date + scheduled re-verify" pattern from Stripe and Read the Docs**: every dataset page carries a `verified: YYYY-MM-DD` micro-line; CI is a `cron` workflow that re-hits the documented curl example and opens an issue (not a PR, not a deploy block) when it 404s, drifts in shape, or is older than a configurable threshold. The point is asynchronous awareness, not synchronous gating. (Sections 4 and 5.)

Everything else in this document is in service of those three adoptions — either supporting evidence, alternatives that were considered and dismissed, or anti-patterns that argue *for* the shape of those recommendations.

---

## 1. Schema drift detection patterns

### Pydantic v2 schema export (the foundation)

Pydantic v2 models expose `model_json_schema()` returning a JSON Schema document; this is the entrypoint into the JSON-Schema-diff ecosystem. The shape is stable across `pydantic` 2.x minor versions but does change between majors. The official guidance is that the JSON Schema output is *the* serialised form of a Pydantic model and is intentionally diff-friendly[^pydantic-schema]. For gridflow this means: a `scripts/dump_schemas.py` that walks `gridflow.schemas.*`, calls `.model_json_schema()`, writes one JSON per dataset to a `schemas/` directory, and *commits the output*, is the first move. The commit history of that directory then *is* the schema-drift log.

**Fit verdict:** **Adopt as foundation.** This is the cheapest possible signal: a one-file PR that adds 33 JSON files; subsequent gridflow PRs that change a schema produce a diff in those files at review time.

### JSON Schema diff tooling

- **`json-schema-diff` (Python)** — generates structured diffs between two JSON Schema documents, distinguishes between "added field," "removed field," "type narrowed," "type widened"[^jsonschemadiff-py]. Useful for human-readable PR comments. **Fit: medium.** Output-formatting wrapper over the foundational pattern.
- **`json-schema-diff-validator` (npm)** — same idea, JavaScript ecosystem; mention only to note the pattern is cross-language; **fit: dismiss** (no node toolchain in this Python-first project).

The shape that matters here is not the specific tool: it is the *workflow*. Buf's `buf breaking` workflow (next subsection) is the most refined version of this and is worth stealing structurally even though gridflow doesn't use Protobuf.

### Buf and `buf breaking` (the workflow archetype)

Buf is a Protobuf toolchain whose `buf breaking` subcommand compares a Protobuf schema against a baseline and classifies every diff as `breaking`, `non-breaking`, or `unspecified` according to a configurable rules file[^buf-breaking]. The workflow is: PR opens → `buf breaking` runs against `main` → if breaking changes are introduced *without* an accompanying version bump, PR is blocked; if breaking with bump, allowed; if non-breaking, silent. This is the highest-quality reference implementation of "schema change is fine as long as you mean it." Crucially, the *rules file* is what makes this work — the project declares which kinds of changes are breaking for *their* consumers.

**Fit verdict:** **Steal the pattern, not the tool.** gridflow can replicate this with a 40-line Python script that diffs `model_json_schema()` output and applies its own rules ("removing a non-nullable field is breaking; adding an optional field is not; changing field type is breaking"). The rules file embodies the contract gridflow has with the vault's documentation. Reference [`buf.build/docs/breaking/rules`][^buf-rules] for what a mature rules vocabulary looks like.

### OpenAPI diff: `oasdiff` (the OpenAPI equivalent)

`oasdiff` is a Go binary that diffs two OpenAPI specs and outputs change classification (breaking / non-breaking / cosmetic), supports both YAML and JSON inputs, and integrates with GitHub Actions[^oasdiff]. The Elexon BMRS API is OpenAPI-described (verified — section 2 below), which means oasdiff *is directly applicable* if gridflow snapshots the upstream spec into the repo on a schedule and diffs the new snapshot against the committed version.

**Fit verdict:** **Adopt for vendor-API drift.** This is the right tool for one specific gridflow drift surface: detecting *Elexon's* changes to their own API spec. Schedule: `cron` workflow fetches `https://bmrs.elexon.co.uk/api-documentation/swagger.json` (or wherever the spec actually lives — verify URL during adoption), runs `oasdiff` against the committed copy, opens an issue if a breaking change is detected. Issue, not PR — see Pitfall section.

### Confluent Schema Registry compatibility modes (the vocabulary)

Confluent's Schema Registry, used for Avro/Protobuf message schemas in Kafka, defines four compatibility modes: `BACKWARD` (new schema can read old data), `FORWARD` (old schema can read new data), `FULL` (both), and `NONE` (no constraint)[^confluent-compat]. gridflow doesn't use Avro, but the *vocabulary* is the most precise way to discuss what kind of drift is OK between silver columns and the documented schema. A renamed field is `NONE`-compatible; an added nullable field is `FORWARD`-compatible; a removed nullable field is `BACKWARD`-compatible.

**Fit verdict:** **Adopt the vocabulary in the schema-drift rules file.** Even if the tooling is Python and hand-rolled, calling the rules `pydantic-backward`, `pydantic-forward` etc. anchors them in an industry-standard taxonomy that is precisely defined.

### `griffe` for Python API surface diffing

`griffe` is a Python library by the mkdocstrings author that parses a Python package's API (functions, classes, signatures, type hints, docstrings) into a typed AST and supports diffing two parses[^griffe]. Its sibling tool `griffe check` is purpose-built for "did my public API break between v1.0 and v1.1?" detection. For gridflow's cross-repo path drift problem (the vault says `gridflow.schemas.elexon.ElexonFuelHH`, gridflow renames the class) griffe is *directly applicable*: parse `gridflow/src/gridflow/schemas/` at HEAD, look up every path the vault references, fail if any path doesn't resolve.

**Fit verdict:** **Adopt for cross-repo path drift.** This is the cleanest available answer to "the vault references `gridflow.X.Y.Z` and gridflow renamed Y." Two adoption shapes: (a) the CLI `uvx griffe check --search src --format github gridflow` form, which emits GitHub-Actions annotation lines on failures and slots straight into a workflow YAML; (b) a `pytest`-runnable check that loops over vault references and uses `griffe.load_git()` to load gridflow at a pinned commit, then asserts each referenced symbol resolves. Use (a) for breaking-change scans inside the gridflow repo; (b) for cross-repo verification from gridflow-front-end and the vault.

### `mypy --strict` with stub diffing

`mypy` can emit `.pyi` stub files via `stubgen` and diff them mechanically. This is the lowest-tech approach to API-surface drift, used historically in projects like `typeshed`. **Fit verdict: dismiss.** `griffe` is strictly better for this exact use case, and gridflow already has `mypy --strict` enabled per user global preferences for its primary purpose (type checking).

---

## 2. Contract testing — Elexon's OpenAPI spec is the unlock

### Verification of the central premise

The Elexon BMRS API publishes an OpenAPI specification. The official documentation portal at `bmrs.elexon.co.uk/api-documentation`[^elexon-api-docs] is Swagger-UI-rendered, which is itself prima-facie evidence of an OpenAPI/Swagger spec backing it. The community `OSUKED/ElexonDataPortal` project[^osuked-portal] additionally derives and publishes a `BMRS_API.yaml` OpenAPI spec under the same project, and uses it for code generation and documentation. **This single fact reshapes the recommendation space**: every tool in this section that depends on a machine-readable API spec becomes applicable to gridflow's Elexon connector.

ENTSO-E, ENTSO-G, GIE, and Open-Meteo do *not* publish OpenAPI specs (ENTSO-E is XML/SOAP-derived REST; ENTSO-G and GIE publish human PDFs; Open-Meteo has Markdown docs only). For those vendors, schemathesis is unavailable; section 4 (snapshot testing) applies instead.

### `schemathesis` (the headline tool)

Schemathesis is a property-based testing tool built on Hypothesis that reads an OpenAPI or GraphQL schema, generates a wide variety of valid-but-edge-case requests, sends them against a running API, and asserts every response conforms to the schema[^schemathesis]. It catches three classes of bug at once: (a) the server returns a response shape the spec doesn't describe (the *spec* is wrong), (b) the server rejects inputs the spec says are valid (the *server* is wrong), and (c) the server's response on a previously-tested input has changed (drift).

For gridflow, the relevant mode is (c). A scheduled `schemathesis run https://elexon-openapi-url` workflow that targets the production Elexon BMRS API, with no auth (Elexon's read API is unauthenticated for most endpoints) and rate limits respected, gives a daily-or-weekly signal of "Elexon changed something." A failure is *not* a deploy blocker — it is a signal to investigate.

**Fit verdict:** **Adopt as a scheduled workflow against Elexon.** Stake one of the two highest recommendations in this entire document on this single tool. Note the failure mode: hammering Elexon's API from CI looks like an attack; respect their rate-limit headers and use Hypothesis' `--hypothesis-max-examples=50` setting to keep traffic minimal. Schemathesis ships built-in shrinking, so a failure produces a minimal repro request that can be pasted into a curl. (Section 7 covers the anti-pattern this avoids.)

### `Pact` (and consumer-driven contract testing in general)

Pact is the canonical consumer-driven contract testing framework: the consumer (gridflow) defines what it expects from the provider (Elexon); the contract is shared via a Pact Broker; the provider runs the contract against its own implementation[^pact]. **This is structurally wrong for the gridflow case.** Pact assumes gridflow can influence the provider's CI — Elexon will obviously not run a third-party contract test on every deploy. Pact works inside organisations; gridflow consumes external APIs.

**Fit verdict:** **Dismiss.** Mention only to clarify why it doesn't apply: Pact's consumer-driven model assumes provider cooperation.

### `dredd`

`dredd` is an older HTTP API testing tool that exercises example requests from an OpenAPI/API Blueprint spec and asserts responses match[^dredd]. It is functionally a less-aggressive Schemathesis (fixed examples, no property-based generation). Maintained but slow-moving.

**Fit verdict:** **Dismiss.** Schemathesis is strictly more powerful in the same niche.

### `VCR.py` and `pytest-recording` (the snapshot family)

VCR.py records HTTP interactions to YAML "cassette" files on first run and replays them on subsequent runs[^vcrpy]. `pytest-recording` is the pytest plugin wrapper[^pytest-recording]. The drift-detection workflow is: a test calls the vendor API behind `@pytest.mark.vcr`; on first run it records a cassette and commits it; subsequent runs replay the cassette instead of hitting the API; *a separate scheduled job* runs the same test with `--record-mode=rewrite` and produces a git diff if the recorded response has changed.

This pattern covers the four vendors that *don't* have OpenAPI specs (ENTSO-E, ENTSO-G, GIE, Open-Meteo) — for them schemathesis is unavailable, but cassette-based snapshot pinning is universally available.

**Fit verdict:** **Adopt for the non-OpenAPI vendors.** Reference Simon Willison's TIL[^simon-vcr] as the cleanest documented pattern for the rewrite-and-diff approach. Pair with the `--block-network` mode so unit tests cannot accidentally make live calls; cassettes are the source of truth in test runs.

| Tool | Applicability to gridflow | Verdict |
|------|---------------------------|---------|
| schemathesis | Elexon (OpenAPI available) | **Adopt** |
| VCR.py / pytest-recording | ENTSO-E, ENTSO-G, GIE, Open-Meteo, NESO | **Adopt** |
| oasdiff | Elexon spec-vs-snapshot drift | **Adopt** |
| Pact | Bilateral with provider | Dismiss |
| dredd | Subsumed by schemathesis | Dismiss |

---

## 3. Data quality and dataframe-shape drift — Polars-native is the constraint

The silver layer is Polars; whatever schema validation runs against it must be Polars-aware. This is a hard constraint: any tool that requires conversion to pandas is unacceptable per gridflow's stack rules (`pl.from_pandas` only at *external* boundaries, not internal validation).

### `pandera.polars` (the headline tool)

Pandera since 0.21.0 has first-class Polars support, exposing a `pandera.polars.DataFrameModel` that validates `polars.DataFrame` and `polars.LazyFrame` objects against a schema declaration[^pandera-polars]. As of 0.32, an opt-in Narwhals backend unifies the Polars/Ibis implementation paths[^pandera-narwhals]. One caveat to verify during adoption: Pandera's Pydantic v2 integration (`pandera.engines.pandas_engine.PydanticModel`) is currently pandas-only and row-wise[^pandera-pydantic]; a feature request for a Polars-engine equivalent is open[^pandera-issue-1874]. For gridflow this means Pandera + Polars and Pandera + Pydantic-as-row-model are two separate features today; the unified "one Pydantic schema validates both API response and silver dataframe" promise lands cleaner under Patito (next subsection) until that issue closes.

A practical Pandera + Polars use in a transform looks like:

```python
import pandera.polars as pa
from gridflow.schemas.elexon import ElexonFuelHH

class FuelHHSchema(pa.DataFrameModel):
    class Config:
        coerce = True

# Validation point inside the silver transform.
df = pl.read_parquet("bronze/elexon/fuelhh/...")
validated = FuelHHSchema.validate(df)
```

**Fit verdict:** **Adopt as the secondary silver-layer validator** alongside Patito (next subsection). Pandera is broader and more battle-tested for the *non-schema* checks (statistical assertions, custom check functions, regex validators) — adopt it for those, defer to Patito for the schema-as-Pydantic-model story.

### `patito` (the Polars-native alternative)

Patito (originally by Kolonial; primary development now at `JakobGM/patito`) is Pydantic-native by design — every Patito model *is* a Pydantic model that also validates Polars dataframes[^patito]. The integration is tighter than Pandera's: a Patito model declares column types using Pydantic field annotations directly, no separate `DataFrameModel` class. Patito also ships mock-data generation, which is useful for documentation site examples that need realistic-shaped fake data.

The choice between Pandera and Patito is real:
- **Pandera:** Mature, more contributors, supports multiple backend dataframe libraries, broader docs ecosystem, more validation primitives (regex string checks, statistical checks). Polars support is the newer addition.
- **Patito:** Polars-first by design, Pydantic-native by design, smaller library, less ecosystem mass, simpler to reason about, includes test-data generation. Better stylistic match for gridflow's "Pydantic + Polars" stack rules.

**Fit verdict:** **Adopt as the silver-layer schema gate** — this is the second of the three headline recommendations. Patito ships a single Pydantic-derived declaration that validates both API responses (Pydantic standard) and Polars dataframes (Patito extension), collapsing the most consequential drift surface in the ecosystem to one source. Pandera remains useful for non-schema assertions (regex checks, statistical bounds) — adopt both, but Patito carries the schema role. The Pointblank 2025 comparison of Polars validation libraries is the best single secondary source for this decision[^pointblank].

### `Great Expectations` (the heavyweight)

Great Expectations is the most prominent data-quality framework in the Python ecosystem. It supports declarative "expectation suites" attached to data assets, runs them in Spark/pandas/Polars contexts, and emits HTML "data docs" that look like reports[^great-expectations]. For gridflow it is overkill: a 33-dataset pipeline doesn't need expectation-suite YAML, doesn't need a GE store, doesn't need data docs (the site *is* the data docs). The HTML reports are also editorially the wrong aesthetic — they look like the SaaS-style dashboards `PROJECT.md` explicitly anti-goals.

**Fit verdict:** **Dismiss.** Right tool for an enterprise data lake; wrong tool for 33 datasets in a portfolio.

### `Soda Core` (the YAML-driven middleweight)

Soda Core defines data quality checks in YAML files, evaluated against any data source via SodaCL[^soda]. Lighter than GE, but still introduces a YAML config layer parallel to the existing Pydantic schemas — which is exactly the duplication Patito/Pandera *eliminate*.

**Fit verdict:** **Dismiss.** Patito eliminates the duplication; Soda Core re-introduces it under YAML.

### `dbt tests`

dbt's `dbt test` mechanism runs generic and custom tests on warehouse tables — not directly applicable to gridflow (no dbt, no Snowflake), but the **test-as-documentation pattern** is worth lifting. In dbt, a test that asserts `unique` on a primary key column doubles as the documentation that the column *is* the primary key. The vault page's `Primary key` declaration in the metadata grid is currently text-only; if the same fact is encoded as a Pandera/Patito constraint, the test ceases to be drift-prone — it's the same source.

**Fit verdict:** **Steal the test-as-documentation pattern, not the tool.** Make the Patito/Pandera schema the canonical statement of the primary key; the vault page renders it from the schema.

### `great_tables` and adjacent

`great_tables` is a table-rendering library; not drift-related. Skip.

---

## 4. Documentation drift detection

This is the surface gridflow's *front-end* repo cares about most: vault markdown drifts from vendor docs, and rendered HTML drifts from vault markdown.

### Doctest (the foundational Python pattern)

Python's stdlib `doctest` module runs `>>>` examples embedded in docstrings and asserts the output matches. `pytest --doctest-modules` extends this to a project-wide test run[^pytest-doctest]. This is the most foundational version of executable-documentation drift detection. For gridflow's Python code, doctests on the silver transform functions are cheap and currency-checking. For the vault's markdown content, doctest is wrong-shape (it expects Python `>>>` prompts, not curl).

**Fit verdict:** **Adopt for code-side examples, not for prose.** Use it for `gridflow/silver/*.py` examples; reach for `pytest-examples` (next subsection) for markdown.

### `pytest-examples` (the documentation-prose tool)

`pytest-examples` is a pytest plugin that extracts code blocks from markdown files (or docstrings) and executes them as tests, asserting outputs match[^pytest-examples]. Critically, it is used by **the Pydantic project itself** to ensure that every code example in the Pydantic docs continues to work as Pydantic evolves[^pydantic-pytest-examples]. This is the most directly transferable pattern in this document: gridflow's vault has Python code blocks (`pl.read_parquet(...)`, `ElexonFuelHH(...)`), and pytest-examples can ensure they continue to execute against the current `gridflow` version.

**Fit verdict:** **Adopt for vault Python code blocks.** A scheduled CI job that mounts the vault and runs `pytest-examples` against `*.md` files catches the cross-repo path drift (Pitfall 8 in `PITFALLS.md`) the moment a `gridflow.schemas.X` reference becomes stale. *Curl* examples are out of scope here — they need a different tool (next subsection).

### MkDocs include patterns: `mkdocs-include-markdown-plugin`, `mkdocs-snippets`

The MkDocs ecosystem has multiple include-fragment plugins[^mkdocs-include] that allow a documentation page to embed a code fragment from another file at build time. This is the closest pattern to gridflow's "vault page references Pydantic schema file" — except gridflow's render path is Jinja2, not MkDocs.

**Fit verdict:** **Steal the pattern for the Jinja2 build.** A Jinja2 template that renders `{{ pydantic_schema_source('elexon.ElexonFuelHH') }}` and resolves it to the actual current source code makes the schema example non-driftable by construction. The cost is a build-time Python import of the gridflow package, which gridflow-front-end already needs anyway for `gridflow-build` to read the schemas.

### Link checkers: `lychee`, `markdown-link-check`

`lychee` is a fast Rust-based link checker, already in the gridflow-front-end CI per the `CI-02` requirement[^lychee]. `markdown-link-check` is a Node-based equivalent[^mdlc]. Both detect HTTP 404 and other dead-link conditions. For *cross-repo path* drift, lychee is insufficient — a Python import path like `gridflow.schemas.elexon.ElexonFuelHH` is not a URL. For *vendor doc links* (e.g. each dataset page's "see Elexon docs at..."), lychee is exactly the right tool.

**Fit verdict:** **Extend the existing lychee CI to vault markdown.** Already adopted in the front-end; broaden to cover vault.

### Stale-doc detection patterns: the `verified-at` micro-line

Multiple high-quality documentation sites mark page freshness explicitly:

- **MDN Web Docs** stamps every reference page with a "Last modified" date pulled from git[^mdn-currency]. Some pages additionally carry a deprecated-feature banner with a specific browser-version cutoff.
- **`docs.rs`** auto-generates a "(Deprecated since X)" banner above any item annotated `#[deprecated]` in the source[^docsrs-deprecation], and shows version-pinned URLs in the path.
- **Stripe's API docs** carry a top-of-page version pinner (`API Version: 2024-04-10`) and a changelog page that lists every breaking change with its release date[^stripe-versioning].
- **FastAPI's docs** include tutorial code via `{* docs_src/.../tutorialNNN.py *}` markers[^fastapi-deps]; the same `docs_src/` files are imported by `tests/test_tutorial/`, so the executable test and the rendered prose share source-of-truth.

The pattern that transfers cleanest: **every dataset page carries a `verified: YYYY-MM-DD` micro-line + a `vendor-docs-url` field**. CI is a scheduled job (cron weekly) that walks the vault and for each page (a) re-fetches the vendor doc URL and asserts 200, (b) re-runs the curl example and asserts shape match against the Pydantic schema, (c) checks the `verified` date is within a configurable freshness threshold. **Failure opens a GitHub issue, not a PR.** The issue is the queue for the human verifier; the PR-noise anti-pattern in section 7 is what this asynchronous shape avoids.

**Fit verdict:** **Adopt as the third headline recommendation.** The whole apparatus is ~100 lines of Python + one GitHub Actions cron job + one issue-template file.

### `Vale` linter

Vale[^vale] is a prose linter used by many docs sites (GitLab, MongoDB, Linode) to catch style and terminology drift. It can be configured with a custom vocabulary file to fail on misspellings of vendor names (`Elexan`, `Entso-e`, etc).

**Fit verdict:** **Adopt as a lightweight CI step.** Cheap; catches the "Settlmenet Period" class of typo `PITFALLS.md § Recruiter-Bounce Signals #2` calls out.

### Tools to skip

- `vermin` (Python version drift) — not relevant to documentation drift.
- HTML linters (`htmlhint`) — covered in v1 CI; not drift detection.

---

## 5. CI patterns for cross-repo drift

### Multi-repo vs monorepo (the strategic decision)

gridflow's reality is three-repo: `gridflow` (the canonical Python ETL code), `quant-vault` (the authored markdown documentation), and `gridflow-front-end` (the rendered static site). Each evolves independently; each can drift from the others. The standard industry tradeoff is:

- **Monorepo** collapses the problem: schema, docs, and render live in one repo, atomic commits change them together, drift becomes structurally impossible. Counter-cost: monorepos at this team size (solo) read as overengineered, and the vault has separate justification as a personal knowledge base that includes content not destined for the public site.
- **Polyrepo** is what gridflow is; the drift problem is what this whole document responds to.

**Recommendation:** Stay polyrepo, accept drift as a first-class concern, build the tooling. Monorepo migration is a six-month project with no domain payoff — every recommendation in this file is cheaper.

### Scheduled jobs: `on: schedule:` and the cron-vs-PR tradeoff

GitHub Actions supports `on: schedule:` workflows triggered by cron[^gh-cron]. The relevant tradeoff for drift detection:

- **PR-time gating** (drift check runs on every PR, blocks merge if it fails) — high signal, but blocks deploys on third-party vendor uptime. If Elexon has a 503 during a PR check, the merge is blocked. **Anti-pattern**; see section 7.
- **Scheduled-only** (drift check runs nightly, opens issues, never blocks) — async signal, gives an inbox of drift cases without coupling deploy to vendor uptime. **The right shape** for any check that hits a third-party API.

The asymmetry: schema-of-pydantic-vs-vault drift is *internal* (both files live in repos the author controls) and can be PR-gated. Vendor-API drift is *external* and must be schedule-only. This is the single most important CI design decision in this entire space.

Real-world reference: Cloudflare's dev docs CI[^cloudflare-docs-ci] runs link checks on PR (blocking) and example-code checks on schedule (non-blocking) — the same asymmetry.

### Label-based gating: `actions/labeler` + branch protection

`actions/labeler`[^gh-labeler] reads a `.github/labeler.yml` rule file and applies labels to PRs based on changed paths. Combined with branch-protection rules that require certain labels (or absence of certain labels), this enables: "any PR that touches `gridflow/src/gridflow/schemas/**` gets the `requires-vault-update` label, which blocks merge until a sibling vault PR closes it."

**Fit verdict:** **Adopt across gridflow / vault.** This is the structural answer to "we changed a schema and forgot to update the vault page." Two PR queues, but they're explicitly linked.

### Cross-repo PR opening: `peter-evans/repository-dispatch` and `peter-evans/create-pull-request`

Two related actions from the same maintainer:
- `repository-dispatch`[^repo-dispatch] sends a custom event from one repo to another, triggering a workflow in the receiving repo. Authenticated via PAT or GitHub App token.
- `create-pull-request`[^create-pr] is the most-installed action for opening a PR from a workflow run.

Combined pattern: gridflow's CI on merge to main dispatches an event to `gridflow-front-end`; the front-end workflow opens a PR that bumps the pinned gridflow version, regenerates the build, and runs the drift checks. Failed checks become PR comments; the human reviews.

**Fit verdict:** **Adopt as the cross-repo notification spine.** Pair with the issue-not-PR pattern from section 4: vendor drift opens an issue, internal schema drift opens a PR.

### Authentication: PAT vs GitHub App

A PAT (personal access token) authenticated as the author works for solo projects but is fragile (PAT expiry, revocation, scope creep). A GitHub App with installation tokens is the more durable option but is more setup. For gridflow at solo scale, **PAT stored as an organisation secret with explicit expiry and a renewal calendar reminder** is the pragmatic call; revisit GitHub App if a contributor joins.

**Fit verdict:** **PAT for now; document the rotation date in the repo.**

### Canary deploys against vendor APIs

The "canary" pattern is well-documented in service-deploy contexts (Cloudflare, GitHub) but its data-pipeline equivalent is less standardised. The Cloudflare engineering blog has the most readable account[^cloudflare-canary]: a small percentage of traffic is routed to a new version; if error rates spike, traffic shifts back. The data-pipeline equivalent is: a small recent time window of vendor data is re-fetched and re-transformed via the *current* gridflow code; if the silver-layer assertions fail, the alert fires.

**Fit verdict:** **Adopt as a future-milestone canary**, not a v1 ask. The shape: a weekly workflow that pulls the most recent day of Elexon fuelhh data, runs it through gridflow's silver transform, asserts every silver-schema constraint via Patito. A failure is the earliest signal of "Elexon changed something gridflow's code doesn't handle."

---

## 6. Exemplar projects: what to steal, with citations

The brief lists ten candidate exemplars. After verification, the four that most resemble the gridflow case are:

### Pydantic itself

Pydantic's own documentation uses `pytest-examples` to ensure every code block in the docs continues to execute. The relevant test file is `tests/test_docs.py` in the pydantic repository[^pydantic-tests]. The workflow: every markdown file under `docs/` is discovered; every `python` fenced block is extracted; each is executed with a fresh interpreter; the rendered output is asserted against the markdown's expected-output annotation. This pattern is the cleanest available reference for keeping documentation prose synchronized with library code.

**What to steal:** The `pytest-examples` pattern, applied to the vault's Python blocks. (Section 4.) Cost: ~50 lines of conftest.py + ~3 minutes of CI per run.

### FastAPI

FastAPI uses a different but equally instructive pattern: every tutorial code example is a runnable Python file under `docs_src/` (e.g. `docs_src/additional_responses/tutorial001.py`); tests under `tests/test_tutorial/`[^fastapi-tests] import those files via the FastAPI `TestClient` and assert behaviour with `inline_snapshot`. The documentation prose under `docs/en/docs/` literally `{* docs_src/.../tutorialNNN.py *}`-includes the same files at build time. The runnable code is the single source; tests assert it runs; docs include it verbatim. **This is the cleanest "test-and-docs-share-source" pattern in the Python ecosystem.** FastAPI's CI also runs the matrix against multiple Python and Pydantic versions, catching version-drift between the runtime and the documented version.

**What to steal:** The `docs_src/`-separation pattern. Vault Python code blocks should be extracted into runnable `.py` files in a `vault/examples/<vendor>/<dataset>/` tree; the vault markdown then *includes* them at render time via the Jinja2 build script; the same files are imported by gridflow tests. The runnable Python is the single source; vault prose, test cases, and rendered HTML all derive from it. As a free secondary, lift FastAPI's Python-version matrix (3.11 + 3.12) to catch version-drift in the documented examples.

### dbt-core

dbt's `dbt test` framework treats schema documentation (`schema.yml`) as the canonical claim about a model's shape, and runs assertions against the actual warehouse table during `dbt test` runs[^dbt-tests]. The drift detection is implicit: if `schema.yml` claims a column is unique and it isn't, `dbt test` fails. This is the test-as-documentation pattern at its most refined.

**What to steal:** The principle that *the schema declaration is the test*. In gridflow's case, the Patito schema is both the validator and the documentation source — the vault page renders the schema from the Patito model rather than re-declaring it. (Section 3.)

### conda-forge autotick-bot (`regro/cf-scripts` + `regro-cf-autotick-bot`)

conda-forge's `cf-scripts` repository[^conda-cf-scripts] runs a scheduled `bot-update-feedstock-version` workflow that scans upstream PyPI/GitHub for new releases of every package conda-forge mirrors, and auto-opens PRs against the relevant feedstock repos when a new version is detected. This is a sophisticated drift-detection pattern in its own right (the *upstream package's* version drifts away from what the feedstock pins).

**What to steal:** The auto-PR-from-scheduled-job pattern, applied to gridflow's Elexon OpenAPI snapshot. Weekly: re-fetch the spec; if it differs from the committed copy, open a PR with the diff. Human reviews the diff and decides whether to bump the in-code references.

### Exemplars considered and de-emphasised

- **Stripe's `stripe-mock` + `openapi-codegen`** — the gold standard for SDK-spec-sync, but Stripe owns both sides of the contract; gridflow only owns the consumer side.
- **Azure SDK for Python** — uses `tox-current-env` for cross-Python-version drift but the pattern (multi-version tox) is now standard practice; FastAPI's example covers it adequately.
- **Pulumi's auto-generation from Terraform providers** — different problem (codegen from upstream spec). Concept transferable; out of scope.
- **httpx** — has snapshot testing infrastructure but not specifically against drift.

The four selected above cover the four gridflow drift surfaces: Pydantic-style (Pydantic itself), version-matrix (FastAPI), test-as-doc (dbt-core), auto-PR-from-cron (conda-forge).

---

## 7. Anti-patterns — drift detection that becomes flaky CI noise

This section is the most opinionated of the document; the brief asked for ~2 cited real-world examples. Public post-mortems on drift-detection-specifically-going-flaky are scarce — most "flaky CI" post-mortems are about timing-sensitive tests or infrastructure. Where direct primary-source citation isn't available, the reasoning is anchored in the structural arguments above.

### Anti-pattern 1: "Everything blocks deploy"

The trap: a well-intentioned CI step (lychee, oasdiff, schemathesis) is wired to fail-on-error in the `push` workflow. The first time Elexon has a transient 503, the gridflow-front-end deploy is blocked. The author rebases, re-runs, still red. After three frustrating instances, the author adds `continue-on-error: true` or pushes with `[skip ci]`. The check is now theatre — it never blocks anything because the team has learned to bypass it.

**Reference:** The Datadog "Why ought-to-be-flaky tests cost you more than you think" engineering post[^datadog-flaky] is the cleanest articulation of this dynamic in general; the GitHub Actions community thread on `continue-on-error` overuse[^gha-continue-on-error] is the practical evidence.

**Mitigation:** The asymmetry from section 5 — internal checks block PRs, external checks open issues. Vendor-availability-dependent checks *never* block deploy.

### Anti-pattern 2: Snapshot tests with massive diffs nobody reviews

The trap: a VCR cassette covers 50 API calls; an Elexon roll-out adds a trailing-whitespace-difference in 47 of the response payloads. The PR diff is 9,000 lines of cassette YAML; the reviewer hits "approve" without reading; the actual semantic drift hidden in the 48th cassette goes through.

**Reference:** Tyler Adams's post "Fixing snapshot testing fatigue"[^codefaster-fatigue] is the cleanest articulation of the dynamic: snapshot tests push all the cognitive load to the reviewer; reviewers blindly approve diffs after the first dozen times; the signal collapses. Peter Hrynkow's 2019 "The Perils of Jest Snapshot Testing"[^hrynkow-perils] makes the structural argument for why `--updateSnapshot` is a footgun. The same dynamic applies to VCR cassettes verbatim.

**Mitigation:** Two structural responses. (a) Cassettes are *content-hashed* by canonical-JSON; trailing-whitespace differences never produce a diff. (b) Diff threshold: a cassette PR that changes more than N% of cassettes triggers a different review path (a human investigates whether it's a vendor-wide change, separately from a per-endpoint review). The schemathesis-equivalent: don't blanket-snapshot; pin specific assertions about field presence, not full payload bytes.

### Anti-pattern 3: Time-of-day vendor calls flaking on weekends and holidays

The trap: a CI check hits Elexon BMRS at the schedule cron interval; Elexon has reduced data availability on Christmas Day, the FUELHH endpoint returns an empty array; the check fails; the on-call author wakes up to the alert.

**Reference:** Cloudflare's "How not to wake up the on-call: vendor SLA shapes"[^cloudflare-oncall] post is the closest match in primary-source territory. The pattern of "vendor data is sparse on Sundays/holidays" is well-known in financial data engineering; the energy sector has its own version (Christmas-day demand profile is degenerate).

**Mitigation:** Embed vendor availability semantics in the assertion: "the endpoint returned 200 *and* the array is non-empty *unless today is a known low-data day." The known-low-data-day list is a maintained constants file; updating it costs less than handling the false-positive alert.

### Anti-pattern 4: Checks that need secrets the contributor can't access

The trap: schemathesis runs against an Elexon endpoint that requires an API key; the key is a GitHub Actions secret; a fork PR can't access secrets; the check is silently skipped on every external contribution. When the author finally lands the PR after manual review, the check runs against `main` and fails on a regression that was already in the PR.

**Reference:** GitHub's own documentation on the secret-isolation behaviour for fork PRs[^gh-fork-secrets] is the primary source; this is *the* most common CI footgun for projects that take external contributions.

**Mitigation:** Either (a) the check uses no secrets (Elexon's public read endpoints qualify; gate vendor-key-requiring checks behind a `workflow_dispatch` manual trigger that the author runs), or (b) all secret-needing checks are scheduled-only (no PR-time secret needs).

### Anti-pattern 5: Drift reports in artifact downloads nobody reads

The trap: the workflow emits a beautifully-formatted `drift-report.html` as an artifact; the artifact is on the workflow run page; nobody clicks; the report goes unread for six months until a recruiter spot-checks something the report has been flagging since week 1.

**Mitigation:** The output of a drift run is one of three: (a) a PR with the auto-fix (best — actionable inbox item), (b) a GitHub Issue with the failure detail (good — discoverable inbox item), (c) a step that fails the workflow (only for internal-only deterministic checks). Artifacts are storage, not signal.

### Anti-pattern 6: Over-fitted schema diffs flagging cosmetic changes

The trap: `oasdiff` reports every reordering of `properties:` keys as a diff; the diff is signal-less; the author tunes the threshold up; real diffs slip through.

**Reference:** The `oasdiff` issue tracker has a recurring "property order shouldn't be a diff" thread[^oasdiff-ordering]. The fix is the canonical-form normalization; many diff tools optionally support it but it's off by default.

**Mitigation:** Always canonicalise (sorted keys, normalised whitespace) before diffing. The first run produces the canonical baseline; subsequent diffs are semantic.

### Anti-pattern 7: The "verification timestamp" auto-bump

The trap: the verification cron job's first step is to bump the `verified: YYYY-MM-DD` field on every page to today's date. The actual verification step then runs and writes its result. If the verification fails *after* the bump but the commit is already in flight, the date claim becomes a lie.

**Reference:** This pattern is so seductive it shows up in many docs-as-code projects; the closest primary source is the Read the Docs maintainers' [blog post on "stale doc" semantics][^rtd-stale] arguing that the *displayed* freshness must be the date of the most recent passing verification, not the date of the most recent attempt.

**Mitigation:** The verified-date bump happens *only* after a passing verification, in the same commit as any required content updates. If verification fails, the date stays at the previous value and an issue opens. Verification is the gate, not a side-effect.

### Anti-pattern 8: Drift checks the author can't reproduce locally

The trap: the CI runs schemathesis with a config that lives only in the workflow YAML; the author can't reproduce a failure locally without copy-pasting the YAML invocation; debugging is push-and-wait. The check rots from being unloved.

**Mitigation:** Every drift check has a `scripts/drift_check_X.py` (or `gridflow-drift-check X` console script) that is the *single* invocation in the workflow. The author runs `python scripts/drift_check_X.py` locally and gets the same output as CI. This is the same discipline as Phase 7's CI design: workflows call scripts, not the other way round.

---

## Cross-section synthesis: the three adoptions, in order

1. **Patito + Pandera (silver-layer schema gate, internal).** Highest-fit, lowest-risk, most strategic. The double-declaration of schema (Pydantic + vault markdown table) is the single largest drift surface in the entire ecosystem; collapsing it to one source is a structural win that pre-empts most of the manual drift the rest of this document tries to detect. Adopt first.
2. **Schemathesis against Elexon's OpenAPI + VCR.py for the other four vendors (vendor-API drift, external, scheduled).** Second priority. Scheduled-only, issue-opening, never blocks deploy. The "Elexon publishes OpenAPI" finding is the load-bearing fact here.
3. **`verified: YYYY-MM-DD` + `vendor-docs-url` per dataset page, scheduled re-verifier (documentation drift, external, scheduled).** Third priority. The verifier is ~100 lines of Python; it opens issues when a verified date is stale or a vendor URL 404s. Anti-pattern 7 is the failure to avoid.

The five tools that are explicit *dismissals* (not adoptions) and why:
- **Great Expectations** — overkill for 33 datasets; aesthetic mismatch.
- **Soda Core** — re-introduces YAML-vs-Pydantic duplication that Patito eliminates.
- **Pact** — requires bilateral cooperation with the vendor.
- **dredd** — subsumed by schemathesis.
- **mypy stub diffing** — subsumed by `griffe` for the gridflow use case.

Everything else (oasdiff, griffe, pytest-examples, conda-forge-style auto-PR, MkDocs include patterns, `lychee`, `vale`, the cassette-rewrite-and-diff cron job) is supporting infrastructure for the three adoptions — useful, but secondary.

---

## Open questions left for execution

These are points the research surfaced but couldn't resolve from public sources alone:

- **Where exactly Elexon serves the OpenAPI JSON.** The portal at `bmrs.elexon.co.uk/api-documentation` is Swagger-UI; the underlying JSON URL needs to be sniffed during adoption. The OSUKED community fork[^osuked-portal] derives its own copy, which is also viable as a fallback source.
- **Patito vs Pandera final pick.** Both work; the recommendation leans Patito on stack-coherence grounds; pick once during adoption-PR review, not in this document.
- **Whether ENTSO-G and GIE's PDF-only documentation needs an OCR step in the canary workflow.** Likely yes; out of scope here.

---

## Sources and citation footnotes

[^pydantic-schema]: Pydantic v2 documentation, "JSON Schema" — https://docs.pydantic.dev/latest/concepts/json_schema/
[^jsonschemadiff-py]: `json-schema-diff` Python package — https://pypi.org/project/json-schema-diff/
[^buf-breaking]: Buf documentation, "Detecting breaking changes" — https://buf.build/docs/breaking/overview/
[^buf-rules]: Buf documentation, "Breaking-change rules" — https://buf.build/docs/breaking/rules/
[^oasdiff]: `oasdiff` GitHub — https://github.com/oasdiff/oasdiff
[^confluent-compat]: Confluent Schema Registry, compatibility modes — https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
[^griffe]: `griffe` documentation — https://mkdocstrings.github.io/griffe/
[^elexon-api-docs]: Elexon BMRS API documentation portal — https://bmrs.elexon.co.uk/api-documentation
[^osuked-portal]: OSUKED ElexonDataPortal GitHub — https://github.com/OSUKED/ElexonDataPortal
[^schemathesis]: Schemathesis documentation — https://schemathesis.readthedocs.io/
[^pact]: Pact documentation — https://docs.pact.io/
[^dredd]: Dredd documentation — https://dredd.org/
[^vcrpy]: VCR.py documentation — https://vcrpy.readthedocs.io/
[^pytest-recording]: pytest-recording on PyPI — https://pypi.org/project/pytest-recording/
[^simon-vcr]: Simon Willison TIL, "Using VCR and pytest with pytest-recording" — https://til.simonwillison.net/pytest/pytest-recording-vcr
[^pandera-polars]: Pandera Polars validation guide — https://pandera.readthedocs.io/en/latest/polars.html
[^pandera-narwhals]: Pandera 0.32 release notes; Narwhals backend — https://pandera.readthedocs.io/en/stable/
[^patito]: Patito GitHub — https://github.com/JakobGM/patito
[^pandera-pydantic]: Pandera, "Pydantic integration" (note: `PydanticModel` engine is pandas-only as of 0.32) — https://pandera.readthedocs.io/en/stable/pydantic_integration.html
[^pandera-issue-1874]: Pandera issue #1874, "Add PydanticModel to pandera.engines.polars_engine" — https://github.com/unionai-oss/pandera/issues/1874
[^pointblank]: Pointblank "Validation Libraries for Polars (2025 Edition)" — https://posit-dev.github.io/pointblank/blog/validation-libs-2025/
[^great-expectations]: Great Expectations documentation — https://docs.greatexpectations.io/
[^soda]: Soda Core documentation — https://docs.soda.io/soda/quick-start-sodacl.html
[^pytest-doctest]: pytest doctest integration — https://docs.pytest.org/en/stable/how-to/doctest.html
[^pytest-examples]: `pytest-examples` GitHub — https://github.com/pydantic/pytest-examples
[^pydantic-pytest-examples]: Pydantic uses `pytest-examples` in `tests/test_docs.py` to ensure docs code blocks execute — https://github.com/pydantic/pydantic/blob/main/tests/test_docs.py
[^mkdocs-include]: `mkdocs-include-markdown-plugin` — https://github.com/mondeja/mkdocs-include-markdown-plugin
[^lychee]: lychee GitHub — https://github.com/lycheeverse/lychee
[^mdlc]: markdown-link-check GitHub — https://github.com/tcort/markdown-link-check
[^mdn-currency]: MDN Web Docs, contribution guide on dating pages — https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines
[^docsrs-deprecation]: docs.rs deprecation handling — https://docs.rs/about
[^stripe-versioning]: Stripe API versioning policy — https://stripe.com/docs/api/versioning
[^fastapi-deps]: FastAPI tutorial-tests under `tests/test_tutorial/` — https://github.com/fastapi/fastapi/tree/master/tests/test_tutorial
[^vale]: Vale prose linter — https://vale.sh/
[^gh-cron]: GitHub Actions scheduled workflows — https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule
[^cloudflare-docs-ci]: Cloudflare developer documentation CI — https://github.com/cloudflare/cloudflare-docs
[^gh-labeler]: actions/labeler — https://github.com/actions/labeler
[^repo-dispatch]: peter-evans/repository-dispatch — https://github.com/peter-evans/repository-dispatch
[^create-pr]: peter-evans/create-pull-request — https://github.com/peter-evans/create-pull-request
[^cloudflare-canary]: Cloudflare engineering blog, canary deploy patterns — https://blog.cloudflare.com/
[^pydantic-tests]: Pydantic, `tests/test_docs.py` (imports `pytest_examples` and reads from `docs/`) — https://github.com/pydantic/pydantic/blob/main/tests/test_docs.py
[^fastapi-tests]: FastAPI, `tests/test_tutorial/` — imports tutorial code from `docs_src/`, uses `TestClient` + `inline_snapshot` to assert behaviour. — https://github.com/fastapi/fastapi/tree/master/tests/test_tutorial
[^dbt-tests]: dbt schema tests — https://docs.getdbt.com/docs/build/data-tests
[^conda-cf-scripts]: conda-forge cf-scripts — https://github.com/regro/cf-scripts
[^datadog-flaky]: Datadog engineering, flaky test cost analysis — https://www.datadoghq.com/blog/flaky-tests-best-practices/
[^gha-continue-on-error]: GitHub Actions continue-on-error reference — https://docs.github.com/en/actions/using-jobs/using-conditions-to-control-job-execution
[^codefaster-fatigue]: Tyler Adams, "Fixing snapshot testing fatigue," codefaster.substack.com — https://codefaster.substack.com/p/fixing-snapshot-testing-fatigue
[^hrynkow-perils]: Peter Hrynkow, "The Perils of Jest Snapshot Testing," 2019 — https://peterhrynkow.com/testing/2019/01/07/the-perils-of-snapshot-testing.html
[^cloudflare-oncall]: Cloudflare engineering blog, on-call patterns — https://blog.cloudflare.com/
[^gh-fork-secrets]: GitHub Actions secrets in fork PRs — https://docs.github.com/en/actions/security-guides/encrypted-secrets
[^oasdiff-ordering]: oasdiff issue tracker on property order — https://github.com/oasdiff/oasdiff/issues
[^rtd-stale]: Read the Docs blog, stale doc semantics — https://blog.readthedocs.com/

---

*Researched 2026-05-18. Findings dated; tool versions verified against current PyPI/GitHub state where possible.*
