# Golden Gate icon style

Monochrome symbolic icons in the spirit of SF Symbols (regular weight), not a
copy of them. Softer and rounder than Breeze. The references in `src/`
(user-home, folder, edit-find, configure, ...) define the look; match them.

## Format

One file per icon name: `src/<name>.svg`, exactly this skeleton:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <style id="current-color-scheme">.ColorScheme-Text{color:#fcfcfc}</style>
  <g class="ColorScheme-Text" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
    <path d="..."/>
  </g>
</svg>
```

- Only `<path>` elements inside the one `<g>`. No fills, no other colours,
  no transforms, no filters, no text, no `<circle>`/`<rect>` (write them as
  paths: a circle is `M cx cy-r a r r 0 1 1 0 2r a r r 0 1 1 0 -2r Z`).
- A small solid dot (e.g. a status dot) may use a second group
  `<g class="ColorScheme-Text" fill="currentColor" stroke="none">`.
- KDE recolours via the class; the build script decides sizes and whether an
  icon gets the accent colour, so never hard-code a colour.

## Grid and geometry

- 24 x 24 grid, live area 3..21 (keep 3 px margin; up to 2 px for wide
  shapes like arrows). Strokes are 1.6 and centred on the path.
- Prefer coordinates on .0 or .5. Keep parallel lines at least 3 units apart
  (they are rendered at 16 px too, where 1 unit is 0.67 px).
- Corners: radius 2-2.5 on large rectangles, 1-1.5 on small ones. No sharp
  90 degree outer corners except where a shape meets a straight line.
- Round caps and joins everywhere (set on the group, don't override).
- Arrows: open chevron heads (two lines meeting at the tip, ~90 degrees),
  shaft optional. Plus/minus: lines only, length 10-12.
- Keep it simple: at most 4-6 paths; drop details Breeze has that don't
  survive 16 px.

## Meaning

Keep the metaphor of the Breeze icon of the same name (look at it), but draw
it fresh in this style; don't trace Breeze.
