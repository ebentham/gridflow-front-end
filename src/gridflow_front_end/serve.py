"""gridflow-serve — one-command local server for the Gridflow static site.

Usage:
    gridflow-serve              # port 8765, opens browser automatically
    gridflow-serve --port 9000  # custom port
    gridflow-serve --no-open    # skip browser launch
"""
from __future__ import annotations

import argparse
import http.server
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path


# Root of the static site relative to this package, resolved at import time.
_PACKAGE_DIR = Path(__file__).parent
_PROJECT_ROOT = _PACKAGE_DIR.parent.parent  # src/gridflow_front_end -> src -> project root
_SITE_DIR = _PROJECT_ROOT / "site" / "hifi"


class _SilentHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler that suppresses per-request log lines."""

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        # Silence the default "GET /index.html 200 -" noise.
        pass

    def log_error(self, format: str, *args: object) -> None:  # noqa: A002
        # Still surface real errors.
        sys.stderr.write(f"[gridflow-serve] ERROR: {format % args}\n")


def _open_browser(url: str, delay: float = 0.5) -> None:
    """Open *url* in the default browser after a short delay.

    The delay gives the server socket time to bind before the browser hits it.
    """
    def _go() -> None:
        time.sleep(delay)
        webbrowser.open(url)

    t = threading.Thread(target=_go, daemon=True)
    t.start()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="gridflow-serve",
        description="Serve the Gridflow static site locally.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="TCP port to listen on (default: 8765)",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        default=False,
        help="Do not open a browser tab automatically",
    )
    args = parser.parse_args()

    if not _SITE_DIR.is_dir():
        sys.exit(
            f"[gridflow-serve] Site directory not found: {_SITE_DIR}\n"
            "Run the project setup or copy the hifi files into site/hifi/ first."
        )

    # SimpleHTTPRequestHandler serves relative to the process cwd.
    os.chdir(_SITE_DIR)

    url = f"http://localhost:{args.port}/"
    handler = _SilentHandler

    try:
        server = http.server.HTTPServer(("", args.port), handler)
    except OSError as exc:
        sys.exit(
            f"[gridflow-serve] Could not bind to port {args.port}: {exc}\n"
            f"Try a different port with --port <number>."
        )

    print(f"Gridflow  ·  serving on {url}")
    print("Press Ctrl+C to stop.\n")

    if not args.no_open:
        _open_browser(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[gridflow-serve] Stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
