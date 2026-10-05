# Diagram mode

One picture, three files, one folder:

```
docs/diagrams/<topic>/
  <name>.mmd          for agents: the text you write and diff
  <name>.drawio       for the user: drag, drop, restyle in draw.io
  <name>.drawio.png   for people: PRs, docs, chat (the drawio XML is embedded)
```

`<topic>` and `<name>` are kebab-case. One topic folder can hold many diagrams.

## Workflow

1. **Status first.** If the topic folder exists, run `scripts/diagram.py status docs/diagrams/<topic>`.
   - `clean`: the `.mmd` is the source of truth. Edit the `.mmd`.
   - `hand-edited`: the `.drawio` is the source of truth. Go to [Edit a hand-edited diagram](#edit-a-hand-edited-diagram).
   - `drawio-only`: there is no `.mmd`. Treat it as hand-edited.
   - `(png out of date)`: run `export`.
2. **Decide if a graph earns its place** (SKILL.md picture rules). If it does not, tell the user and suggest a list or table. Do not draw it.
3. **Write the `.mmd`.** Header first, then the diagram:
   ```
   %% caption: Each payment ends in 1 cash report.
   flowchart LR
     A["Cashier records sale"] --> B{"Payment matches invoice?"}
     B -- "yes" --> C["Invoice closes"]
     B -- "no" --> D["Person examines payment"]
     D --> C
     C --> E["Cash report"]
   ```
   - Put every label in double quotes. Do not put raw `<`, `>` or `&` in a label.
   - Use `flowchart LR` for flows and `flowchart TD` for hierarchies. Sequence, state, ER, timeline and the other Mermaid types also convert.
   - Do not add `%%{init}%%` or colour `classDef`. draw.io styles the diagram, and the user restyles it there.
   - Match the label language to the user's language. In English, obey STE.
4. **Build:** `scripts/diagram.py build docs/diagrams/<topic>/<name>.mmd`
   - It runs `lint` first. Fix every ERROR in the `.mmd`. Do not use `--no-lint` to get past the lint. An altitude error means you must rewrite the label in plain words. Do not rename the label only to get past the regex.
   - Read each WARN and decide. An under-4-nodes warning usually means you must delete the graph.
5. **Look at the PNG** (Read the file) before you report it. `build` and `export` also open it for the user. Pass `--no-open` only when the user says not to open it. Bad layout? Change the direction (`LR` ↔ `TD`) or the node order, then build again.
6. **Report** the three paths and the caption. Write the report in STE.

## Edit a hand-edited diagram

The user moved, restyled or added things in draw.io. Those edits live only in the `.drawio`, and a rebuild from the `.mmd` deletes them. So:

1. Read the `.drawio`. It is uncompressed mxGraph XML. Each node is a `UserObject` (with `label=`) or an `mxCell` (with `value=`) that contains an `mxGeometry`.
2. Make the change with exact string edits on the XML:
   - Rename a node: change its `label`/`value`.
   - Add a node: copy a sibling cell, give it a new unique `id`, and move its `mxGeometry` x/y.
   - Add an edge: `<mxCell id="e-new" edge="1" parent="1" source="<id>" target="<id>" style="edgeStyle=orthogonalEdgeStyle;"><mxGeometry relative="1" as="geometry"/></mxCell>`. The child `mxGeometry` is required.
   - Never add XML comments. Escape `&amp; &lt; &gt; &quot;` in attributes.
3. Run `scripts/diagram.py export docs/diagrams/<topic>/<name>.drawio`. It re-exports the PNG and marks the `.mmd` `STALE`.
4. Leave the `STALE` `.mmd` in place. It is history, not truth. Rebuild from it only when the user says to discard the draw.io edits (`build --force`).

The picture rules and STE apply to hand edits too. `lint` reads only `.mmd` files, so check your new labels yourself.

## Commands

| Command | Does |
|---|---|
| `diagram.py status [dir\|file ...]` | `new`, `clean`, `hand-edited`, `drawio-only`, `(png out of date)` for each diagram. Default dir: `docs/diagrams`. |
| `diagram.py lint <name.mmd>` | Altitude and STE checks only. |
| `diagram.py build <name.mmd> [--scale 2] [--force] [--no-open]` | lint → `.drawio` → `.drawio.png`, records the hash, opens the PNG. Exit 2 = refused, the `.drawio` was edited. |
| `diagram.py export <name.drawio> [--scale 2] [--no-open]` | `.drawio` → `.drawio.png`, opens the PNG. Marks the `.mmd` STALE if the hashes differ. |

## draw.io notes

- The scripts need draw.io Desktop (`brew install --cask drawio`). They find `drawio` on PATH or in `/Applications/draw.io.app`.
- Mermaid → PNG in one step is broken in draw.io Desktop. The script always goes `.mmd` → `.drawio` → PNG.
- The PNG has a white background in every theme, because people paste it into GitHub, docs and chat.
- The user can open the `.drawio.png` itself in draw.io, because the XML is embedded. The `.drawio` is still the file to edit.
- Need AWS, Azure or network shapes, or exact positions? Mermaid cannot do that. Write the `.drawio` XML directly (`/drawio:drawio` has the XML reference), skip the `.mmd`, and run `export`. `status` then shows `drawio-only`. That is correct.
