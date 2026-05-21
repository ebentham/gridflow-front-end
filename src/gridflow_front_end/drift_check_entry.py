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
            here.parents[4]
            / "Learning"
            / "AI"
            / "quant-vault"
            / "30-vendors"
            / "scripts"
            / "gridflow_drift_check.py",
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
