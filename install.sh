#!/usr/bin/env bash
# Install the Golden Gate theme into ~/.local/share and apply it.
# Run inside a Plasma session. Safe to run again; each run backs up the
# config it changes first (see backup.sh, undo with restore.sh).
# Usage: ./install.sh [--layout]
#   --layout  also replace your panels with the theme's floating top panel
#             (drops your current panel setup and pinned launchers).
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
data=${XDG_DATA_HOME:-$HOME/.local/share}
config=${XDG_CONFIG_HOME:-$HOME/.config}

echo "backup: $("$here/backup.sh")"

mkdir -p "$data"
cp -r "$here/src/." "$data/"

# Global theme: colors, Plasma style and decoration (and the panel layout on request).
if [[ ${1:-} == --layout ]]; then
  plasma-apply-lookandfeel -a golden-gate --resetLayout
else
  plasma-apply-lookandfeel -a golden-gate
fi

# Things a global theme does not carry.
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnLeft XIA
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnRight ""
kwriteconfig6 --file kwinrc --group Plugins --key blurEnabled true
kwriteconfig6 --file kwinrc --group Plugins --key contrastEnabled true
qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true

# libadwaita takes the button order from GNOME's setting when one exists.
gsettings set org.gnome.desktop.wm.preferences button-layout "close,minimize,maximize:" 2>/dev/null || true

# GTK: Breeze picks up the KDE colors and decoration through kde-gtk-config;
# our CSS adds what it does not carry (separators, libadwaita buttons).
qdbus6 org.kde.kded6 /modules/gtkconfig org.kde.GtkConfig.setGtkTheme Breeze 2>/dev/null || true
for v in 3.0 4.0; do
  dir=$config/gtk-$v
  mkdir -p "$dir"
  kwriteconfig6 --file "$dir/settings.ini" --group Settings --key gtk-theme-name Breeze
  kwriteconfig6 --file "$dir/settings.ini" --group Settings --key gtk-decoration-layout "close,minimize,maximize:"
  cp "$here/gtk/golden-gate.css" "$dir/"
  grep -qxF "@import 'golden-gate.css';" "$dir/gtk.css" 2>/dev/null ||
    echo "@import 'golden-gate.css';" >>"$dir/gtk.css"
done

# Flatpak apps cannot see the host GTK config or themes: let them read the
# config, and give GTK3 apps Breeze from Flathub.
if command -v flatpak >/dev/null; then
  flatpak override --user --filesystem=xdg-config/gtk-3.0:ro --filesystem=xdg-config/gtk-4.0:ro
  flatpak install --user -y --noninteractive flathub org.gtk.Gtk3theme.Breeze >/dev/null 2>&1 ||
    echo "note: could not install org.gtk.Gtk3theme.Breeze for Flatpak GTK3 apps" >&2
fi
