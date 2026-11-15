#!/usr/bin/env python3
"""Draw the battery family into dev/icons/src like the macOS menu bar battery:
no outline, the whole body is one solid shape. The charged part is opaque, the
rest dim; while charging a bolt is cut out of both (even-odd fill).

Power profile variants look like the plain icon: the badge doesn't survive the
tray size. battery-profile-*, battery-missing and battery-ups stay hand drawn.

  python3 dev/icons/gen-battery.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "src"
LEVELS = range(0, 101, 10)
PROFILES = ["", "-profile-balanced", "-profile-performance", "-profile-powersave"]

X0, X1, Y0, Y1, R = 1.6, 20.2, 5.6, 18.4, 3.8    # body
NUB = (21, 9.6, 22.6, 14.4, 0.8)                  # x0, y0, x1, y1, r
DIM = 0.35                                        # opacity of the empty part
BOLT = "M12.4 7.4 L8 12.8 H10.9 L9.8 16.6 L14.2 11.2 H11.3 Z"

HEAD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <style id="current-color-scheme">.ColorScheme-Text{color:#fcfcfc}</style>
"""


def rrect(x0, y0, x1, y1, r):
    return (f"M{x0 + r:g} {y0:g} H{x1 - r:g} a{r:g} {r:g} 0 0 1 {r:g} {r:g} V{y1 - r:g} "
            f"a{r:g} {r:g} 0 0 1 {-r:g} {r:g} H{x0 + r:g} a{r:g} {r:g} 0 0 1 {-r:g} {-r:g} "
            f"V{y0 + r:g} a{r:g} {r:g} 0 0 1 {r:g} {-r:g} Z")


def battery(level, charging):
    split = round(X0 + (X1 - X0) * level / 100, 2)
    body = rrect(X0, Y0, X1, Y1, R) + (" " + BOLT if charging else "")
    out = HEAD + ('  <defs>\n'
                  f'    <clipPath id="lit"><path d="M0 0 H{split:g} V24 H0 Z"/></clipPath>\n'
                  f'    <clipPath id="empty"><path d="M{split:g} 0 H24 V24 H{split:g} Z"/></clipPath>\n'
                  '  </defs>\n')
    g = '  <g class="ColorScheme-Text" fill="currentColor" fill-rule="evenodd"{}>\n    <path d="{}"{}/>\n  </g>\n'
    if level < 100:
        out += g.format(f' opacity="{DIM}"', body, ' clip-path="url(#empty)"')
    if level > 0:
        out += g.format("", body, ' clip-path="url(#lit)"')
    out += g.format("" if level == 100 else f' opacity="{DIM}"', rrect(*NUB), "")
    return out + "</svg>\n"


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
