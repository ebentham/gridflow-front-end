# Technology Stack

**Analysis Date:** 2026-05-17

## Languages

**Primary:**
- Python `>=3.11` — local development server (`src/gridflow_front_end/serve.py`); declared in `pyproject.toml` (`requires-python = ">=3.11"`).
- HTML5 — static site content under `site/hifi/`. Every page begins with `<!doctype html>` and `<html lang="en">` (e.g. `site/hifi/index.html:1-2`, `site/hifi/data-sources.html:1-2`).
- CSS3 — single design-system stylesheet at `site/hifi/assets/theme.css`. Uses CSS custom properties on `:root` (forest + cream palette: `--paper`, `--ink`, `--accent`, etc., `site/hifi/assets/theme.css:5-36`).
- JavaScript (browser ES2017+, no transpilation) — vanilla JS IIFEs in `site/hifi/assets/site.js` and `site/hifi/assets/charts.js`. Uses template literals, arrow functions, optional chaining (`navigator.clipboard?.writeText`, `site/hifi/assets/site.js:127`), and `dataset` access; no module system, scripts are loaded with plain `<script src="…">` tags.

**Secondary:**
- JSON — vendor/dataset reference data (`site/hifi/data/vendors.json`, `site/hifi/data/elexon.json`).
- YAML — GitHub Actions workflow (`.github/workflows/deploy.yml`).
- TOML — project metadata (`pyproject.toml`).
- SVG — inline charts and diagrams generated from the JS chart module (`site/hifi/assets/charts.js:88-247`) and hand-authored diagrams (e.g. `site/hifi/architecture.html:338`).

## Runtime

**Environment:**
- Python 3.11+ (CPython, stdlib only). The serve module uses `http.server.HTTPServer` and `SimpleHTTPRequestHandler` (`src/gridflow_front_end/serve.py:11`, `src/gridflow_front_end/serve.py:26-31`), so no extra runtime is required.
- Modern evergreen browsers for the static site. The site relies on `document.body.dataset`, `Element.insertAdjacentHTML`, `navigator.clipboard`, and ES2017+ syntax (`site/hifi/assets/site.js`). No polyfills or legacy targets.

**Package Manager:**
- `uv` per user preference (`uv pip install -e ".[dev]"`, `uv run gridflow-serve`). No `requirements.txt` or `uv.lock` is committed to the repo.
- Build backend: `setuptools>=68` declared in `pyproject.toml:1-3`.
- Lockfile: missing (no `uv.lock`, `poetry.lock`, or `requirements*.txt` present).

## Frameworks

**Core:**
- None on the front end. The site is hand-authored HTML/CSS/JS with shared chrome injected at runtime by `site/hifi/assets/site.js:9-77` (nav + footer rendered into every page via `insertAdjacentHTML`). Static-site generation is not used.
- Python backend uses only the standard library — no Flask/FastAPI/Django. `http.server.HTTPServer` serves `site/hifi/` directly (`src/gridflow_front_end/serve.py:82-100`).

**Testing:**
- Not detected. No `tests/`, `test_*.py`, `*.test.*`, or `pytest`/`unittest` configuration exists.

**Build/Dev:**
- `setuptools` (build backend, `pyproject.toml:1-3`).
- `gridflow-serve` console script entry point declared in `pyproject.toml:12-13` and bound to `gridflow_front_end.serve:main`.
- No bundler, transpiler, or asset pipeline — assets ship as-authored from `site/hifi/assets/`.

## Key Dependencies

**Critical:**
- None. `pyproject.toml:10` declares `dependencies = []`. The serve module imports only Python stdlib (`argparse`, `http.server`, `os`, `sys`, `threading`, `time`, `webbrowser`, `pathlib`, `src/gridflow_front_end/serve.py:10-17`).

**Infrastructure:**
- `setuptools>=68` (build backend, `pyproject.toml:2`).

**Browser-side external resources (loaded at runtime, not packaged):**
- Google Fonts — Fraunces (serif), Inter (sans), JetBrains Mono (mono). Loaded on every page via `<link rel="preconnect">` to `https://fonts.googleapis.com` / `https://fonts.gstatic.com` and a `css2` stylesheet link (`site/hifi/index.html:8-10`, `site/hifi/data-sources.html:7-9`, `site/hifi/architecture.html:7-9`, identical block in every `site/hifi/data-sources/elexon/*.html`).
- Font stack fallbacks declared in `site/hifi/assets/theme.css:28-30`: `"Fraunces"`, `"Iowan Old Style"`, `"Georgia"`, serif; `"Inter"`, `-apple-system`, `BlinkMacSystemFont`, `"Segoe UI"`, system-ui, sans-serif; `"JetBrains Mono"`, `"Courier New"`, ui-monospace, monospace.

## Configuration

**Environment:**
- No environment variables. The Python server accepts only CLI flags: `--port` (default `8765`, `src/gridflow_front_end/serve.py:56-61`) and `--no-open` (`src/gridflow_front_end/serve.py:62-67`).
- No `.env` file present. The project ships no runtime configuration files beyond `pyproject.toml`.

**Build:**
- `pyproject.toml` — single source of truth for packaging. Declares build system (setuptools), project metadata, the `gridflow-serve` script, package discovery (`tool.setuptools.packages.find` rooted at `src/`), and `py.typed` marker support (`pyproject.toml:15-19`).
- `.gitignore` excludes `.venv/`, `__pycache__/`, `*.pyc`, `*.egg-info/`, `dist/`, `build/`, `.idea/` (`.gitignore:1-7`).

## Platform Requirements

**Development:**
- Python 3.11+ available on PATH.
- `uv` installed for package management per user preference.
- Local `.venv/` directory (committed-out via `.gitignore:1`); present in repo root.
- Any modern browser to view the served pages at `http://localhost:8765/`.
- The package is installed editable: `uv pip install -e .` (no `[dev]` extras are declared in `pyproject.toml`, so `uv pip install -e ".[dev]"` would fail — install plain editable).

**Production:**
- GitHub Pages. The site is published as a static artifact from `site/hifi/` by `.github/workflows/deploy.yml:28-33` (`actions/upload-pages-artifact@v3` with `path: site/hifi` followed by `actions/deploy-pages@v4`). No Python runtime is required at the deploy target — the `gridflow-serve` Python module is a local-development convenience only.

---

*Stack analysis: 2026-05-17*
