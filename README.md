# Golden Gate for KDE Plasma

A lean Plasma 6 theme with the feel of macOS Golden Gate: traffic-light window
buttons, rounded corners with a soft shadow, a floating translucent top panel
with soft rounded task highlights, and a dark color scheme with blur.

## Install

Run inside a Plasma session:

```sh
./install.sh            # keep your panels, change only the look
./install.sh --layout   # also replace your panels with the theme's top panel
```

`--layout` drops your current panel setup and pinned launchers.

## Revert

```sh
./uninstall.sh            # back to Breeze Dark, Breeze window buttons
./uninstall.sh --layout   # also reset the panels (if you installed with --layout)
```

## Develop

The SVGs under `src/aurorae` and `src/plasma/desktoptheme` are generated:
edit `dev/gen-aurorae.py` or `dev/gen-plasma.py` and rerun them.

To see the result without touching your desktop, render a screenshot in a
pinned headless Plasma 6.8 (needs Docker and `/dev/dri`):

```sh
dev/shot-docker.sh tmp/shots/out.png --install dolphin konsole
```
