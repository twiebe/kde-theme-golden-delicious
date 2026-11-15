#!/usr/bin/env python3
"""Draw the battery family into dev/icons/src like the macOS menu bar battery:
no outline, the whole body is one solid shape. The charged part is opaque, the
rest dim. While charging a solid bolt, taller than the body, sits on top with a
thin gap cut around it.

Power profile variants look like the plain icon: the badge doesn't survive the
tray size. battery-profile-*, battery-missing and battery-ups stay hand drawn.

  python3 dev/icons/gen-battery.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "src"
LEVELS = range(0, 101, 10)
PROFILES = ["", "-profile-balanced", "-profile-performance", "-profile-powersave"]

X0, X1, Y0, Y1, R = 1.6, 20.2, 5.6, 18.4, 3.8    # body
NUB = (20.9, 10.2, 22.3, 13.8, 0.7)               # x0, y0, x1, y1, r
DIM = 0.45                                        # opacity of the empty part
BOLT = [(12.9, 4.3), (8.3, 12.4), (11.1, 12.4), (10.1, 19.7), (14.7, 11.4), (11.9, 11.4)]
GAP = 0.85                                        # cut around the bolt

HEAD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <style id="current-color-scheme">.ColorScheme-Text{color:#fcfcfc}</style>
"""


def poly(pts):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"


def grow(pts, d):
    """The polygon pts pushed outward by d (mitred corners)."""
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sign = 1 if area > 0 else -1
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        l = (dx * dx + dy * dy) ** 0.5
        nx, ny = sign * dy / l * d, -sign * dx / l * d
        lines.append(((x0 + nx, y0 + ny), (dx, dy)))
    out = []
    for i in range(n):
        (p, r), (q, s) = lines[i - 1], lines[i]
        t = ((q[0] - p[0]) * s[1] - (q[1] - p[1]) * s[0]) / (r[0] * s[1] - r[1] * s[0])
        out.append((p[0] + t * r[0], p[1] + t * r[1]))
    return out


def rrect(x0, y0, x1, y1, r):
    return (f"M{x0 + r:g} {y0:g} H{x1 - r:g} a{r:g} {r:g} 0 0 1 {r:g} {r:g} V{y1 - r:g} "
            f"a{r:g} {r:g} 0 0 1 {-r:g} {r:g} H{x0 + r:g} a{r:g} {r:g} 0 0 1 {-r:g} {-r:g} "
            f"V{y0 + r:g} a{r:g} {r:g} 0 0 1 {r:g} {-r:g} Z")


def battery(level, charging):
    split = round(X0 + (X1 - X0) * level / 100, 2)
    body = rrect(X0, Y0, X1, Y1, R)
    out = HEAD + ('  <defs>\n'
                  f'    <clipPath id="lit"><path d="M0 0 H{split:g} V24 H0 Z"/></clipPath>\n'
                  f'    <clipPath id="empty"><path d="M{split:g} 0 H24 V24 H{split:g} Z"/></clipPath>\n')
    if charging:
        out += f'    <clipPath id="gap"><path clip-rule="evenodd" d="M-8 -8 H32 V32 H-8 Z {poly(grow(BOLT, GAP))}"/></clipPath>\n'
    out += '  </defs>\n'
    open_ = '  <g class="ColorScheme-Text" fill="currentColor"{}>\n'
    part = '    <path d="{}"{}{}/>\n'
    out += open_.format(' clip-path="url(#gap)"' if charging else "")
    if level < 100:
        out += part.format(body, f' opacity="{DIM}"', ' clip-path="url(#empty)"')
    if level > 0:
        out += part.format(body, "", ' clip-path="url(#lit)"')
    out += "  </g>\n" + open_.format("")
    out += part.format(rrect(*NUB), "" if level == 100 else f' opacity="{DIM}"', "")
    if charging:
        out += part.format(poly(BOLT), "", "")
    return out + "  </g>\n</svg>\n"


def main():
    n = 0
    for level in LEVELS:
        for charging in (False, True):
            for profile in PROFILES:
                name = f"battery-{level:03}{'-charging' if charging else ''}{profile}.svg"
                (OUT / name).write_text(battery(level, charging))
                n += 1
    print(f"{n} battery icons")


if __name__ == "__main__":
    main()
