#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Mechanical checks on a BUILT report (never on a bare fragment).

    validate_report.py <report.html> [--diagram-budget N]

Catches what is invisible in a light-theme browser: hardcoded colours, scripts
in <main>, external assets, the diagram budget, missing diagram PNGs, missing
captions, unfilled {{placeholders}}, classes with no CSS, and ASD-STE100 errors
in the report prose. Exit 1 on any ERROR; warnings never fail the run.

A CSS line that must keep a literal colour is exempt with the marker
`validator-ok` in a comment on the same line.
"""

import argparse
import html as htmllib
import re
import sys
from pathlib import Path

import ste_check

COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--diagram-budget", type=int, default=1)
    a = ap.parse_args()

    path = Path(a.path)
    page = path.read_text(encoding="utf-8")
    errors, warnings = [], []

    style = "\n".join(re.findall(r"(?s)<style>(.*?)</style>", page))
    if not style:
        warnings.append("no <style> block: is this a built report?")

    # 1. colours: literal colours are legal only inside the :root token blocks
    for line in re.sub(r"(?s):root[^{]*\{.*?\}", "", style).splitlines():
        if "validator-ok" not in line and COLOUR.search(line):
            errors.append(f"hardcoded colour outside the :root tokens (one theme breaks): {line.strip()}")
    for decl in re.findall(r'style="([^"]*)"', page):
        if COLOUR.search(decl) or re.search(r"\bcolor\s*:", decl):
            errors.append(f"colour in an inline style, use a token class: {decl}")

    # 2. zero JS inside <main>
    s, e = page.find("<main>"), page.rfind("</main>")
    main_html = page[s + 6 : e] if 0 <= s < e else page
    if re.search(r"(?i)<script", main_html):
        errors.append("a <script> inside <main>: components must work with zero JS.")
    for m in re.findall(r"(?i)\son(?:click|load|mouseover|change|input|submit)=", main_html):
        errors.append(f"inline event handler in <main> ({m.strip()}).")

    # 3. offline: no external assets
    for url in re.findall(r'(?i)(?:src|href)="(https?://[^"]+)"', page):
        errors.append(f"external asset, the report must open offline: {url}")
    for m in re.findall(r"(?i)@import|url\(\s*['\"]?https?://", style):
        errors.append(f"remote CSS asset ({m}).")

    # 4. diagrams: draw.io PNGs only, on budget, file present
    if re.search(r'<pre class="mermaid"', main_html):
        errors.append('<pre class="mermaid"> found: build the diagram with diagram.py and embed its .drawio.png.')
    pngs = re.findall(r'<img[^>]+src="([^"]+\.drawio\.png)"', main_html)
    if len(pngs) > a.diagram_budget:
        errors.append(f"{len(pngs)} diagrams, budget is {a.diagram_budget}. Convert the rest to a rail, swimlane or stack;"
                      " pass --diagram-budget 2 only for a separate branching flow, and say why.")
    for src in pngs:
        if not (path.parent / src).exists():
            errors.append(f"diagram image not found (relative to the report): {src}")

    # 5. every diagram card has a caption
    for m in re.finditer(r'class="card diagram"', main_html):
        rest = main_html[m.end():]
        stops = [i for i in (rest.find('class="card'), rest.find("</section>")) if i > 0]
        chunk = rest[: min(stops)] if stops else rest
        if 'class="cap"' not in chunk:
            head = re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", chunk)).strip()[:80]
            warnings.append(f'a .card.diagram has no <p class="cap"> line: {head}')

    # 6. unfilled placeholders (whole page: {{PLAN TITLE}} lives in <head>)
    left = sorted(set(re.findall(r"\{\{.+?\}\}", page)))
    if left:
        errors.append(f"{len(left)} unfilled placeholder(s): {' '.join(left[:6])}")

    # 7. classes with no CSS behind them
    defined = set(re.findall(r"\.([a-zA-Z][\w-]*)", style))
    used = {c for m in re.findall(r'class="([^"]+)"', main_html) for c in m.split()}
    unknown = sorted(used - defined)
    if unknown:
        warnings.append("classes with no CSS (typo, or custom CSS not added): " + ", ".join(unknown))

    # 8. full ASD-STE100 on the prose. Code, headings and footers are not controlled text.
    prose = re.sub(r"(?is)<(style|code|pre|h[1-6]|footer)\b.*?</\1>|<!--.*?-->", " ", main_html)
    prose = re.sub(r"(?i)</?(?:a|b|strong|em|i|abbr)\b[^>]*>", " ", prose)
    blocks = [htmllib.unescape(re.sub(r"\s+", " ", b)).strip() for b in re.split(r"<[^>]+>", prose)]
    approved = ste_check.load_approved()
    report = ste_check.Report()
    for b in blocks:
        if re.search(r"[A-Za-z]{2}", b):
            ste_check.check_text(b + "\n", "descriptive", report, f'"{b[:50]}"', approved)
    errors += [f"STE {loc} [rule {rule}] {msg}" for loc, rule, msg in report.errors]
    warnings += [f"STE {loc} [rule {rule}] {msg}" for loc, rule, msg in report.warnings]
    if report.unknown:
        errors.append("STE words not approved: " + ", ".join(sorted(report.unknown))
                      + ". Replace them (references/substitutions.md), or add technical names/verbs to ./.ste-allow.txt.")

    print(f"checked {path.name}: {len(pngs)} diagram(s), {len(used)} distinct classes\n")
    for x in errors:
        print(f"ERROR   {x}")
    for x in warnings:
        print(f"WARN    {x}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
