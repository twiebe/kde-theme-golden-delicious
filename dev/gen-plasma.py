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
PANEL_SHADOW = 14       # the floating panel's own shadow, so it stands out from the wallpaper
PANEL_SHADOW_ALPHA = 0.20
PANEL_SHADOW_FALLOFF = ((0, 1), (0.25, 0.6), (0.5, 0.3), (0.75, 0.1), (1, 0))  # soft, no hard line at the edge
PANEL_RIM = 0           # opacity of a 1 px light rim like the windows'; 0 for none
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


def frame(prefix, r, cls, op, margin, rim=0, inset=0):
    """Rounded-rect 9-patch with radius r. prefix '' gives unprefixed names.
    rim > 0 adds a 1 px ColorScheme-Text ring of that opacity along the edge;
    inset draws the shape that far inside the tiles' outer edge."""
    n = (lambda s: f"{prefix}-{s}") if prefix else (lambda s: s)
    f = lambda extra: f'<path {fill(cls, op, extra)}/>' if extra.startswith("d=") else f'<rect {fill(cls, op, extra)}/>'
    i, p = inset, r - inset
    arcs = {
        "topleft": f'd="M{i},{r} A{p},{p} 0 0 1 {r},{i} L{r},{r} Z"',
        "topright": f'd="M0,{i} A{p},{p} 0 0 1 {p},{r} L0,{r} Z"',
        "bottomleft": f'd="M{r},{p} A{p},{p} 0 0 1 {i},0 L{r},0 Z"',
        "bottomright": f'd="M{p},0 A{p},{p} 0 0 1 0,{p} L0,0 Z"',
    }
    ring = lambda d: f'<path {fill("ColorScheme-Text", rim, d)}/>' if rim else ""
    q = r - 1
    rings = {  # the corner arc minus the same arc 1 px further in
        "topleft": f'd="M0,{r} A{r},{r} 0 0 1 {r},0 L{r},1 A{q},{q} 0 0 0 1,{r} Z"',
        "topright": f'd="M0,0 A{r},{r} 0 0 1 {r},{r} L{q},{r} A{q},{q} 0 0 0 0,1 Z"',
        "bottomleft": f'd="M{r},{r} A{r},{r} 0 0 1 0,0 L1,0 A{q},{q} 0 0 0 {r},{q} Z"',
        "bottomright": f'd="M{r},0 A{r},{r} 0 0 1 0,{r} L0,{q} A{q},{q} 0 0 0 {q},0 Z"',
    }
    out = [piece(n(k), r, r, f(v) + ring(rings[k])) for k, v in arcs.items()]
    edges = {"top": "M0,0 h1 v1 h-1 Z", "bottom": f"M0,{q} h1 v1 h-1 Z",
             "left": "M0,0 h1 v1 h-1 Z", "right": f"M{q},0 h1 v1 h-1 Z"}
    at = lambda a: f'{a}="{i}" ' if i else ""
    body = {"top": f'{at("y")}width="1" height="{p}"', "bottom": f'width="1" height="{p}"',
            "left": f'{at("x")}width="{p}" height="1"', "right": f'width="{p}" height="1"',
            "center": 'width="1" height="1"'}
    for k, w, h in (("top", 1, r), ("bottom", 1, r), ("left", r, 1), ("right", r, 1), ("center", 1, 1)):
        out.append(piece(n(k), w, h, f(body[k]) + (ring(f'd="{edges[k]}"') if k in edges else "")))
    for side in ("top", "bottom", "left", "right"):
        out.append(f'<rect id="{n("hint-" + side + "-margin")}" width="{margin}" height="{margin}" fill="none"/>')
    return "".join(out)


def svg(content):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><defs>{STYLE}</defs>{content}</svg>\n')


def shadow(R=DIALOG_R, S=SHADOW, I=SHADOW_INSET, A=SHADOW_ALPHA, falloff=((0, 1), (0.65, 0.35), (1, 0))):
    """Shadow 9-patch around a rounded popup. Corner gradients are centred on
    the popup's corner arc, so the shadow follows the curve; inside the popup
    they stay clear, which matters under a translucent background. falloff
    gives the opacity (times A) at fractions of the reach out from the edge."""
    T = S + I
    inner = R / (R + S)
    stop = lambda o, a: f'<stop offset="{o:.4f}" stop-color="#000" stop-opacity="{A * a:.3f}"/>'
    stops = (stop(0, 0) + stop(inner - 0.001, 0)
             + "".join(stop(inner + (1 - inner) * t, a) for t, a in falloff))
    side = ("".join(stop(S / T * (1 - t), a) for t, a in reversed(falloff))
            + stop(S / T + 0.001, 0) + stop(1, 0))
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
    return svg(frame("", PANEL_R, "ColorScheme-Background", op, PANEL_MARGIN, PANEL_RIM)
               # Blur and contrast stop 1 px short of the edge: at fractional
               # scales the mask is not anti-aliased, and its saturated wallpaper
               # would show as a coloured line through the edge's partial pixels.
               + frame("mask", PANEL_R, "ColorScheme-Background", 1, PANEL_MARGIN, inset=1)
               + shadow(PANEL_R, PANEL_SHADOW, PANEL_R, PANEL_SHADOW_ALPHA, PANEL_SHADOW_FALLOFF))


BREEZE_WIDGETS = Path("/usr/share/plasma/desktoptheme/default/widgets")
BREEZE_SLIDER = BREEZE_WIDGETS / "slider.svgz"


def sheen(gid, cx, cy, r):
    """Light on a round knob like on the traffic lights (dev/gen-aurorae.py):
    a bright crescent under the top edge, a glow low inside and a rim that is
    brightest at top and bottom. White over the accent colour, so it follows it."""
    user = 'gradientUnits="userSpaceOnUse"'
    stop = lambda o, a: f'<stop offset="{o}" stop-color="#ffffff" stop-opacity="{a}"/>'
    vert = f'x1="0" y1="{cy - r:g}" x2="0" y2="{cy + r:g}" {user}'
    w = r / 14
    return (f'<defs>'
            f'<radialGradient id="{gid}t" cx="{cx:g}" cy="{cy + r * 0.58:.4g}" r="{r * 1.53:.4g}" {user}>'
            f'{stop(0.675, 0)}{stop(0.8375, 0.22)}</radialGradient>'
            f'<radialGradient id="{gid}g" cx="{cx:g}" cy="{cy + r * 0.55:.4g}" r="{r * 0.69:.4g}" {user}>'
            f'{stop(0.38, 0.16)}{stop(0.69, 0.08)}{stop(1, 0)}</radialGradient>'
            f'<linearGradient id="{gid}r" {vert}>{stop(0, 0.6)}{stop(0.265, 0)}{stop(0.735, 0)}{stop(1, 0.4)}</linearGradient>'
            f'</defs>'
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="url(#{gid}t)"/>'
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="url(#{gid}g)"/>'
            f'<circle cx="{cx:g}" cy="{cy:g}" r="{r - w / 2:.4g}" fill="none" stroke="url(#{gid}r)" stroke-width="{w:.4g}"/>')


def accent_knob(text, element, gid, cx, cy, r, new_id=None):
    """The group element of a Breeze widget SVG with its knob in the accent
    colour and the sheen on top; as a copy named new_id if given."""
    start = text.rindex("<g", 0, text.index(f'id="{element}"'))
    end = text.index("</g>", start)
    part = re.sub(r'class="ColorScheme-(ButtonBackground|Frame)"', 'class="ColorScheme-Highlight"',
                  text[start:end])
    if new_id:
        part = part.replace(f'id="{element}"', f'id="{new_id}"', 1)
        part = re.sub(r'\sid="(?!' + re.escape(new_id) + r'")[^"]*"', "", part)  # no clashing ids
        return text[:end + 4] + part + sheen(gid, cx, cy, r) + "</g>" + text[end + 4:]
    return text[:start] + part + sheen(gid, cx, cy, r) + text[end:]


def slider():
    """Breeze's slider with the knob in the accent colour, like the filled groove."""
    text = gzip.decompress(BREEZE_SLIDER.read_bytes()).decode()
    for knob in ("horizontal-slider-handle", "vertical-slider-handle"):
        text = accent_knob(text, knob, f"s{knob[0]}", 16, 39, 8.3333)
    return text


def switch():
    """Breeze's switch with the knob in the accent colour, on or off, lit like
    the traffic lights; a little brighter on hover, darker while pressed."""
    text = gzip.decompress((BREEZE_WIDGETS / "switch.svgz").read_bytes()).decode()
    text = accent_knob(text, "handle", "sw", 78, 26, 11)
    for element, gid, tint in (("handle-hover", "swh", '#fff" fill-opacity="0.14'),
                               ("handle-pressed", "swp", '#000" fill-opacity="0.18')):
        start = text.rindex("<g", 0, text.index(f'id="{element}"'))
        head = text[start:text.index(">", start) + 1]
        end = text.index("</g>", start)
        knob = ('<circle cx="73" cy="91" r="11" class="ColorScheme-Highlight" fill="currentColor"/>'
                f'<circle cx="73" cy="91" r="11" fill="{tint}"/>' + sheen(gid, 73, 91, 11))
        text = text[:start] + head + knob + text[end:]
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
        (OUT / "widgets/switch.svg").write_text(switch())
    else:
        print(f"{BREEZE_SLIDER} missing: widgets/slider.svg left as is")


if __name__ == "__main__":
    main()
