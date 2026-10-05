# viz

An agent skill that makes diagrams and plan reports that a non-developer can read.

- **Diagram mode** writes a Mermaid `.mmd`, converts it to an editable `.drawio`, and exports a `.drawio.png`. All 3 files stay:
  - the `.mmd` is for agents,
  - the `.drawio` is for you (drag and drop in draw.io),
  - the `.drawio.png` is for PRs, docs and chat.
- **Report mode** turns a spec/plan markdown into 1 HTML page (light and dark themes, offline, zero JS in the content) with at most 1 draw.io diagram.
- **All words obey ASD-STE100** Simplified Technical English. This includes labels, captions, report text and the agent's messages to you.

## Install

Use [skills.sh](https://skills.sh). This is the preferred method:

```bash
npx skills add msadig/viz-skill -g -a claude-code
```

- `-g` installs for all your projects. Remove it to install into the current project only.
- `-a` selects the agent. Remove it to select agents from a list.
- The repo is private. `skills` uses your Git credentials, the GitHub CLI (`gh auth login`), or SSH.

Update: `npx skills update`. Remove: `npx skills remove viz`.

## Requirements

| Tool | For | Install |
|---|---|---|
| [uv](https://docs.astral.sh/uv/) | runs the scripts (Python 3.11+, no packages) | `brew install uv` |
| [draw.io Desktop](https://www.drawio.com/) | `.mmd` → `.drawio` → `.png` | `brew install --cask drawio` |

## Use

```
/viz diagram payments  draw how a payment gets matched to an invoice
/viz report docs/superpowers/specs/2026-09-19-my-feature-design.md
```

Diagrams go to `docs/diagrams/<topic>/`. The skill opens the PNG after it builds it. Say "do not open" to stop this.

If you edit a `.drawio` by hand, the `.drawio` becomes the source of truth. The skill will not rebuild over your edits. It edits the `.drawio` and marks the `.mmd` as `STALE`.

## Layout

```
skills/viz/
  SKILL.md       entry point
  DIAGRAM.md     diagram workflow
  REPORT.md      report workflow
  STE.md         the STE rules
  scripts/       diagram.py, build_report.py, validate_report.py, ste_check.py
  references/    component catalog, body skeleton, STE rules and word list
  assets/        report template, component demo page
```

## Credits

- Report kit: from the `ezi-visualize-plan` skill. The PowerShell scripts were rewritten in Python, and draw.io diagrams replace Mermaid.
- STE rules and checker: [0xpili/simplified-technical-english](https://github.com/0xpili/simplified-technical-english) (MIT). The word list comes from the ASD-STE100 dictionary, which is the property of ASD. See `skills/viz/references/STE-NOTICE.md`.
