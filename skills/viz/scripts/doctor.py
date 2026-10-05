#!/usr/bin/env python3
"""Check the optional tools for viz and suggest what to install. Never fails.

    python3 <skill>/scripts/doctor.py

Plain python3 on purpose: this script must run when uv is not installed.
Every check is a suggestion. viz works without each tool, with less help.
"""

import shutil
import sys
from pathlib import Path

HOME = Path.home()


def drawio_cli():
    for c in (shutil.which("drawio"), "/Applications/draw.io.app/Contents/MacOS/draw.io"):
        if c and Path(c).exists():
            return c
    return None


def drawio_skill():
    roots = [HOME / ".claude/skills", HOME / ".agents/skills", HOME / ".config/agents/skills",
             Path(".claude/skills"), Path(".agents/skills")]
    hits = [r / "drawio/SKILL.md" for r in roots if (r / "drawio/SKILL.md").exists()]
    plugins = HOME / ".claude/plugins/cache"
    if plugins.exists():
        hits += list(plugins.glob("*/drawio/*/skills/drawio/SKILL.md"))
    return hits[0] if hits else None


def main():
    mac = sys.platform == "darwin"
    checks = [
        ("uv", shutil.which("uv"),
         ("brew install uv" if mac else "curl -LsSf https://astral.sh/uv/install.sh | sh"),
         "Without uv, run each script as: python3 <skill>/scripts/<name>.py"),
        ("draw.io Desktop (CLI)", drawio_cli(),
         ("brew install --cask drawio" if mac else "https://github.com/jgraph/drawio-desktop/releases"),
         "Without it there is no Mermaid conversion and no PNG. The agent can write .drawio XML by hand,"
         " and you export the PNG in draw.io (File > Export as > PNG, with 'Include a copy of my diagram')."),
        ("drawio skill", drawio_skill(),
         "npx skills add jgraph/drawio-mcp -g",
         "Gives the agent the draw.io XML reference for hand edits and special shapes (AWS, network)."),
    ]
    print(f"viz doctor (python {sys.version.split()[0]})\n")
    missing = 0
    for name, found, install, why in checks:
        if found:
            print(f"OK       {name}: {found}")
        else:
            missing += 1
            print(f"SUGGEST  {name} is not installed. For a better result, install it:\n"
                  f"         {install}\n         {why}")
    print("\nAll optional tools are installed." if not missing
          else f"\n{missing} suggestion(s). viz still works. Tell the user each suggestion 1 time, then continue.")


if __name__ == "__main__":
    main()
