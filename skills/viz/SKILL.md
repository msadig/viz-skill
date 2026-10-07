---
name: viz
description: Makes diagrams and plan reports that a non-developer can read. Diagram mode writes a Mermaid .mmd, converts it to an editable .drawio, and exports a .drawio.png for PRs and docs, keeping all three files. Report mode turns a spec/plan markdown into a light/dark HTML page built from zero-JS components, a cascade build order, and at most one diagram (its .drawio.png). Report prose obeys ASD-STE100 Simplified Technical English; diagram labels use it as a guide. Use when the user says "viz", "/viz", "visualize", "diagram this", "draw the flow", "make a .drawio", "PNG for the PR", "visualize the plan", "plan report", or asks for an .mmd → .drawio → .png diagram.
---

# viz

Two modes. Both use one set of rules for pictures and one set of rules for words.

| Mode | Input | Output |
|---|---|---|
| `/viz diagram <topic> [what to draw]` | a description, code, or a doc | `docs/diagrams/<topic>/<name>.mmd` + `.drawio` + `.drawio.png` |
| `/viz report [spec/plan path or topic]` | `docs/specs/*.md` + `docs/plans/*.md` | `docs/reports/<date>-<topic>.html` |

No mode given? A request for one picture → diagram. A spec/plan → report.

`<skill>` below means the directory of this SKILL.md (for Claude Code with a global install: `~/.claude/skills/viz`). The scripts are uv scripts, so run them directly. Run them from the project root, because they read `./.ste-allow.txt` and use `docs/diagrams` as the default directory.

## Folders

The defaults are `docs/diagrams/`, `docs/reports/`, `docs/specs/` and `docs/plans/`. Other folders override these defaults. The order is:
1. The folders in the user's request ("put it in design/").
2. The folders that the project's `CLAUDE.md` or `AGENTS.md` names for viz, for example: `viz: diagrams in design/diagrams, reports in design/reports, specs in rfcs/`.
3. The defaults above.

If the user wants different folders for all the work in a project, tell the user to add a line like the example in step 2 to `CLAUDE.md` or `AGENTS.md`. Every path in this skill shows the defaults. Use the resolved folders in their place. For `diagram.py status`, give the folder as an argument.

## Before you start

The first time you use viz in a session, run `python3 <skill>/scripts/doctor.py`. It checks 3 optional tools: uv, draw.io Desktop and the drawio skill. It never fails. For each `SUGGEST` line, tell the user 1 time what to install and why, then continue. Do not stop the task.

- No uv: run each script as `python3 <skill>/scripts/<name>.py`.
- No draw.io Desktop: `build` stops after the lint. Write the `.drawio` XML by hand (DIAGRAM.md), and tell the user to export the PNG in draw.io.
- No drawio skill: hand edits of `.drawio` XML get no XML reference. Be careful with the XML.

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
3. Build the one big-picture diagram (if one earns its place) in diagram mode, then embed its `.drawio.png`. Use an inline `<pre class="mmd">` graph only for a small flowchart with no colours and no groups.
4. Run `scripts/build_report.py <fragment> <out.html>`, then `scripts/validate_report.py <out.html>`.
5. Open the page.

## Picture rules (both modes)

A diagram must be useful, not only short. Show the real flow.

- **Colour by role.** Every graph of 6 or more nodes uses the `classDef` palette in [DIAGRAM.md](DIAGRAM.md#colour-palette): actor, step, decision, store, external system, good outcome, warning, failure. Add a legend line to the caption when the colours are not clear.
- **Group with `subgraph`.** Put the nodes of 1 system, team or phase in 1 subgraph.
- **Show the failure paths.** Draw the main path with solid edges, and the error, retry and rollback paths with dotted edges (`-. "label" .->`) to `warn` or `bad` nodes.
- **Altitude: the reader decides.** For a non-developer, use plain names (the lint warns on code identifiers). For developers, real service, queue and table names are correct.
- **Size.** Up to about 30 nodes. A label line has 8 words or fewer. Use `<br/>` for a 2nd line with detail (for example "Record payment<br/>in the ledger").
- **Earn its place.** A straight chain of 3 steps is a list, not a graph.
- **Caption is required.** The first line of the `.mmd` is `%% caption: <what the reader must take from it>`.
- Report mode: **1 diagram per report**. A 2nd needs a separate flow and a stated reason. The report shows the diagram as its PNG (REPORT.md).

## Word rules: full ASD-STE100

**Talk to the user in STE while this skill is active.** This includes your questions, status lines and the final summary. Use short sentences, the active voice, and can/must/will only. Do not use "-ing" verbs. If the user asks for a different style, the user's request wins.

Report prose obeys Simplified Technical English. Code, identifiers, paths and quoted text are exempt. Core rules: [STE.md](STE.md). `validate_report.py` runs `ste_check` in strict mode. A word that is not approved is an error.

**Diagram labels and captions: STE is a guide, not a gate.** `diagram.py` shows STE findings as warnings and does not stop the build. Use the clearest word for the reader, for example "payment", "invoice", "team". Keep labels short and plain. Change a word only when a simpler word is as clear.

To fix a report error, use this order:
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
| `scripts/doctor.py` | checks the optional tools, suggests installs (plain python3) |
| `scripts/diagram.py` | lint / build / export / status |
| `scripts/build_report.py`, `scripts/validate_report.py` | report splice (copies `.mmd` text in) and checks |
| `scripts/ste_check.py` | STE checker (`--strict`, `--allow FILE`) |
| `references/` | component catalog, body skeleton, STE rules, word list, substitutions, technical words |
| `assets/` | `template.html` (never read it; holds the kit CSS and the `.mmd` graph script), `components-demo.html` (every component, both themes; rebuild it from `demo-body.html`) |
