# Report mode

Turns a spec/plan markdown pair into one self-contained HTML page (light/dark, offline, zero JS in the content). Readers see the scope in 10 seconds.

## 1. Find the source docs

In this order:
1. **Session context**: the spec/plan that this conversation wrote or discussed.
2. **Argument**: a path → use it. A topic → glob `docs/superpowers/specs/*<arg>*.md` and `docs/superpowers/plans/*<arg>*.md`, and take the newest match.
3. **Nothing found**: list the 10 newest files in specs/ and plans/ and ask the user which one.

**Pair rule:** a spec and its plan share a `YYYY-MM-DD-<topic>` stem (the plan can drop `-design`). If there is no exact partner, glob the other folder by the topic words and take the newest match that fits. Read BOTH files. The spec gives the intent, scope and architecture. The plan gives the tasks, the order and the files that change. A spec alone is fine. Tell the user that there is no plan.

## 2. Write the body, build the page

**You write the body fragment only.** Copy `references/body-skeleton.html` to the scratchpad and fill it.

- The fragment is `<section>` markup only: no `<html>`, `<head>`, `<body>` or `<main>`.
- **Do not read `assets/template.html`.** It holds about 25k characters of tokens, CSS and scripts. The build script adds them.
- The page title comes from the fragment's `<h1>`: the plan's H1, else the spec's H1. Remove boilerplate such as "Implementation Plan".
- Use colours only through the tokens (`var(--accent)` and others). Never hardcode a hex value.
- Pick components from `references/components.json`. Its `select` index maps the *shape of the material* to a component. Copy the component's `example_lines`. Nothing fits? Build a custom component from `references/custom-components.md`. Never draw a diagram only because no component matched.

```bash
<skill>/scripts/build_report.py <scratchpad>/report-body.html docs/superpowers/reports/<date>-<topic>.html
<skill>/scripts/validate_report.py docs/superpowers/reports/<date>-<topic>.html
```

**The output stem** is the plan's stem, else the spec stem without `-design`. The date comes from the stem, not from today.

## 3. Pick the visual

A diagram that only repeats a list wastes the reader's first 10 seconds. Use the lightest visual that shows the shape.

- The reader's problem is never "not enough boxes".
- **Components first**: `.rail` (stages), `.stack` (tiers), `.swim` (actor × stage), `.tiles` (counts), `.matrix` (risk), `.timeline`, `.chips` (2 or 3 order facts), `.compare`, `.status-table`, `.callout`. There is no limit on components.
- **At most 1 diagram**: the big-picture one. It shows who starts the feature, what it becomes, and where it lands. Build it in diagram mode, in `docs/diagrams/<topic>/`. Then put it in the architecture section:
  ```html
  <div class="card diagram">
    <img src="../../diagrams/<topic>/<name>.drawio.png" alt="<caption>">
    <p class="cap"><caption></p>
  </div>
  ```
- A 2nd diagram needs a separate flow that branches. Say why in the summary, and validate with `--diagram-budget 2`. Zero diagrams is a good report.
- A numbered task order is **not** a dependency graph. Draw an order as a graph only when the plan says that tasks fan out or join.

## 4. Sections

All sections are optional. **Delete a section that has no source material. Never invent content and never leave an empty section.** A short, dense report is better than a report that only looks complete.

| Section | Source | Typical visual |
|---|---|---|
| Header | title, doc date, relative links to the source MDs that exist | — |
| Summary / scope | goal + in-scope / out-of-scope lists | scope grid, `.tiles` |
| Architecture and flow | only if the spec describes one | `.stack`, `.swim`, `.rail`, or the 1 diagram |
| Phase / task breakdown | 1 card per phase. Add a "Done means" line only when the plan states a criterion | `.phase` cards, `.waterfall` |
| Order and dependencies | only when the plan states real blockers | `.chips`, `.rail` |
| Risks / open questions | stated risks, unknowns, open decisions | `.matrix`, `.callout` |
| File-touch map | files by layer (Backend, Frontend, Migrations, Tests, Docs, Infra), only the layers that occur | `.layer-grid`, `.bars` |

**Identifiers have a home.** File names, classes and routes go in `<code>` in the breakdown cards and the file-touch map. They never go in the diagram. `<code>` content is exempt from STE.

**Images in the source MDs:** keep them in their section. Rewrite `src` relative to `docs/superpowers/reports/`. Put consecutive images in 1 `<div class="gallery">`. The lightbox does the zoom.

## 5. STE in the report

All prose in the report obeys full ASD-STE100 ([STE.md](STE.md)): paragraphs, list items, captions, tiles, callouts. Headings, `<code>`, `<pre>` and the footer are exempt. The validator runs strict STE on the prose. Write in STE from the start, because a rewrite after the validator runs costs more.

The source spec is often not in STE. Do not copy its sentences. Rewrite each one.

## 6. Validate and open

- Validate the **built page**, never the fragment.
- An ERROR fails the run. Fix the fragment, build again, and validate again. Do not report around an error.
- The validator checks: hardcoded colours, colour in inline styles, scripts or handlers in `<main>`, external assets, `<pre class="mermaid">`, diagram count over budget, diagram PNG not found, diagram card without `.cap`, unfilled `{{placeholders}}`, classes without CSS, and STE errors in the prose.
- Open the page with `open <abs path>` (macOS) or `xdg-open` (Linux). If the open fails, give the path.
- Give the absolute path in a fenced code block AND as a markdown link. Then say in STE which sections you built, which you skipped and why, and the diagram count.
- Do not commit the report unless the user asks.

## Bad input

A doc that is malformed or very large: build the header, the summary and the breakdown from the parts that you can read. Put a short note above the footer that lists the parts you omitted.
