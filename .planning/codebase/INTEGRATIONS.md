# External Integrations

**Analysis Date:** 2026-05-17

## APIs & External Services

All "integrations" in this repo are **documentary references**: this is a static documentation site that describes upstream data vendors used by sibling projects (`gridflow`, `gridflow-models`). The site itself does not call these APIs at runtime — endpoint URLs appear in HTML/JSON content for reader reference only. The canonical vendor list lives in `site/hifi/data/vendors.json:1-102`.

**Electricity vendors:**
- **Elexon BMRS** — GB electricity balancing & settlement data (prices, generation, demand, balancing actions). Region: United Kingdom. Auth: Public (no key). Rate limit: 2 req/s · 7,200/hour. Format: JSON, ISO-8601, UTC. History: from 2014-04. Catalogued in `site/hifi/data/vendors.json:3-16` and `site/hifi/data-sources/elexon.html:41-71`.
  - Base URL: `https://data.elexon.co.uk/bmrs/api/v1`
  - Vendor docs: `https://bmrs.elexon.co.uk/` (`site/hifi/data-sources/elexon.html:41`)
  - 28 datasets documented; the 22 with dedicated pages live in `site/hifi/data-sources/elexon/` (`agpt`, `agws`, `boal`, `disbsad`, `fou2t14d`, `freq`, `fuelhh`, `fuelinst`, `indo`, `indod`, `itsdo`, `mid`, `ndf`, `ndfd`, `netbsad`, `nonbm`, `pn`, `system_prices`, `temp`, `tsdf`, `uou2t14d`, `windfor`). Example endpoint URL embedded in copy: `https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH?...` (`site/hifi/data-sources/elexon/fuelhh.html:453`).
- **ENTSO-E** — European transmission system operator transparency data (prices, load, cross-border flows). Region: EU. Auth: API key. Rate limit: 6 req/s. 14 datasets. History from 2015-01. (`site/hifi/data/vendors.json:17-30`).
  - Base URL: `https://web-api.tp.entsoe.eu`
- **NESO (Carbon Intensity)** — Real-time carbon intensity of the GB electricity grid. Region: UK. Auth: Public. Rate limit: 10 req/s. 1 dataset. History from 2018-01. (`site/hifi/data/vendors.json:88-100`).
  - Base URL: `https://api.carbonintensity.org.uk`

**Gas vendors:**
- **ENTSO-G** — European gas transmission flows at interconnection points. Region: EU. Auth: Public. Rate limit: 5 req/s. 1 dataset. History from 2018-01. (`site/hifi/data/vendors.json:31-44`).
  - Base URL: `https://transparency.entsog.eu/api/v1`
- **GIE AGSI** — Underground gas storage levels by country and facility. Region: EU. Auth: API key. Rate limit: 5 req/s. 1 dataset. History from 2011-01. (`site/hifi/data/vendors.json:45-58`).
  - Base URL: `https://agsi.gie.eu`

**LNG vendors:**
- **GIE ALSI** — LNG terminal send-out and inventories. Region: EU. Auth: API key. Rate limit: 5 req/s. 1 dataset. History from 2012-01. (`site/hifi/data/vendors.json:59-72`).
  - Base URL: `https://alsi.gie.eu`

**Weather vendors:**
- **Open-Meteo** — Temperature, wind, radiation; forecast and historical. Region: Global. Auth: Public. Rate limit: 5 req/s. 2 datasets. History from 1940-01. (`site/hifi/data/vendors.json:73-86`).
  - Base URL: `https://api.open-meteo.com/v1`

## Data Storage

**Databases:**
- None used by this repository. The medallion (bronze/silver/gold) warehouse described in the marketing copy (e.g. `site/hifi/architecture.html`, `site/hifi/assets/site.js:43-46` footer blurb) lives in sibling project `gridflow`, not here.

**File Storage:**
- Local filesystem only. Static assets are served from `site/hifi/` via `os.chdir(_SITE_DIR)` in `src/gridflow_front_end/serve.py:77`. Reference data files: `site/hifi/data/vendors.json`, `site/hifi/data/elexon.json`.

**Caching:**
- None at the repository level. Production caching is delegated to the GitHub Pages CDN.

## Authentication & Identity

**Auth Provider:**
- None. Both the local server and the deployed static site are fully public; no login, no session, no API key handling.

## Monitoring & Observability

**Error Tracking:**
- None.

**Logs:**
- Local dev server: per-request access logs are suppressed (`_SilentHandler.log_message` is a no-op, `src/gridflow_front_end/serve.py:29-31`); only true errors are emitted to stderr with the prefix `[gridflow-serve] ERROR: …` (`src/gridflow_front_end/serve.py:33-35`).
- GitHub Pages deploy: standard GitHub Actions run logs in the `Deploy to GitHub Pages` workflow.

## CI/CD & Deployment

**Hosting:**
- GitHub Pages. The deployment URL is captured by the workflow as `${{ steps.deployment.outputs.page_url }}` (`.github/workflows/deploy.yml:20-22`).
- Three sibling-project repositories are linked from the footer (`site/hifi/assets/site.js:66-68`): `https://github.com/EBentham/gridflow`, `https://github.com/EBentham/gridflow-models`, `https://github.com/EBentham/gridflow-front-end`. Additional outbound links: `https://github.com/EBentham` (`site/hifi/index.html:830`), `https://github.com/EBentham/gridflow-models` (`site/hifi/models/demand-forecast.html:266`), generic `https://github.com` (`site/hifi/architecture.html:1156`).

**CI Pipeline:**
- Single workflow: `.github/workflows/deploy.yml` — `Deploy to GitHub Pages`. Trigger: `push` to `main` or manual `workflow_dispatch` (`.github/workflows/deploy.yml:3-6`).
- Permissions: `contents: read`, `pages: write`, `id-token: write` (`.github/workflows/deploy.yml:8-11`).
- Concurrency group `pages` with `cancel-in-progress: true` (`.github/workflows/deploy.yml:13-15`).
- Steps (`.github/workflows/deploy.yml:23-33`):
  1. `actions/checkout@v4`
  2. `actions/configure-pages@v5`
  3. `actions/upload-pages-artifact@v3` with `path: site/hifi`
  4. `actions/deploy-pages@v4`
- Runs on `ubuntu-latest` under environment `github-pages` (`.github/workflows/deploy.yml:19-22`).

## Environment Configuration

**Required env vars:**
- None. The local server uses CLI flags only (`--port`, `--no-open`, `src/gridflow_front_end/serve.py:56-67`). The deploy workflow uses no custom env vars — it relies entirely on GitHub-provided `GITHUB_TOKEN` permissions and OIDC (`id-token: write`).

**Secrets location:**
- No secrets are stored, read, or required by this repository. No `.env`, `.env.*`, or `secrets/` files exist.

## Webhooks & Callbacks

**Incoming:**
- None. The deployed artifact is static; the local server only serves files from `site/hifi/` and has no `POST` handling (it uses `SimpleHTTPRequestHandler`, `src/gridflow_front_end/serve.py:26`).

**Outgoing:**
- None at runtime. The Python server makes no outbound network calls.
- At browser render time, each page issues outbound requests to `https://fonts.googleapis.com` and `https://fonts.gstatic.com` for the Google Fonts CSS/woff2 (e.g. `site/hifi/index.html:8-10`, repeated in every page under `site/hifi/`). No other third-party hosts are contacted by the served pages.

## Third-Party Browser Services

**Google Fonts:**
- Used by every page in `site/hifi/`. Loads Fraunces, Inter, and JetBrains Mono via `https://fonts.googleapis.com/css2?...&display=swap` (`site/hifi/index.html:10`, `site/hifi/data-sources.html:9`, `site/hifi/data-sources/elexon.html:9`, `site/hifi/architecture.html:9`, `site/hifi/models/demand-forecast.html:10`, and every file under `site/hifi/data-sources/elexon/`).
- This is the only third-party browser dependency; all other scripts/styles are first-party under `site/hifi/assets/`.

---

*Integration audit: 2026-05-17*
