# Golden Gate KDE Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A lean Plasma 6 theme with the feel of macOS Golden Gate: traffic-light window decoration, soft floating top panel without boxy task highlights, dark colors, blur.

**Architecture:** Data files only, grouped per KDE theme kind under `src/`. `install.sh` copies them to `~/.local/share` and applies them. A headless harness (`dev/shot.sh`) starts `kwin_wayland --virtual` + `plasmashell` and takes a screenshot; screenshots are the test.

**Tech Stack:** Plasma 6 look-and-feel package, Aurorae SVG decoration, Plasma Style (desktoptheme) SVGs, KDE color scheme, bash.

**Spec:** `docs/superpowers/specs/2026-11-14-golden-gate-kde-theme-design.md`

## Global Constraints

- Target Plasma 6.8; test on Debian Plasma 6.3.6 headless.
- No C++, no Kvantum, no icon/cursor theme, no global menu, no dock.
- Theme id everywhere: `golden-gate` (color scheme file `GoldenGate.colors`).
- Traffic lights left: close `#FF5F57`, minimize `#FEBC2E`, maximize `#28C840`, 12 px diameter, 8 px gap.
- Window corner radius 12 px. Accent blue `#0A84FF`. Window bg `#2B2B2D`, view bg `#1E1E1E`, text `#F2F2F7`.
- Panel: top, floating, slightly translucent, blurred. Task states rounded (radius ~10 px), low contrast; dot indicator for running apps.

## Review Focus

- Re-running `install.sh` on a configured system: must be idempotent, no duplicate panels. Test in Task 5 (run twice, count panels).
- HiDPI 2x: SVGs must stay sharp (vector only, no embedded bitmaps). Check in Task 3 via `QT_SCALE_FACTOR=2` screenshot.
- Inactive windows: traffic lights turn grey, title stays readable. Screenshot with two windows in Task 3.
- Plasma 6.8 drift: panel padding may differ; keep SVG margins in `hint-*` elements, not hard-coded layout JS. Covered by Task 4 structure.
- Revert: `plasma-apply-lookandfeel -a org.kde.breezedark.desktop` restores stock look. Check in Task 5.

---

## File Structure

```
dev/shot.sh                                   headless session + screenshot
install.sh                                    copy + apply
src/color-schemes/GoldenGate.colors
src/aurorae/themes/golden-gate/{metadata.desktop,golden-gaterc,decoration.svg,close.svg,minimize.svg,maximize.svg,restore.svg}
src/plasma/desktoptheme/golden-gate/{metadata.json,plasmarc,widgets/panel-background.svg,widgets/tasks.svg}
src/plasma/look-and-feel/golden-gate/{metadata.json,contents/defaults,contents/layouts/org.kde.plasma.desktop-layout.js}
```

`src/` mirrors `~/.local/share/`, so `install.sh` is one `cp -r src/. ~/.local/share/`.

### Task 1: Headless screenshot harness

**Files:** Create `dev/shot.sh`

**Interfaces:** Produces `dev/shot.sh <out.png> [app...]`: starts dbus session, `kwin_wayland --virtual --width 1600 --height 1000 --xwayland`, `plasmashell`, launches given apps, waits ~8 s, `spectacle -b -n -f -o <out.png>`, kills session. Exit 0 and non-empty PNG on success.

- [ ] Step 1: Write `dev/shot.sh`.
- [ ] Step 2: Run `dev/shot.sh tmp/shots/stock.png konsole`. Expected: PNG shows Breeze panel and a Konsole window. Read the image to confirm.
- [ ] Step 3: Commit `feat(dev): add headless screenshot harness`.

### Task 2: Color scheme + install script

**Files:** Create `src/color-schemes/GoldenGate.colors`, `install.sh`

**Interfaces:** Produces `install.sh` (no args): `cp -r src/. ~/.local/share/`, then apply steps added by later tasks. This task applies `plasma-apply-colorscheme GoldenGate`.

- [ ] Step 1: Write `GoldenGate.colors` (copy BreezeDark structure, set Global Constraints colors, `[General] ColorScheme=GoldenGate`).
- [ ] Step 2: Write `install.sh`; `shellcheck install.sh` clean.
- [ ] Step 3: Run harness with `install.sh` before plasmashell; check `kreadconfig6 --group General --key ColorScheme` prints `GoldenGate`; screenshot shows new colors.
- [ ] Step 4: Commit `feat: add dark color scheme and installer`.

### Task 3: Aurorae decoration

**Files:** Create `src/aurorae/themes/golden-gate/*`

**Interfaces:** Theme name for kwinrc: `__aurorae__svg__golden-gate`. `install.sh` sets `kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae` and `--key theme __aurorae__svg__golden-gate`, `ButtonsOnLeft=XIA`, `ButtonsOnRight=` empty, then `qdbus6 org.kde.KWin /KWin reconfigure`.

- [ ] Step 1: `decoration.svg` with `decoration-*` (active) and `decoration-inactive-*` frames, 12 px top corner radius, titlebar fill = window bg, `shadow-*` elements soft.
- [ ] Step 2: Button SVGs: `active`, `inactive` (grey `#5A5A5E`), `hover` (glyph shown), `pressed` elements; 12 px circle in 20 px box.
- [ ] Step 3: `golden-gaterc`: `TitleHeight=28`, `ButtonWidth=20`, `ButtonSpacing=0`, `PaddingLeft=8`, `TitleAlignment=Center`.
- [ ] Step 4: Screenshot with two Konsole windows, also at `QT_SCALE_FACTOR=2`. Expected: traffic lights left, grey on inactive window, rounded top corners, crisp at 2x.
- [ ] Step 5: Commit `feat: add traffic-light window decoration`.

### Task 4: Plasma style (panel + tasks)

**Files:** Create `src/plasma/desktoptheme/golden-gate/*`

**Interfaces:** Style name `golden-gate`, `metadata.json` with `"X-Plasma-API": "5.0"` style fallback `default` (Breeze) so only the two widgets are overridden. `install.sh` runs `plasma-apply-desktoptheme golden-gate`.

- [ ] Step 1: `widgets/panel-background.svg`: frame with ~14 px corners, fill `#1E1E1E` at ~70 % opacity, `hint-*` margins, `mask-*` elements for blur region, `shadow-*`.
- [ ] Step 2: `widgets/tasks.svg`: `normal` empty; `hover`, `focus`, `attention`, `minimized` as rounded rects (radius 10) with white at 8–15 % opacity; `north-*`/`south-*` variants identical. Running indicator: small 4 px dot via `normal`-prefixed bottom element.
- [ ] Step 3: Screenshot with panel at top floating and two apps open. Expected: no boxy highlights, soft rounded hover/active, panel blurred and rounded.
- [ ] Step 4: Commit `feat: add plasma style with soft panel and task states`.

### Task 5: Global theme + blur

**Files:** Create `src/plasma/look-and-feel/golden-gate/*`; modify `install.sh`

**Interfaces:** `plasma-apply-lookandfeel -a golden-gate` sets color scheme, decoration, plasma style and layout. Layout JS: one top panel, `floating = true`, height 44, launcher + icontasks + spacer + systemtray + digitalclock. `install.sh` ends with `plasma-apply-lookandfeel -a golden-gate --resetLayout` and `kwriteconfig6 --file kwinrc --group Plugins --key blurEnabled true`.

- [ ] Step 1: Write `metadata.json`, `contents/defaults`, layout JS.
- [ ] Step 2: Fresh harness run: `install.sh`, screenshot. Expected: full look in one go.
- [ ] Step 3: Run `install.sh` twice; screenshot shows exactly one panel.
- [ ] Step 4: `plasma-apply-lookandfeel -a org.kde.breezedark.desktop` restores Breeze (screenshot).
- [ ] Step 5: Add short `README.md` (install, revert). Commit `feat: add golden-gate global theme`.
