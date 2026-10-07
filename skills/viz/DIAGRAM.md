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

1. **Status first.** Always run `<skill>/scripts/diagram.py status docs/diagrams/<topic>`. `no diagrams in ...` means a new topic.
   - `clean`: the `.mmd` is the source of truth. Edit the `.mmd`.
   - `hand-edited`: the `.drawio` is the source of truth. Go to [Edit a hand-edited diagram](#edit-a-hand-edited-diagram).
   - `drawio-only`: there is no `.mmd`. Treat it as hand-edited.
   - `(png out of date)`: run `export`.
2. **Decide if a graph earns its place** (SKILL.md picture rules). If it does not, tell the user and suggest a list or table. Do not draw it.
3. **Write the `.mmd`.** Header first, then the diagram. Use groups, colour and the failure paths:
   ```
   %% caption: Each payment goes to a match. A person examines each payment that does not match.
   flowchart LR
     subgraph IN["Input"]
       A["Customer pays<br/>card or bank"]:::actor
       B["Bank sends daily file"]:::ext
     end
     subgraph CORE["Payment service"]
       C["Record payment"]:::step
       D{"Payment matches invoice?"}:::decision
       E[("Payments store")]:::store
     end
     F["Invoice closes"]:::ok
     G["Person examines payment"]:::warn
     H["Payment stays open"]:::bad
     A --> C
     B --> C
     C --> E
     C --> D
     D -- "yes" --> F
     D -- "no" --> G
     G -- "match found" --> F
     G -. "no match" .-> H
     classDef actor fill:#dae8fc,stroke:#6c8ebf,color:#000
     classDef ext fill:#f5f5f5,stroke:#666666,color:#000
     classDef step fill:#d5e8d4,stroke:#82b366,color:#000
     classDef decision fill:#fff2cc,stroke:#d6b656,color:#000
     classDef store fill:#e1d5e7,stroke:#9673a6,color:#000
     classDef ok fill:#d5e8d4,stroke:#82b366,color:#000,stroke-width:2px
     classDef warn fill:#ffe6cc,stroke:#d79b00,color:#000
     classDef bad fill:#f8cecc,stroke:#b85450,color:#000
   ```
   - Put every label in double quotes. Do not put raw `<`, `>` or `&` in a label. `<br/>` is the only tag.
   - Use `flowchart LR` for flows and `flowchart TD` for hierarchies. Sequence, state, ER, timeline and the other Mermaid types also convert.
   - Do not add `%%{init}%%`. draw.io keeps `classDef`, `:::class`, `style`, subgraphs, `[( )]` stores and dotted edges.
   - Match the label language to the user's language. In English, prefer STE words, but use the clearest word for the reader. STE findings are warnings.

### Colour palette

Copy only the `classDef` lines that the diagram uses. These are the draw.io default colours, so the user can restyle in draw.io with the same palette.

| Class | Colour | For |
|---|---|---|
| `actor` | blue | a person or a team that starts something |
| `step` | green | an action of the system |
| `decision` | yellow | a question with 2 or more answers (`{"..."}`) |
| `store` | purple | data that stays (`[("...")]`) |
| `ext` | grey | an external system or a supplier |
| `ok` | green, thick border | a good end result |
| `warn` | orange | a manual step, a retry, a wait |
| `bad` | red | a failure end result |

To colour a subgraph, add `style CORE fill:#f9f9f9,stroke:#999999`.

4. **Build:** `scripts/diagram.py build docs/diagrams/<topic>/<name>.mmd`
   - It runs `lint` first. Fix every ERROR in the `.mmd`. Do not use `--no-lint` to get past the lint. An altitude error means you must rewrite the label in plain words. Do not rename the label only to get past the regex.
   - Read each WARN and decide. A `no classDef` warning means: add the colours.
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

The picture rules apply to hand edits too. `lint` reads only `.mmd` files, so check your new labels yourself.

## Commands

| Command | Does |
|---|---|
| `diagram.py status [dir\|file ...]` | `new`, `clean`, `hand-edited`, `drawio-only`, `(png out of date)` for each diagram. Default dir: `docs/diagrams`. |
| `diagram.py lint <name.mmd>` | Altitude and STE checks only. |
| `diagram.py build <name.mmd> [--scale 2] [--force] [--no-open]` | lint → `.drawio` → `.drawio.png`, records the hash, opens the PNG. Exit 2 = refused, the `.drawio` was edited. |
| `diagram.py export <name.drawio> [--scale 2] [--no-open]` | `.drawio` → `.drawio.png`, opens the PNG. Marks the `.mmd` STALE if the hashes differ. |

## draw.io notes

- `build` and `export` use draw.io Desktop (`brew install --cask drawio`). They find `drawio` on PATH or in `/Applications/draw.io.app`. Without it, `lint` and `status` still work. Write the `.drawio` XML by hand, and the user exports the PNG in draw.io with "Include a copy of my diagram" set.
- Mermaid → PNG in one step is broken in draw.io Desktop. The script always goes `.mmd` → `.drawio` → PNG.
- The PNG has a white background in every theme, because people paste it into GitHub, docs and chat.
- The user can open the `.drawio.png` itself in draw.io, because the XML is embedded. The `.drawio` is still the file to edit.
- Need AWS, Azure or network shapes, or exact positions? Mermaid cannot do that. Write the `.drawio` XML directly (`/drawio:drawio` has the XML reference), skip the `.mmd`, and run `export`. `status` then shows `drawio-only`. That is correct.
