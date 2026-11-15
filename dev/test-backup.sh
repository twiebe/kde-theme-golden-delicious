#!/usr/bin/env bash
# Checks backup.sh rotation and restore.sh in a throwaway home.
# Usage: dev/test-backup.sh   (exit 0 when all checks pass)
set -uo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d)
export HOME=$T XDG_CONFIG_HOME=$T/.config XDG_STATE_HOME=$T/.local/state
fail=0
check() { if eval "$2"; then echo "PASS $1"; else echo "FAIL $1"; fail=1; fi; }

mkdir -p "$T/.config/gtk-4.0"
echo "ColorScheme=Mine" >"$T/.config/kdeglobals"
echo "user css" >"$T/.config/gtk-4.0/gtk.css"

b1=$(./backup.sh)
echo "ColorScheme=GoldenDelicious" >"$T/.config/kdeglobals"
echo "@import 'golden-delicious.css';" >>"$T/.config/gtk-4.0/gtk.css"
mkdir -p "$T/.config/gtk-3.0"
for _ in 1 2 3 4 5 6; do ./backup.sh >/dev/null; done
check "rotation keeps 5" '[[ $(./restore.sh --list | wc -l) == 5 ]]'
check "oldest dropped" '[[ ! -d $b1 ]]'
check "missing backup refused" '! ./restore.sh "$b1" >/dev/null 2>&1'
b0=$(./backup.sh)
check "newest survives rotation" '[[ -d $b0 ]]'

# Turn b0 into a backup of the original state, then restore it.
find "${b0:?}" -mindepth 1 -delete
echo "ColorScheme=Mine" >"$b0/kdeglobals"
mkdir "$b0/gtk-4.0" && echo "user css" >"$b0/gtk-4.0/gtk.css"
echo gtk-3.0 >"$b0/absent"
./restore.sh "$b0" >/dev/null
check "kdeglobals restored" 'grep -q Mine "$T/.config/kdeglobals"'
check "gtk.css restored" '[[ $(cat "$T/.config/gtk-4.0/gtk.css") == "user css" ]]'
check "absent path removed" '[[ ! -e $T/.config/gtk-3.0 ]]'
check "restore backed up current state first" 'grep -q GoldenDelicious "$(./restore.sh --list | tail -n 1)/kdeglobals"'

rm -rf "${T:?}"
exit $fail
