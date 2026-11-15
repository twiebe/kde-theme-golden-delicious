#!/usr/bin/env bash
# Start a throwaway headless Plasma session, optionally install the theme,
# launch apps, take a full-screen screenshot. Meant to run in the image from
# dev/docker (see dev/shot-docker.sh), with /dev/dri available.
# Usage: dev/shot.sh <out.png> [--install] [app...]
# Env: SHOT_W/SHOT_H (default 1600x1000), SHOT_WAIT (seconds, default 10),
#      SHOT_HOME (persistent fake home; default: fresh temp dir).
set -euo pipefail

out=$(realpath -m "$1"); shift
install=0
if [[ ${1:-} == --install ]]; then install=1; shift; fi
repo=$(cd "$(dirname "$0")/.." && pwd)
w=${SHOT_W:-1600} h=${SHOT_H:-1000}

home=${SHOT_HOME:-$(mktemp -d)}
mkdir -p "$home"
export HOME=$home
export XDG_CONFIG_HOME=$home/.config XDG_DATA_HOME=$home/.local/share XDG_CACHE_HOME=$home/.cache
export XDG_RUNTIME_DIR=$home/run
mkdir -p "$XDG_RUNTIME_DIR" && chmod 700 "$XDG_RUNTIME_DIR"
export XDG_CURRENT_DESKTOP=KDE XDG_SESSION_TYPE=wayland KDE_FULL_SESSION=true
# startplasma puts the look-and-feel defaults layer on the config path; do the same.
export XDG_CONFIG_DIRS=$XDG_CONFIG_HOME/kdedefaults:/etc/xdg

run() {
  # Restricted protocols are granted by exe path; skip that check in this fake session.
  KWIN_WAYLAND_NO_PERMISSION_CHECKS=1 kwin_wayland --virtual --no-lockscreen --xwayland \
    --width "$w" --height "$h" --socket wayland-shot >"$home/kwin.log" 2>&1 &
  for _ in $(seq 50); do [[ -S $XDG_RUNTIME_DIR/wayland-shot ]] && break; sleep 0.2; done
  export WAYLAND_DISPLAY=wayland-shot QT_QPA_PLATFORM=wayland
  dbus-update-activation-environment --all
  /usr/lib/kactivitymanagerd >"$home/kamd.log" 2>&1 &
  kded6 >"$home/kded.log" 2>&1 &
  sleep 1
  plasmashell >"$home/plasmashell.log" 2>&1 &
  sleep 5
  if [[ $install == 1 ]]; then
    "$repo/install.sh" --yes --layout --tiles >"$home/install.log" 2>&1 || true
    # A live session picks the new style up on its own; this fake one starts
    # without the kdedefaults watcher, so restart the shell.
    kquitapp6 plasmashell >/dev/null 2>&1 || true
    sleep 1
    plasmashell >>"$home/plasmashell.log" 2>&1 &
    sleep 4
  fi
  sleep 2
  local app
  for app in "$@"; do $app >/dev/null 2>&1 & sleep 1.5; done
  sleep "${SHOT_WAIT:-10}"
  spectacle -b -n -f -o "$out" >"$home/spectacle.log" 2>&1
  jobs -p | xargs -r kill 2>/dev/null || true
}

export -f run
export home install repo out w h
dbus-run-session -- bash -c 'run "$@"' _ "$@" 2>"$home/session.log"
[[ -s $out ]] && echo "$out"
