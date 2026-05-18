"""gridflow-build — render dataset pages from Obsidian Vault markdown.

Reads vault `.md` files under `<vault>/elexon/*.md`, parses YAML frontmatter
and the structured sections (Overview, API endpoint, Silver layer, Known
issues, etc.), and renders one HTML file per dataset using Jinja2 templates
under `templates/`. Also rebuilds the vendor hub (`site/hifi/data-sources/elexon.html`)
from the manifest at `site/hifi/data/elexon.json`.

Build inputs (single source of truth):
- vault/<vendor>/<slug>.md       — authored content (frontmatter + sections)
- site/hifi/data/<vendor>.json   — structural manifest (id/title/freq/lag/rows)

Build outputs (gitignored, regenerated on every run):
- site/hifi/data-sources/<vendor>/<slug>.html
- site/hifi/data-sources/<vendor>.html

The deployed artefact stays pure static HTML/CSS/JS — Jinja2 is a build-time
dependency only (declared in pyproject.toml's [build] extras).

Usage
-----
    gridflow-build                                  # build everything
    gridflow-build --vault-path /path/to/vault      # override vault location
    gridflow-build --check                          # build twice; non-zero on drift

Vault path resolution order:
    1. --vault-path CLI flag
    2. $GRIDFLOW_VAULT_PATH env var
    3. <repo>/vault/ (vendored fallback)
"""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from html import escape as html_escape
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "templates"
SITE_DIR = REPO_ROOT / "site" / "hifi"
DEFAULT_VAULT = REPO_ROOT / "vault"


# ──────────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────────


@dataclass
class SchemaRow:
    name: str
    pk: bool
    type: str
    nullable: bool
    note: str


@dataclass
class Caveat:
    title: str
    text: str


@dataclass
class DatasetDoc:
    slug: str
    vendor_id: str  # "elexon"
    vendor_label: str  # "Elexon BMRS"
    last_verified: str  # "2026-05-08"
    title_line: str  # H1 of the vault doc
    api_code: str  # e.g. "FUELHH"
    overview_paragraphs: list[str] = field(default_factory=list)
    base_url: str = ""
    api_path: str = ""
    auth_note: str = ""
    silver_path: str = ""
    transformer_class: str = ""
    pydantic_schema: str = ""
    dedup_key: str = ""
    point_in_time_field: str = ""
    pydantic_schema_wired: bool = False
    schema_rows: list[SchemaRow] = field(default_factory=list)
    sample_columns: list[str] = field(default_factory=list)
    sample_rows: list[list[str]] = field(default_factory=list)
    sample_language: str = "json"
    sample_raw: str = ""
    caveats: list[Caveat] = field(default_factory=list)
    bronze_path: str = ""

    @property
    def vendor_doc_url(self) -> str:
        """Link to the canonical Elexon BMRS endpoint reference."""
        return f"https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/{self.api_code}"

    @property
    def silver_dir(self) -> str:
        """Directory glob root for the silver layer (drops trailing partition spec)."""
        if not self.silver_path:
            return f"data/silver/elexon/{self.slug}"
        # Truncate at the first `<` or `=` partition marker, or at the filename basename
        head = re.split(r"/[^/]*[=<]", self.silver_path)[0]
        return head.rstrip("/")

    @property
    def first_pk_column(self) -> str:
        """First PK column (for the DuckDB date-filter example)."""
        for row in self.schema_rows:
            if row.pk:
                return row.name
        return "settlement_date"


# ──────────────────────────────────────────────────────────────────────
# Vault parsing
# ──────────────────────────────────────────────────────────────────────


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_text = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    frontmatter: dict[str, str] = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            frontmatter[k.strip()] = v.strip()
    return frontmatter, body


_HEADING_RE = re.compile(r"^(#+)\s+(.*?)\s*$", re.MULTILINE)


def _split_sections(body: str) -> dict[str, str]:
    """Split a markdown body into sections keyed by lowercased heading text.

    Recognises any `## Heading` line. Sections include nested `### subheads`
    in their content. Returns ordered dict (insertion order = source order).
    """
    sections: dict[str, str] = {}
    matches = list(re.finditer(r"^##\s+(?P<title>.*?)\s*$", body, re.MULTILINE))
    for i, m in enumerate(matches):
        key = m.group("title").strip().lower()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[key] = body[start:end].strip()
    return sections


def _strip_link(text: str) -> str:
    """Strip markdown links '[a](b)' → 'a'."""
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)


def _markdown_inline(text: str) -> str:
    """Render a minimal markdown subset: backticks → <code>, **bold**, *italic*."""
    text = html_escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def _parse_overview(section: str) -> list[str]:
    """Split overview body into paragraphs; strip 'Link to relevant domain...' note."""
    text = section.strip()
    # Drop the "→ Link to relevant domain..." auto-inserted block (and its bullets)
    text = re.sub(
        r"→ Link to relevant domain concept notes.*?(?=\n\n|\Z)",
        "",
        text,
        flags=re.DOTALL,
    )
    paragraphs = []
    for p in re.split(r"\n\s*\n", text):
        p = p.strip()
        # Drop empty paragraphs and lone markdown horizontal rules
        if not p or re.fullmatch(r"-{3,}", p):
            continue
        paragraphs.append(p)
    return paragraphs


def _strip_title_backticks(line: str) -> str:
    """Strip backticks but keep ALLCAPS dataset code visible: 'X (`FOO`)' → 'X (FOO)'."""
    return line.replace("`", "")


def _parse_markdown_table(text: str) -> list[list[str]] | None:
    """Parse a single markdown table; return rows including header. None if not a table."""
    lines = [ln for ln in text.strip().splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return None
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
    # Detect alignment row (---|---|...) and drop it
    if len(rows) >= 2 and all(re.match(r"^:?-+:?$", c) for c in rows[1]):
        rows.pop(1)
    return rows


def _extract_api_table(section: str) -> dict[str, str]:
    """Parse the API endpoint key/value table from the 'API endpoint' section."""
    rows = _parse_markdown_table(section)
    if not rows:
        return {}
    out: dict[str, str] = {}
    for row in rows[1:]:
        if len(row) < 2:
            continue
        key = row[0].lower()
        value = row[1]
        out[key] = value
    return out


def _extract_silver_metadata(section: str) -> dict[str, str]:
    """Parse the bold key/value pairs at the top of the Silver layer section.

    Values may be backtick-quoted with an optional trailing note (e.g.
    `` `ingested_at` (no native PIT field) ``). Extract the first backtick value
    when present; otherwise return the raw value with surrounding backticks stripped.
    """
    meta: dict[str, str] = {}
    for line in section.splitlines():
        m = re.match(r"\*\*(?P<key>[^*]+)\*\*\s*:\s*(?P<val>.*?)\s*$", line)
        if not m:
            continue
        key = m.group("key").strip().lower()
        val = m.group("val").strip()
        # Prefer the first backtick-bounded value if present (the canonical code value)
        code_match = re.match(r"`([^`]+)`", val)
        if code_match:
            meta[key] = code_match.group(1)
        else:
            meta[key] = val.strip("`")
    return meta


def _parse_pk_columns(dedup_key: str) -> set[str]:
    """Extract PK column names from a dedup-key string like '(a, b, c)' or 'a, b'."""
    cleaned = dedup_key.strip().strip("()").strip()
    if not cleaned:
        return set()
    return {c.strip().strip("`") for c in cleaned.split(",") if c.strip()}


def _extract_silver_schema_rows(section: str, pk_columns: set[str]) -> list[SchemaRow]:
    """Parse the silver schema table under '### Silver schema'."""
    sub_match = re.search(r"###\s+Silver schema\s*\n(.*?)(?=\n###\s|\n##\s|\Z)", section, re.DOTALL)
    if not sub_match:
        return []
    table = _parse_markdown_table(sub_match.group(1))
    if not table or len(table) < 2:
        return []
    header = [c.lower() for c in table[0]]
    name_i = header.index("field") if "field" in header else 0
    type_i = header.index("python type") if "python type" in header else 1
    nullable_i = header.index("nullable") if "nullable" in header else 2
    rows: list[SchemaRow] = []
    for r in table[1:]:
        if len(r) < 3:
            continue
        raw_name = r[name_i].strip("`").strip()
        is_pk = raw_name in pk_columns
        nullable_raw = r[nullable_i].strip()
        nullable = nullable_raw.lower() in {"yes", "true"}
        notes = ""
        if len(r) >= 5:
            notes = r[4].strip()
        elif len(r) == 4:
            notes = r[3].strip()
        type_str = r[type_i].strip("`").strip()
        if "pk" in notes.lower() or "primary key" in notes.lower():
            is_pk = True
        rows.append(
            SchemaRow(
                name=raw_name,
                pk=is_pk,
                type=type_str,
                nullable=nullable,
                note=notes,
            )
        )
    return rows


def _extract_silver_sample(section: str) -> tuple[list[str], list[list[str]], str, str]:
    """Parse silver sample. Returns (columns, rows, language, raw_block).

    Vault format varies: sometimes a Python list of dicts, sometimes JSON, sometimes
    a markdown table. We render it as code-block sample (raw) on the page; columns/rows
    are used by the data-table when a structured form can be derived.
    """
    sub_match = re.search(r"###\s+Silver sample\s*\n(.*?)(?=\n###\s|\n##\s|\Z)", section, re.DOTALL)
    if not sub_match:
        return [], [], "json", ""
    sub_text = sub_match.group(1)
    # Find first fenced code block
    fence = re.search(r"```(\w*)\n(.*?)```", sub_text, re.DOTALL)
    if fence:
        lang = fence.group(1) or "json"
        raw = fence.group(2).strip()
        # Try to extract list[dict] into a structured table
        rows_struct, cols_struct = _try_parse_listdict(raw)
        return cols_struct, rows_struct, lang, raw
    # Else try a markdown table
    table = _parse_markdown_table(sub_text)
    if table:
        return table[0], table[1:], "table", ""
    return [], [], "json", sub_text.strip()


def _try_parse_listdict(raw: str) -> tuple[list[list[str]], list[str]]:
    """Best-effort: parse a python-list-of-dicts literal into rows+columns."""
    try:
        # Python dicts allow trailing commas and unquoted keys sometimes —
        # safer to do a coarse parse
        s = raw.strip()
        if not s.startswith("["):
            return [], []
        # Replace Python None/True/False with JSON nulls/bools
        s_json = s.replace("'", '"').replace("True", "true").replace("False", "false").replace("None", "null")
        # Drop trailing commas before ] or }
        s_json = re.sub(r",(\s*[\]}])", r"\1", s_json)
        data = json.loads(s_json)
    except (ValueError, json.JSONDecodeError):
        return [], []
    if not isinstance(data, list) or not data:
        return [], []
    if not isinstance(data[0], dict):
        return [], []
    columns = list(data[0].keys())
    rows = [[str(d.get(c, "")) for c in columns] for d in data]
    return rows, columns


def _extract_caveats(section: str) -> list[Caveat]:
    """Parse 'Known issues and gotchas' bullet list into numbered caveats.

    The vault format is a bulleted list with `- **Title** — body` or
    `- **Title**: body` shapes.
    """
    caveats: list[Caveat] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        content = stripped[1:].strip()
        m = re.match(r"\*\*(?P<title>[^*]+)\*\*\s*[—:\-–]\s*(?P<body>.*)$", content)
        if m:
            caveats.append(Caveat(title=m.group("title").strip(), text=m.group("body").strip()))
        else:
            # Fallback: take the first sentence as title
            title = content.split(".", 1)[0]
            body = content[len(title):].lstrip(". ").strip()
            caveats.append(Caveat(title=title, text=body))
    return caveats


def _extract_api_code_from_title(title_line: str, slug: str) -> str:
    """Extract '(FUELHH)' style code from the title line."""
    m = re.search(r"\(`?([A-Z][A-Z0-9_\-/]+)`?\)", title_line)
    if m:
        return m.group(1).replace("-", "_").replace("/", "_")
    return slug.upper()


def parse_vault_file(path: Path, vendor_id: str = "elexon", vendor_label: str = "Elexon BMRS") -> DatasetDoc:
    text = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)
    slug = fm.get("dataset_key", path.stem)
    # First H1 is the title; strip backticks so HTML escaping doesn't lose semantics
    h1_match = re.search(r"^#\s+(.*?)\s*$", body, re.MULTILINE)
    raw_title = h1_match.group(1).strip() if h1_match else slug
    # Strip leading "Elexon - " or "Vendor - " prefix; the vendor breadcrumb already shows it
    title_line = re.sub(r"^(Elexon|ENTSO-E|ENTSO-G|GIE|NESO|Open-Meteo)\s*-\s*", "", raw_title)
    title_line = _strip_title_backticks(title_line)
    api_code = _extract_api_code_from_title(title_line, slug)

    sections = _split_sections(body)
    overview = _parse_overview(sections.get("overview", ""))
    api_meta = _extract_api_table(sections.get("api endpoint", ""))
    silver_section = sections.get("silver layer", "")
    silver_meta = _extract_silver_metadata(silver_section)
    dedup_key_raw = silver_meta.get("dedup key", "").strip("`")
    pk_cols = _parse_pk_columns(dedup_key_raw)
    schema_rows = _extract_silver_schema_rows(silver_section, pk_cols)
    sample_cols, sample_rows, sample_lang, sample_raw = _extract_silver_sample(silver_section)
    caveats = _extract_caveats(sections.get("known issues and gotchas", ""))
    bronze_section = sections.get("bronze layer", "")
    bronze_meta = _extract_silver_metadata(bronze_section)  # same key/value shape

    # Detect whether the pydantic schema is wired: must look like a dotted module path
    raw_schema = silver_meta.get("pydantic schema", "").strip("`")
    pydantic_wired = bool(re.match(r"^[\w]+(\.[\w]+)+$", raw_schema))

    return DatasetDoc(
        slug=slug,
        vendor_id=vendor_id,
        vendor_label=vendor_label,
        last_verified=fm.get("last_verified", ""),
        title_line=title_line,
        api_code=api_code,
        overview_paragraphs=overview,
        base_url=api_meta.get("base url", "").strip("`"),
        api_path=api_meta.get("path", "").strip("`"),
        auth_note=api_meta.get("auth", ""),
        silver_path=silver_meta.get("path pattern", "").strip("`"),
        transformer_class=silver_meta.get("transformer class", "").strip("`"),
        pydantic_schema=raw_schema if pydantic_wired else "",
        pydantic_schema_wired=pydantic_wired,
        dedup_key=silver_meta.get("dedup key", "").strip("`"),
        point_in_time_field=silver_meta.get("point-in-time field", "").strip("`"),
        schema_rows=schema_rows,
        sample_columns=sample_cols,
        sample_rows=sample_rows,
        sample_language=sample_lang,
        sample_raw=sample_raw,
        caveats=caveats,
        bronze_path=bronze_meta.get("path pattern", "").strip("`"),
    )


# ──────────────────────────────────────────────────────────────────────
# Manifest loading
# ──────────────────────────────────────────────────────────────────────


def load_manifest(vendor_id: str = "elexon") -> dict:
    path = SITE_DIR / "data" / f"{vendor_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_index(manifest: dict) -> dict[str, dict]:
    """Map slug → manifest entry (with group injected)."""
    index = {}
    for group in manifest["groups"]:
        for ds in group["datasets"]:
            entry = dict(ds)
            entry["group"] = group["name"]
            entry["group_blurb"] = group["blurb"]
            index[ds["id"]] = entry
    return index


def manifest_siblings(manifest: dict, slug: str) -> list[dict]:
    """Return sibling dataset entries in the same group as slug (incl. slug itself)."""
    for group in manifest["groups"]:
        ids = [d["id"] for d in group["datasets"]]
        if slug in ids:
            return list(group["datasets"])
    return []


def manifest_total_count(manifest: dict) -> int:
    return sum(len(g["datasets"]) for g in manifest["groups"])


# ──────────────────────────────────────────────────────────────────────
# Rendering
# ──────────────────────────────────────────────────────────────────────


def make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=False,
        lstrip_blocks=False,
        keep_trailing_newline=True,
    )
    env.filters["md_inline"] = _markdown_inline
    return env


def render_dataset(env: Environment, doc: DatasetDoc, manifest: dict) -> str:
    template = env.get_template("dataset.html.j2")
    siblings = manifest_siblings(manifest, doc.slug)
    manifest_entry = manifest_index(manifest).get(doc.slug, {})
    return template.render(
        doc=doc,
        manifest=manifest_entry,
        siblings=siblings,
        all_groups=manifest["groups"],
        manifest_total=manifest_total_count(manifest),
    )


def render_vendor_hub(env: Environment, manifest: dict, vendor_id: str, vendor_label: str) -> str:
    template = env.get_template("vendor-hub.html.j2")
    return template.render(
        vendor_id=vendor_id,
        vendor_label=vendor_label,
        manifest=manifest,
        manifest_total=manifest_total_count(manifest),
    )


# ──────────────────────────────────────────────────────────────────────
# Driver
# ──────────────────────────────────────────────────────────────────────


def resolve_vault_path(cli_arg: str | None) -> Path:
    if cli_arg:
        return Path(cli_arg).expanduser().resolve()
    env_path = os.environ.get("GRIDFLOW_VAULT_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return DEFAULT_VAULT


def build(vault_path: Path, output_dir: Path | None = None) -> tuple[int, int]:
    """Render all elexon dataset pages + the vendor hub. Returns (n_pages, n_hubs)."""
    env = make_env()
    elexon_dir = vault_path / "elexon"
    if not elexon_dir.is_dir():
        sys.exit(
            f"[gridflow-build] ERROR: vault directory not found: {elexon_dir}\n"
            f"  Set --vault-path or $GRIDFLOW_VAULT_PATH, or vendor vault content into "
            f"{DEFAULT_VAULT.relative_to(REPO_ROOT)}/."
        )
    out_root = output_dir or SITE_DIR
    out_dataset_dir = out_root / "data-sources" / "elexon"
    out_dataset_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest("elexon")
    manifest_slugs = {d["id"] for g in manifest["groups"] for d in g["datasets"]}

    vault_files = sorted(elexon_dir.glob("*.md"))
    vault_slugs = {p.stem for p in vault_files}

    missing_in_vault = manifest_slugs - vault_slugs
    missing_in_manifest = vault_slugs - manifest_slugs
    if missing_in_vault:
        sys.exit(
            f"[gridflow-build] ERROR: manifest declares datasets without vault files: {sorted(missing_in_vault)}"
        )
    # Datasets present in the vault but not in the manifest are tolerated (out-of-scope datasets).

    n_pages = 0
    for path in vault_files:
        slug = path.stem
        if slug not in manifest_slugs:
            print(f"  skip (not in manifest): {slug}")
            continue
        doc = parse_vault_file(path)
        html = render_dataset(env, doc, manifest)
        out_path = out_dataset_dir / f"{slug}.html"
        out_path.write_text(html, encoding="utf-8")
        n_pages += 1
        print(f"  wrote: data-sources/elexon/{slug}.html")

    hub_html = render_vendor_hub(env, manifest, "elexon", "Elexon BMRS")
    hub_path = out_root / "data-sources" / "elexon.html"
    hub_path.write_text(hub_html, encoding="utf-8")
    print(f"  wrote: data-sources/elexon.html")
    return n_pages, 1


def _snapshot_outputs(temp_dir: Path) -> None:
    """Copy current generated outputs into temp_dir for diff comparison."""
    src = SITE_DIR / "data-sources"
    dst = temp_dir / "data-sources"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for path in src.rglob("*.html"):
        rel = path.relative_to(src)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, out)


def _diff_outputs(temp_dir: Path) -> list[str]:
    """Compare the snapshot in temp_dir against current outputs. Return list of differing paths."""
    src = SITE_DIR / "data-sources"
    snap = temp_dir / "data-sources"
    differing: list[str] = []
    for path in src.rglob("*.html"):
        rel = path.relative_to(src)
        snap_path = snap / rel
        if not snap_path.exists():
            differing.append(str(rel))
            continue
        if not filecmp.cmp(str(path), str(snap_path), shallow=False):
            differing.append(str(rel))
    return differing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gridflow-build", description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--vault-path",
        default=None,
        help="Path to the Obsidian vault root (containing elexon/). "
        "Defaults to $GRIDFLOW_VAULT_PATH, then the vendored ./vault/ directory.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Build twice and exit non-zero if any output changes between builds (idempotence check).",
    )
    args = parser.parse_args(argv)

    vault_path = resolve_vault_path(args.vault_path)
    print(f"[gridflow-build] vault: {vault_path}")

    n_pages, n_hubs = build(vault_path)
    print(f"[gridflow-build] wrote {n_pages} dataset pages + {n_hubs} vendor hub")

    if args.check:
        with tempfile.TemporaryDirectory(prefix="gridflow-build-check-") as tmp:
            tmp_path = Path(tmp)
            _snapshot_outputs(tmp_path)
            n_pages2, _ = build(vault_path)
            differing = _diff_outputs(tmp_path)
            if differing:
                print(
                    f"[gridflow-build] FAIL: {len(differing)} file(s) differ between builds (non-idempotent):"
                )
                for p in differing:
                    print(f"    {p}")
                return 1
            print(f"[gridflow-build] OK: idempotent across {n_pages} pages.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
