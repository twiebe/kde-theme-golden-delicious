# Golden Gate KDE theme: design

## Intent

A lean KDE Plasma 6 theme that gives the impression of macOS Golden Gate (27):
proportions, window decorations, blur. 80/20, not pixel-perfect. Lowest
possible complexity: config, SVG and color files only, no C++.

Target: Plasma 6.8 (user's machine). Tested in a headless Plasma 6.3.6 in the
dev container (`kwin_wayland --virtual` + `plasmashell`, screenshots via
spectacle). Theme formats are unchanged across 6.x; small visual drift is
accepted.

## Reference (from the Golden Gate VM, logical px)

- No separate titlebar look: titlebar blends with window content.
- Traffic lights left, ~12 px, 8 px gap. Window corner radius ~12 px, soft wide shadow.
- Translucent, blurred surfaces (sidebar, menubar, dock); opaque dark content.
- Flat controls, neutral greys, blue system accent.

## Goals

- Window decoration with traffic-light buttons and rounded corners.
- Keep the user's current panel concept: one floating, slightly translucent
  panel at the top. Replace the boxy (Windows-like) task highlights with soft
  rounded hover/active shapes and a small dot under running apps.
- Dark color scheme, KWin blur on.
- Installable by one script.

## Non-goals

Global menu bar, bottom dock, icon theme, cursor, Kvantum/app style, light
variant, KDE Store packaging.

## Approaches

- A, picked: test in local Debian Plasma 6.3 headless. Available now, enough for 80/20.
- B: Docker with Arch/Fedora on Plasma 6.8. Exact version, more setup, docker
  daemon not available. Fallback if the user's screenshots drift noticeably.

## Parts

1. Global theme `golden-gate` (look-and-feel package): sets the pieces below
   and the panel layout.
2. Aurorae decoration: traffic lights left, slim titlebar in window color,
   12 px radius.
3. Plasma style based on Breeze, overriding only `widgets/panel-background.svg`
   (rounded, translucent) and `widgets/tasks.svg` (soft rounded states, dot
   indicator).
4. Dark color scheme `GoldenGate.colors`.
5. `install.sh`: copies into `~/.local/share`, applies with
   `plasma-apply-lookandfeel` and friends, enables blur.

## Left to the builder

Exact colors, SVG geometry, shadow tuning.
