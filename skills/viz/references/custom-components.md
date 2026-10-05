# Building a custom component

The kit in `components.json` covers the shapes plans usually take. When the
source material has a shape none of them carries, **build one** — that is a
supported path, not a workaround. What is *not* supported is reaching for a
diagram because no component fit.

Two ways, in order of preference:

1. **Compose primitives** — no new CSS at all. Covers most cases.
2. **Compose primitives + a small CSS block** — when the layout genuinely needs
   geometry the primitives don't express (a gauge, a calendar strip, a nested
   bracket).

---

## 1. The token contract

A custom component must express **every** colour, and every surface, through
these. They are the only things that flip between light and dark.

| Token | Means | Use it for |
|---|---|---|
| `--bg` | Page ground | Cut-outs, dot borders that must read as "on the page" |
| `--surface` | Glass card fill | `.card` only |
| `--surface-2` | Solid-ish inner fill | Anything sitting *inside* a card |
| `--border` | Hairline divider | Borders, tracks, grid lines |
| `--hairline` | Top light edge | The `::before` highlight on cards |
| `--shadow` | Card elevation | `box-shadow` |
| `--text` | Body text | Default text |
| `--muted` | Secondary text | Labels, captions, axis text |
| `--accent` | Primary / neutral-positive | Default emphasis, step numbers, links |
| `--green` | Good / done | Success, completed |
| `--amber` | Attention / in progress | Warnings, current state |
| `--red` | Bad / blocked | Failures, blockers |
| `--d-node`, `--d-node-2`, `--d-line`, `--d-border`, `--d-note` | Diagram solids (alpha-free) | unused (legacy) |

Geometry conventions, so a custom piece sits with the rest: radius `10–12px`
inside a card (`14px` for the card itself), padding `12–16px`, gaps `8–14px`,
`1px solid var(--border)` hairlines, `3px` solid accent bars for emphasis,
micro-labels at `11.5px` uppercase `letter-spacing:.05em` in `var(--muted)`.

---

## 2. Rules a custom component must satisfy

- **Tokens only.** No literal hex, `rgb()`, or named colour anywhere outside the
  `:root` blocks. One hardcoded colour = one unreadable theme.
- **Zero JS.** No `<script>`, no inline handlers, no `:hover`-dependent meaning.
  The board renders reports in a sandboxed, script-free iframe.
- **No external assets.** No CDN, no web fonts, no remote images. Reports open
  from `file://` and must survive being offline.
- **Both themes.** Check light and dark before shipping; a `rgba(0,0,0,.05)`
  overlay that reads fine on white disappears on `#0b0e14`.
- **Narrow screens.** Either it reflows (grid/flex with `auto-fit`) or its
  container carries `class="card diagram"` so it scrolls instead of stretching
  the page.
- **Semantic where free.** A list of dated events is a `<ul>`; a label/value set
  is a `<dl>`; a matrix of facts is a `<table>`. Divs are the fallback, not the
  default.
- **It earns its place.** Same test as a diagram: if you can't write the one-line
  `<p class="cap">` takeaway, don't build it.

Where the CSS goes: a `<style>` block at the **top of your body fragment**, under
a clearly marked comment so it never gets confused with the shared kit:

```html
<style>
/* ── report-specific: <name> ───────────────────────────── */
.window { ... }
</style>
```

The shared kit's `<style>` lives in the shell's `<head>`, which you never author
or read — see SKILL.md §2. `validate_report.py` collects **every** `<style>` in
the built page, so report-local CSS is held to exactly the same token rules as
the kit: no hex, no `rgb()`, no `hsl()` outside the `:root` blocks.

If the same custom component shows up in a third report, promote it: add the CSS
to `assets/template.html` and add an entry to `references/components.json`.

---

## 3. Worked example — a "capacity ledger", composed only

Source material: *"Team has 40 dev-days this cycle; sub-project 1 needs 12,
sub-project 2 needs 18, and 6 are held for support."* No kit component carries
"budget vs claims vs remainder". Composed from primitives, zero new CSS:

```html
<div class="card">
  <div class="split">
    <div class="u-label">Capacity ledger</div>
    <div class="u-sm u-muted">cycle 2026-08</div>
  </div>

  <div class="tiles" style="margin-top:12px">
    <div class="tile accent"><div class="v u-num">40</div><div class="k">Dev-days</div></div>
    <div class="tile warn"><div class="v u-num">36</div><div class="k">Claimed</div></div>
    <div class="tile good"><div class="v u-num">4</div><div class="k">Free</div></div>
  </div>

  <div class="bars" style="margin-top:14px">
    <div class="row">
      <div>Sub-project 1</div>
      <div class="track"><div class="fill" style="width:30%"></div></div>
      <div class="num">12 d</div>
    </div>
    <div class="row">
      <div>Sub-project 2</div>
      <div class="track"><div class="fill warn" style="width:45%"></div></div>
      <div class="num">18 d</div>
    </div>
    <div class="row">
      <div>Support reserve</div>
      <div class="track"><div class="fill good" style="width:15%"></div></div>
      <div class="num">6 d</div>
    </div>
  </div>

  <p class="cap">Four dev-days of slack — any scope growth lands on the support reserve.</p>
</div>
```

Nothing new was invented: `split` + `u-label` for the header, `tiles` for the
headline numbers, `bars` for the split, `cap` for the takeaway.

---

## 4. Worked example — new geometry, ~12 lines of CSS

Source material: *"Rollout is 4 weeks; the migration window is week 2–3."* A span
inside a range is real geometry no primitive carries. Add the CSS block, keep
every colour a token:

```css
/* ── report-specific: window strip ─────────────────────── */
.window {
  position: relative; height: 44px; border-radius: 10px;
  background: var(--surface-2); border: 1px solid var(--border);
}
.window .span {
  position: absolute; top: 6px; bottom: 6px; border-radius: 8px;
  background: var(--accent); opacity: .55;
}
.window .ticks {
  display: grid; grid-auto-flow: column; grid-auto-columns: 1fr;
  position: absolute; inset: 0; font-size: 11.5px; color: var(--muted);
}
.window .ticks span {
  display: flex; align-items: center; justify-content: center;
  border-left: 1px solid var(--border);
}
.window .ticks span:first-child { border-left: 0; }
```

```html
<div class="card">
  <div class="window">
    <div class="span" style="left:25%;width:50%"></div>
    <div class="ticks">
      <span>Week 1</span><span>Week 2</span><span>Week 3</span><span>Week 4</span>
    </div>
  </div>
  <p class="cap">The migration window sits mid-rollout — weeks 1 and 4 are buffer.</p>
</div>
```

Checks it passes: tokens only, no JS, no assets, readable in both themes,
geometry in percentages so it reflows, and it has a caption.

---

## 5. Before shipping

Run the validator on the finished report:

```
<skill>/scripts/validate_report.py <report.html>
```

It flags hardcoded colours outside the token blocks, `<script>` inside `<main>`,
external asset URLs, diagrams with no caption, and more diagrams than the
budget allows. It cannot judge whether the component was the right choice — that
is still the earn-its-place test in `SKILL.md`.
