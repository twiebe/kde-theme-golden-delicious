#!/usr/bin/env bash
# Put back the config from a backup made by backup.sh. The current state is
# backed up first, so a restore can be undone too.
# Usage: ./restore.sh          restore the newest backup
#        ./restore.sh --list   list backups, newest last
#        ./restore.sh <dir>    restore that backup
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
config=${XDG_CONFIG_HOME:-$HOME/.config}
state=${XDG_STATE_HOME:-$HOME/.local/state}
# Backups made under the old name Golden Gate move along.
[[ -d $state/golden-gate && ! -e $state/golden-delicious ]] && mv "$state/golden-gate" "$state/golden-delicious"
root=$state/golden-delicious/backups

if [[ ${1:-} == --list ]]; then
  find "$root" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort
  exit
fi

src=${1:-$(find "$root" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | tail -n 1)}
[[ -n $src && -d $src ]] || { echo "no backup found in $root" >&2; exit 1; }

before=$("$here/backup.sh")
echo "current config saved to $before"

for p in "$src"/*; do
  name=$(basename "$p")
  [[ $name == absent ]] && continue
  rm -rf "${config:?}/$name"
  cp -a "$p" "$config/"
done
if [[ -f $src/absent ]]; then
  while read -r name; do rm -rf "${config:?}/$name"; done <"$src/absent"
fi

qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true
echo "restored $src; log out and back in to see it everywhere"
