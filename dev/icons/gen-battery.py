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

X0, X1, Y0, Y1, R = 3, 19.2, 7, 17, 3          # body outline, stroke centred
IX0, IX1, IY0, IY1, IR = 4.9, 17.3, 8.9, 15.1, 1.4   # charge bar area
BOLT = "M12.3 8.2 L8.8 12.5 H11.1 L10.1 15.8 L13.6 11.5 H11.3 Z"

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
    out += '    <path d="M21.2 10.5 V13.5"/>\n  </g>\n'
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
