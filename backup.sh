#!/usr/bin/env bash
# Back up the config files the Golden Gate install touches, keeping the newest
# few backups. install.sh and restore.sh call this before they change anything.
# Usage: ./backup.sh   (prints the new backup directory)
# Env: GG_KEEP_BACKUPS (default 5)
set -euo pipefail

config=${XDG_CONFIG_HOME:-$HOME/.config}
root=${XDG_STATE_HOME:-$HOME/.local/state}/golden-gate/backups
keep=${GG_KEEP_BACKUPS:-5}

# Paths relative to $config.
paths=(
  kdeglobals kwinrc plasmarc plasmashellrc ksplashrc
  plasma-org.kde.plasma.desktop-appletsrc
  kdedefaults gtk-3.0 gtk-4.0 xsettingsd
)

# A fixed-width counter keeps names in time order within the same second.
# Count on from the highest one, never into a gap rotation left behind.
mkdir -p "$root"
stamp=$(date +%Y%m%d-%H%M%S)
last=$(find "$root" -mindepth 1 -maxdepth 1 -name "$stamp-*" | sort | tail -n 1)
n=0
[[ -n $last ]] && n=$((10#${last##*-} + 1))
dir=$root/$stamp-$(printf %02d "$n")
mkdir -p "$dir"

for p in "${paths[@]}"; do
  if [[ -e $config/$p ]]; then
    cp -a "$config/$p" "$dir/"
  else
    # Remembered so a restore can remove what the install created.
    echo "$p" >>"$dir/absent"
  fi
done

# Rotate: drop all but the newest $keep backups.
mapfile -t old < <(find "$root" -mindepth 1 -maxdepth 1 -type d | sort | head -n -"$keep")
for d in "${old[@]}"; do rm -rf "$d"; done

echo "$dir"
