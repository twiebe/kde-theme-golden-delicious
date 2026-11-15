#!/usr/bin/env python3
"""Generate the Golden Gate icon theme: a few small symbolic icons drawn with
Phosphor Icons, everything else inherited.

Run from the repo root: python3 dev/gen-icons.py
Fetches Phosphor once into tmp/phosphor (gitignored, needs npm) and writes
into src/icons/golden-gate/.
"""
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/icons/golden-gate"
CACHE = ROOT / "tmp/phosphor"
PHOSPHOR = "@phosphor-icons/core@2.1.1"
WEIGHT = "bold"         # regular is a 1 px hairline at 16 px, like Breeze

INHERITS = "WhiteSur-dark,breeze-dark,hicolor"
SIZES = (16, 22, 24)    # only the symbolic sizes; larger ones come from Inherits
# Places and devices exist only as scaled (@2x, @3x) directories. KIconLoader
# matches those by exact size, so a 64 px folder in the file view still falls
# through to the inherited theme. A plain 16 px directory would be the best
# match for every size and replace the big folder icons too.
PLACE_SCALES = (2, 3)
ACTION_SCALES = (1, 2, 3)

# Colors only matter as fallbacks; KDE swaps in the color scheme.
STYLE = ('<style type="text/css" id="current-color-scheme">'
         '.ColorScheme-Text { color: #fcfcfc; } .ColorScheme-Highlight { color: #3daee9; } </style>')

TEXT, ACCENT = "ColorScheme-Text", "ColorScheme-Highlight"

# context dir: {freedesktop name: (phosphor name, color class)}
ICONS = {
    "places": {
        "user-home": ("house", ACCENT),
        "user-desktop": ("desktop", ACCENT),
        "folder": ("folder", ACCENT),
        "folder-open": ("folder-open", ACCENT),
        "folder-documents": ("file-text", ACCENT),
        "folder-download": ("arrow-circle-down", ACCENT),
        "folder-downloads": ("arrow-circle-down", ACCENT),
        "folder-music": ("music-note", ACCENT),
        "folder-pictures": ("image", ACCENT),
        "folder-videos": ("film-strip", ACCENT),
        "folder-network": ("globe-simple", ACCENT),
        "network-workgroup": ("globe-simple", ACCENT),
        "folder-open-recent": ("clock", ACCENT),
        "document-open-recent": ("clock", ACCENT),
        "user-trash": ("trash", ACCENT),
        "user-trash-full": ("trash", ACCENT),
    },
    "devices": {
        "drive-harddisk": ("hard-drive", ACCENT),
        "drive-harddisk-root": ("hard-drive", ACCENT),
        "drive-removable-media": ("hard-drive", ACCENT),
        "drive-removable-media-usb": ("usb", ACCENT),
        "drive-optical": ("disc", ACCENT),
        "media-optical": ("disc", ACCENT),
    },
    "actions": {
        "go-previous": ("caret-left", TEXT),
        "go-next": ("caret-right", TEXT),
        "go-up": ("arrow-up", TEXT),
        "go-down": ("arrow-down", TEXT),
        "go-home": ("house", TEXT),
        "view-list-icons": ("squares-four", TEXT),
        "view-list-details": ("list-bullets", TEXT),
        "view-list-tree": ("tree-view", TEXT),
        "view-split-left-right": ("square-split-horizontal", TEXT),
        "view-sidetree": ("sidebar-simple", TEXT),
        "view-preview": ("eye", TEXT),
        "view-visible": ("eye", TEXT),
        "view-hidden": ("eye-slash", TEXT),
        "view-visible-off": ("eye-slash", TEXT),
        "view-filter": ("funnel", TEXT),
        "view-refresh": ("arrow-clockwise", TEXT),
        "view-more": ("dots-three", TEXT),
        "view-more-horizontal": ("dots-three", TEXT),
        "edit-find": ("magnifying-glass", TEXT),
        "search": ("magnifying-glass", TEXT),
        "edit-clear": ("x-circle", TEXT),
        "edit-copy": ("copy", TEXT),
        "edit-cut": ("scissors", TEXT),
        "edit-paste": ("clipboard", TEXT),
        "edit-delete": ("trash", TEXT),
        "edit-rename": ("pencil-simple", TEXT),
        "edit-undo": ("arrow-counter-clockwise", TEXT),
        "edit-redo": ("arrow-clockwise", TEXT),
        "application-menu": ("list", TEXT),
        "open-menu": ("list", TEXT),
        "configure": ("gear", TEXT),
        "list-add": ("plus", TEXT),
        "list-remove": ("minus", TEXT),
        "tab-new": ("plus", TEXT),
        "tab-close": ("x", TEXT),
        "folder-new": ("folder-plus", TEXT),
        "document-new": ("file-plus", TEXT),
        "document-import": ("tray-arrow-down", TEXT),
        "get-hot-new-stuff": ("sparkle", TEXT),
    },
}

CONTEXTS = {"places": "Places", "devices": "Devices", "actions": "Actions"}


def fetch():
    src = CACHE / "package/assets" / WEIGHT
    if not src.is_dir():
        CACHE.mkdir(parents=True, exist_ok=True)
        tgz = subprocess.run(["npm", "pack", PHOSPHOR, "--silent"], cwd=CACHE,
                             check=True, capture_output=True, text=True).stdout.strip()
        subprocess.run(["tar", "xzf", tgz], cwd=CACHE, check=True)
    return src


def icon(src, name, cls):
    suffix = "" if WEIGHT == "regular" else f"-{WEIGHT}"
    body = (src / f"{name}{suffix}.svg").read_text()
    paths = re.findall(r'<path d="([^"]+)"', body)
    assert paths, name
    shapes = "".join(f'<path class="{cls}" style="fill:currentColor; fill-opacity:1; stroke:none" d="{d}"/>'
                     for d in paths)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">'
            f'<defs>{STYLE}</defs>{shapes}</svg>\n')


def dirname(ctx, size, scale):
    return f"{ctx}/{size}" + (f"@{scale}x" if scale > 1 else "")


def main():
    src = fetch()
    if OUT.exists():
        shutil.rmtree(OUT)
    sections = []
    for ctx, icons in ICONS.items():
        for scale in (PLACE_SCALES if ctx in ("places", "devices") else ACTION_SCALES):
            for size in SIZES:
                d = dirname(ctx, size, scale)
                (OUT / d).mkdir(parents=True)
                for fd, (ph, cls) in icons.items():
                    (OUT / d / f"{fd}.svg").write_text(icon(src, ph, cls))
                sections.append((d, size, scale, CONTEXTS[ctx]))

    lines = ["[Icon Theme]", "Name=Golden Gate",
             "Comment=Phosphor symbolic icons on top of the inherited theme",
             f"Inherits={INHERITS}", "FollowsColorScheme=true",
             "DisplayDepth=32", "SmallDefault=16", "SmallSizes=16",
             "ToolbarDefault=22", "ToolbarSizes=16,22,24",
             "MainToolbarDefault=22", "MainToolbarSizes=16,22,24",
             "PanelDefault=48", "DialogDefault=32", "DesktopDefault=48",
             "Directories=" + ",".join(s[0] for s in sections if s[2] == 1),
             "ScaledDirectories=" + ",".join(s[0] for s in sections if s[2] > 1), ""]
    for d, size, scale, ctx in sections:
        lines += [f"[{d}]", f"Size={size}"] + ([f"Scale={scale}"] if scale > 1 else []) + \
                 [f"Context={ctx}", "Type=Fixed", ""]
    (OUT / "index.theme").write_text("\n".join(lines))
    shutil.copy(src.parent.parent / "LICENSE", OUT / "LICENSE")


if __name__ == "__main__":
    main()
