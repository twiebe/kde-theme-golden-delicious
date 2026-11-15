#!/usr/bin/env python3
"""Generate the Plasma style SVGs for Golden Delicious.

Run from the repo root: python3 dev/gen-plasma.py
Writes into src/plasma/desktoptheme/golden-delicious/. The slider comes from
Breeze's, so run it in the harness image to refresh that one.
"""
import gzip
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "src/plasma/desktoptheme/golden-delicious"

PANEL_R = 14            # panel corner radius
PANEL_OPACITY = 0.96    # solid/: opaque panel, adaptive with a maximized window
PANEL_TRANSLUCENT = 0.70  # widgets/: translucent panel
PANEL_MARGIN = 4
TASK_R = 10
DIALOG_R = 16           # popups (applets, krunner): same radius as the windows
DIALOG_OPACITY = 0.82   # dialogs/: translucent, KWin blurs behind it
DIALOG_MARGIN = 6       # keeps content out of the rounded corners
SHADOW = 18             # popup shadow reach
SHADOW_INSET = 16       # tiles reach under the popup to fill around the round corners
SHADOW_ALPHA = 0.30
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


def shadow():
    """Shadow 9-patch around a rounded popup. Corner gradients are centred on
    the popup's corner arc, so the shadow follows the curve; inside the popup
    they stay clear, which matters under a translucent background."""
    S, I, R, A = SHADOW, SHADOW_INSET, DIALOG_R, SHADOW_ALPHA
    T = S + I
    inner = R / (R + S)
    stops = (f'<stop offset="0" stop-color="#000" stop-opacity="0"/>'
             f'<stop offset="{inner - 0.001:.4f}" stop-color="#000" stop-opacity="0"/>'
             f'<stop offset="{inner:.4f}" stop-color="#000" stop-opacity="{A}"/>'
             f'<stop offset="{inner + (1 - inner) * 0.35:.4f}" stop-color="#000" stop-opacity="{A * 0.35:.3f}"/>'
             f'<stop offset="1" stop-color="#000" stop-opacity="0"/>')
    side = (f'<stop offset="0" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="{0.35 * S / T:.4f}" stop-color="#000" stop-opacity="{A * 0.35:.3f}"/>'
            f'<stop offset="{S / T:.4f}" stop-color="#000" stop-opacity="{A}"/>'
            f'<stop offset="{S / T + 0.001:.4f}" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="0"/>')
    defs, out = [], []
    # corner: (id, centre of the corner arc in tile coords)
    for k, cx, cy in (("topleft", S + R, S + R), ("topright", I - R, S + R),
                      ("bottomleft", S + R, I - R), ("bottomright", I - R, I - R)):
        defs.append(f'<radialGradient id="g-{k}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{R + S}">{stops}</radialGradient>')
        out.append(piece(f"shadow-{k}", T, T, f'<rect width="{T}" height="{T}" fill="url(#g-{k})"/>'))
    for k, w, h, x1, y1, x2, y2 in (("top", 1, T, 0, 0, 0, T), ("bottom", 1, T, 0, T, 0, 0),
                                    ("left", T, 1, 0, 0, T, 0), ("right", T, 1, T, 0, 0, 0)):
        defs.append(f'<linearGradient id="g-{k}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{side}</linearGradient>')
        out.append(piece(f"shadow-{k}", w, h, f'<rect width="{w}" height="{h}" fill="url(#g-{k})"/>'))
    out.append(piece("shadow-center", 1, 1))
    for side_ in ("top", "bottom", "left", "right"):
        # KWin pads the popup by the margin and draws each tile from the outer
        # edge, so tiles larger than the margin reach under the popup.
        out.append(f'<rect id="shadow-hint-{side_}-margin" width="{S}" height="{S}" fill="none"/>')
        out.append(f'<rect id="shadow-hint-{side_}-inset" width="{I}" height="{I}" fill="none"/>')
    return "<defs>" + "".join(defs) + "</defs>" + "".join(out)


def dialog(op):
    return svg(frame("", DIALOG_R, "ColorScheme-Background", op, DIALOG_MARGIN)
               + frame("mask", DIALOG_R, "ColorScheme-Background", 1, DIALOG_MARGIN)
               + shadow())


def panel(op):
    return svg(frame("", PANEL_R, "ColorScheme-Background", op, PANEL_MARGIN)
               + frame("mask", PANEL_R, "ColorScheme-Background", 1, PANEL_MARGIN))


BREEZE_SLIDER = Path("/usr/share/plasma/desktoptheme/default/widgets/slider.svgz")


def slider():
    """Breeze's slider with the knob in the accent colour, like the filled groove."""
    text = gzip.decompress(BREEZE_SLIDER.read_bytes()).decode()
    for knob in ("horizontal-slider-handle", "vertical-slider-handle"):
        start = text.index(f'id="{knob}"')
        end = text.index("</g>", start)
        part = re.sub(r'class="ColorScheme-(ButtonBackground|Frame)"', 'class="ColorScheme-Highlight"',
                      text[start:end])
        text = text[:start] + part + text[end:]
    return text


def main():
    (OUT / "widgets").mkdir(parents=True, exist_ok=True)
    # Plasma 6 draws the translucent panel from widgets/ and cross-fades the
    # opaque one from solid/; without solid/ it falls back to Breeze's shape.
    (OUT / "solid/widgets").mkdir(parents=True, exist_ok=True)
    (OUT / "widgets/panel-background.svg").write_text(panel(PANEL_TRANSLUCENT))
    (OUT / "solid/widgets/panel-background.svg").write_text(panel(PANEL_OPACITY))
    for d in ("dialogs", "solid/dialogs"):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    (OUT / "dialogs/background.svg").write_text(dialog(DIALOG_OPACITY))
    (OUT / "solid/dialogs/background.svg").write_text(dialog(1))
    (OUT / "widgets/tasks.svg").write_text(
        svg("".join(frame(s, TASK_R, c, o, TASK_MARGIN) for s, (c, o) in TASKS.items())))
    if BREEZE_SLIDER.exists():
        (OUT / "widgets/slider.svg").write_text(slider())
    else:
        print(f"{BREEZE_SLIDER} missing: widgets/slider.svg left as is")


if __name__ == "__main__":
    main()
