#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""The viz diagram pipeline: .mmd -> .drawio -> .drawio.png. All three files stay.

    diagram.py lint   <name.mmd>       altitude + STE checks only
    diagram.py build  <name.mmd>       lint, convert to .drawio, export .drawio.png, open it
    diagram.py export <name.drawio>    re-export the PNG after a .drawio edit, open it
                                       (--no-open on both: do not open the PNG)
    diagram.py status [dir|file ...]   state of each diagram (default: docs/diagrams)

The .mmd header records the hash of the .drawio that `build` wrote:

    %% caption: Every payment ends in one cash report.
    %% drawio-sha: 3f2a...

If the .drawio no longer has that hash, a person (or the agent) edited it, so the
.drawio is the source of truth: `build` refuses (pass --force to throw the edits
away), and `export` marks the .mmd with a `%% STALE:` line.
"""

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

import ste_check

SHA_RE = re.compile(r"^%%\s*drawio-sha:\s*(\S+)\s*$", re.M)
CAP_RE = re.compile(r"^%%\s*caption:\s*(.+?)\s*$", re.M)
STALE_LINE = "%% STALE: the .drawio was edited by hand. The .drawio is the source of truth."

# ------------------------------------------------------------------ lint rules
# A diagram is the big picture in plain words. Code identifiers, multi-line
# labels and error-path edges mean it was drawn at implementation altitude --
# rewrite the label, do not rename past the regex.
IDENTIFIERS = [
    (r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+\b", "CamelCase class / component name"),
    (r"\b[a-z0-9]+_[a-z0-9_]+\b", "snake_case table / column / variable"),
    (r"::|\(\)|->|=>", "method call or operator"),
    (r"\.(?:php|jsx?|tsx?|py|go|rs|vue|xlsx?|csv|json|ya?ml|xml|sql|md|html?)\b", "file extension"),
    (r"\b(?:GET|POST|PUT|PATCH|DELETE)\s+\S|(?<![\w)])/[a-z0-9-]+/[a-z0-9-]+", "HTTP route"),
    (r"\b[1-5]\d\d\b", "HTTP status code"),
    (r"\b(?:mysql|sqlite|postgres|redis|sql|db|json|http|cdn|jwt|uuid|null|bool)\b", "plumbing term"),
]
ERROR_PATH = re.compile(
    r"(?i)\b(?:rollback|roll back|rolled back|exception|throws?|fails?|failure|error|"
    r"timeout|retry|retries|crash|abort|invalid|reject(?:ed)?)\b"
)
KEYWORDS = {"flowchart", "graph", "lr", "rl", "td", "tb", "bt", "subgraph", "end", "classdef",
            "class", "style", "linkstyle", "click", "direction", "default"}


def labels(src):
    """Every quoted label (node and edge) plus |pipe| edge labels."""
    return re.findall(r'"([^"]*)"', src) + re.findall(r"\|([^|\"]+)\|", src)


def count_nodes(body):
    """Approximate distinct node ids in a flowchart."""
    s = re.sub(r'"[^"]*"', "", body)
    s = re.sub(r"\|[^|]*\|", "", s)
    s = re.sub(r"\[[^\]]*\]|\{[^}]*\}|\([^)]*\)", " ", s)
    ids = set()
    for line in s.splitlines():
        if re.match(r"\s*(?:classDef|class|style|linkStyle|click)\b", line):
            continue
        ids |= {w for w in re.findall(r"\b[A-Za-z_][\w]*\b", line) if w.lower() not in KEYWORDS}
    return len(ids)


def lint(mmd):
    """Return (errors, warnings) for one .mmd file."""
    return lint_src(mmd.read_text(encoding="utf-8"))


def lint_src(src):
    """Return (errors, warnings) for .mmd text (validate_report.py lints inline graphs with it)."""
    errors, warnings = [], []
    body = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("%%"))
    first = next((l.strip().split()[0] for l in body.splitlines() if l.strip()), "")
    cap = CAP_RE.search(src)

    if not cap:
        errors.append("no '%% caption: <one line>' header. Cannot write the caption? Delete the diagram.")
    if re.search(r"(?i)<br\s*/?>", body):
        errors.append("a label uses <br/>: one line, five words or fewer.")
    if re.search(r"(?m)^\s*%%\{", src):
        warnings.append("an %%{init}%% block: draw.io sets the style, drop it.")

    if first in ("flowchart", "graph"):
        n = count_nodes(body)
        if n > 8:
            warnings.append(f"{n} nodes, over 8: that is a system, not a story. Split it or use a report component.")
        if n < 4:
            warnings.append(f"{n} nodes, under 4: a step rail or a list reads better than a graph.")
        if not re.search(r"(?m)^\s*\w+\s*\{|-->.*-->|-- \"|\|", body) and n <= 4:
            warnings.append("no branch, merge or cycle visible: does this diagram earn its place?")
        if re.search(r"(?im)^\s*subgraph\b", body):
            warnings.append("subgraph: layer boxes are plumbing, not story.")
        if "[(" in body:
            warnings.append("database cylinder: say what happens, not where it is stored.")

    for text in labels(body):
        text = text.strip()
        if not text:
            continue
        for pattern, why in IDENTIFIERS:
            if re.search(pattern, text):
                errors.append(f'label "{text}" contains a {why}. Draw at product altitude: actors, concepts, outcomes.')
                break
        if ERROR_PATH.search(text):
            errors.append(f'label "{text}" is an error path. Happy path only; put failures in the text beside the diagram.')
        if len(text.split()) > 5:
            warnings.append(f'label "{text}" has {len(text.split())} words (max 5).')

    # Full ASD-STE100 on every label and the caption. Each label is its own paragraph.
    approved = ste_check.load_approved()
    report = ste_check.Report()
    for text in labels(body) + ([cap.group(1)] if cap else []):
        if text.strip():
            ste_check.check_text(text.strip() + "\n", "descriptive", report, f'"{text.strip()}"', approved)
    errors += [f"STE {loc} [rule {rule}] {msg}" for loc, rule, msg in report.errors]
    warnings += [f"STE {loc} [rule {rule}] {msg}" for loc, rule, msg in report.warnings]
    if report.unknown:
        errors.append("STE words not approved: " + ", ".join(sorted(report.unknown))
                      + ". Replace them (references/substitutions.md), or add a technical name/verb to ./.ste-allow.txt.")
    return errors, warnings


# ------------------------------------------------------------------ pipeline

def drawio_bin():
    for c in (shutil.which("drawio"), "/Applications/draw.io.app/Contents/MacOS/draw.io"):
        if c and Path(c).exists():
            return c
    sys.exit("draw.io Desktop is not installed, so this step cannot make the .drawio or the PNG.\n"
             "The lint passed. Suggest to the user: brew install --cask drawio (see doctor.py).\n"
             "Without it: write the .drawio XML by hand (DIAGRAM.md), and the user exports the PNG in draw.io.")


def run(*args):
    r = subprocess.run([drawio_bin(), *args], capture_output=True, text=True)
    out = Path(args[args.index("-o") + 1])
    if r.returncode or not out.exists() or out.stat().st_size == 0:
        sys.exit(f"draw.io failed ({' '.join(args)}):\n{r.stdout}{r.stderr}")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def recorded_sha(mmd):
    m = SHA_RE.search(mmd.read_text(encoding="utf-8")) if mmd.exists() else None
    return m.group(1) if m else None


def set_header(mmd, digest):
    """Write the drawio-sha line and drop any STALE line."""
    lines = [l for l in mmd.read_text(encoding="utf-8").splitlines()
             if not SHA_RE.match(l) and not l.startswith("%% STALE:")]
    at = 1 if lines and CAP_RE.match(lines[0]) else 0
    lines.insert(at, f"%% drawio-sha: {digest}")
    mmd.write_text("\n".join(lines) + "\n", encoding="utf-8")


def paths(p):
    stem = p.name.removesuffix(".mmd").removesuffix(".drawio.png").removesuffix(".drawio")
    d = p.parent
    return d / f"{stem}.mmd", d / f"{stem}.drawio", d / f"{stem}.drawio.png"


def state(mmd, drawio, png):
    if not drawio.exists():
        return "new" if mmd.exists() else "missing"
    rec = recorded_sha(mmd)
    if not mmd.exists():
        s = "drawio-only"
    elif rec != sha(drawio):
        s = "hand-edited"
    else:
        s = "clean"
    if not png.exists() or png.stat().st_mtime < drawio.stat().st_mtime:
        s += " (png out of date)"
    return s


def open_file(path, a):
    """Open the PNG in the default viewer, unless --no-open."""
    if a.no_open:
        return
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    if shutil.which(opener):
        subprocess.run([opener, str(path)], check=False)


def print_lint(name, errors, warnings):
    for e in errors:
        print(f"ERROR   {name}: {e}")
    for w in warnings:
        print(f"WARN    {name}: {w}")


def cmd_lint(a):
    mmd, _, _ = paths(Path(a.file))
    errors, warnings = lint(mmd)
    print_lint(mmd.name, errors, warnings)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


def cmd_build(a):
    mmd, drawio, png = paths(Path(a.file))
    if not mmd.exists():
        sys.exit(f"not found: {mmd}")
    if drawio.exists() and recorded_sha(mmd) != sha(drawio) and not a.force:
        print(f"REFUSED {drawio.name} was edited after the last build, so it is the source of truth.\n"
              f"        Edit {drawio.name} and run: diagram.py export {drawio}\n"
              f"        Or pass --force to rebuild from the .mmd and LOSE those edits.")
        return 2
    errors, warnings = lint(mmd)
    print_lint(mmd.name, errors, warnings)
    if errors and not a.no_lint:
        print(f"{len(errors)} error(s): fix the .mmd, then build again.")
        return 1
    run("-x", "-f", "xml", "-o", str(drawio), str(mmd))
    set_header(mmd, sha(drawio))
    run("-x", "-f", "png", "-e", "-s", str(a.scale), "-b", "10", "-o", str(png), str(drawio))
    print(f"built  {mmd}\n       {drawio}\n       {png.resolve()}")
    open_file(png, a)
    return 0


def cmd_export(a):
    mmd, drawio, png = paths(Path(a.file))
    if not drawio.exists():
        sys.exit(f"not found: {drawio}")
    run("-x", "-f", "png", "-e", "-s", str(a.scale), "-b", "10", "-o", str(png), str(drawio))
    if mmd.exists() and recorded_sha(mmd) != sha(drawio):
        text = mmd.read_text(encoding="utf-8")
        if STALE_LINE not in text:
            mmd.write_text(STALE_LINE + "\n" + text, encoding="utf-8")
        print(f"marked {mmd.name} STALE (the .drawio is the source of truth)")
    print(f"exported {png.resolve()}")
    open_file(png, a)
    return 0


def cmd_status(a):
    targets = [Path(t) for t in a.paths] or [Path("docs/diagrams")]
    stems = set()
    for t in targets:
        files = [t] if t.is_file() else [*t.rglob("*.mmd"), *t.rglob("*.drawio")]
        stems |= {paths(f)[0] for f in files}
    for mmd in sorted(stems):
        print(f"{state(*paths(mmd)):<34} {mmd.with_suffix('')}")
    if not stems:
        print(f"no diagrams in {' '.join(map(str, targets))}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lint"); p.add_argument("file"); p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("build"); p.add_argument("file"); p.set_defaults(fn=cmd_build)
    p.add_argument("--force", action="store_true", help="rebuild even if the .drawio was edited (loses the edits)")
    p.add_argument("--no-lint", action="store_true", help="build even with lint errors")
    p.add_argument("--scale", type=float, default=2, help="PNG scale (default 2, sharp in PRs)")
    p.add_argument("--no-open", action="store_true", help="do not open the PNG after the build")
    p = sub.add_parser("export"); p.add_argument("file"); p.set_defaults(fn=cmd_export)
    p.add_argument("--scale", type=float, default=2)
    p.add_argument("--no-open", action="store_true", help="do not open the PNG after the export")
    p = sub.add_parser("status"); p.add_argument("paths", nargs="*"); p.set_defaults(fn=cmd_status)
    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
