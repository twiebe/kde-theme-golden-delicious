#!/usr/bin/env python3
"""Generate the Golden Delicious icon theme from our own drawings in dev/icons/src,
under Breeze Dark's names, sizes and aliases.

A name we have not drawn yet falls back to Breeze's monochrome icon with
thicker, rounder strokes: every filled shape gets a round-joined stroke in its
own colour, which widens each line by WIDTH and softens the corners. Colourful
icons are left out and keep coming from the inherited themes.

Runs inside the harness image, which has the pinned Breeze icons:
  docker run --rm -v "$PWD:/repo" -w /repo --entrypoint python3 \\
    golden-delicious-shot:6.8 dev/gen-icons.py
"""
import os
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

SRC = Path("/usr/share/icons/breeze-dark")
REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "src/icons/golden-delicious"
OURS = REPO / "dev/icons/src"
# Names we don't draw separately: -symbolic twins and coloured folders.
TWIN = re.compile(r"-symbolic$|(?<=^folder)-(brown|magenta|green|black|yellow|cyan|orange|violet|grey|blue|red)$")

WIDTH = 0.4                     # px added to every line
CONTEXTS = ["actions", "places", "devices", "status", "emblems"]
ACCENT = {"places", "devices"}  # drawn in the accent colour, like Finder's sidebar
SIZES = [16, 22, 24]
# Icons whose 1 px gaps close up when thickened; they keep Breeze's drawing.
EXCLUDE = {
    "draw-highlight",
    "edit-line-width",
    "flashlight-off",
    "flashlight-on",
    "show-guides",
    "view-grid",
    "view-sort",
    "view-sort-ascending",
    "view-sort-descending",
}

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
SHAPES = {f"{{{SVG}}}{t}" for t in ("path", "rect", "circle", "ellipse", "polygon")}


def style(s):
    return {k.strip(): v.strip() for k, v in
            (kv.split(":", 1) for kv in (s or "").split(";") if ":" in kv)}


def thicken(text, accent):
    root = ET.fromstring(text)
    parent = {c: p for p in root.iter() for c in p}

    def inherited(el, key, default):
        while el is not None:
            v = style(el.get("style")).get(key, el.get(key))
            if v is not None:
                return v
            el = parent.get(el)
        return default

    for el in root.iter():
        if el.tag not in SHAPES:
            continue
        fill = inherited(el, "fill", "#000")
        if fill == "none" or inherited(el, "stroke", "none") != "none":
            continue
        st = style(el.get("style"))
        st.update({"stroke": fill, "stroke-width": str(WIDTH), "stroke-linejoin": "round",
                   "stroke-linecap": "round",
                   "stroke-opacity": st.get("fill-opacity", el.get("fill-opacity", "1"))})
        el.attrib.pop("stroke", None)
        el.set("style", ";".join(f"{k}:{v}" for k, v in st.items()))
    out = ET.tostring(root, encoding="unicode")
    if accent:
        out = out.replace("ColorScheme-Text", "ColorScheme-Highlight")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + out + "\n"


def ours(name, accent):
    """Our drawing for a name, or None."""
    for n in (name, TWIN.sub("", name)):
        f = OURS / f"{n}.svg"
        if f.exists():
            text = f.read_text()
            return text.replace("ColorScheme-Text", "ColorScheme-Highlight") if accent else text
    return None


def monochrome(text):
    # Recolourable and no fixed colours of its own.
    return "currentColor" in text and not re.search(r'(?:fill|stop-color)[:=]\s*"?#', text)


def big_names():
    """Names Breeze also has above 24 px: shipping them at 1x would make our
    small drawing win at every size, so they only go into the @2x/@3x dirs."""
    names = set()
    for d in SRC.glob("*/*"):
        if d.name.split("@")[0].isdigit() and int(d.name.split("@")[0]) > 24:
            names.update(p.stem for p in d.glob("*.svg"))
    return names


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    big = big_names()
    fixed, scaled = [], []
    drawn, fallback = set(), set()
    for ctx in CONTEXTS:
        for size in SIZES:
            src = SRC / ctx / str(size)
            if not src.is_dir():
                continue
            hi = OUT / ctx / f"{size}@2x"   # every icon, for scaled screens
            lo = OUT / ctx / str(size)       # only icons Breeze has no big version of
            hi.mkdir(parents=True)
            lo.mkdir(parents=True)
            entries = sorted(src.glob("*.svg"))
            accent = ctx in ACCENT
            for f in entries:                # real files first, then aliases
                if f.is_symlink():
                    continue
                if (own := ours(f.stem, accent)) is not None:
                    (hi / f.name).write_text(own)
                    drawn.add(f.stem)
                elif f.stem not in EXCLUDE and monochrome(text := f.read_text()):
                    (hi / f.name).write_text(thicken(text, accent))
                    fallback.add(f.stem)
            for f in entries:
                if not f.is_symlink():
                    continue
                target = f.resolve()
                # Our own drawing of the alias name wins over the alias target.
                own = ours(f.stem, accent)
                if own is None and not (target.parent == src.resolve() and (hi / target.name).exists()):
                    own = ours(target.stem, accent)
                if own is not None:
                    (hi / f.name).write_text(own)
                elif target.parent == src.resolve() and (hi / target.name).exists():
                    (hi / f.name).symlink_to(target.name)
                elif target.stem not in EXCLUDE and target.exists() and monochrome(target.read_text()):
                    (hi / f.name).write_text(thicken(target.read_text(), accent))
            if ctx == "places" and (hi / "folder.svg").exists():
                (hi / "inode-directory.svg").symlink_to("folder.svg")
            for f in sorted(hi.iterdir()):
                if f.stem not in big:
                    (lo / f.name).symlink_to(f"../{hi.name}/{f.name}")
            (OUT / ctx / f"{size}@3x").symlink_to(hi.name)
            if any(lo.iterdir()):
                fixed.append((ctx, size, f"{ctx}/{size}", 1))
            else:
                lo.rmdir()
            scaled += [(ctx, size, f"{ctx}/{size}@2x", 2), (ctx, size, f"{ctx}/{size}@3x", 3)]

    head = f"""[Icon Theme]
Name=Golden Delicious
Comment=Soft line icons in the spirit of macOS, under Breeze's names
Inherits=WhiteSur-dark,breeze-dark,hicolor
FollowsColorScheme=true
DisplayDepth=32
SmallDefault=16
SmallSizes=16
ToolbarDefault=22
ToolbarSizes=16,22,24
MainToolbarDefault=22
MainToolbarSizes=16,22,24
PanelDefault=48
DialogDefault=32
DesktopDefault=48
Directories={",".join(d for *_, d, _ in fixed)}
ScaledDirectories={",".join(d for *_, d, _ in scaled)}
"""
    sections = "".join(
        f"\n[{d}]\nSize={size}\n" + (f"Scale={scale}\n" if scale > 1 else "")
        + f"Context={ctx.capitalize()}\nType=Fixed\n"
        for ctx, size, d, scale in fixed + scaled)
    (OUT / "index.theme").write_text(head + sections)
    shutil.copy("/usr/share/licenses/spdx/LGPL-3.0-or-later.txt", OUT / "LICENSE")
    (OUT / "README").write_text(
        "Golden Delicious icons, drawn for this theme (dev/icons/src). Names not drawn\n"
        "yet are modified Breeze icons (KDE, LGPL-3.0-or-later): monochrome icons\n"
        f"from breeze-dark with every line widened by {WIDTH} px. See dev/gen-icons.py.\n")
    fallback -= drawn
    print(f"{len(drawn)} drawn, {len(fallback)} thickened Breeze: {' '.join(sorted(fallback)[:30])}")


if __name__ == "__main__":
    main()
