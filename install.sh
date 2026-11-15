#!/usr/bin/env bash
# Install the Golden Gate theme into ~/.local/share and apply it.
# Run inside a Plasma session. Safe to run again.
# Usage: ./install.sh [--layout]
#   --layout  also replace your panels with the theme's floating top panel
#             (drops your current panel setup and pinned launchers).
set -euo pipefail

src=$(cd "$(dirname "$0")" && pwd)/src
data=${XDG_DATA_HOME:-$HOME/.local/share}

mkdir -p "$data"
cp -r "$src/." "$data/"

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
