#!/usr/bin/env python3
"""Draw the wifi family into dev/icons/src like the macOS menu bar: always the
full fan (a dot and two bands); the signal strength lights the parts from the
dot outward, the rest stays dim. Lock and "limited" variants look the same as
their level; the badge is noise at tray size.

  python3 dev/icons/gen-wifi.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "src"
CX, CY = 12, 19.4       # fan centre
ANGLE = 41              # half the fan's opening, degrees
DIM = 0.35              # opacity of the unlit parts
BANDS = [(7.2, 3.0), (12.6, 3.0)]   # (radius of the band's centre line, thickness)

HEAD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <style id="current-color-scheme">.ColorScheme-Text{color:#fcfcfc}</style>
"""


def pt(r, deg):
    a = math.radians(deg)
    return f"{CX + r * math.sin(a):.2f} {CY - r * math.cos(a):.2f}"


def parts(lit, slash=False):
    """lit: how many of dot, inner band, outer band are lit (0..3)."""
    op = lambda i: "" if i < lit else f' opacity="{DIM}"'
    # Dot: a small wedge with rounded corners (filled, plus a round-joined rim).
    r = 3.2
    dot = f"M{CX} {CY} L{pt(r, -ANGLE)} A{r} {r} 0 0 1 {pt(r, ANGLE)} Z"
    out = (f'  <g class="ColorScheme-Text" fill="currentColor" stroke="currentColor" stroke-width="1.2" '
           f'stroke-linejoin="round"{op(0)}>\n    <path d="{dot}"/>\n  </g>\n')
    for i, (rad, w) in enumerate(BANDS, 1):
        arc = f"M{pt(rad, -ANGLE)} A{rad} {rad} 0 0 1 {pt(rad, ANGLE)}"
        out += (f'  <g class="ColorScheme-Text" fill="none" stroke="currentColor" stroke-width="{w}" '
                f'stroke-linecap="round"{op(i)}>\n    <path d="{arc}"/>\n  </g>\n')
    if slash:
        out += ('  <g class="ColorScheme-Text" fill="none" stroke="currentColor" stroke-width="1.6" '
                'stroke-linecap="round">\n    <path d="M4 4 L20 20"/>\n  </g>\n')
    return HEAD + out + "</svg>\n"


def lit_for(v):
    return 0 if v == 0 else 1 if v <= 25 else 2 if v <= 60 else 3


def main():
    icons = {}
    for v in (0, 20, 40, 60, 80, 100):
        for suffix in ("", "-locked", "-limited"):
            icons[f"network-wireless-{v}{suffix}"] = parts(lit_for(v))
    for v in ("00", "20", "25", "40", "50", "60", "75", "80", "100"):
        icons[f"network-wireless-connected-{v}"] = parts(lit_for(int(v)))
    icons["network-wireless-on"] = parts(3)
    icons["network-wireless-available"] = parts(0)
    icons["network-wireless-acquiring"] = parts(1)
    icons["network-wireless-disconnected"] = parts(0)
    icons["network-wireless-off"] = parts(0, slash=True)
    for name, svg in icons.items():
        (OUT / f"{name}.svg").write_text(svg)
    print(f"{len(icons)} wifi icons")


if __name__ == "__main__":
    main()
