#!/usr/bin/env bash
# Switch back to Breeze Dark and undo what install.sh set outside the global theme.
# Usage: ./uninstall.sh [--layout]
#   --layout  also reset the panels to the Breeze default (use it if you
#             installed with --layout).
set -euo pipefail

if [[ ${1:-} == --layout ]]; then
  plasma-apply-lookandfeel -a org.kde.breezedark.desktop --resetLayout
else
  plasma-apply-lookandfeel -a org.kde.breezedark.desktop
fi

kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnLeft --delete
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnRight --delete
qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true

config=${XDG_CONFIG_HOME:-$HOME/.config}
for v in 3.0 4.0; do
  rm -f "$config/gtk-$v/golden-delicious.css"
  [[ -f $config/gtk-$v/gtk.css ]] && sed -i "/^@import 'golden-delicious.css';$/d" "$config/gtk-$v/gtk.css"
done

if command -v flatpak >/dev/null; then
  flatpak override --user --nofilesystem=xdg-config/gtk-3.0 --nofilesystem=xdg-config/gtk-4.0
fi
