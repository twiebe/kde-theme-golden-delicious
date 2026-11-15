#!/usr/bin/env bash
# Switch back to Breeze Dark, undo what install.sh set outside the global theme
# and remove the theme's files. Your backups stay (see restore.sh).
# Usage: ./uninstall.sh [--layout] [-y | --yes]
#   --layout  also reset the panels to the Breeze default (use it if you
#             installed with --layout).
#   -y, --yes don't ask, go ahead
set -euo pipefail

layout=0 yes=0
for arg in "$@"; do
  case $arg in
    --layout) layout=1 ;;
    -y | --yes) yes=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

config=${XDG_CONFIG_HOME:-$HOME/.config}
data=${XDG_DATA_HOME:-$HOME/.local/share}
state=${XDG_STATE_HOME:-$HOME/.local/state}

log() { echo "==> $*"; }

if [[ $yes == 0 ]]; then
  echo "This removes the Golden Delicious theme for your user. It will:"
  if [[ $layout == 1 ]]; then
    echo "  - switch to Breeze Dark and reset your panels to Breeze's default"
  else
    echo "  - switch to Breeze Dark (your panels stay)"
  fi
  echo "  - put the window buttons back on the right (KDE, GTK and libadwaita)"
  echo "  - stop and remove the app icon tiles service"
  echo "  - remove golden-delicious.css from gtk-3.0 and gtk-4.0"
  echo "  - take back the Flatpak read access to the GTK config"
  echo "  - delete the theme's files from $data"
  echo "Your backups in $state/golden-delicious/backups stay."
  echo
  echo "No warranty: this changes your desktop settings, at your own risk."
  if [[ ! -t 0 ]]; then
    echo "No terminal to ask: run with --yes to go ahead." >&2
    exit 1
  fi
  read -rp "Continue? [y/N] " answer
  [[ ${answer,,} == y* ]] || { echo "Nothing changed."; exit 0; }
  echo
fi

# Breeze Dark brings back its colours, Plasma style, decoration and icons.
log "Switching to Breeze Dark$([[ $layout == 1 ]] && echo " and resetting the panels")"
if [[ $layout == 1 ]]; then
  plasma-apply-lookandfeel -a org.kde.breezedark.desktop --resetLayout
else
  plasma-apply-lookandfeel -a org.kde.breezedark.desktop
fi

# Window buttons back on the right (Breeze's default order).
log "Window buttons back on the right"
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnLeft --delete
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnRight --delete
qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true
gsettings reset org.gnome.desktop.wm.preferences button-layout 2>/dev/null || true

# App icon tiles.
log "Removing the app icon tiles service"
systemctl --user disable --now golden-delicious-tiles.path golden-delicious-tiles.service 2>/dev/null || true
rm -f "$config/systemd/user/golden-delicious-tiles."{service,path}
systemctl --user daemon-reload 2>/dev/null || true

# GTK: our CSS and the button order install.sh wrote.
log "Removing golden-delicious.css from the GTK config"
for v in 3.0 4.0; do
  rm -f "$config/gtk-$v/golden-delicious.css"
  if [[ -f $config/gtk-$v/gtk.css ]]; then
    # Also when it ended up on kde-gtk-config's line (no final newline there).
    sed -i "s/@import 'golden-delicious.css';//; /^$/d" "$config/gtk-$v/gtk.css"
  fi
  if [[ -f $config/gtk-$v/settings.ini ]]; then
    kwriteconfig6 --file "$config/gtk-$v/settings.ini" --group Settings --key gtk-decoration-layout --delete
  fi
done
qdbus6 org.kde.kded6 /modules/gtkconfig org.kde.GtkConfig.setGtkTheme Breeze 2>/dev/null || true

# Flatpak: take back only the read access to the GTK config that install.sh
# gave (and the blocks an older uninstall.sh wrote instead). `flatpak override
# --nofilesystem` would not undo it but forbid the folders outright.
log "Taking back the Flatpak access to the GTK config"
overrides=$data/flatpak/overrides/global
if [[ -f $overrides ]]; then
  sed -i -E '/^filesystems=/{:a;s/([=;])!?xdg-config\/gtk-[34]\.0(:ro)?(;|$)/\1/;ta;/^filesystems=$/d}' "$overrides"
fi

# The theme's files.
log "Deleting the theme's files"
rm -rf "${data:?}"/aurorae/themes/golden-delicious "${data:?}"/plasma/desktoptheme/golden-delicious \
  "${data:?}"/plasma/look-and-feel/golden-delicious "${data:?}"/icons/golden-delicious \
  "${data:?}"/icons/golden-delicious-apps "${data:?}"/color-schemes/GoldenDelicious.colors \
  "${data:?}"/golden-delicious

echo
echo "Golden Delicious is removed. Log out and back in once so every app picks"
echo "up Breeze again. Backups of your old config are still in"
echo "$state/golden-delicious/backups (see restore.sh)."
