#!/usr/bin/env python3
"""Generate the Plasma style SVGs for Golden Delicious.

Run from the repo root: python3 dev/gen-plasma.py
Writes into src/plasma/desktoptheme/golden-delicious/.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "src/plasma/desktoptheme/golden-delicious"

PANEL_R = 14            # panel corner radius
PANEL_OPACITY = 0.96    # solid/: opaque panel, adaptive with a maximized window
PANEL_TRANSLUCENT = 0.70  # widgets/: translucent panel
PANEL_MARGIN = 4
TASK_R = 10
TASK_MARGIN = 4
TASKS = {               # state: (color class, opacity)
    "normal": ("ColorScheme-Text", 0.05),
    "hover": ("ColorScheme-Text", 0.10),
    "focus": ("ColorScheme-Text", 0.16),
    "minimized": ("ColorScheme-Text", 0.03),
    "attention": ("ColorScheme-NegativeText", 0.30),
}

STYLE = ('<style type="text/css" id="current-color-scheme">'
         '.ColorScheme-Background{color:#1e1e1e;}.ColorScheme-Text{color:#f2f2f7;}'
         '.ColorScheme-NegativeText{color:#ff9f0a;}</style>')


def piece(eid, w, h, body=""):
    return (f'<g id="{eid}"><rect width="{w}" height="{h}" fill="#000" fill-opacity="0"/>{body}</g>')


def fill(cls, op, extra):
    return f'class="{cls}" fill="currentColor" fill-opacity="{op}" {extra}'


def frame(prefix, r, cls, op, margin):
    """Rounded-rect 9-patch with radius r. prefix '' gives unprefixed names."""
    n = (lambda s: f"{prefix}-{s}") if prefix else (lambda s: s)
    f = lambda extra: f'<path {fill(cls, op, extra)}/>' if extra.startswith("d=") else f'<rect {fill(cls, op, extra)}/>'
    arcs = {
        "topleft": f'd="M0,{r} A{r},{r} 0 0 1 {r},0 L{r},{r} Z"',
        "topright": f'd="M0,0 A{r},{r} 0 0 1 {r},{r} L0,{r} Z"',
        "bottomleft": f'd="M{r},{r} A{r},{r} 0 0 1 0,0 L{r},0 Z"',
        "bottomright": f'd="M{r},0 A{r},{r} 0 0 1 0,{r} L0,0 Z"',
    }
    out = [piece(n(k), r, r, f(v)) for k, v in arcs.items()]
    for k, w, h in (("top", 1, r), ("bottom", 1, r), ("left", r, 1), ("right", r, 1), ("center", 1, 1)):
        out.append(piece(n(k), w, h, f(f'width="{w}" height="{h}"')))
    for side in ("top", "bottom", "left", "right"):
        out.append(f'<rect id="{n("hint-" + side + "-margin")}" width="{margin}" height="{margin}" fill="none"/>')
    return "".join(out)


def svg(content):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><defs>{STYLE}</defs>{content}</svg>\n')


def panel(op):
    return svg(frame("", PANEL_R, "ColorScheme-Background", op, PANEL_MARGIN)
               + frame("mask", PANEL_R, "ColorScheme-Background", 1, PANEL_MARGIN))


def main():
    (OUT / "widgets").mkdir(parents=True, exist_ok=True)
    # Plasma 6 draws the translucent panel from widgets/ and cross-fades the
    # opaque one from solid/; without solid/ it falls back to Breeze's shape.
    (OUT / "solid/widgets").mkdir(parents=True, exist_ok=True)
    (OUT / "widgets/panel-background.svg").write_text(panel(PANEL_TRANSLUCENT))
    (OUT / "solid/widgets/panel-background.svg").write_text(panel(PANEL_OPACITY))
    (OUT / "widgets/tasks.svg").write_text(
        svg("".join(frame(s, TASK_R, c, o, TASK_MARGIN) for s, (c, o) in TASKS.items())))


if __name__ == "__main__":
    main()
