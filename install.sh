#!/usr/bin/env bash
# Install the Golden Delicious theme into ~/.local/share and apply it.
# Run inside a Plasma session. Safe to run again; each run backs up the
# config it changes first (see backup.sh, undo with restore.sh).
# Usage: ./install.sh [--layout] [--tiles | --no-tiles] [-y | --yes]
#   --layout    also replace your panels with the theme's floating top panel
#               (drops your current panel setup and pinned launchers).
#   --tiles     set up the app icon tiles without asking
#   --no-tiles  leave them out (an existing setup is kept as it is)
#   -y, --yes   don't ask: go ahead, and set up the tiles unless --no-tiles
set -euo pipefail

layout=0 tiles=ask yes=0
for arg in "$@"; do
  case $arg in
    --layout) layout=1 ;;
    --tiles) tiles=yes ;;
    --no-tiles) tiles=no ;;
    -y | --yes) yes=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

here=$(cd "$(dirname "$0")" && pwd)
data=${XDG_DATA_HOME:-$HOME/.local/share}
config=${XDG_CONFIG_HOME:-$HOME/.config}
state=${XDG_STATE_HOME:-$HOME/.local/state}

log() { echo "==> $*"; }

if [[ $yes == 0 ]]; then
  echo "This installs the Golden Delicious theme for your user. It will:"
  echo "  - back up the config it changes to $state/golden-delicious/backups"
  echo "  - copy the theme into $data (window decoration, Plasma style,"
  echo "    global theme, color scheme, icons)"
  if [[ $layout == 1 ]]; then
    echo "  - apply it as global theme and replace your panels with its top panel"
  else
    echo "  - apply it as global theme (your panels stay)"
  fi
  echo "  - put the window buttons on the left and turn on blur in KWin"
  echo "  - set GTK to Breeze with the same buttons, add golden-delicious.css"
  echo "    to gtk-3.0 and gtk-4.0 and set GNOME's button layout"
  case $tiles in
    yes) echo "  - set up the app icon tiles (a systemd user service)" ;;
    ask) [[ -f $config/systemd/user/golden-delicious-tiles.service ]] &&
           echo "  - update the app icon tiles service" ||
           echo "  - ask whether to set up the app icon tiles (a systemd user service)" ;;
  esac
  echo "  - let Flatpak apps read the GTK config and install the Breeze GTK"
  echo "    theme for them from Flathub"
  echo
  echo "No warranty: this changes your desktop settings, at your own risk."
  echo "uninstall.sh and restore.sh undo it."
  if [[ ! -t 0 ]]; then
    echo "No terminal to ask: run with --yes to go ahead." >&2
    exit 1
  fi
  read -rp "Continue? [y/N] " answer
  [[ ${answer,,} == y* ]] || { echo "Nothing changed."; exit 0; }
  echo
fi

log "Backing up your config"
echo "    $("$here/backup.sh")"

log "Copying the theme into $data"
mkdir -p "$data"
# The theme used to be called Golden Gate: drop what an old install left.
for p in aurorae/themes/golden-gate plasma/desktoptheme/golden-gate plasma/look-and-feel/golden-gate \
  icons/golden-gate color-schemes/GoldenGate.colors; do
  rm -rf "${data:?}/$p"
done
for v in 3.0 4.0; do
  rm -f "$config/gtk-$v/golden-gate.css"
  [[ -f $config/gtk-$v/gtk.css ]] && sed -i "s/@import 'golden-gate.css';//; /^$/d" "$config/gtk-$v/gtk.css"
done
# Replace our own theme dirs whole, so files dropped from the repo don't linger.
(cd "$here/src" && find . -mindepth 2 -maxdepth 3 -name 'golden-delicious' -o -name 'GoldenDelicious.colors') |
  while read -r p; do rm -rf "${data:?}/$p"; done
cp -r "$here/src/." "$data/"

# Global theme: colors, Plasma style and decoration (and the panel layout on request).
log "Applying the global theme$([[ $layout == 1 ]] && echo " and its panel layout")"
if [[ $layout == 1 ]]; then
  plasma-apply-lookandfeel -a golden-delicious --resetLayout
else
  plasma-apply-lookandfeel -a golden-delicious
fi

# Things a global theme does not carry.
log "Window buttons on the left, blur on (KWin)"
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnLeft XIA
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnRight ""
kwriteconfig6 --file kwinrc --group Plugins --key blurEnabled true
kwriteconfig6 --file kwinrc --group Plugins --key contrastEnabled true
qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true

# libadwaita takes the button order from GNOME's setting when one exists.
log "Window buttons on the left for GTK and libadwaita apps"
gsettings set org.gnome.desktop.wm.preferences button-layout "close,minimize,maximize:" 2>/dev/null || true

# GTK: Breeze picks up the KDE colors and decoration through kde-gtk-config;
# our CSS adds what it does not carry (separators, libadwaita buttons).
log "GTK theme Breeze with golden-delicious.css"
qdbus6 org.kde.kded6 /modules/gtkconfig org.kde.GtkConfig.setGtkTheme Breeze 2>/dev/null || true
for v in 3.0 4.0; do
  dir=$config/gtk-$v
  mkdir -p "$dir"
  kwriteconfig6 --file "$dir/settings.ini" --group Settings --key gtk-theme-name Breeze
  kwriteconfig6 --file "$dir/settings.ini" --group Settings --key gtk-decoration-layout "close,minimize,maximize:"
  cp "$here/gtk/golden-delicious.css" "$dir/"
  # kde-gtk-config writes gtk.css without a final newline: start our line on its own.
  if ! grep -qF "@import 'golden-delicious.css';" "$dir/gtk.css" 2>/dev/null; then
    [[ -s $dir/gtk.css && -n $(tail -c1 "$dir/gtk.css") ]] && echo >>"$dir/gtk.css"
    echo "@import 'golden-delicious.css';" >>"$dir/gtk.css"
  fi
done

# App icons on squircle tiles: a user service draws them into the icon theme
# golden-delicious-apps and runs again whenever apps come or go. Asked for on
# the first install; an existing setup is updated without asking.
if [[ $tiles == ask ]]; then
  if [[ -f $config/systemd/user/golden-delicious-tiles.service || $yes == 1 ]]; then
    tiles=yes
  else  # a terminal is there: without one and without --yes the script stopped above
    echo "App icon tiles put every app icon on a macOS-style squircle tile. A small"
    echo "user service keeps them in step when you install or remove apps."
    read -rp "Set up the app icon tiles? [Y/n] " answer
    [[ ${answer,,} == n* ]] && tiles=no || tiles=yes
  fi
fi
if [[ $tiles == yes ]]; then
  log "Setting up the app icon tiles service and drawing the tiles"
  mkdir -p "$data/golden-delicious" "$config/systemd/user"
  cp "$here/tiles/golden-delicious-tiles.py" "$data/golden-delicious/"
  sed "s|@SCRIPT@|$data/golden-delicious/golden-delicious-tiles.py|" "$here/tiles/golden-delicious-tiles.service" \
    >"$config/systemd/user/golden-delicious-tiles.service"
  cp "$here/tiles/golden-delicious-tiles.path" "$config/systemd/user/"
  if systemctl --user daemon-reload 2>/dev/null; then
    systemctl --user enable --now golden-delicious-tiles.path
    systemctl --user enable golden-delicious-tiles.service
    systemctl --user restart golden-delicious-tiles.service ||
      echo "note: drawing the app icon tiles failed, see: journalctl --user -u golden-delicious-tiles" >&2
  else  # no systemd user session: draw them once
    python3 "$data/golden-delicious/golden-delicious-tiles.py" || echo "note: drawing the app icon tiles failed" >&2
  fi
fi

# Flatpak apps cannot see the host GTK config or themes: let them read the
# config, and give GTK3 apps Breeze from Flathub.
if command -v flatpak >/dev/null; then
  log "Flatpak: read access to the GTK config, Breeze GTK theme"
  flatpak override --user --filesystem=xdg-config/gtk-3.0:ro --filesystem=xdg-config/gtk-4.0:ro
  flatpak install --user -y --noninteractive flathub org.gtk.Gtk3theme.Breeze >/dev/null 2>&1 ||
    echo "note: could not install org.gtk.Gtk3theme.Breeze for Flatpak GTK3 apps" >&2
fi

echo
echo "Golden Delicious is installed. Log out and back in once so every app,"
echo "the panel and the icon caches pick up all of it."
