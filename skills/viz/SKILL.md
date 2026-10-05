---
name: viz
description: Makes diagrams and plan reports that a non-developer can read. Diagram mode writes a Mermaid .mmd, converts it to an editable .drawio, and exports a .drawio.png for PRs and docs, keeping all three files. Report mode turns a spec/plan markdown into a light/dark HTML page built from zero-JS components with at most one draw.io diagram. All labels, captions and prose obey ASD-STE100 Simplified Technical English. Use when the user says "viz", "/viz", "visualize", "diagram this", "draw the flow", "make a .drawio", "PNG for the PR", "visualize the plan", "plan report", or asks for an .mmd → .drawio → .png diagram.
---

# viz

Two modes. Both use one set of rules for pictures and one set of rules for words.

| Mode | Input | Output |
|---|---|---|
| `/viz diagram <topic> [what to draw]` | a description, code, or a doc | `docs/diagrams/<topic>/<name>.mmd` + `.drawio` + `.drawio.png` |
| `/viz report [spec/plan path or topic]` | `docs/superpowers/specs\|plans/*.md` | `docs/superpowers/reports/<date>-<topic>.html` |

No mode given? A request for one picture → diagram. A spec/plan → report.

`<skill>` below means the directory of this SKILL.md (for Claude Code with a global install: `~/.claude/skills/viz`). The scripts are uv scripts, so run them directly. Run them from the project root, because they read `./.ste-allow.txt` and use `docs/diagrams` as the default directory.

## Diagram mode: quick start

```bash
mkdir -p docs/diagrams/payments
# write docs/diagrams/payments/match-flow.mmd (first line: %% caption: ...)
<skill>/scripts/diagram.py status docs/diagrams/payments   # ALWAYS first
<skill>/scripts/diagram.py build  docs/diagrams/payments/match-flow.mmd
```

`build` lints the .mmd (altitude and STE), converts it to `.drawio`, exports `.drawio.png` at 2x with the XML embedded, records the `.drawio` hash in the `.mmd`, and **opens the PNG**. All three files stay. Add `--no-open` only when the user says not to open it.

**The `.drawio` wins after a hand edit.** If `status` says `hand-edited`, never rebuild from the `.mmd` (`build` refuses this). Edit the `.drawio` XML in place, then run `diagram.py export <name>.drawio`. That re-exports the PNG and marks the `.mmd` `STALE`. Full workflow: [DIAGRAM.md](DIAGRAM.md).

## Report mode: quick start

Read [REPORT.md](REPORT.md) before you build a report. In short:
1. Read the spec AND the plan.
2. Write a body fragment from `references/body-skeleton.html`. Use components from `references/components.json`.
3. Build the one big-picture diagram (if one earns its place) in diagram mode, then embed its PNG.
4. Run `scripts/build_report.py <fragment> <out.html>`, then `scripts/validate_report.py <out.html>`.
5. Open the page.

## Picture rules (both modes)

- **Product altitude.** Nodes are actors, concepts and outcomes that a non-developer can read. Never use class, file, route, table or function names. Put identifiers in the text or the report's file-touch map.
- **Earn its place.** Draw a graph only when it has a branch, merge, cycle or cross-cutting edge, AND 4 or more nodes. A straight chain is a list or a `.rail`.
- **8 nodes or fewer. Labels of 5 words or fewer, on one line.** Do not use `<br/>`.
- **Happy path only.** Put error, retry and rollback paths in the text beside the diagram.
- **Caption is required.** The first line of the `.mmd` is `%% caption: <what the reader must take from it>`. If you cannot write the caption, delete the diagram.
- Report mode: **1 diagram per report**. A 2nd needs a separate branching flow and a stated reason.

## Word rules: full ASD-STE100

**Talk to the user in STE while this skill is active.** This includes your questions, status lines and the final summary. Use short sentences, the active voice, and can/must/will only. Do not use "-ing" verbs. If the user asks for a different style, the user's request wins.

All labels, captions and report prose obey Simplified Technical English. Code, identifiers, paths and quoted text are exempt. Core rules: [STE.md](STE.md). `diagram.py` and `validate_report.py` run `ste_check` in strict mode. A word that is not approved is an error. Fix it in this order:
1. Use an approved word (`references/substitutions.md`).
2. If the word is a real technical name or technical verb of the project, add it to `./.ste-allow.txt` (one word per line). The shared list is `references/technical-words.txt`.

Never put a word in the allowlist only to get past a rule. "Should", "-ing" verbs and long sentences are rule errors, not vocabulary problems.

Check free text (PR body, doc section): `scripts/ste_check.py --strict --mode descriptive <file>`.

## Finish

Write this message in STE. Give the user the absolute path(s) in a fenced block and as a markdown link. Say what was built, what was skipped and why, and the diagram count. Do not commit unless the user asks.

## Files

| Path | What |
|---|---|
| [DIAGRAM.md](DIAGRAM.md) | Diagram workflow, .mmd format, edit loop, draw.io gotchas |
| [REPORT.md](REPORT.md) | Report workflow, sections, components, validation |
| [STE.md](STE.md) | ASD-STE100 rules to obey while you write |
| `scripts/diagram.py` | lint / build / export / status |
| `scripts/build_report.py`, `scripts/validate_report.py` | report splice and checks |
| `scripts/ste_check.py` | STE checker (`--strict`, `--allow FILE`) |
| `references/` | component catalog, body skeleton, STE rules, word list, substitutions, technical words |
| `assets/` | `template.html` (never read it), `components-demo.html` (every component, both themes) |
