"""Colour folders like macOS for the big sizes (32 px and up), where Breeze has
its colour folders: a blue folder with the place's symbol embossed on the front.
The symbol comes from our own line drawing of the name (dev/icons/src), without
the folder outline those drawings carry. Breeze's colour variants (folder-red...)
become plain folders in the macOS tag colours.

Used by dev/gen-icons.py; needs rsvg-convert and magick (the harness image).
"""
import re
import subprocess
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
BREEZE = Path("/usr/share/icons/breeze/places/64")
# Non-folder names in Breeze's places that keep their Breeze icon.
NOT_FOLDERS = re.compile(r"^(certificate-server|favorites|library-music|network-.*|start-here.*|user-trash.*|folder-trash)$")

# (top, bottom) of the front panel, back panel and tab, symbol colour.
BLUE = ("#8fd0fb", "#5fb5f3", "#4ea3e6", "#2f7fc4")
TAGS = {  # macOS tag colours
    "red": "#ff6961", "orange": "#ffa94d", "yellow": "#ffd84d", "green": "#5fd77a",
    "cyan": "#6fd6f5", "blue": None, "violet": "#c58af0", "magenta": "#f57aa8",
    "brown": "#c4a27c", "grey": "#a8a8ae", "black": "#55555b",
}


def shade(hex_, f):
    """hex_ lightened (f > 0) or darkened (f < 0) by f."""
    c = [int(hex_[i:i + 2], 16) for i in (1, 3, 5)]
    c = [round(v + (255 - v) * f) if f > 0 else round(v * (1 + f)) for v in c]
    return "#" + "".join(f"{v:02x}" for v in c)


def palette(tag):
    base = TAGS.get(tag)
    if not base:
        return BLUE
    return (shade(base, 0.25), base, shade(base, -0.12), shade(base, -0.4))


def folder(colours, glyph=""):
    top, bottom, back, _ = colours
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
  <defs>
    <linearGradient id="front" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/>
    </linearGradient>
  </defs>
  <path fill="{back}" d="M8 28 a8 8 0 0 1 8 -8 H44 a8 8 0 0 1 5.6 2.3 L54 27 H112 a8 8 0 0 1 8 8 V100 a8 8 0 0 1 -8 8 H16 a8 8 0 0 1 -8 -8 Z"/>
  <path fill="url(#front)" d="M8 44 a8 8 0 0 1 8 -8 H112 a8 8 0 0 1 8 8 V100 a8 8 0 0 1 -8 8 H16 a8 8 0 0 1 -8 -8 Z"/>
  <path fill="#ffffff" fill-opacity="0.35" d="M16 36 H112 a8 8 0 0 1 8 8 V45 a8 8 0 0 0 -8 -8 H16 a8 8 0 0 0 -8 8 V44 a8 8 0 0 1 8 -8 Z"/>
{glyph}</svg>
"""


def strip_folder(text):
    """Our line drawing without the folder outline it may carry."""
    text = re.sub(r'\s*<path d="[^"]*H9\.3[^"]*"/>', "", text)
    text = re.sub(r'\s*<path d="M3\.5 10 H20\.5"/>', "", text)
    return text


def bbox(text):
    """Extent of a 24-grid drawing as (x0, y0, x1, y1), or None if empty."""
    with tempfile.TemporaryDirectory() as tmp:
        svg, png = Path(tmp) / "g.svg", Path(tmp) / "g.png"
        svg.write_text(text.replace('viewBox="0 0 24 24"', 'viewBox="0 0 24 24" width="240" height="240"'))
        subprocess.run(["rsvg-convert", str(svg), "-o", str(png)], check=True)
        out = subprocess.run(["magick", str(png), "-alpha", "extract", "-format", "%@", "info:"],
                             capture_output=True, text=True, check=True).stdout
    m = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", out)
    if not m or int(m[1]) >= 240:
        return None
    w, h, x, y = (int(v) / 10 for v in m.groups())
    return x, y, x + w, y + h


def emboss(text, colour):
    """The drawing as a symbol centred on the folder's front panel."""
    box = bbox(text)
    if not box:
        return ""
    x0, y0, x1, y1 = box
    size = 38 / max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    body = re.sub(r"<style.*?</style>\s*", "", text, flags=re.S)
    body = re.sub(r"^.*?<svg[^>]*>\s*|\s*</svg>\s*$", "", body, flags=re.S)
    body = body.replace(' class="ColorScheme-Text"', "").replace("currentColor", colour)
    # The symbol keeps its line weight at any symbol size: 1.6 of 24 at 64 px.
    body = re.sub(r'stroke-width="([\d.]+)"', lambda m: f'stroke-width="{float(m[1]) * 1.7 / size:.3f}"', body)
    return (f'  <g transform="translate(64 73) scale({size:.4f}) translate({-cx:.3f} {-cy:.3f})" opacity="0.85">\n'
            f"    {body}\n  </g>\n")


def names():
    """The Breeze names we draw as colour folders."""
    return [f.stem for f in sorted(BREEZE.glob("*.svg"))
            if not NOT_FOLDERS.match(f.stem)
            and (f.stem.startswith("folder") or f.stem in ("user-home", "user-desktop", "desktop", "stock_folder"))]


def build(out, ours):
    """Write the colour folders into out. ours(name) gives our drawing of a
    name (or None). Returns the names written."""
    out.mkdir(parents=True, exist_ok=True)
    done = []
    for name in names():
        f = BREEZE / f"{name}.svg"
        tag = name.removeprefix("folder-")
        if tag in TAGS:
            svg = folder(palette(tag))
        else:
            candidates = [name] + ([f.resolve().stem] if f.is_symlink() else [])
            text = next((t for n in candidates if (t := ours(n)) is not None), None)
            glyph = emboss(strip_folder(text), BLUE[3]) if text and name not in ("folder", "stock_folder", "folder-open") else ""
            svg = folder(BLUE, glyph)
        (out / f"{name}.svg").write_text(svg)
        done.append(name)
    (out / "inode-directory.svg").symlink_to("folder.svg")
    return done
