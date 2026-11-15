#!/usr/bin/env python3
"""Generate the Aurorae decoration SVGs for Golden Gate.

Run from the repo root: python3 dev/gen-aurorae.py
Writes into src/aurorae/themes/golden-gate/. Tune the constants below and rerun.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "src/aurorae/themes/golden-gate"

P = 20          # shadow padding, must match Padding* in golden-gaterc
R = 12          # top corner radius
C = P + R       # corner piece size

STATES = {
    # prefix: (titlebar fill, shadow opacity at window edge)
    "decoration": ("#2B2B2D", 0.45),
    "decoration-inactive": ("#2B2B2D", 0.25),
}

LIGHTS = {"close": "#FF5F57", "minimize": "#FEBC2E", "maximize": "#28C840"}
LIGHT_INACTIVE = "#5A5A5E"
GLYPH = "#3A1A10"
BTN = 22        # button box, must match ButtonWidth/ButtonHeight
DOT = 7         # light radius -> 14 px diameter, 8 px gap in a 22 px box


def box(eid, w, h, body, defs=""):
    # Transparent rect pins the element's bounds to exactly w x h.
    return (f'<g id="{eid}">{defs}'
            f'<rect width="{w}" height="{h}" fill="#000" fill-opacity="0"/>{body}</g>')


def frame(prefix, fill, a):
    s = f'stop-color="#000"'
    g = []
    # Corners: top ones rounded (radius R), bottom ones square (client covers them).
    for name, rounded, flip in (("topleft", True, ""), ("topright", True, f"translate({C},0) scale(-1,1)"),
                                ("bottomleft", False, f"translate(0,{C}) scale(1,-1)"),
                                ("bottomright", False, f"translate({C},{C}) scale(-1,-1)")):
        gid = f"{prefix}-{name}-sh"
        if rounded:
            inner = R / C
            grad = (f'<radialGradient id="{gid}" cx="{C}" cy="{C}" r="{C}" gradientUnits="userSpaceOnUse">'
                    f'<stop offset="{inner:.4f}" {s} stop-opacity="{a}"/><stop offset="1" {s} stop-opacity="0"/></radialGradient>')
            shape = f'<path d="M{P},{C} A{R},{R} 0 0 1 {C},{P} L{C},{C} Z" fill="{fill}"/>'
            body = f'<g transform="{flip}"><rect width="{C}" height="{C}" fill="url(#{gid})"/>{shape}</g>'
        else:
            # Square corner: radial in the outer P x P cell, linear strips beside it.
            grad = (f'<radialGradient id="{gid}" cx="{P}" cy="{P}" r="{P}" gradientUnits="userSpaceOnUse">'
                    f'<stop offset="0" {s} stop-opacity="{a}"/><stop offset="1" {s} stop-opacity="0"/></radialGradient>'
                    f'<linearGradient id="{gid}v" x1="0" y1="0" x2="0" y2="{P}" gradientUnits="userSpaceOnUse">'
                    f'<stop offset="0" {s} stop-opacity="0"/><stop offset="1" {s} stop-opacity="{a}"/></linearGradient>'
                    f'<linearGradient id="{gid}h" x1="0" y1="0" x2="{P}" y2="0" gradientUnits="userSpaceOnUse">'
                    f'<stop offset="0" {s} stop-opacity="0"/><stop offset="1" {s} stop-opacity="{a}"/></linearGradient>')
            body = (f'<g transform="{flip}"><rect width="{P}" height="{P}" fill="url(#{gid})"/>'
                    f'<rect x="{P}" width="{R}" height="{P}" fill="url(#{gid}v)"/>'
                    f'<rect y="{P}" width="{P}" height="{R}" fill="url(#{gid}h)"/>'
                    f'<rect x="{P}" y="{P}" width="{R}" height="{R}" fill="{fill}"/></g>')
        g.append(box(f"{prefix}-{name}", C, C, body, f"<defs>{grad}</defs>"))
    # Edges: 1 px long, stretched by KWin.
    for name, w, h, x1, y1, x2, y2, rx, ry, rw, rh in (
            ("top", 1, C, 0, 0, 0, P, 0, P, 1, R),
            ("bottom", 1, C, 0, C, 0, R, 0, 0, 1, R),
            ("left", C, 1, 0, 0, P, 0, P, 0, R, 1),
            ("right", C, 1, C, 0, R, 0, 0, 0, R, 1)):
        gid = f"{prefix}-{name}-sh"
        grad = (f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0" {s} stop-opacity="0"/><stop offset="1" {s} stop-opacity="{a}"/></linearGradient>')
        body = (f'<rect width="{w}" height="{h}" fill="url(#{gid})"/>'
                f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{fill}"/>')
        g.append(box(f"{prefix}-{name}", w, h, body, f"<defs>{grad}</defs>"))
    g.append(box(f"{prefix}-center", 1, 1, f'<rect width="1" height="1" fill="{fill}"/>'))
    return "".join(g)


def svg(content):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">{content}</svg>\n')


def glyph(kind):
    c, w = BTN / 2, 1.4
    st = f'stroke="{GLYPH}" stroke-width="{w}" stroke-linecap="round" fill="none"'
    if kind == "close":
        d = 2.6
        return f'<path d="M{c-d},{c-d} L{c+d},{c+d} M{c+d},{c-d} L{c-d},{c+d}" {st}/>'
    if kind == "minimize":
        return f'<path d="M{c-3.2},{c} L{c+3.2},{c}" {st}/>'
    if kind == "maximize":
        return f'<path d="M{c-3.2},{c} L{c+3.2},{c} M{c},{c-3.2} L{c},{c+3.2}" {st}/>'
    return f'<path d="M{c-2.6},{c+2.6} L{c-2.6},{c-0.6} M{c-2.6},{c+2.6} L{c-0.6},{c+2.6} ' \
           f'M{c+2.6},{c-2.6} L{c+2.6},{c+0.6} M{c+2.6},{c-2.6} L{c+0.6},{c-2.6}" {st}/>'  # restore


def button(kind, color):
    c = BTN / 2
    dot = lambda col, op=1: f'<circle cx="{c}" cy="{c}" r="{DOT}" fill="{col}" fill-opacity="{op}"/>'
    shade = f'<circle cx="{c}" cy="{c}" r="{DOT}" fill="#000" fill-opacity="0.2"/>'
    els = {
        "active": dot(color),
        "inactive": dot(LIGHT_INACTIVE),
        "hover": dot(color) + glyph(kind),
        "hover-inactive": dot(color) + glyph(kind),
        "pressed": dot(color) + shade + glyph(kind),
        "pressed-inactive": dot(color) + shade + glyph(kind),
        "deactivated": dot(LIGHT_INACTIVE, 0.5),
        "deactivated-inactive": dot(LIGHT_INACTIVE, 0.5),
    }
    # Aurorae draws buttons as frames: the state name is a prefix, "-center" the element.
    return svg("".join(box(f"{k}-center", BTN, BTN, v) for k, v in els.items()))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "decoration.svg").write_text(svg("".join(frame(p, f, a) for p, (f, a) in STATES.items())))
    for kind, color in LIGHTS.items():
        (OUT / f"{kind}.svg").write_text(button(kind, color))
    (OUT / "restore.svg").write_text(button("restore", LIGHTS["maximize"]))


if __name__ == "__main__":
    main()
