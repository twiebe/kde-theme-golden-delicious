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

`--layout` drops your current panel setup and pinned launchers. Log out and
back in afterwards so every app picks the theme up.

GTK apps follow too: Breeze GTK takes the colors and window buttons from KDE,
and `gtk/golden-gate.css` adds the traffic lights for libadwaita apps and hides
separators.

## Backups

Each install first saves the config it touches (kdeglobals, kwinrc, plasma
rc files, kdedefaults, gtk-3.0, gtk-4.0) to
`~/.local/state/golden-gate/backups/`. The newest 5 are kept; set
`GG_KEEP_BACKUPS` to change that.

```sh
./restore.sh --list   # list backups, newest last
./restore.sh          # restore the newest one
./restore.sh <dir>    # restore that one
```

A restore backs up the current state first, so it can be undone the same way.

## Revert

```sh
./uninstall.sh            # back to Breeze Dark, Breeze window buttons
./uninstall.sh --layout   # also reset the panels (if you installed with --layout)
```

## Develop

The SVGs under `src/aurorae` and `src/plasma/desktoptheme` are generated:
edit `dev/gen-aurorae.py` or `dev/gen-plasma.py` and rerun them.
`dev/gen-icons.py` builds the icon theme in `src/icons/golden-gate` from
Phosphor Icons (bold), fetched once into `tmp/phosphor` with npm.

To see the result without touching your desktop, render a screenshot in a
pinned headless Plasma 6.8 (needs Docker and `/dev/dri`):

```sh
dev/shot-docker.sh tmp/shots/out.png --install dolphin konsole
```
