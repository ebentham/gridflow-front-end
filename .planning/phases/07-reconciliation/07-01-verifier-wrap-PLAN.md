---
id: 07-01-verifier-wrap
phase: 07-reconciliation
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py"   # renamed from verify_curl_and_silver_schema.py
  - "pyproject.toml"                                                                                       # add [project.scripts] gridflow-drift-check + [drift] extras
requirements:
  - RECON-01
autonomous: true
must_haves:
  truths:
    - "Running `gridflow-drift-check --help` exits 0 from a fresh shell on Windows AND on a Linux-like environment (no `curl.exe` baked in; no hardcoded `C:\\Users\\Bobbo` default required)"
    - "The renamed script in `quant-vault/30-vendors/scripts/gridflow_drift_check.py` exists; the old `verify_curl_and_silver_schema.py` no longer exists (renamed, not duplicated)"
    - "`pyproject.toml` in `gridflow-front-end` declares `gridflow-drift-check` under `[project.scripts]` and a `[drift]` optional-dependencies group with PyYAML + pydantic"
    - "`grep -E 'C:\\\\Users\\\\Bobbo|curl\\.exe' gridflow_drift_check.py` returns zero hits (no Windows-only assumptions remain)"
    - "API keys (`ENTSOE_API_KEY`, `GIE_API_KEY`) are not printed in any log/verbose path — secret-leak guard holds"
  artifacts:
    - path: "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py"
      provides: "Renamed verifier with Windows-portability fixes (curl discoverable, vault root parameterised)"
      min_lines: 700
    - path: "pyproject.toml"
      provides: "Console-script entry and `[drift]` optional-dependencies group"
      contains: "gridflow-drift-check"
  key_links:
    - from: "pyproject.toml [project.scripts]"
      to: "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py:main"
      via: "uv pip install -e \".[drift]\""
      pattern: "gridflow-drift-check\\s*=\\s*\"[a-zA-Z_.]+:main\""
    - from: "gridflow_drift_check.py curl invocation"
      to: "system `curl` binary"
      via: "shutil.which('curl') or env var GRIDFLOW_CURL_BIN"
      pattern: "shutil\\.which\\(.curl.\\)"
---

<objective>
Rename `quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py` to `gridflow_drift_check.py` and fix the two Windows-specific portability blockers identified in the drift research (TOOLING-AUDIT § 1-2): (a) the hardcoded `args[0] = "curl.exe"` substitution at L180 and (b) the hardcoded `C:\Users\Bobbo\...` default vault/gridflow paths at L20-26. Expose the renamed script as a `gridflow-drift-check` console script via `[project.scripts]` and declare a `[drift]` optional-dependencies group in `gridflow-front-end/pyproject.toml` (Q-DD-16: lean to `gridflow-front-end` because `quant-vault` has no `pyproject.toml`, confirmed by a Glob on 2026-05-19).

Purpose: produce the wrapped verifier that 07-02 will invoke against all 6 Vendors. RECON-01 from REQUIREMENTS.md is the single acceptance gate.

Output: Renamed verifier file in the upstream Vault directory + new `[project.scripts]` and `[project.optional-dependencies]` entries in `pyproject.toml`. No CI YAML change (cross-repo automated drift CI is explicitly deferred per ADR-0002).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/07-reconciliation/07-CONTEXT.md
@.planning/research/post-v1/drift-detection/SUMMARY.md
@.planning/research/post-v1/drift-detection/TOOLING-AUDIT.md
@docs/adr/0002-vault-hosted-private-github-repo.md

<interfaces>
<!-- Key shapes from the existing verifier the executor must preserve.            -->
<!-- Read the actual file before touching anything; do not assume line numbers   -->
<!-- without re-checking.                                                        -->

From `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py` (current state, ~765 lines):

```python
# L19-26 — hardcoded defaults to parameterise:
VAULT = Path(os.environ.get("VENDOR_VAULT_DIR", Path(__file__).resolve().parents[1]))
GRIDFLOW = Path(
    os.environ.get(
        "GRIDFLOW_REPO",
        r"C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow",
    )
)
REPORT_JSON = VAULT / "vault-curl-schema-validation.json"
REPORT_MD = VAULT / "vault-curl-schema-validation.md"
ENV_FILE = Path(os.environ.get("GRIDFLOW_ENV_FILE", GRIDFLOW / ".env"))

# L176-194 — curl_args(): the Windows-only substitution:
def curl_args(command: str) -> list[str]:
    args = shlex.split(command, posix=True)
    if not args:
        raise ValueError("empty curl command")
    args[0] = "curl.exe"           # <-- L180: must become discoverable
    ...
```

Public surfaces to preserve (so 07-02 can keep using them):
- `REPORT_JSON` and `REPORT_MD` constants — 07-02 reads these paths to consume reports
- the JSON schema written to `REPORT_JSON` — additive extension allowed per Q-DD-17, no breaking changes
- the `main()` function entry point — `[project.scripts]` will point at `<module>:main`
- environment-variable overrides: `VENDOR_VAULT_DIR`, `GRIDFLOW_REPO`, `GRIDFLOW_ENV_FILE` (already present)
</interfaces>

<extras_pattern>
<!-- Existing pyproject.toml pattern to mirror. Read pyproject.toml directly      -->
<!-- before editing; the planner's snippet may be stale.                          -->

```toml
[project.optional-dependencies]
build = ["Jinja2>=3.1,<4"]

[project.scripts]
gridflow-serve = "gridflow_front_end.serve:main"
gridflow-build = "gridflow_front_end.build:main"
```
</extras_pattern>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Rename verifier + fix the two Windows-specific blockers</name>
  <files>
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py (renamed from verify_curl_and_silver_schema.py)
  </files>
  <read_first>
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py (FULL file; ~765 lines — read top-to-bottom to verify current line numbers before editing)
    - .planning/research/post-v1/drift-detection/TOOLING-AUDIT.md (§ 1-2 — the "two Windows-specific blockers" reference)
    - .planning/phases/07-reconciliation/07-CONTEXT.md (specifics block — secret-leak guard)
    - CLAUDE.md (universal: `from __future__ import annotations` already present; preserve; ruff-format on save)
  </read_first>
  <action>
    Perform a single `git mv` of the script file (use `git -C "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault" mv 30-vendors/scripts/verify_curl_and_silver_schema.py 30-vendors/scripts/gridflow_drift_check.py`). Then edit the renamed file to make exactly the changes below — no other refactor, no Polars introduction, no signature changes beyond what's specified.

    Concrete edits (re-read the file first to confirm current line numbers; quoted lines below are from the planner's snapshot but may shift by a line or two):

    1. **Replace the hardcoded GRIDFLOW default (around L20-26).** Current:
       ```python
       GRIDFLOW = Path(
           os.environ.get(
               "GRIDFLOW_REPO",
               r"C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow",
           )
       )
       ```
       Replace with no Windows-specific default. Required new shape:
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
               Path(__file__).resolve().parents[3] / "gridflow",         # sibling of quant-vault
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
       Keep `VAULT`, `REPORT_JSON`, `REPORT_MD`, `ENV_FILE`, and the `sys.path.insert(0, str(GRIDFLOW / "src"))` line **exactly** as-is — only the GRIDFLOW resolution changes. `VENDOR_VAULT_DIR` and `GRIDFLOW_ENV_FILE` env-var overrides stay.

    2. **Replace the `args[0] = "curl.exe"` line (around L180).** Add this module-level helper near the top of the file (just below the imports, before `AUTH_PLACEHOLDERS`):
       ```python
       def _discover_curl() -> str:
           """Resolve the curl binary. Order: GRIDFLOW_CURL_BIN env var, shutil.which('curl'), shutil.which('curl.exe'), fail."""
           env = os.environ.get("GRIDFLOW_CURL_BIN")
           if env:
               return env
           import shutil
           for candidate in ("curl", "curl.exe"):
               found = shutil.which(candidate)
               if found:
                   return found
           raise RuntimeError(
               "curl binary not found on PATH. Install curl or set GRIDFLOW_CURL_BIN."
           )

       _CURL_BIN = _discover_curl()
       ```
       Then in `curl_args(command)` (currently around L176-194), replace `args[0] = "curl.exe"` with `args[0] = _CURL_BIN`. Do not change any other line in `curl_args`. The `-o`/`--output`/`--output=` stripping logic stays untouched.

    3. **Add Google-style docstrings to `_discover_curl()` and the new GRIDFLOW resolution block.** No other docstring changes.

    4. **Update the module-level docstring (if present) or first comment block** to reflect the rename: change any "verify_curl_and_silver_schema" mention to "gridflow_drift_check". If no module docstring exists, add a 3-line one:
       ```python
       """gridflow-drift-check: Verify vault dataset markdown against Canonical Pydantic schemas and Live API responses.

       Renamed and Linux-portable. Original: verify_curl_and_silver_schema.py.
       """
       ```

    5. **Secret-leak guard.** After editing, run a guard grep over the file:
       ```bash
       grep -nE "print\\(.*ENTSOE_API_KEY|print\\(.*GIE_API_KEY|logging\\..*ENTSOE_API_KEY|logging\\..*GIE_API_KEY" gridflow_drift_check.py
       ```
       This MUST return zero hits. If it returns anything, that line is leaking secrets in `--verbose` mode and must be redacted before commit. (This is a check, not a code change; flag and fix anything that matches.)

    Conventional Commit message: `refactor(07-01): rename verifier to gridflow_drift_check and parameterise Windows-specific blockers`

    Run `ruff check gridflow_drift_check.py` and `ruff format gridflow_drift_check.py` after edits (universal prefs). No new `mypy --strict` errors introduced (the file is already not strict-mypy-clean per CLAUDE.md universal — preserve status quo; do not add new violations).
  </action>
  <verify>
    <automated>cd "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts" && test -f gridflow_drift_check.py && ! test -f verify_curl_and_silver_schema.py && grep -nE 'curl\\.exe|C:\\\\Users\\\\Bobbo' gridflow_drift_check.py ; echo "exit=$?" ; uv run --with pyyaml --with pydantic python -c "import ast,sys; ast.parse(open('gridflow_drift_check.py').read()); print('parse ok')"</automated>
  </verify>
  <acceptance_criteria>
    - `test -f C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py` succeeds.
    - `test ! -f C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py` succeeds (old file gone — `git mv`, not copy).
    - `grep -nE 'C:\\\\Users\\\\Bobbo|"curl\\.exe"' gridflow_drift_check.py` returns zero hits (the `_discover_curl()` helper handles both `curl` and `curl.exe` via `shutil.which`, so a literal `"curl.exe"` string inside `_discover_curl()` is allowed only inside the tuple `("curl", "curl.exe")` — adjust the grep to: `grep -nE '"curl\\.exe"' gridflow_drift_check.py | grep -v 'shutil\\.which' | grep -v '"curl", "curl.exe"'` returns zero hits).
    - `grep -n 'shutil.which' gridflow_drift_check.py` returns at least one hit inside `_discover_curl`.
    - `grep -nE 'GRIDFLOW_CURL_BIN|GRIDFLOW_REPO' gridflow_drift_check.py` returns at least 2 hits each.
    - `grep -nE 'print\\(.*ENTSOE_API_KEY|print\\(.*GIE_API_KEY|logging\\..*ENTSOE_API_KEY|logging\\..*GIE_API_KEY' gridflow_drift_check.py` returns zero hits (secret-leak guard).
    - `python -c "import ast; ast.parse(open('C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py').read())"` exits 0 (the file parses).
    - The renamed file still imports `from gridflow.cli import _import_transformers` and `from gridflow.silver.registry import _REGISTRY` (the gridflow integration is preserved); confirmed by `grep -nE 'from gridflow\\.(cli|silver)' gridflow_drift_check.py | wc -l` >= 2.
    - `ruff check` and `ruff format --check` both exit 0.
  </acceptance_criteria>
  <done>
    Renamed verifier file lives at `quant-vault/30-vendors/scripts/gridflow_drift_check.py`; the two Windows blockers are parameterised via `shutil.which` / sibling-discovery; the original filename no longer exists; secret-leak guard passes; ruff is clean.
  </done>
</task>

<task type="auto">
  <name>Task 2: Expose `gridflow-drift-check` console script + declare `[drift]` extras in `gridflow-front-end/pyproject.toml`</name>
  <files>
    - pyproject.toml
  </files>
  <read_first>
    - pyproject.toml (FULL — only 26 lines; verify the `[project.scripts]` and `[project.optional-dependencies]` sections before editing)
    - .planning/phases/07-reconciliation/07-CONTEXT.md (Q-DD-16: lean to gridflow-front-end if no vault pyproject.toml — confirmed)
  </read_first>
  <action>
    Edit `pyproject.toml` to add two things, mirroring the existing `[build]` / `gridflow-build` patterns (Q-DD-16 default lean per 07-CONTEXT.md, confirmed by the planner via `Glob C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/pyproject.toml` returning no files on 2026-05-19).

    1. **Under `[project.optional-dependencies]`**, add a `drift` group after the existing `build` line:
       ```toml
       [project.optional-dependencies]
       # Build-time templating; not required for `gridflow-serve` runtime.
       build = ["Jinja2>=3.1,<4"]
       # Drift verification; consumes the renamed gridflow_drift_check.py script.
       # Pydantic is transitive via the editable gridflow install used by the script.
       drift = ["PyYAML>=6,<7"]
       ```
       Note: pydantic is NOT listed explicitly — the script gets it via the `sys.path.insert(0, str(GRIDFLOW / "src"))` editable-install hop into gridflow's own dependency tree. PyYAML IS direct (the script uses `import yaml` at L17 of the current file). Do not add `gridflow` itself as a wheel dependency — the script imports it via the sibling-repo `sys.path` insert; adding it as a pip dependency would conflict.

    2. **Under `[project.scripts]`**, add an entry after the existing `gridflow-build` line:
       ```toml
       [project.scripts]
       gridflow-serve = "gridflow_front_end.serve:main"
       gridflow-build = "gridflow_front_end.build:main"
       gridflow-drift-check = "gridflow_front_end.drift_check_entry:main"
       ```
       This requires a tiny shim module to exist at `src/gridflow_front_end/drift_check_entry.py` because the actual script lives in the sibling `quant-vault` repo and entry-points can only reference installed packages. Create that file with this content:
       ```python
       """Entry-point shim for `gridflow-drift-check`. Locates the verifier in a sibling quant-vault checkout and runs it."""
       from __future__ import annotations

       import os
       import runpy
       import sys
       from pathlib import Path


       def main() -> None:
           """Locate `gridflow_drift_check.py` in a sibling `quant-vault` checkout and execute its `main()`."""
           override = os.environ.get("GRIDFLOW_DRIFT_CHECK_SCRIPT")
           if override:
               script = Path(override)
           else:
               # Sibling discovery: this package lives in gridflow-front-end;
               # quant-vault is expected as a sibling directory.
               here = Path(__file__).resolve()
               candidates = [
                   here.parents[3] / "quant-vault" / "30-vendors" / "scripts" / "gridflow_drift_check.py",
                   Path.cwd() / "quant-vault" / "30-vendors" / "scripts" / "gridflow_drift_check.py",
                   # Author's Windows layout (Learning/AI/quant-vault sibling of Python/gridflow-front-end):
                   here.parents[4] / "Learning" / "AI" / "quant-vault" / "30-vendors" / "scripts" / "gridflow_drift_check.py",
               ]
               script = next((c for c in candidates if c.is_file()), candidates[0])
               if not script.is_file():
                   raise SystemExit(
                       "gridflow_drift_check.py not found. Set GRIDFLOW_DRIFT_CHECK_SCRIPT or "
                       "check out quant-vault as a sibling of gridflow-front-end. Tried: "
                       + ", ".join(str(c) for c in candidates)
                   )
           sys.argv[0] = str(script)
           runpy.run_path(str(script), run_name="__main__")
       ```
       This shim is the minimum needed for `[project.scripts]` to resolve and for 07-02 to invoke the wrapped verifier as a console command across both author-local and CI/Linux layouts.

    No other pyproject.toml changes — do not bump `version`, do not touch `[build-system]`, do not modify `dependencies = []`.

    Conventional Commit message: `feat(07-01): expose gridflow-drift-check console script with [drift] extras`
  </action>
  <verify>
    <automated>uv pip install -e ".[drift]" --quiet && gridflow-drift-check --help 2>&1 | head -5 && grep -nE 'gridflow-drift-check|\\[drift\\]|PyYAML' pyproject.toml</automated>
  </verify>
  <acceptance_criteria>
    - `grep -nE '^drift\\s*=\\s*\\[' pyproject.toml` returns exactly one hit referencing `PyYAML`.
    - `grep -nE '^gridflow-drift-check\\s*=' pyproject.toml` returns exactly one hit referencing `gridflow_front_end.drift_check_entry:main`.
    - `test -f src/gridflow_front_end/drift_check_entry.py` succeeds; the shim contains a `def main()` and references `GRIDFLOW_DRIFT_CHECK_SCRIPT`.
    - `uv pip install -e ".[drift]"` succeeds (exits 0). PyYAML installs.
    - `which gridflow-drift-check` (or `where gridflow-drift-check` on Windows) returns a path inside the active virtualenv.
    - `GRIDFLOW_DRIFT_CHECK_SCRIPT="C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py" gridflow-drift-check --help` exits 0 (the verifier may or may not implement `--help` itself; if it doesn't, then exit-0 is sufficient evidence that the shim resolved the script and Python parsed it — record actual behaviour in 07-01 SUMMARY).
    - `python -c "import ast; ast.parse(open('src/gridflow_front_end/drift_check_entry.py').read())"` exits 0.
  </acceptance_criteria>
  <done>
    `gridflow-drift-check` is installable via `uv pip install -e ".[drift]"` and resolves to a working entry point that locates the renamed verifier in a sibling `quant-vault` checkout (or via `GRIDFLOW_DRIFT_CHECK_SCRIPT`). RECON-01 success criterion 1 is satisfied.
  </done>
</task>

</tasks>

<threat_model>

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| `.env` file → verifier process | `ENTSOE_API_KEY` and `GIE_API_KEY` cross this boundary as plaintext env vars |
| Verifier process → stdout/log file | Verbose output may contain auth headers / curl commands with substituted keys |
| `pyproject.toml` `[project.scripts]` → user PATH | New console command installed by `uv pip install -e ".[drift]"` |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-07-01-01 | I (Information disclosure) | `gridflow_drift_check.py` verbose/debug log paths | mitigate | Acceptance grep in Task 1 enforces zero `print(...ENTSOE_API_KEY` / `logging.<level>(...ENTSOE_API_KEY` matches; same for `GIE_API_KEY`. Existing `_substitute_auth_placeholders` (around L160-173) already substitutes via `command.replace(placeholder, value)` which means the substituted curl command **does** contain the live key — confirm that command is never written to the JSON or markdown reports (it currently isn't; this is preservation of existing behaviour, not a new control). |
| T-07-01-02 | T (Tampering) | `GRIDFLOW_CURL_BIN` env var | accept | A user with shell access can already substitute `curl`; introducing the env var doesn't widen the attack surface beyond what the user already controls. No mitigation required. |
| T-07-01-03 | E (Elevation of privilege) | `runpy.run_path` in `drift_check_entry.py` | accept | `runpy` executes a Python file at a known sibling path. An attacker who can write to that sibling-checkout's `gridflow_drift_check.py` already has code-execution on the user's machine via easier paths. Documented in the shim's docstring. |
| T-07-01-04 | D (Denial of service) | `_discover_curl()` raises `RuntimeError` when no curl found | accept | Fail-loud is the desired behaviour — silent fallback to a stub curl would mask the bug. Error message names the env var to set. |

</threat_model>

<verification>

Plan-level acceptance — re-run after both tasks land:

```bash
# 1. Renamed file present, original gone:
test -f "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py"
test ! -f "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py"

# 2. Windows-only patterns gone (the helper's tuple `("curl", "curl.exe")` is allowed; bare assignment is not):
grep -nE 'args\\[0\\]\\s*=\\s*"curl\\.exe"' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py"
# Expect: no output

grep -nE 'C:\\\\Users\\\\Bobbo' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py"
# Expect: no output

# 3. Console script installs and resolves:
uv pip install -e ".[drift]"
gridflow-drift-check --help 2>&1 | head -3
# Expect: exit 0 (or a known verifier help output; record actual behaviour in SUMMARY)

# 4. pyproject.toml structural checks:
grep -nE '^gridflow-drift-check\\s*=' pyproject.toml | wc -l                  # expect: 1
grep -nE '^drift\\s*=\\s*\\[' pyproject.toml | wc -l                          # expect: 1
```

</verification>

<success_criteria>

RECON-01 from REQUIREMENTS.md is satisfied:
- `gridflow-drift-check` exists as a console script on PATH (renamed from `verify_curl_and_silver_schema.py` → `gridflow_drift_check.py`)
- Portable to Linux CI: no `curl.exe` baked in; no `C:\Users\Bobbo\...` baked in; both blockers are env-var/discovery-driven
- `[drift]` extras declared in `gridflow-front-end/pyproject.toml` (Q-DD-16 default lean — `quant-vault` has no `pyproject.toml`, confirmed by Glob 2026-05-19)

</success_criteria>

<output>
After both tasks complete, create `.planning/phases/07-reconciliation/07-01-SUMMARY.md` per the standard summary template. Capture:
- The final shape of `_discover_curl()` and the GRIDFLOW resolution block (paste them)
- Actual behaviour of `gridflow-drift-check --help` (does the underlying verifier accept `--help`?)
- Any secret-leak grep hits found and fixed
- Confirmation that the file parses and ruff is clean
- Conventional Commit hashes for the two commits
</output>
