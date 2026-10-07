# Report mode

Turns a spec/plan markdown pair into one self-contained HTML page (light/dark, offline, zero JS in the content). Readers see the scope in 10 seconds.

## 1. Find the source docs

In this order:
1. **Session context**: the spec/plan that this conversation wrote or discussed.
2. **Argument**: a path → use it. A topic → glob `docs/specs/*<arg>*.md` and `docs/plans/*<arg>*.md` (or the folders from SKILL.md "Folders"), and take the newest match. No match? Glob `docs/**/*<arg>*.md`.
3. **Nothing found**: list the 10 newest markdown files in the spec and plan folders and ask the user which one.

**Pair rule:** a spec and its plan share a `YYYY-MM-DD-<topic>` stem (the plan can drop `-design`). If there is no exact partner, glob the other folder by the topic words and take the newest match that fits. Read BOTH files. The spec gives the intent, scope and architecture. The plan gives the tasks, the order and the files that change. A spec alone is fine. Tell the user that there is no plan. Then the spec's own build order, phases and verify steps are the source for the breakdown and the "Complete when" lines. Remove the plan link from the header.

## 2. Write the body, build the page

**You write the body fragment only.** Copy `references/body-skeleton.html` to the scratchpad and fill it.

- The fragment is `<section>` markup only: no `<html>`, `<head>`, `<body>` or `<main>`.
- **Do not read `assets/template.html`.** It holds about 25k characters of tokens, CSS and scripts. The build script adds them.
- The page title comes from the fragment's `<h1>`: the plan's H1, else the spec's H1. Remove boilerplate such as "Implementation Plan".
- Use colours only through the tokens (`var(--accent)` and others). Never hardcode a hex value.
- Pick components from `references/components.json`. Its `select` index maps the *shape of the material* to a component. Copy the component's `example_lines`. Nothing fits? Build a custom component from `references/custom-components.md`. Never draw a diagram only because no component matched.

```bash
<skill>/scripts/build_report.py <scratchpad>/report-body.html docs/reports/<date>-<topic>.html
<skill>/scripts/validate_report.py docs/reports/<date>-<topic>.html
```

**The output stem** is the plan's stem, else the spec stem without `-design`. The date comes from the stem, not from today.

The page title gets the suffix "— Plan Report". For a page that is not a plan report, pass `--title "<title>" --no-suffix`.

## 3. Pick the visual

A diagram that only repeats a list wastes the reader's first 10 seconds. Use the lightest visual that shows the shape.

- The reader's problem is never "not enough boxes".
- **Components first**: `.rail` (stages), `.stack` (tiers), `.swim` (actor × stage), `.tiles` (counts), `.matrix` (risk), `.timeline`, `.chips` (2 or 3 order facts), `.compare`, `.status-table`, `.callout`. There is no limit on components.
- **At most 1 diagram**: the big-picture one. It shows who starts the feature, what it becomes, and where it lands. Build it in diagram mode, in `docs/diagrams/<topic>/`, with its colours and groups. Then put its PNG in the architecture section:
  ```html
  <div class="card diagram">
    <img src="../diagrams/<topic>/<name>.drawio.png" alt="<caption>">
    <p class="cap"><caption></p>
  </div>
  ```
  The PNG keeps the colours, the groups and the draw.io layout. An inline graph (`<pre class="mmd" data-src="../diagrams/<topic>/<name>.mmd"></pre>`) draws in the page colours and follows the light or dark theme, but it ignores `classDef` colours and subgraphs and it is good only for about 12 nodes. Use it only for a small flowchart with no colours and no groups. The validator lints an inline `.mmd` (altitude and STE), warns when it has colours or groups, and counts it in the budget.
- All links and `src` paths are relative to the report file. With the default folders, a diagram is `../diagrams/...` and a spec is `../specs/...`. With other folders, calculate the relative path. The validator stops when a diagram PNG is not found.
- A 2nd diagram needs a separate flow that branches. Say why in the summary, and validate with `--diagram-budget 2`. Zero diagrams is a good report.
- **Build order = cascade (`.waterfall`), always.** It shows what waits for what, and what can run in parallel:
  - A step 1 column to the right waits for the step above it. An arrow joins them. Go down 1 level at a time.
  - Set `style="--levels:N"` on the `.waterfall`, with N = the deepest `--d` + 1. The validator stops when a step does not fit.
  - Steps in 1 `.wf-par` row can run at the same time. Use a `.wf-par` row only when the source says so ("together", "in parallel", "independent"), or when the plan gives the same single blocker for 2 tasks. Never guess parallel work. If the source says nothing, use 1 step per level.
  - Status: `.good` = complete, `.warn` = started or blocked, no class = not started. Add the `.legend` from the skeleton when you use status.
  - Use `.rail` or `.chips` only for a flow that is not a build order (for example, the stages of a data flow).
- A numbered task order is **not** a dependency graph. Draw an order as a graph only when the plan says that tasks fan out or join.

## 4. Sections

All sections are optional. **Delete a section that has no source material. Never invent content and never leave an empty section.** A short, dense report is better than a report that only looks complete.

| Section | Source | Typical visual |
|---|---|---|
| Header | title, doc date, relative links to the source MDs that exist | — |
| Summary / scope | goal + in-scope / out-of-scope lists | scope grid, `.tiles` |
| Architecture and flow | only if the spec describes one | `.stack`, `.swim`, `.rail`, or the 1 diagram |
| Phase / task breakdown | 1 card per phase. Add a "Complete when" line only when the source states a criterion | `.phase` cards, `.waterfall` |
| Build order | the plan's task order, or the spec's phases / build order | `.waterfall` (the default, see below) |
| Risks / open questions | stated risks, unknowns, open decisions | `.matrix`, `.callout` |
| File-touch map | files by layer (Backend, Frontend, Migrations, Tests, Docs, Infra), only the layers that occur | `.layer-grid`, `.bars` |

**Counts** in `.tiles` must come from the source. You can count items that the source lists (for example, phases 0 to 6 = 7 phases). Do not estimate.

**Identifiers have a home.** File names, classes and routes go in `<code>` in the breakdown cards and the file-touch map. They never go in the diagram. `<code>` content is exempt from STE.

**Images in the source MDs:** keep them in their section. Rewrite `src` relative to the report folder. Put consecutive images in 1 `<div class="gallery">`. The lightbox does the zoom.

## 5. STE in the report

All prose in the report obeys full ASD-STE100 ([STE.md](STE.md)): paragraphs, list items, table cells, captions, tiles, callouts. Headings, table headers (`<th>`), callout labels (the first `<b>`), `<code>`, `<pre>` and the footer are exempt.

A capitalized word inside a sentence counts as a name (Tailscale, Private Relay), so product names pass. Use the official capitals. The validator runs strict STE on the prose. Write in STE from the start, because a rewrite after the validator runs costs more.

The source spec is often not in STE. Do not copy its sentences. Rewrite each one.

## 6. Validate and open

- Validate the **built page**, never the fragment.
- An ERROR fails the run. Fix the fragment, build again, and validate again. Do not report around an error.
- The validator checks: hardcoded colours, colour in inline styles, scripts or handlers in `<main>`, external assets, `<pre class="mermaid">`, diagram count over budget (PNGs and inline `.mmd` graphs), diagram PNG not found, the lint of inline `.mmd` graphs, a `.waterfall` with too few `--levels`, diagram card without `.cap`, unfilled `{{placeholders}}`, classes without CSS, and STE errors in the prose.
- Open the page with `open <abs path>` (macOS) or `xdg-open` (Linux). If the open fails, give the path.
- Give the absolute path in a fenced code block AND as a markdown link. Then say in STE which sections you built, which you skipped and why, and the diagram count.
- Do not commit the report unless the user asks.

## Bad input

A doc that is malformed or very large: build the header, the summary and the breakdown from the parts that you can read. Put a short note above the footer that lists the parts you omitted.
