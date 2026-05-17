# Feature Research

**Domain:** Editorial portfolio + technical data-documentation site for UK/EU energy markets, audience = full-stack data-science recruiters in energy trading
**Researched:** 2026-05-17
**Confidence:** HIGH on dataset-page and model-case-study anatomy (extracted directly from the user's reference templates `fuelhh.html` and `demand-forecast.html`); HIGH on anti-features (PROJECT.md anti-goal is explicit); MEDIUM on differentiator novelty (benchmark sites referenced from training data, not re-fetched).

## How to read this file

The downstream planner needs to scope features per page type, not as a flat list. Each section below answers one of the six sub-questions in the kickoff: dataset pages, home/landing, architecture, cross-page navigation, model case studies, and honesty signals. Within each, **table stakes**, **differentiators**, and **anti-features** are called out separately. A consolidated dependency map and MVP definition sit at the end.

A feature here "earns its slot" if a quant doing UK/EU energy data would spot it and trust the author more. Generic personal-portfolio advice has been left out.

---

## 1. Dataset reference pages — what a "good" page has

The canonical template is `site/hifi/data-sources/elexon/fuelhh.html`. Below, the page anatomy is extracted as features so all 22 Elexon pages (and any new ENTSO-E dataset) can hit the same fidelity bar.

### Table stakes (must have for the page to read as a real dataset doc)

| Feature | Why expected | Complexity | Notes |
|---|---|---|---|
| Breadcrumbs (`Gridflow / Data sources / Elexon BMRS / <slug>`) | Recruiter needs to know the level of the page without scrolling | LOW | Already present in `fuelhh.html` line 118; trivial to replicate |
| Slug + display title in hero (`fuelhh` in mono, then prose title) | The slug *is* the API path; showing both signals "I know the wire-level name" | LOW | Pattern: 28px mono slug above the serif H1 |
| 6-cell metadata card next to the hero (silver path / API path / param style / earliest data / volume / primary key) | This is the "fingerprint" a recruiter scans in <5s — proves the author has actually wired it | LOW | Hard-coded grid; one source of truth per dataset |
| Stats strip (5 numbers): resolution, lag, rows/SP, history, primary entity count | Numeric density signals depth without prose | LOW | Already present; just needs filling for 16 stubs |
| Sticky sidebar with "on this page" + sibling-datasets-in-category | Reference docs are scanned, not read top-to-bottom; sticky sidebar is the norm (Stripe docs, Tailwind docs) | MEDIUM | Sticky positioning + IntersectionObserver scroll-spy (already implemented, scattered across 22 pages — needs consolidation) |
| Overview section (3 short paragraphs: what it is, how it's sourced, when it was backfilled) | Without prose context, the metadata is just numbers | LOW | Avoid marketing tone; first sentence should mention the BMRS endpoint by name |
| Schema table (column / type / nullable / description / PK badge) | Recruiter looks at this to verify the author understands the source's actual shape, not just its existence | LOW | `fuelhh.html` schema-table CSS is already production-quality; needs extracting to `theme.css` to apply to all 22 pages |
| Sample-data table (real-looking 8–12 rows of the silver-layer output) | "Show me a row" is the universal sniff test for data documentation | LOW | Tables look better dark/inverted vs. cream page — visual contrast emphasises "this is a data preview" |
| Numbered caveats section (5 specific items, each with a heading + 1-sentence failure mode) | This is the page's credibility tax — generic disclaimers ("data may be inaccurate") fail; specific failure modes ("Embedded generation is excluded — sub-1 MW solar appears as reduced demand, not generation") pass | MEDIUM | Each caveat should be specific enough that the recruiter learns something they didn't know about the dataset |
| Related-datasets cards (2-column grid, each with slug + a "pair with X to do Y" blurb) | Cross-linking turns the catalog from a tree into a graph and signals systems thinking | LOW | The blurb is the value — "Join on (settlement_date, settlement_period) to add price context to the dispatch stack" is what a quant writes |
| Static snapshot chart (one inline SVG, deterministic seed, clearly labeled "static snapshot · live wiring planned") | Charts make the page feel like documentation, not a spec; static framing keeps honesty | LOW | `data-chart="stackedArea"` infrastructure already exists; just need to ensure every dataset has at least one |

### Differentiators (set this apart from a "good enough" dataset doc)

| Feature | Value proposition | Complexity | Notes |
|---|---|---|---|
| Tab group on the API section (Example URL / DuckDB SQL / Python parquet) | Shows three angles on the same data: the raw vendor request, the warehouse query, the dataframe read. This is the "I know how a quant uses this" move | LOW | Already exists in `fuelhh.html`; the `setTab()` JS just needs consolidating |
| "Param style" cell calling out vendor-specific date-window patterns | `publishDateTimeFrom / To` is an Elexon quirk; surfacing it tells the reader the author has actually paginated the API | LOW | A one-line cell in the metadata card |
| Domain-specific "fuel types" or "PSR types" section with colour swatches and one-line definitions | The level of detail (CCGT, NPSHYD, INTFR, etc., each defined) signals deep familiarity. This is where energy-data depth shows | MEDIUM | The 16-pill fuel-type grid in `fuelhh.html` is the exemplar; not every dataset has this, but those that do (`fuelhh`, `agpt`, `agws`) should |
| Inline link to the Pydantic schema class name (`gridflow/schemas/elexon.py · ElexonFuelHH`) | Bridges the on-site doc to the actual source-of-truth code — signals "this is wired, not just written" | LOW | One line under the schema-table heading |
| Partition info card (parquet path / partition by / dedup key) | Tells the reader the silver layer is queryable Hive-partitioned Parquet, not just a vague "warehouse" | LOW | Three-cell card; one of the strongest "this person knows data engineering" signals |
| Cross-vendor consistency: same template applied to ENTSO-E (and later GIE, ENTSO-G) so the *shape* of the doc is comparable across vendors | A recruiter who knows ENTSO-E can navigate the Elexon page on muscle memory and vice versa | HIGH | This is the v1 cross-vendor proof; requires generalising the template beyond Elexon-specific cells (e.g. `period`/`settlement_date` is Elexon-only) |
| Inline `<code>` for endpoint paths, schema class names, and column names — always monospace, always with `padding: 2px 6px; border: 1px solid var(--rule)` | The visual texture of "the on-site text mentions the same identifier you'd type in your IDE" is what makes it feel like a doc, not a description | LOW | Already in `fuelhh.html` body prose; needs to be the convention everywhere |

### Anti-features (deliberately NOT on dataset pages)

| Feature | Why requested | Why problematic | Alternative |
|---|---|---|---|
| Live "last fetch" timestamps ("42 s ago") | Looks dynamic, looks impressive | The site is static; the timestamp is a lie that breaks credibility on the first reload | Replace with `PRIMARY KEY` cell (already done on `fuelhh.html`, line 167) or with an explicit "Data through YYYY-MM-DD · static snapshot" footnote |
| "Live · 30 min" chips in the hero | Suggests the chart will refresh in 30 minutes | It won't. CONCERNS.md flags this across all 22 pages. | Replace with `static snapshot · live wiring planned` chip or `D+1 settled` chip — both are honest and informative |
| Try-it-now embedded query runner | Demo-friendly | Requires a live API path the site doesn't have; adds JS/security surface; turns docs into a SaaS dashboard | Provide copy-able SQL/URL/Python snippets only. Reader runs them in their own DuckDB / curl / Jupyter |
| Per-dataset usage analytics ("3.2k views this week") | Social proof | The page is for one recruiter at a time, not a community; analytics on a personal site reads as performative | Omit |
| Interactive chart hover tooltips | Standard chart UX | Adds JS complexity; tooltips imply live data; the chart is illustrative anyway | Inline SVG with no event handlers; if a tooltip is needed, write the values into the legend |
| Per-dataset comments / "Was this helpful?" widgets | Engagement | The page is a one-way reference, not a community | Omit; the related-datasets cards do the cross-linking |
| "Coming soon" date promises ("Live wiring · Q3 2026") | Commitment signal | Dates miss; missed dates damage credibility more than no date | Phrase as state, not promise: `static snapshot · live wiring planned` says "we know it's static, we have a plan, we're not committing to a date" |
| Cosmetic export buttons (`<span>Export CSV</span>` with no handler) | Looks complete | CONCERNS.md lines 102 flag a dead "Export CSV" chip on `data-sources.html`. Buttons that don't do anything are worse than no button | If the function is real (SQL/Python copy buttons), wire it. If not, remove it. |

---

## 2. Home / landing page — what a recruiter notices in 30 seconds

The 30-second test is the dominant constraint (PROJECT.md core value). The home page must land a credibility signal in the visible viewport before any scrolling.

### Table stakes

| Feature | Why expected | Complexity | Notes |
|---|---|---|---|
| Above-the-fold framing sentence that names the domain ("a pipeline and catalogue for UK & European energy data") | The recruiter needs to know in <5s whether this is the kind of work they hire for | LOW | Already present in `index.html` line 308–314; serves the purpose |
| Three "pillar" tiles immediately below the hero (Architecture / Catalogue / Models) | A site-shape map — the reader can predict the navigation without exploring it. Standard for Stripe Press / FT Alphaville / Linear docs | LOW | Already present `index.html` line 397–474; needs the false "Shipping" status badges removed (in-flight refactor) |
| One "feature" visual artifact on the home page that proves the author's domain depth — currently the donut + fuel-mix card | Without a concrete piece of energy-data work visible on the home page, the pillars are abstract. The donut is the proof | LOW | Already present; needs the timestamp framed as "Static snapshot · refreshed nightly" (currently in-flight as part of honesty sweep) |
| Models section listing all five planned models with **explicit stage labels** (Shipping / Planned · F6 / Planned · F7) and the shipping one linking to a case study | Recruiters want to see ambition (roadmap) + shipped work (case study). Both, not either-or | LOW | Already present `index.html` line 671–733; the `Planned · F6` framing is good (concrete identifier, not date) |
| About section with name, location, one paragraph of focus, contact links | The site is a *person's* portfolio; identifying the person is non-negotiable | LOW | Present; the `<!-- TODO: replace 'E. Bentham' -->` comment needs cleaning |
| Direct GitHub links to the sibling repos (`gridflow`, `gridflow-models`) | The site documents code that exists; the recruiter wants the code | LOW | Present in the about section |

### Differentiators

| Feature | Value proposition | Complexity | Notes |
|---|---|---|---|
| Scope strip with 5 inline numbers (`7 vendors · 49 datasets · 12 y history · 3 layers · 0 cloud deps`) | A glanceable density of facts that says "this is a real thing of measurable size", not "I have some interests in energy" | LOW | Already present `index.html` line 367; needs the count discrepancy reconciled (CONCERNS.md notes 7/49 is hand-maintained in 3 places) |
| A literal **query example** ("Query it · SQL or Python — pick one") on the home page | The recruiter sees what using this looks like, not just what it is. Stripe docs do this on their home page — the API call IS the marketing | LOW | Already present `index.html` line 742; the tabs UX is already wired through `[data-tabs]` |
| Architecture preview block (mini bronze/silver/gold cards) before the full architecture page | The reader sees the medallion shape on the home page; if they want depth, they click; if not, they've already absorbed the concept | LOW | Already present `index.html` line 479; visually distinctive (paper-deep background bar) |
| The "about" facts list with `Tools · Polars · DuckDB · LightGBM · Pydantic` as visible monospace tags | The tech stack is the trust signal; the recruiter scans for "the libraries they use here" | LOW | Present; the choice of Polars over pandas (per user CLAUDE.md) is itself a signal |
| One serif italic accent on every H1 (`<span class="italic">energy data.</span>`) | The Fraunces italic-ending pattern is the editorial-quiet identity move — distinguishes this from a tech-bro/SaaS-template look | LOW | Already in use; the in-flight refactor strips `fg-accent` colour and keeps the italic, which is correct |

### Anti-features

| Feature | Why requested | Why problematic | Alternative |
|---|---|---|---|
| Hero KPI strip with "Datasets ingested today / Models running / 99.97% uptime" | Looks like a working data platform | Lies. The site is static; nothing is ingesting; nothing is "running" | The static scope-strip numbers (`7 vendors · 49 datasets · 12 y history`) are facts about the project, not lies about runtime |
| Animated "live grid frequency: 49.97 Hz" ticker | Genuine energy-trading visual; great in a real product | Same lie; would also be hard to keep accurate at deploy time | The static snapshot donut is the right tradeoff: it shows what the data looks like without claiming to be live |
| Photo of the author + "Hi I'm <name>" salutation | Standard portfolio template move | Personal-brand framing; works against the "I'm a quant who happens to have a site" framing. Stripe Press / FT Alphaville never show authors as glamour shots | The text-only about section (already present) is correct |
| Testimonials / "recommended by" logos | Social proof | The author doesn't have these; faking them is fatal; chasing them shifts the page into marketing register | Use the GitHub link instead — code is the testimonial |
| Newsletter signup / "subscribe for updates" | Engagement | The site has no updates schedule; a newsletter form with no list behind it is decorative | Omit; the GitHub stars/watches handle this organically |
| Dark-mode toggle | Modern affordance | Adds CSS surface and persistence logic; the cream + forest palette is the identity — toggling it dilutes it | Single light theme; the inverted dark blocks (sample-data tables, code blocks) provide intra-page contrast |
| Scroll-triggered animations / fade-ins | Looks polished | Editorial-quiet sites (Stripe Press) are still and confident — animations on a docs site read as nervous | None |
| Hire-me CTA button in the nav | Common portfolio pattern | Overt; the about section's "Open to roles in energy trading & quantitative research" line does the same job in a quieter register | Keep the "Status" line in the about facts; the nav stays clean |
| Blog / writing index page | Portfolio default | Empty blogs look abandoned; writing dates show how stale things are | The model case studies *are* the writing. Add more case studies, not a separate blog |
| Project / portfolio "tiles" grid (cards with screenshots and tags) | Standard portfolio | The three pillars *are* the projects, framed by what they do (architecture / data / models) not what they're called | Keep the pillars; resist the urge to add a "selected work" cards grid |

---

## 3. Architecture page — how to explain a data pipeline visually + textually

The architecture page is the deepest "this person can think about systems" signal on the site. Below 5 minutes of skimming it should be obvious whether the author understands the trade-offs in their own design.

### Table stakes

| Feature | Why expected | Complexity | Notes |
|---|---|---|---|
| One canonical block diagram of the system at the top (input vendors → bronze → silver → gold → consumers) | Without a top-level diagram, the page reads as prose-only and recruiters bail | MEDIUM | `architecture.html` line 338 has an SVG arch-title diagram; the role/labelledby usage is the only one on the site (good a11y precedent) |
| Layered explanation: a card for each layer (bronze / silver / gold) with what's *in* it, what it *guarantees*, and one example file path | The layers are the architecture's load-bearing concept; explaining each is the table-stakes minimum | LOW | Already present (`index.html` line 500 shows the pattern; the full architecture page extends it) |
| Numbered trace-steps: walk one piece of data (e.g. an Elexon `fuelhh` response) from API call to gold query | Concrete trace is what separates a real systems person from someone who can draw a diagram | MEDIUM | `architecture.html` has `.trace-step` and `.trace-guarantee` CSS — the convention is present but needs writing up |
| Named design decisions (architecture decision records) inline, each with title + tag + body | Quants and senior engineers read decision records before they read code; this is where the author shows judgement | MEDIUM | `.decision` block in `architecture.html` is the affordance; needs filling. ADR-014, ADR-019, ADR-039 are referenced in `demand-forecast.html` and create natural cross-links |
| Tech stack grid (library name + role) | The recruiter wants the list: Polars, DuckDB, Pydantic v2, LightGBM, MAPIE. Spelled out, monospace | LOW | `.stack-grid` already in `architecture.html` |

### Differentiators

| Feature | Value proposition | Complexity | Notes |
|---|---|---|---|
| **Bitemporal callout** — explicit mention of event-time + ingestion-time on every row, point-in-time queries | Bitemporal data engineering is signal-rich vocabulary; calling it out by name says "I know the literature, not just the recipes" | LOW | Already in `index.html` line 491 prose; expand on the architecture page |
| Repo tree as a styled `<pre>` (dark background, accent for directories, dim for placeholders) | Shows the actual layout of the codebase — recruiters can map prose claims to filenames before clicking through to GitHub | LOW | `pre.repo-tree` CSS already in `architecture.html`; needs content |
| Trade-off prose alongside each diagram ("Considered: X. Rejected: Y. Outcome: Z") | Diagrams without trade-offs read as marketing; trade-offs are what a senior engineer skims for | MEDIUM | The `.callout` strong-tag pattern in `demand-forecast.html` (e.g. `Why indo not itsdo?`) is the template |
| External links to the actual vendor docs that the pipeline calls into (Elexon BMRS docs, ENTSO-E TP) — `target="_blank"` with `rel="noopener"` | Proves the author hasn't paraphrased vendor concepts and is treating vendor docs as the absolute source of truth (per PROJECT.md hierarchy) | LOW | The architecture page already links to GitHub but is missing the vendor docs link |
| One "constraint" callout per layer ("idempotent backfills · Pydantic v2 schema gating · DuckDB views only in gold") | Constraints are stronger than features for revealing design taste | LOW | One sentence per layer; can co-locate with the layer-card |

### Anti-features

| Feature | Why requested | Why problematic | Alternative |
|---|---|---|---|
| Architecture page as an interactive flow chart (click nodes to drill in) | Modern docs aesthetic (Mermaid, Excalidraw embeds) | Adds complexity and a heavy library; the diagram needs to render statically for GitHub Pages and not be a re-implementation of system understanding | Inline SVG with a single static diagram (already done); use `role="img" aria-labelledby="..."` for accessibility |
| Real-time pipeline health dashboard ("3 connectors green · 0 errors today") | Standard SRE dashboard | The pipeline does not run on the site's infrastructure; the dashboard would have to lie about state | A "What this isn't" block on the architecture page saying explicitly: "Gridflow runs locally; this site documents the design, not a hosted instance" |
| Performance benchmarks ("Ingests 1.4M rows in 32 s") | Looks impressive | Numbers change; un-versioned benchmarks rot. If the bench moves, the page is stale and embarrassing | Cite shapes ("~1.4M rows / month", "~90 s end-to-end on a 2024 laptop" per `demand-forecast.html`) — they're estimates, framed as estimates |
| Multiple architecture diagrams that contradict each other | Reflects iteration | Recruiters can't tell which is current; a single canonical diagram is the load-bearing artifact | One diagram, kept current. Trade-offs go in prose underneath |
| "Click to expand" collapsed sections for each subsystem | Saves vertical space | Hidden-by-default content does not serve the 30-second skim; recruiters won't expand. Long-form is fine if the diagram + headings let them skim | Inline everything; rely on a sticky sidebar or in-page anchors if the page exceeds ~1200 lines |

---

## 4. Cross-page navigation — catalog browse, sidebar, related links

Navigation makes a 28-dataset catalog feel like a coherent reference, or like a maze.

### Table stakes

| Feature | Why expected | Complexity | Notes |
|---|---|---|---|
| Persistent top nav (Architecture · Catalogue · Model · About) injected on every page | Standard docs convention; missing it makes every page feel orphaned | LOW | Already implemented in `assets/site.js` via `data-page` / `data-root` contract |
| Breadcrumbs on every non-home page | Tells the reader where they are without scrolling to the URL bar | LOW | Already present on dataset pages, catalogue pages, model pages |
| Active-state nav highlighting (`active` class + `aria-current="page"`) | Reader's location in the IA is unambiguous | LOW | `active` class is present; `aria-current` is missing (CONCERNS.md a11y note) |
| Catalogue hub at `data-sources.html` listing every vendor with a card grid | Without a hub, there's no top-down view of what's documented | LOW | Already present; needs the 5 dead `href="#"` stubs (ENTSO-E, ENTSO-G, GIE, Open-Meteo, NESO) replaced with real "coming soon" landing pages (per PROJECT.md Active item) |
| Per-vendor hub at `data-sources/<vendor>.html` listing every dataset in that vendor with cards (slug, freq, lag, one-liner) | The vendor hub is the index for browsing a single vendor's datasets | MEDIUM | Already present for Elexon (`data-sources/elexon.html`); needs replicating for ENTSO-E (per PROJECT.md Active item) |
| In-page anchor links from sidebars to `#overview`, `#schema`, `#sample`, `#api`, `#caveats`, `#related` | Long pages need section jumps | LOW | The pattern works on 6 complete dataset pages; broken on 16 stubs because sections don't exist (CONCERNS.md) |
| Scroll-spy that highlights the active sidebar section as the reader scrolls | Reader knows where they are within the page | LOW | Implementation already exists (in two variants, scattered); needs consolidating into `site.js` |
| "Related datasets" cards at the bottom of every dataset page | After reading one dataset, the obvious next read is signposted | LOW | Already in `fuelhh.html` lines 533–610; bring all 22 to this fidelity |

### Differentiators

| Feature | Value proposition | Complexity | Notes |
|---|---|---|---|
| Catalogue manifest (`data/elexon.json`) as the source of truth, *driving* the vendor hub's card list | A single edit propagates to all pages that list the dataset; eliminates the count-drift bug currently in CONCERNS.md (22 files / 25 manifest entries / 28 catalog claim) | HIGH | Currently the manifest is inert (CONCERNS.md "Unused JSON manifests"). Wiring `site.js` to `fetch()` it requires browser-side rendering of the cards — a real upgrade but a substantive change |
| Sibling-dataset list in the sidebar (`fuelhh.html` lines 218–226 shows the pattern) | Reader on `fuelhh` can jump to `fuelinst` / `agpt` / `agws` / `windfor` without going back to the vendor hub | LOW | Already in `fuelhh.html`; needs to land on all 22 pages with the right per-category siblings |
| "Pair with X to do Y" blurbs on related cards | Most cross-doc links just say "see also"; the *why* is what makes the cross-link informative | LOW | Already in `fuelhh.html`: "Join on (settlement_date, settlement_period) to add price context to the dispatch stack" |
| Cross-vendor cross-references (an Elexon page linking to an ENTSO-E page with "ENTSO-E publishes the same metric at zonal granularity") | Demonstrates the author understands when one vendor's dataset replaces another | LOW | Requires the cross-vendor template to exist first (dependency: Elexon-fidelity ENTSO-E dataset page) |
| Mobile-functional nav with a hamburger toggle | The site is recruiter-facing and recruiters check on phones | LOW (after viewport fix) | `site.js` already wires the mobile menu; the 23-page `width=1280` viewport bug breaks it on most pages (per PROJECT.md and CONCERNS.md) |

### Anti-features

| Feature | Why requested | Why problematic | Alternative |
|---|---|---|---|
| Full-text search box in the nav (`Algolia DocSearch`-style) | Standard for big docs sites | Premature for ~28 datasets; adds JS, requires a search index, signals "I'm pretending to be Stripe docs" | Sidebar + breadcrumbs + browser Ctrl+F is sufficient at this scale |
| Mega-menu hover panels in the top nav | Common in vendor docs | The site has 4 top-level sections; a mega-menu over 4 links is overbuilt | Plain links. If the site grows past ~10 top sections, reconsider |
| Tag-cloud / faceted browser ("filter by frequency · daily / hourly / 30-min") | Discovery affordance | Adds JS + state management; the vendor hub already groups by category | Static grouping by category (Generation / Prices & Balancing / Demand & Forecasts / System & Reference) on the vendor hub is the natural facet axis |
| "Recently viewed" or "your bookmarks" | Personalisation | Requires client state, costs trust (cookies, storage); the site is a one-time read for a recruiter | None |
| Comments / discussion threads at the bottom of pages | Engagement | Needs moderation, looks abandoned without traffic, costs hosting | None |
| Cosmetic "Export CSV" / "Subscribe" chips with no handler | Looks complete | CONCERNS.md flags this — dead buttons mislead more than they inform | Either wire the handler (copy SQL/Python is real) or remove the chip |
| Multiple competing taxonomies (a "domains" tag + a "vendors" tag + a "frequency" tag, all faceted) | Comprehensive | Two taxonomies are usually wrong-and-conflicting; one is enough | Catalog by vendor (the natural taxonomy); cross-cut by category on the vendor hub |

---

## 5. Model case study pages — how quants write up models for outsiders

The canonical template is `site/hifi/models/demand-forecast.html`. It's the deepest single artifact on the site and the page most likely to convert a 30-second skim into a 10-minute read. The features below extract its anatomy.

### Table stakes

| Feature | Why expected | Complexity | Notes |
|---|---|---|---|
| Hero with model name, model ID (`day_ahead.lgbm_demand.v1`), and metadata strip (family / market / product / units / horizon / currency) | A model write-up needs to assert what it is before it explains how — the 6-cell strip is the canonical move | LOW | Already in `demand-forecast.html` lines 247–278 |
| "The question" section in plain prose — what does the model do, why is it hard | The outsider (recruiter) doesn't have context; the quant needs to set it up. A two-paragraph framing block does this | LOW | Already at `demand-forecast.html` lines 393–424 |
| KPI strip with the model's headline metrics and their gate thresholds visible (`pinball p50: 348 · gate ≤ 1500`) | The numbers + the bar to clear is what proves the model is evaluated, not just trained | LOW | Already at `demand-forecast.html` lines 281–308 |
| Inputs section: target + feature pipeline as a named list, each feature with its role | The set of features *is* the model when audience is generalist; a list with descriptions is more readable than a notebook cell | LOW | Already at `demand-forecast.html` lines 426–499 (`.feature-list`) |
| Estimator section: explicit hyperparameter table | Hyperparameters are the spec; hiding them in code is a tell that the author doesn't track them | LOW | Already at `demand-forecast.html` lines 537–550 |
| Validation diagram: walk-forward fold viz with per-fold metric (`612 MW · 595 MW · 620 MW · 576 MW · 601 MW · 587 MW`) | Walk-forward / expanding-window is the gold-standard time-series validation; visualising it proves it was done, not just claimed | MEDIUM | Already at `demand-forecast.html` lines 593–652 (`.wf-diagram`) |
| Reliability table: nominal vs empirical coverage, gate column | Calibration is the headline diagnostic for probabilistic models; this table is what a recruiter who knows quantile regression looks for | LOW | Already at `demand-forecast.html` lines 694–730 (`.cov-table`) |
| Caveats / "What this isn't" — three blocks, each with title + 1-paragraph honest scope statement | Naming the model's limits is the strongest credibility move on the page | LOW | Already at `demand-forecast.html` lines 854–883 |
| GitHub link to the sibling repo (`gridflow-models`) | Reader who's hooked clicks through to code | LOW | Already present in the hero metadata |

### Differentiators

| Feature | Value proposition | Complexity | Notes |
|---|---|---|---|
| Fan chart with `realised` line overlaid + an `as-of` vertical marker | This is the chart pattern that probabilistic forecasters live by; rendering it inline (no Plotly) shows DIY confidence | MEDIUM | Already at `demand-forecast.html` lines 311–391; pure inline SVG paths — the SVG is hand-drawn but the convention is right |
| "Why X not Y?" callouts (`Why indo not itsdo?`) inline with the input section | These show the author's selection process, not just the selection. They're the highest-density signal of taste on the page | LOW | Already at `demand-forecast.html` lines 451–460 (the `.callout` strong/span pattern) |
| ADR references inline (`per ADR-014`, `per ADR-019`, `per ADR-039`) | Architecture decision records show the author writes them, which is what senior practitioners do. Citing them inline is the proof-of-existence move | LOW | Already in `demand-forecast.html`; the cross-link to the architecture page (which would list the ADRs) is implicit and would strengthen if explicit |
| Reproduce-it SQL block at the bottom (the actual query that pulls the training data) | Reader can copy-paste and verify; nothing reads as more honest than working code | LOW | Already at `demand-forecast.html` lines 824–834 |
| Residual breakdown by hour-of-day (24-bar plot) showing where the model errs | Goes beyond aggregate metrics to the *shape* of the error. Quants notice this immediately | MEDIUM | Already at `demand-forecast.html` lines 750–781 (`.hod-bars`) |
| "What's next" / bench-list with explicit feature IDs (`F5-F`, `F6`, `F7`) | Shows the model is part of a system; the IDs hint at a tracker the author owns; the framing is honest about state | LOW | Already in `demand-forecast.html` lines 889–933 |
| Forecast object's literal API (`forecast.quantiles → {'q_0.05': [...], 'q_0.5': [...]}`) shown inline | The shape of the artefact the model emits is concrete proof the author runs it, not just describes it | LOW | Already in `demand-forecast.html` lines 564–581 (in the code block comment) |
| Citations to the academic literature (`Marcjasz 2022, Lago 2021`) inline | These are the canonical EPF references; citing them by short author-year says "I read this literature" | LOW | Already in `demand-forecast.html` line 516 |

### Anti-features

| Feature | Why requested | Why problematic | Alternative |
|---|---|---|---|
| Interactive "tune the model" widget (sliders for hyperparameters) | Showy; engaging | The model isn't running on the site; the widget would have to fake responses. The whole site's anti-goal | None |
| Live model predictions ("Tomorrow's forecast · pulled at 14:02") | Genuine product feel | Same: no live wiring. The user is explicit in PROJECT.md | The fan chart with a fixed date range and a clearly-labeled `as-of` marker is the right form |
| Notebook embed (full Jupyter as an iframe) | Reproducibility-coded | Heavy, ugly, breaks on mobile, takes over the page. A SQL block + a GitHub link does the same with 1/100 the weight | The reproduce-it SQL pattern (already used) is the right size |
| One-click "deploy this model" button | SaaS-coded | Same anti-goal as the site overall; suggests this is a product | None |
| Performance benchmarks for the model framework (`fits in 47ms · serves 12,000 QPS`) | Engineering bona fides | These are training infrastructure metrics, not model-quality metrics. They distract from the calibration / coverage / MAE story | The "Roughly 90 seconds end-to-end on a 2024 laptop" framing (already in `demand-forecast.html` line 841) is right: a shape, not a benchmark |
| User testimonials for the model | Marketing surface | The audience is one recruiter at a time, not a market of buyers | None |
| Star-ratings on caveats ("3-star caveat: minor issue") | Triage affordance | Caveats are equally weighted because they all matter at decision time; ranking creates a hierarchy that lets readers skip | Numbered caveats with one-line failure modes (the dataset-page pattern); on case studies, the three-column "What this isn't" works |

---

## 6. Honesty signals — credible static-ness without looking unfinished

This is the highest-novelty section. The user's anti-goal (no SaaS framing, no fake live) creates a real risk: a site that's *too quiet* about being static can read as abandoned or stalled. The features below are the moves that make explicit static-ness read as a deliberate choice, not a missing feature.

### Table stakes (without these, the site reads as "this person forgot to wire it up")

| Feature | Why expected | Complexity | Notes |
|---|---|---|---|
| Explicit "static snapshot · live wiring planned" chip on every chart and dynamic-looking widget | Reader sees the framing on first contact; no one is misled into thinking the chart is live | LOW | Already on `fuelhh.html` line 277; needs replicating on every page with a `data-chart` widget |
| `Data through YYYY-MM-DD` footnote on every dataset's sample table or chart | Tells the reader exactly how stale the page is; if it says 2024-06-15, the reader trusts that's the snapshot date, not a system-broken-since-2024 signal | LOW | Already present in `fuelhh.html` line 397 ("Showing SP1 rows for 2024-06-15 only") |
| "Last edited: YYYY-MM-DD" or "Documentation updated: YYYY-MM-DD" footer line per page (NOT "last sync") | Decouples "I keep this page current" from "the data is live" — both are honesty signals but only the first is a property of the site | LOW | Currently the footer has "last sync 2026-04-30 14:02 UTC" which CONCERNS.md flags as a lie; replace with "Last edited" or remove |
| Numbered caveats section on every dataset page with specific failure modes (not generic disclaimers) | Honest sites enumerate their gotchas; marketing sites bury them. Five numbered items per dataset is the bar | LOW | `fuelhh.html` lines 488–528 is the exemplar; needs replicating across 22 pages |
| "What this isn't" section on every model case study | Mirrors the caveats pattern at the model level; states scope limits explicitly | LOW | `demand-forecast.html` lines 854–883 is the exemplar |
| Replace `<span class="chip live">live · 30 min</span>` with `<span class="chip snapshot">static · D+1 settled</span>` or `<span class="chip">D+1 settled</span>` site-wide | The visual chip is fine; the *label* needs to be honest | LOW | This is the PROJECT.md "Honesty sweep" Active item |

### Differentiators (these make static-ness an asset, not a confession)

| Feature | Value proposition | Complexity | Notes |
|---|---|---|---|
| Source-of-truth hierarchy stated openly somewhere on the site (vendor docs > on-site docs > Vault) | Naming the hierarchy reframes "this is static" as "this is downstream of the truth, and the truth is one click away" — proactively honest | LOW | The hierarchy is in PROJECT.md; surfacing it on a "Methodology" or "About this documentation" page or as a footer note on every dataset page is the move |
| External link to the original vendor doc at the top of every dataset page (e.g. Elexon BMRS official `/datasets/FUELHH` reference) | Reader can verify the on-site doc against the source in <10s. CONCERNS.md notes `elexon.html` already does this with a `target="_blank"` button | LOW | One line in the hero metadata or the API section; add `rel="noopener"` |
| Explicit author voice acknowledging illustrative-ness ("The chart below uses a deterministic seed — the *shape* is realistic but the values are illustrative, not real Elexon outputs") | Pre-empts the "is this real data?" question; trades a small confession for a large credibility gain | LOW | One italicised sentence under every `data-chart` widget; pairs with the existing `snapshot-note` CSS |
| "Why X not Y?" callouts throughout (the `demand-forecast.html` pattern of "Why indo not itsdo?") | Every selection has an alternative; surfacing the rejected option proves the choice was deliberate. Honesty-by-selection-disclosure | LOW | The `.callout` pattern is already CSS-defined; needs adoption on dataset pages (e.g. "Why FUELHH not FUELINST?") |
| Inline change-log / "Backfill complete to 2014-04-01 (changelog 2026-04-29)" line | Dating the data without timestamping the page lets the reader assess freshness at the *data* level | LOW | Already in `fuelhh.html` line 256 |
| Stage labels (`Shipping · Planned · F6 · Planned · F7`) instead of dates or "coming soon" | Concrete identifiers (`F6`) imply a real tracker; dates promise things that may not happen; "coming soon" is meaningless | LOW | Already in use on `index.html` model rows; extend to vendor stubs ("ENTSO-E · in progress · F2") instead of `href="#"` placeholders |
| ADR cross-references that anchor decisions to a numbered system | An ADR-014 footnote signals the author has a real decision log somewhere; the number is the cheap signal | LOW | Already in `demand-forecast.html`; an `architecture.html#adr-014` anchor would make them clickable |
| Confidence framing in prose ("median observed lag is 42 s from Gridflow's perspective") | Phrases like "median observed", "in the latest fold", "from Gridflow's perspective" anchor every claim in a measurable property, not a vibe | LOW | Already in `fuelhh.html` line 526; expand this micro-style across all dataset caveats |
| One "About this documentation" or "Methodology" page (or section on home) explaining: this is a static archive, regenerated periodically, source-of-truth hierarchy, last-edited convention | A single canonical reference for all the honesty signals; the rest of the site can short-link to it | MEDIUM | New page or new section; pairs with the source-of-truth-hierarchy point above |

### Anti-features

| Feature | Why requested | Why problematic | Alternative |
|---|---|---|---|
| Bright "STATIC" or "DEMO" watermarks plastered across pages | Maximum honesty | Reads as apologetic / unfinished; signals "this would be better if it were live, sorry"; makes the site feel like a work-in-progress vs. an archive | Small `snapshot-note` chips on charts only; the rest of the site reads as confident documentation |
| Banner at the top of every page: "Notice: this site contains static data only" | Disclaimer-coded | Defensive; readers see banners as legal text, not editorial register | Embed honesty in metadata cells and chart labels, not as a global banner |
| `aria-label="This data is illustrative"` on every chart | Accessibility-flavoured honesty | Conflates a11y with editorial framing; the snapshot-note text already says this for sighted and screen-reader users | One `snapshot-note` element per chart; let it be read normally |
| "Live" toggle that does nothing (toggles to "demo mode" or "snapshot mode") | Looks dynamic, sort of honest | A toggle that doesn't do anything is worse than no toggle (CONCERNS.md flags this pattern with the cosmetic `Export CSV` chip) | None |
| "I built this in N hours" / "Total time invested: 240h" | Effort-coded honesty | Cheapens the work; the work speaks for itself; the framing is junior-coded | None |
| Pop-up modal on first visit explaining the site is static | Pre-emptive | Modals are universally read as marketing; static-ness should be sensed within seconds of normal reading, not via interruption | The hero subheading + the `snapshot-note` chips do this in normal reading flow |
| Long footer disclaimer about data accuracy ("we make no warranty...") | Lawyer-coded | Pads pages with non-editorial text; the per-dataset numbered caveats already cover the substance | Per-dataset caveats; one short copyright line in the footer; no legalese |

---

## Feature Dependencies

```
[fix mobile viewport] (~23 pages, trivial)
    └──unblocks──> [mobile-functional nav (already wired in site.js)]
    └──unblocks──> [credible-on-phones recruiter check]

[extract dataset-page CSS to theme.css]
    └──unblocks──> [bring 16 stubs to fuelhh fidelity at maintainable cost]
    └──unblocks──> [cross-vendor template (ENTSO-E dataset page)]
    └──unblocks──> [reduce per-page editing surface 22x]

[consolidate scroll-spy + setTab into site.js]
    └──unblocks──> [scroll-spy bug-fixes apply globally instead of 22x]
    └──unblocks──> [scroll-spy works correctly on stubs once sections exist]

[fix 16 broken dataset stubs (add #overview / #schema / #sample / #api sections)]
    └──unblocks──> [sidebar nav works on every dataset page]
    └──unblocks──> [scroll-spy observes all 6 sections, not just 2]
    └──unblocks──> [22 datasets reach fuelhh-fidelity baseline]
    └──enables───> [Vault sync: PROJECT.md notes sync is on-site → vault, so on-site must be canonical first]

[reconcile dataset count discrepancy (22/25/28)]
    └──unblocks──> [scope-strip on home reads as accurate]
    └──unblocks──> [vendor hub counts match catalog claims]
    └──prerequisite──> [decide: is the manifest the source of truth, or the HTML?]

[wire manifest → cards (data/elexon.json → vendor hub HTML via fetch())]
    └──requires──> [reconciled count + finalised manifest]
    └──enables───> [single edit propagates across pages]
    └──conflicts──> [zero-build-step constraint — manifest must work at runtime, not compile-time]

[ENTSO-E vendor hub + 1 ENTSO-E dataset at fuelhh fidelity]
    └──requires──> [Elexon dataset-page template generalised: no Elexon-specific cells like settlement_period]
    └──requires──> [theme.css contains the shared dataset-page styles (so adding a new vendor doesn't 22x duplicate CSS)]
    └──proves────> [cross-vendor template works → other vendors are repeatable]

[honesty sweep (kill 'live' framing, replace last-sync, replace timestamps)]
    └──unblocks──> [credibility on first reload (CONCERNS.md flags this as biggest credibility hit)]
    └──enables───> [pillar status badges can be honest: "Shipping" was a lie; removing it is in-flight]
    └──enables───> [chart labels read as static-by-design]

[Vault sync to gridflow repo's quant-vault/30-vendors/]
    └──requires──> [stable on-site content (PROJECT.md hierarchy: on-site is the source for Vault)]
    └──requires──> [all 22 dataset pages at consistent fidelity]
    └──spans-repos──> [coordinated commit across this repo and gridflow]

[accessibility pass (<main>, aria-current, aria-hidden on decorative icons)]
    └──independent──> [does not block other work]
    └──complements───> [editorial register: screen-reader-friendly silence is consistent with the aesthetic]
```

### Dependency notes

- **Mobile viewport fix is the single highest-leverage trivial change.** It unblocks recruiter-on-phone credibility immediately, costs ~10 minutes of find-and-replace, and makes the existing mobile nav code actually run.
- **CSS extraction precedes stub completion.** Fixing 16 stubs at the current ~30-line inline-style cost is 480+ lines of duplicate edits. Extracting first means each stub fix is just adding 5 sections, not 5 sections + 30 style lines.
- **Cross-vendor template requires Elexon consistency first.** If only 6 of 22 Elexon pages are full, the template's variance is too high to confidently extrapolate to a second vendor.
- **Manifest-driven rendering conflicts with the zero-build-step constraint** in one specific way: a JSON manifest fetched at runtime is fine for cards, but breaks if GitHub Pages serves stale JSON to a fresh HTML — both files must deploy in the same commit. Mitigation: deploy is atomic anyway; this isn't a blocker.
- **Vault sync is downstream of everything.** It needs the source-of-truth (on-site content) to be stable across all 22 pages and aligned with the vendor docs. PROJECT.md confirms the direction is on-site → Vault, so Vault sync must come last.
- **Honesty sweep is independent of stub fixes** and can ship before them — it's a find-and-replace pass on labels and footer text. Doing it first gives the in-flight refactor a clean commit and lets the stub work proceed against the honest visual register.

---

## MVP definition

The Active section of PROJECT.md already enumerates the v1 cleanup milestone scope. The MVP definition below maps the feature *patterns* above to that scope, not to add tasks but to clarify which patterns are essential.

### Launch with (v1 cleanup milestone)

- [ ] **Mobile-functional viewport on all pages** — recruiter-on-phone is the highest-traffic path; the bug breaks 23 of 27 pages
- [ ] **All 22 Elexon dataset pages at fuelhh fidelity** — the 7-section anatomy (hero metadata · stats strip · sticky sidebar · overview · snapshot chart · schema · sample · API tabs · caveats · related) is the per-page table-stakes pattern; this is the "show the catalog is real" move
- [ ] **Shared dataset-page CSS extracted to theme.css** — prerequisite for 22-page consistency at maintainable cost
- [ ] **Honesty sweep complete** — all `live` chips relabelled, all "X min ago" timestamps replaced with snapshot framing, footer "last sync" replaced. Specifically: the in-flight `fuelhh.html` honesty edits committed and propagated
- [ ] **Numbered caveats section on every Elexon dataset page** — the credibility tax; generic disclaimers fail, specific failure modes pass
- [ ] **Reconciled dataset count** — pick one (22 or 25 or 28), align the 3 places where the count appears, decide whether the manifest is the source of truth
- [ ] **One ENTSO-E vendor hub + 1 ENTSO-E dataset page at fuelhh fidelity** — the cross-vendor template proof
- [ ] **Coming-soon landing pages for ENTSO-G, GIE, Open-Meteo, NESO** — kills the 5 dead `href="#"` stubs; replace with "Planned · F<n>" framing, not "Coming soon"
- [ ] **Accessibility minimum: `<main>` landmark, `aria-current` on active nav, `aria-hidden` on decorative icons, sidebar hover fix** — table-stakes a11y, not differentiator
- [ ] **One license, one LICENSE file, aligned strings** — credibility move; current MIT-vs-Apache-2.0 contradiction is a small but real hit
- [ ] **Vault sync to gridflow repo's quant-vault/30-vendors/** — depends on everything above; ship last in the milestone

### Add after v1 (next milestone candidates)

- [ ] Wire `data/elexon.json` and `data/vendors.json` to render vendor-hub cards via `site.js fetch()` — eliminates the count-drift bug class entirely
- [ ] More model case studies at the demand-forecast fidelity bar (wind, solar, merit-order stack, fundamentals SMP) — the home page already lists them; each is a substantial write-up
- [ ] Per-page "Last edited" footer driven by git metadata at deploy time (replaces the current footer's hardcoded "last sync")
- [ ] Live wiring for one dataset (real Elexon API call → static snapshot regenerated nightly via GitHub Actions, committed back to the repo) — moves the "live wiring planned" framing into honest "live wiring shipping" for a specific dataset
- [ ] Self-hosted Google Fonts (drops the "0 cloud deps" claim contradiction CONCERNS.md flags)

### Defer (v2+)

- [ ] Static-site generator adoption (11ty, Astro, Hugo) — only if the dataset-page count growth makes hand-authoring untenable; current 22 + 1 ENTSO-E is at the edge but not over
- [ ] Search UI (Algolia DocSearch or pagefind) — only at ~50+ datasets, not before
- [ ] A "methodology" / "about this documentation" page — captures the source-of-truth hierarchy in one place; nice to have but not load-bearing if the framing is in chart labels and footnotes
- [ ] Real-time data on any page — explicit anti-goal per PROJECT.md; only revisit if the audience or the project's purpose changes

---

## Feature prioritization matrix

| Feature | User value | Implementation cost | Priority |
|---|---|---|---|
| Mobile viewport fix on all pages | HIGH | LOW (find-and-replace) | **P1** |
| Honesty sweep (kill `live`, replace timestamps, replace last-sync) | HIGH | LOW (find-and-replace, in-flight) | **P1** |
| Bring 16 broken dataset stubs to fuelhh fidelity (sections + content) | HIGH | HIGH (16 pages × ~5 sections each, with real content per dataset) | **P1** |
| Extract dataset-page CSS to theme.css | MEDIUM | LOW (cut/paste once) | **P1** (prerequisite for stub work) |
| Numbered caveats section on every Elexon dataset | HIGH | MEDIUM (requires domain knowledge per dataset) | **P1** |
| Consolidate scroll-spy + setTab into site.js | LOW | LOW | **P2** (debt; not user-visible if the duplicated copies all work) |
| Reconciled dataset count | MEDIUM | LOW (decide + edit 3 places) | **P1** |
| ENTSO-E hub + 1 ENTSO-E dataset at fuelhh fidelity | HIGH | MEDIUM | **P1** (cross-vendor proof) |
| Coming-soon landing pages for ENTSO-G, GIE, Open-Meteo, NESO | MEDIUM | LOW (4 pages × stub content) | **P1** |
| Accessibility pass (`<main>`, `aria-current`, `aria-hidden`, sidebar hover) | MEDIUM | LOW (small edits across pages) | **P1** |
| License contradiction fix | MEDIUM | LOW (decide + edit 3 places + LICENSE file) | **P1** |
| Vault sync to `gridflow/quant-vault/30-vendors/` | HIGH (cross-repo coherence) | MEDIUM (depends on on-site stability) | **P1** (ship last) |
| Wire manifest → vendor-hub cards via fetch() | MEDIUM | MEDIUM | **P2** (future milestone) |
| Live wiring for one dataset (GitHub Actions nightly snapshot) | HIGH (turns "planned" into "shipping") | HIGH (CI + commit-back-to-repo) | **P3** (future milestone, explicit out-of-scope today) |
| More model case studies (wind, solar, stack, SMP) | HIGH | HIGH | **P3** (deferred per PROJECT.md Out of Scope) |
| Search UI | LOW (at 28-dataset scale) | MEDIUM | **P3** |
| Static-site generator adoption | LOW (right now) | HIGH (re-platform) | **P3** (decision deferred per PROJECT.md) |

**Priority key:**
- **P1**: In the v1 cleanup milestone; ship before declaring done
- **P2**: Next milestone candidate; defer one milestone
- **P3**: Future or explicit out-of-scope today

---

## Benchmark site cross-reference

Where the features above came from:

| Source | What's borrowed |
|---|---|
| **Stripe docs** | Sticky sidebar with `On this page` + section anchors; tab groups on code examples (URL / SQL / Python); persistent top nav; cream/light editorial palette; copy-to-clipboard on code blocks |
| **Tailwind docs** | Sticky sidebar with in-page anchors; the visual register of "monospace identifier next to prose explanation" |
| **Linear docs** | Quiet aesthetic, single font family for body, monospace for technical identifiers; honest "this is a doc, not a marketing site" framing |
| **Stripe Press** | Serif headings, italic accents, generous whitespace, no animations; "still and confident" rather than "fast and animated" |
| **FT Alphaville** | Editorial register; dense numeric content (charts, tables) with prose alongside; no SaaS framing |
| **Elexon BMRS docs** | Dataset-page anatomy (endpoint + params + schema + sample); the param-style framing (`publishDateTimeFrom`) — the on-site doc echoes the vendor doc's vocabulary deliberately |
| **ENTSO-E TP docs** | The cross-vendor template's "PSR types" concept; the dataset hub by domain (Generation / Transmission / Balancing / etc.) |
| **Personal portfolios from quants/data scientists** | Model case study structure (Question → Inputs → Estimator → Validation → Caveats → What's next); ADR-style decision callouts inline; reproduce-it SQL block at the bottom |

The synthesis above is opinionated: the dataset-page anatomy is closer to Elexon's actual docs than to Tailwind's; the model case study borrows the academic-paper structure more than the typical Kaggle write-up. Both directions favour depth over flashiness, which matches the PROJECT.md core value.

---

## Sources

- `site/hifi/data-sources/elexon/fuelhh.html` (user-confirmed reference template; lines 113–648)
- `site/hifi/models/demand-forecast.html` (user-confirmed reference template; lines 232–937)
- `site/hifi/index.html` (current home; lines 300–882)
- `site/hifi/architecture.html` (current architecture; lines 1–200 inspected; full structure in CONCERNS.md and ARCHITECTURE.md)
- `.planning/PROJECT.md` (Active requirements, Anti-goal, Core Value, Out of Scope, Key Decisions)
- `.planning/codebase/ARCHITECTURE.md` (site structure, runtime contract, layers)
- `.planning/codebase/CONCERNS.md` (specifically: "Hardcoded 'live' timestamps" section, "16 of 22 Elexon dataset pages are broken stubs" section, "Many placeholder `href="#"` links" section, accessibility gaps section)
- Training-data knowledge of Stripe Press, FT Alphaville, Stripe docs, Tailwind docs, Linear docs, Elexon BMRS docs, ENTSO-E TP docs (not re-fetched; benchmark patterns are widely-known and stable)

---

*Feature research for: editorial portfolio + UK/EU energy data documentation*
*Researched: 2026-05-17*
