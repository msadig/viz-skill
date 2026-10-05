#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Splice a body fragment into assets/template.html and write the report.

    build_report.py <fragment.html> <out.html> [--title T] [--no-suffix]

You author ONLY the fragment: the <section> markup between the template's
<main> tags. Tokens, kit CSS, theme toggle and lightbox come from the template
and never enter the conversation. The page <title> comes from the fragment's
first <h1>. Validate the OUTPUT afterwards (validate_report.py), never the
fragment: a bare fragment has no <style>, so the CSS checks would misfire.
"""

import argparse
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("body")
    ap.add_argument("out")
    ap.add_argument("--title")
    ap.add_argument("--no-suffix", action="store_true", help="replace the whole <title>, no '— Plan Report'")
    ap.add_argument("--template", default=TEMPLATE)
    a = ap.parse_args()

    shell = Path(a.template).read_text(encoding="utf-8")
    fragment = Path(a.body).read_text(encoding="utf-8").strip()
    if not fragment:
        sys.exit(f"body fragment is empty: {a.body}")

    # comments often TALK about these tags; scan a comment-free copy.
    # the trailing [\s>/] keeps the legal <header> from matching <head
    scan = re.sub(r"(?s)<!--.*?-->", "", fragment)
    for tag in ("html", "head", "body", "main"):
        if re.search(rf"(?i)</?{tag}[\s>/]", scan):
            sys.exit(f"the fragment contains a <{tag}> tag. Write <section> markup only; the shell comes from the template.")

    start, end = shell.find("<main>"), shell.rfind("</main>")
    if start < 0 or end <= start:
        sys.exit(f"template has no <main> ... </main> region: {a.template}")
    head, tail = shell[: start + 6], shell[end:]

    title = a.title
    if not title:
        m = re.search(r"(?s)<h1[^>]*>(.*?)</h1>", scan)
        if not m:
            sys.exit("no <h1> in the fragment and no --title given.")
        title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
    if a.no_suffix or "{{PLAN TITLE}}" not in head:
        head = re.sub(r"(?s)<title>.*?</title>", lambda _: f"<title>{title}</title>", head)
    else:
        head = head.replace("{{PLAN TITLE}}", title)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    report = f"{head}\n{fragment}\n{tail}"
    out.write_text(report, encoding="utf-8")

    print(f"built {out.name}\n  title  : {title}\n  body   : {len(fragment)} chars authored"
          f"\n  report : {len(report)} chars -> {out.resolve()}")
    left = re.findall(r"\{\{.+?\}\}", report)
    if left:
        print(f"\n  {len(left)} unfilled placeholder(s): validate_report.py will fail on these.")


if __name__ == "__main__":
    main()
