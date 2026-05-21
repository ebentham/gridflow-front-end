---
phase: 07-reconciliation
plan: 01
subsystem: tooling
tags: [python, curl, drift-check, pyproject, console-script, portability]

# Dependency graph
requires: []
provides:
  - Renamed verifier at quant-vault/30-vendors/scripts/gridflow_drift_check.py (sibling-discovery, no hardcoded paths)
  - gridflow-drift-check console script installed via uv pip install -e ".[drift]"
  - [drift] optional-dependencies group with PyYAML>=6,<7 in gridflow-front-end/pyproject.toml
  - drift_check_entry.py shim with GRIDFLOW_DRIFT_CHECK_SCRIPT env override and Windows layout candidate
affects: [07-02-run-verification, 07-03-fix-open-bucket, 07-04-push-vault-github]

# Tech tracking
tech-stack:
  added: [PyYAML>=6,<7 (drift extra), runpy shim pattern]
  patterns: [console-script shim delegating to sibling-repo script via runpy.run_path, env-var-first binary discovery via shutil.which]

key-files:
  created:
    - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py"
    - "src/gridflow_front_end/drift_check_entry.py"
  modified:
    - "pyproject.toml"

key-decisions:
  - "PyYAML only in [drift] extras — pydantic comes transitively via gridflow sys.path insert; adding it as wheel would conflict. (Plan frontmatter said 'PyYAML + pydantic'; plan body explicitly said PyYAML only — body wins)"
  - "_discover_curl() at module level: curl discovery runs at import time, failing loudly on misconfigured environments (T-07-01-04 accepted disposition)"
  - "GRIDFLOW sibling discovery uses parents[3]/gridflow + cwd/gridflow; RuntimeError if neither has src/gridflow subdir"
  - "No --help in underlying verifier: shim smoke test uses import-based resolution rather than --help invocation to avoid triggering full API run"
  - "Two pre-existing F401 ruff violations (get_origin, _REGISTRY) preserved as status quo per plan instruction 'do not add new violations'"

patterns-established:
  - "Console-script shim pattern: thin Python module in installed package delegates to sibling-repo script via runpy.run_path with env-var override"
  - "Binary discovery pattern: GRIDFLOW_CURL_BIN env var > shutil.which('curl') > shutil.which('curl.exe') > RuntimeError"
  - "Sibling-repo discovery pattern: Path(__file__).resolve().parents[N] + cwd fallback + RuntimeError fail-loud"

requirements-completed: [RECON-01]

# Metrics
duration: 35min
completed: 2026-05-19
---

# Phase 7 Plan 01: Verifier Wrap Summary

**`verify_curl_and_silver_schema.py` renamed to `gridflow_drift_check.py`, Windows-specific blockers removed via shutil.which + sibling-discovery, and exposed as the `gridflow-drift-check` console script in gridflow-front-end.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-05-19T00:00:00Z
- **Completed:** 2026-05-19
- **Tasks:** 2
- **Files modified:** 3 (gridflow_drift_check.py, pyproject.toml, drift_check_entry.py)

## Accomplishments

- Renamed verifier via `git mv` in a freshly-initialized quant-vault git repo; baseline commit created
- Fixed both Windows-specific portability blockers: hardcoded `C:\Users\Bobbo` GRIDFLOW default and bare `args[0] = "curl.exe"` assignment
- Added module docstring (with `__future__` import after it, per Python language requirement)
- Created `gridflow-drift-check` console script installable via `uv pip install -e ".[drift]"`
- Secret-leak grep clean: zero hits for ENTSOE_API_KEY/GIE_API_KEY in print/logging calls

## Task Commits

1. **Task 1: Rename verifier + fix Windows-specific blockers** - `739c2ed` (refactor) — in quant-vault
2. **Task 2: Expose console script + declare [drift] extras** - `87f0234` (feat) — in gridflow-front-end

## Final Shape of Key Changes

### `_discover_curl()` function (inserted at module level after gridflow imports, before AUTH_PLACEHOLDERS):

```python
def _discover_curl() -> str:
    """Resolve the curl binary.

    Order: GRIDFLOW_CURL_BIN env var, shutil.which('curl'), shutil.which('curl.exe'), fail.

    Returns:
        Absolute path (or name on PATH) of the curl executable.

    Raises:
        RuntimeError: If no curl binary can be found.
    """
    import shutil

    env = os.environ.get("GRIDFLOW_CURL_BIN")
    if env:
        return env
    for candidate in ("curl", "curl.exe"):
        found = shutil.which(candidate)
        if found:
            return found
    raise RuntimeError(
        "curl binary not found on PATH. Install curl or set GRIDFLOW_CURL_BIN."
    )


_CURL_BIN = _discover_curl()
```

### GRIDFLOW resolution block (replaced L21-26 in original):

```python
_GRIDFLOW_ENV = os.environ.get("GRIDFLOW_REPO")
if _GRIDFLOW_ENV:
    GRIDFLOW = Path(_GRIDFLOW_ENV)
else:
    # Sibling repo discovery: assume gridflow checked out next to quant-vault.
    # Linux CI layout: /work/quant-vault + /work/gridflow.
    # Windows author layout: ...\Desktop\Python\gridflow next to
    # ...\Desktop\Learning\AI\quant-vault — falls through to RuntimeError
    # if neither is present, which is the correct fail-loud behaviour.
    _candidates = [
        Path(__file__).resolve().parents[3] / "gridflow",  # sibling of quant-vault
        Path.cwd() / "gridflow",
    ]
    _found = next((p for p in _candidates if (p / "src" / "gridflow").is_dir()), None)
    if _found is None:
        raise RuntimeError(
            "gridflow repo not found. Set GRIDFLOW_REPO env var or check out "
            "gridflow as a sibling of quant-vault. Tried: "
            + ", ".join(str(p) for p in _candidates)
        )
    GRIDFLOW = _found
```

## `gridflow-drift-check --help` Actual Behaviour

The underlying verifier (`gridflow_drift_check.py`) does **not** implement `--help` or any argparse. Passing `--help` would cause the shim to call `runpy.run_path(str(script), run_name="__main__")`, which executes `main()`. That function calls `load_env_file()`, then `_import_transformers()`, then iterates all markdown files and runs curl against live APIs — a multi-minute operation hitting real endpoints.

**Smoke test substituted:** `python -c "from gridflow_front_end.drift_check_entry import main; print('shim resolved')"` — exits 0, confirming shim module is importable and resolves without error.

**Recommendation for 07-02:** Invoke `gridflow-drift-check` without `--help`; it will run the full verifier immediately.

## Secret-Leak Guard Results

Grep command run:
```bash
grep -nE "print\(.*ENTSOE_API_KEY|print\(.*GIE_API_KEY|logging\..*ENTSOE_API_KEY|logging\..*GIE_API_KEY" gridflow_drift_check.py
```
**Result: zero hits.** The `replace_auth_placeholders()` function returns a `missing_env` sentinel instead of substituting keys when env vars are absent; the substituted curl command (which would contain live keys) is never written to JSON/markdown reports — preserved existing behaviour.

## Verification Results

- `test -f gridflow_drift_check.py` — PASS
- `test ! -f verify_curl_and_silver_schema.py` — PASS
- `grep -nE 'args\[0\]\s*=\s*"curl\.exe"' gridflow_drift_check.py` — no output (PASS)
- `grep -nE 'C:\\Users\\Bobbo' gridflow_drift_check.py` — no output (PASS)
- `python -c "import ast; ast.parse(...); print('parse ok')"` — PASS
- `ruff format --check` — PASS (clean after formatting applied)
- `ruff check` — 2 pre-existing F401 violations preserved as status quo (get_origin, _REGISTRY)
- `grep -nE '^drift\s*=' pyproject.toml | wc -l` — 1 (PASS)
- `grep -nE '^gridflow-drift-check\s*=' pyproject.toml | wc -l` — 1 (PASS)
- `uv pip install -e ".[drift]"` — exits 0; PyYAML 6.0.3 installed
- Shim import: `from gridflow_front_end.drift_check_entry import main` — PASS

## Files Created/Modified

- `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py` — Renamed verifier with module docstring, GRIDFLOW sibling-discovery, _discover_curl(), _CURL_BIN, args[0]=_CURL_BIN
- `C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow-front-end/pyproject.toml` — Added [drift] extras and gridflow-drift-check script
- `C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow-front-end/src/gridflow_front_end/drift_check_entry.py` — Created: console-script shim with GRIDFLOW_DRIFT_CHECK_SCRIPT override and three sibling-discovery candidates

## Decisions Made

- **PyYAML only in [drift] extras** — Plan frontmatter `must_haves` said "PyYAML + pydantic" but the plan body explicitly said PyYAML only (pydantic comes transitively via sys.path insert into gridflow). Body wins; pydantic as a wheel dep would conflict with the editable gridflow import chain.
- **Module docstring precedes `from __future__ import annotations`** — Python language requirement; docstring must be the first statement. Applied accordingly.
- **quant-vault git init on default branch** — No feature branch created; 07d handles the GitHub remote setup.
- **shutil import inside `_discover_curl()`** — Deferred import keeps it local to the function per ruff formatting; functionally identical to top-level import since `_discover_curl()` runs at module load time.

## Deviations from Plan

### Plan Frontmatter vs Body Conflict (Informational, not a code deviation)

**1. [Conflict] Plan frontmatter `min_lines: 700` vs actual file size**
- **Issue:** Plan frontmatter said `min_lines: 700`; actual original file was 637 lines. After edits (3-line docstring + ~25-line GRIDFLOW block + ~25-line `_discover_curl()` block), file is ~665 lines.
- **Resolution:** Plan body explicitly states "no other refactor, no Polars introduction, no signature changes beyond what's specified." Body wins over frontmatter metadata. File size is appropriate.
- **Impact:** None — plan body is authoritative spec.

**2. [Conflict] Plan frontmatter `must_haves` listed "PyYAML + pydantic" for [drift] extras**
- **Issue:** Plan body explicitly said PyYAML only, with rationale that pydantic is transitive via sys.path insert.
- **Resolution:** Body wins. Pydantic not added to pyproject.toml extras.
- **Impact:** None — correct behaviour per plan body rationale.

### Quant-vault Git Initialization

The quant-vault directory had no `.git` directory (verified by prompt precondition). Added:
1. `git init` in quant-vault
2. `git add -A` + initial baseline commit: `15ad67f chore: initial commit (pre-rename baseline)`
3. Then `git mv` rename + edits + refactor commit: `739c2ed`

This was a required prerequisite, not a deviation — called out explicitly in the task prompt.

### Ruff Pre-existing Violations Preserved

Two F401 violations existed in the original file (`get_origin` imported but unused; `_REGISTRY` imported but unused). Plan instruction: "preserve status quo; do not add new violations." These were not fixed. Confirmed they were present in the `git show HEAD:...` of the baseline commit.

## Issues Encountered

- `uv pip install -e ".[drift]"` failed first attempt with "Access is denied (os error 5)" on the dist-info directory. Resolved with `--reinstall` flag on second attempt. Package installed successfully.
- `ruff` not found on PATH directly; invoked as `python -m ruff` successfully.
- `uv run ruff` failed due to TLS certificate error in this environment (`invalid peer certificate: UnknownIssuer`); `python -m ruff` used instead.

## Next Phase Readiness

- `gridflow-drift-check` is installed and the shim resolves to the renamed verifier
- 07-02 can invoke `gridflow-drift-check` directly (no `--help`; it runs the full verifier)
- Set `GRIDFLOW_REPO` to `C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow` if sibling-discovery doesn't resolve on the author's machine layout
- Set `GRIDFLOW_CURL_BIN` if curl is not on PATH (unlikely on Windows with curl built-in since Win10 1803)

---
*Phase: 07-reconciliation*
*Completed: 2026-05-19*
