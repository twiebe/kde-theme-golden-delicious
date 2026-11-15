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
    "decoration": ("#2B2B2D", 0.10),
    "decoration-inactive": ("#2B2B2D", 0.055),
}

# Fitted to the Golden Gate lights in a Retina screenshot.
# base: body, top to bottom. top: glow hugging the upper edge. bot: glow blob in
# the lower half, core and halo colour, halo opacity. rim: colour, outer and
# inner opacity at the top and bottom, fading to nothing towards the sides.
LIGHTS = {
    "close": dict(base=("#F75143", "#EE554D"), top="#F86359", bot=("#EF6760", "#F25F57", 1),
                  rim=("#FFFFF6", 0.61, 0.40)),
    "minimize": dict(base=("#FBA800", "#FDCC00"), top="#FBB600", bot=("#FECC2D", "#FFD300", 0.28),
                     rim=("#F8FF80", 0.89, 0.61)),
    "maximize": dict(base=("#00BF00", "#04B800"), top="#44C30F", bot=("#4DC339", "#3CC004", 1),
                     rim=("#A5FF92", 1, 0.74)),
}
LIGHT_INACTIVE = dict(base=("#5A5A5C", "#515153"), rim=("#FFFFFF", 0.4, 0.25))
GLYPH = "#3A1A10"
# Fractional scaling: KWin rasterizes the SVG at device scale, but a button box
# that does not land on whole device pixels gets resampled and the lights go
# soft. So the box and its offsets (TitleEdgeLeft, ButtonMarginTop, Padding*)
# are multiples of 10, which is whole pixels at any scale in 10 % steps.
BTN = 30        # button box, must match ButtonWidth/ButtonHeight
DOT = 9         # light radius -> 18 px diameter
CEN = BTN / 2 + 1   # light centre in the box: 26 px from the window's top and left


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
    c, w = CEN, 1.4
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


def button(kind, light):
    c = CEN
    n = iter(range(100))

    def dot(l, op=1):
        gid = f"l{kind}{next(n)}"
        user = 'gradientUnits="userSpaceOnUse"'
        stop = lambda o, col, a=1: f'<stop offset="{o:.4g}" stop-color="{col}" stop-opacity="{a}"/>'
        vert = f'x1="0" y1="{c - DOT}" x2="0" y2="{c + DOT}" {user}'
        defs = f'<linearGradient id="{gid}b" {vert}>{stop(0, l["base"][0])}{stop(1, l["base"][1])}</linearGradient>'
        body = f'<circle cx="{c}" cy="{c}" r="{DOT}" fill="url(#{gid}b)"/>'
        if "top" in l:
            # Transparent disc centred low, so only a crescent under the upper edge shows.
            defs += (f'<radialGradient id="{gid}t" cx="{c}" cy="{c + DOT * 0.58:.4g}" r="{DOT * 1.53:.4g}" {user}>'
                     f'{stop(0.675, l["top"], 0)}{stop(0.8375, l["top"])}</radialGradient>')
            core, halo, a = l["bot"]
            defs += (f'<radialGradient id="{gid}g" cx="{c}" cy="{c + DOT * 0.55:.4g}" r="{DOT * 0.69:.4g}" {user}>'
                     f'{stop(0.38, core)}{stop(0.69, halo, a)}{stop(1, halo, 0)}</radialGradient>')
            body += "".join(f'<circle cx="{c}" cy="{c}" r="{DOT}" fill="url(#{gid}{k})"/>' for k in "tg")
        col, *alphas = l["rim"]
        w = DOT / 14  # half a point on a 14 pt Mac light
        for i, a in enumerate(alphas):
            defs += (f'<linearGradient id="{gid}r{i}" {vert}>{stop(0, col, a)}{stop(0.265, col, 0)}'
                     f'{stop(0.735, col, 0)}{stop(1, col, a)}</linearGradient>')
            body += (f'<circle cx="{c}" cy="{c}" r="{DOT - w * (i + 0.5):.4g}" fill="none" '
                     f'stroke="url(#{gid}r{i})" stroke-width="{w:.4g}"/>')
        return f'<defs>{defs}</defs><g opacity="{op}">{body}</g>'

    shade = f'<circle cx="{c}" cy="{c}" r="{DOT}" fill="#000" fill-opacity="0.2"/>'
    els = {
        "active": dot(light),
        "inactive": dot(LIGHT_INACTIVE),
        "hover": dot(light) + glyph(kind),
        "hover-inactive": dot(light) + glyph(kind),
        "pressed": dot(light) + shade + glyph(kind),
        "pressed-inactive": dot(light) + shade + glyph(kind),
        "deactivated": dot(LIGHT_INACTIVE, 0.5),
        "deactivated-inactive": dot(LIGHT_INACTIVE, 0.5),
    }
    # Aurorae draws buttons as frames: the state name is a prefix, "-center" the element.
    return svg("".join(box(f"{k}-center", BTN, BTN, v) for k, v in els.items()))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "decoration.svg").write_text(svg("".join(frame(p, f, a) for p, (f, a) in STATES.items())))
    for kind, light in LIGHTS.items():
        (OUT / f"{kind}.svg").write_text(button(kind, light))
    (OUT / "restore.svg").write_text(button("restore", LIGHTS["maximize"]))


if __name__ == "__main__":
    main()
