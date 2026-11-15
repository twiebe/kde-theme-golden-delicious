#!/usr/bin/env python3
"""Draw the battery family into dev/icons/src, wide like the macOS menu bar
battery: a long rounded body, the charge as a solid bar and, while charging, a
bolt cut out of the bar (even-odd fill, so it shows on full and empty alike).

Power profile variants look like the plain icon: the badge doesn't survive the
tray size. battery-profile-*, battery-missing and battery-ups stay hand drawn.

  python3 dev/icons/gen-battery.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "src"
LEVELS = range(0, 101, 10)
PROFILES = ["", "-profile-balanced", "-profile-performance", "-profile-powersave"]

X0, X1, Y0, Y1, R = 2.2, 19.6, 5.5, 18.5, 3.6     # body outline, stroke centred
IX0, IX1, IY0, IY1, IR = 4.1, 17.7, 7.4, 16.6, 1.8   # charge bar area
BOLT = "M12.6 7.6 L8.3 12.6 H11 L9.9 16.4 L14.2 11.4 H11.5 Z"

HEAD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <style id="current-color-scheme">.ColorScheme-Text{color:#fcfcfc}</style>
  <g class="ColorScheme-Text" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
"""


def rrect(x0, y0, x1, y1, r):
    return (f"M{x0 + r:g} {y0:g} H{x1 - r:g} a{r:g} {r:g} 0 0 1 {r:g} {r:g} V{y1 - r:g} "
            f"a{r:g} {r:g} 0 0 1 {-r:g} {r:g} H{x0 + r:g} a{r:g} {r:g} 0 0 1 {-r:g} {-r:g} "
            f"V{y0 + r:g} a{r:g} {r:g} 0 0 1 {r:g} {-r:g} Z")


def battery(level, charging):
    out = HEAD
    out += f'    <path d="{rrect(X0, Y0, X1, Y1, R)}"/>\n'
    out += '    <path d="M21.4 10 V14"/>\n  </g>\n'
    fill = []
    if level:
        w = max((IX1 - IX0) * level / 100, 2 * IR)
        fill.append(rrect(IX0, IY0, round(IX0 + w, 2), IY1, IR))
    if charging:
        fill.append(BOLT)
    if fill:
        out += ('  <g class="ColorScheme-Text" fill="currentColor" fill-rule="evenodd" stroke="none">\n'
                f'    <path d="{" ".join(fill)}"/>\n  </g>\n')
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
