#!/usr/bin/env python3
"""Put every installed app's icon on a macOS-style squircle tile.

Reads the .desktop files (system, ~/.local, Flatpak), finds each app icon the
way the icon theme spec does (breeze-dark, breeze, hicolor) and writes a tiled
copy under the same name into the icon theme golden-delicious-apps, which the
Golden Delicious icon theme inherits first. The app's own icon file stays
untouched. An icon that is already a filled square is masked to the squircle;
anything else sits smaller on a light tile, like macOS in light mode.

Plain Python, no extra modules: the output is SVG that embeds the original
(inline SVG, or a PNG as data URI). Squareness is read from the app's PNG when
it ships one, else from rsvg-convert or ImageMagick if installed; without them an
app with SVG only counts as not square.

Runs again on its own when apps come and go (golden-delicious-tiles.path).
Only redraws what changed; drops tiles of apps that are gone.

  golden-delicious-tiles.py [--force]
"""
import base64
import gzip
import os
import re
import shutil
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import zlib
from configparser import ConfigParser
from pathlib import Path

HOME = Path.home()
DATA_HOME = Path(os.environ.get("XDG_DATA_HOME") or HOME / ".local/share")
DATA_DIRS = [Path(p) for p in (os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share").split(":") if p]
FLATPAK = [DATA_HOME / "flatpak/exports/share", Path("/var/lib/flatpak/exports/share")]
DATA = [DATA_HOME] + [d for d in FLATPAK + DATA_DIRS if d != DATA_HOME]
DATA = list(dict.fromkeys(DATA))  # keep order, drop repeats

THEME = DATA_HOME / "icons/golden-delicious-apps"
OUT = THEME / "scalable/apps"
SOURCES = ["breeze-dark", "breeze", "hicolor"]

SIZE = 256
TILE = (14, 242)          # tile edges inside the 256 canvas, like a Breeze app icon's margin
INNER = 0.72              # how much of the tile a non-square icon's content may fill
OVERSCAN = 1.03           # a square icon is drawn a little past the tile so no corner shows
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
for prefix, uri in [("", SVG_NS), ("xlink", XLINK_NS),
                    ("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"),
                    ("inkscape", "http://www.inkscape.org/namespaces/inkscape")]:
    ET.register_namespace(prefix, uri)


# --- finding the apps and their icons --------------------------------------

def desktop_icons():
    """Icon names of the apps that show up somewhere (menu, task manager)."""
    names = set()
    for root in DATA:
        apps = root / "applications"
        if not apps.is_dir():
            continue
        for f in apps.rglob("*.desktop"):
            cp = ConfigParser(interpolation=None, strict=False)
            try:
                cp.read(f, encoding="utf-8")
                e = cp["Desktop Entry"]
            except Exception:
                continue
            icon = e.get("Icon", "").strip()
            if not icon or icon.startswith("/") or e.get("NoDisplay", "").lower() == "true":
                continue
            names.add(re.sub(r"\.(svgz?|png)$", "", icon))
    return names


def size_of(path):
    """Directory size of an icon file: 'scalable' counts as biggest."""
    for part in reversed(path.parts[:-1]):
        if part == "scalable":
            return 10_000
        m = re.fullmatch(r"(\d+)(?:x\d+)?(?:@(\d+)x?)?", part)
        if m:
            return int(m[1]) * int(m[2] or 1)
    return 0


def index_icons():
    """name -> list of app icon files, first theme that has the name wins."""
    found = {}
    for theme in SOURCES:
        here = {}
        for root in DATA + [HOME / ".icons"]:
            d = root / "icons" / theme if root != HOME / ".icons" else root / theme
            if not d.is_dir():
                continue
            for dirpath, _, files in os.walk(d, followlinks=True):
                if "/apps" not in dirpath:
                    continue
                for f in files:
                    m = re.fullmatch(r"(.+)\.(svgz?|png)", f)
                    if m:
                        here.setdefault(m[1], []).append(Path(dirpath) / f)
        for name, files in here.items():
            found.setdefault(name, files)
    for root in DATA:
        pix = root / "pixmaps"
        if pix.is_dir():
            for f in pix.iterdir():
                m = re.fullmatch(r"(.+)\.(svgz?|png)", f.name)
                if m:
                    found.setdefault(m[1], [f])
    return found


# --- reading a PNG (stdlib only) --------------------------------------------

def rasterise(svg):
    """A 64 px PNG of an SVG file, if a tool for that is installed."""
    for cmd in (["rsvg-convert", "-w", "64", "-h", "64", str(svg)],
                ["magick", "-background", "none", "-density", "300", str(svg), "-resize", "64x64", "png:-"]):
        if shutil.which(cmd[0]):
            try:
                return subprocess.run(cmd, capture_output=True, timeout=20, check=True).stdout
            except (subprocess.SubprocessError, OSError):
                pass
    return None


def alpha_box(data):
    """Content box of PNG data as fractions (x0, y0, x1, y1) and how fully its
    edges are covered (0..1), or None if the PNG can't be read here."""
    if not data or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    pos, idat, trns, ihdr = 8, b"", None, None
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + n]
        if kind == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", chunk)
        elif kind == b"tRNS":
            trns = chunk
        elif kind == b"IDAT":
            idat += chunk
        pos += 12 + n
    if not ihdr:
        return None
    w, h, depth, ctype, _, _, interlace = ihdr
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(ctype)
    if not channels or interlace:
        return None
    raw = zlib.decompress(idat)
    bpp = max(1, channels * depth // 8)               # filter step in bytes
    stride = (w * channels * depth + 7) // 8
    prev = bytearray(stride)
    mask = []
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        prev = line
        if depth < 8:  # palette or grey packed several to a byte
            per = 8 // depth
            vals = [(line[x // per] >> (8 - depth * (x % per + 1))) & ((1 << depth) - 1) for x in range(w)]
        else:
            vals = line[::depth // 8]  # 16 bit: the high byte is enough
        if ctype == 6:
            row = vals[3::4]
        elif ctype == 4:
            row = vals[1::2]
        elif ctype == 3 and trns:
            row = [trns[v] if v < len(trns) else 255 for v in vals]
        else:
            row = [255] * w
        mask.append([v > 128 for v in row])
    xs = [x for row in mask for x, v in enumerate(row) if v]
    ys = [y for y, row in enumerate(mask) if any(row)]
    if not xs:
        return None
    x0, x1, y0, y1 = min(xs), max(xs) + 1, min(ys), max(ys) + 1
    # Fill measured as the least covered of four lines just inside the box's
    # edges: a filled (rounded) square covers all four nearly whole, a shape
    # with feet, a round top or an open side does not.
    ix, iy = max(1, (x1 - x0) // 20), max(1, (y1 - y0) // 20)
    lines = [[mask[y0 + iy][x] for x in range(x0, x1)], [mask[y1 - 1 - iy][x] for x in range(x0, x1)],
             [mask[y][x0 + ix] for y in range(y0, y1)], [mask[y][x1 - 1 - ix] for y in range(y0, y1)]]
    edges = min(sum(line) / len(line) for line in lines)
    return (x0 / w, y0 / h, x1 / w, y1 / h), edges


def is_square(box, edges):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    return edges >= 0.75 and 0.9 <= w / h <= 1.1 and min(w, h) >= 0.6


# --- drawing -----------------------------------------------------------------

def squircle(x0, x1, n=5, steps=96):
    """Superellipse |x|^n + |y|^n = 1 over the square x0..x1, like a macOS tile."""
    import math
    c, r = (x0 + x1) / 2, (x1 - x0) / 2
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        ct, st = math.cos(t), math.sin(t)
        pts.append((c + r * math.copysign(abs(ct) ** (2 / n), ct),
                    c + r * math.copysign(abs(st) ** (2 / n), st)))
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"


def svg_body(path):
    """Inner XML and view box of an SVG file, or None."""
    data = path.read_bytes()
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return None
    vb = root.get("viewBox")
    if vb:
        box = [float(v) for v in re.split(r"[\s,]+", vb.strip())]
    else:
        num = lambda v: float(re.match(r"[\d.]+", v or "0")[0] or 0)
        box = [0, 0, num(root.get("width")), num(root.get("height"))]
    if box[2] <= 0 or box[3] <= 0:
        return None
    return "".join(ET.tostring(c, encoding="unicode") for c in root), box


def place(box, target):
    """Transform mapping box (x, y, w, h) onto target (x, y, size), centred."""
    x, y, w, h = box
    tx, ty, size = target
    s = size / max(w, h)
    return (f"translate({tx + (size - w * s) / 2:.3f} {ty + (size - h * s) / 2:.3f}) "
            f"scale({s:.5f}) translate({-x:.3f} {-y:.3f})")


def tile(files):
    vector = [f for f in files if f.suffix in (".svg", ".svgz")]
    pngs = sorted((f for f in files if f.suffix == ".png"), key=size_of)
    probe = next((f for f in pngs if size_of(f) >= 48), pngs[-1] if pngs else None)
    if probe:
        shape = alpha_box(probe.read_bytes())
    elif vector:
        shape = alpha_box(rasterise(max(vector, key=size_of)))
    else:
        shape = None
    square = shape and is_square(*shape)

    if vector:
        body = svg_body(max(vector, key=size_of))
        if not body:
            return None
        inner, (vx, vy, vw, vh) = body
    elif pngs:
        big = pngs[-1]
        b64 = base64.b64encode(big.read_bytes()).decode()
        vx, vy, vw, vh = 0, 0, 1, 1
        inner = f'<image width="1" height="1" preserveAspectRatio="none" xlink:href="data:image/png;base64,{b64}"/>'
    else:
        return None

    # Content box in the source's own units: from the PNG probe if there is one.
    if shape:
        (fx0, fy0, fx1, fy1), _ = shape
        content = (vx + fx0 * vw, vy + fy0 * vh, (fx1 - fx0) * vw, (fy1 - fy0) * vh)
    else:
        content = (vx, vy, vw, vh)

    t0, t1 = TILE
    span = t1 - t0
    sq = squircle(t0, t1)
    head = (f'<svg xmlns="{SVG_NS}" xmlns:xlink="{XLINK_NS}" viewBox="0 0 {SIZE} {SIZE}" '
            f'width="{SIZE}" height="{SIZE}">\n  <defs>\n'
            # A mask, not a clipPath: Qt ignores clip-path on a group.
            f'    <mask id="gdt-clip" maskUnits="userSpaceOnUse" x="0" y="0" width="{SIZE}" height="{SIZE}">'
            f'<path d="{sq}" fill="#fff"/></mask>\n')
    if square:
        big = span * OVERSCAN
        off = t0 - (big - span) / 2
        return (head + "  </defs>\n"
                f'  <g mask="url(#gdt-clip)">\n    <g transform="{place(content, (off, off, big))}">{inner}</g>\n  </g>\n</svg>\n')
    size = span * INNER
    off = t0 + (span - size) / 2
    return (head +
            '    <linearGradient id="gdt-tile" x1="0" y1="0" x2="0" y2="1">\n'
            '      <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e2e2e6"/>\n'
            '    </linearGradient>\n  </defs>\n'
            f'  <path d="{sq}" fill="url(#gdt-tile)"/>\n'
            f'  <path d="{sq}" fill="none" stroke="#000000" stroke-opacity="0.10" stroke-width="1.5"/>\n'
            f'  <g transform="{place(content, (off, off, size))}">{inner}</g>\n</svg>\n')


INDEX = """[Icon Theme]
Name=Golden Delicious app tiles
Comment=App icons on squircle tiles, made by golden-delicious-tiles.py
Hidden=true
Directories=scalable/apps

[scalable/apps]
Size=256
MinSize=8
MaxSize=1024
Type=Scalable
Context=Applications
"""


def main():
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    (THEME / "index.theme").write_text(INDEX)
    me = Path(__file__).stat().st_mtime
    icons = index_icons()
    wanted, made, failed = set(), 0, []
    for name in sorted(desktop_icons()):
        files = icons.get(name)
        if not files:
            continue
        out = OUT / f"{name}.svg"
        wanted.add(out.name)
        newest = max([me] + [f.stat().st_mtime for f in files if f.exists()])
        if not force and out.exists() and out.stat().st_mtime >= newest:
            continue
        try:
            svg = tile(files)
        except Exception as e:  # one broken icon must not stop the rest
            svg, err = None, e
        if svg:
            out.write_text(svg)
            made += 1
        else:
            failed.append(name)
            out.unlink(missing_ok=True)
            wanted.discard(out.name)
    gone = [f for f in OUT.iterdir() if f.name not in wanted]
    for f in gone:
        f.unlink()
    if made or gone:
        os.utime(THEME)  # icon caches (KIconLoader, GTK) look at the theme dir's time
        os.utime(THEME.parent)
        if shutil.which("dbus-send"):  # running KDE apps reload their icons
            subprocess.run(["dbus-send", "--session", "--type=signal", "/KIconLoader",
                            "org.kde.KIconLoader.iconChanged", "int32:0"], capture_output=True)
    print(f"{len(wanted)} app tiles, {made} redrawn, {len(gone)} dropped"
          + (f", skipped: {' '.join(failed)}" if failed else ""))


if __name__ == "__main__":
    main()
