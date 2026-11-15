#!/usr/bin/env bash
# Start a throwaway Plasma session inside Xvfb, optionally install the theme,
# launch apps, take a full-screen screenshot.
# KWin runs with its nested X11 backend so Mesa llvmpipe gives it OpenGL
# (blur needs it); the virtual backend falls back to QPainter without /dev/dri.
# Usage: dev/shot.sh <out.png> [--install] [app...]
# Env: SHOT_W/SHOT_H (default 1600x1000), SHOT_WAIT (seconds, default 10),
#      SHOT_HOME (persistent fake home; default: fresh temp dir),
#      KWIN (kwin binary; containers need a copy without file caps, and its
#            file name must stay kwin_wayland).
set -euo pipefail

out=$(realpath -m "$1"); shift
install=0
if [[ ${1:-} == --install ]]; then install=1; shift; fi
repo=$(cd "$(dirname "$0")/.." && pwd)
kwin=${KWIN:-kwin_wayland}
w=${SHOT_W:-1600} h=${SHOT_H:-1000}

home=${SHOT_HOME:-$(mktemp -d)}
mkdir -p "$home"
export HOME=$home
export XDG_CONFIG_HOME=$home/.config XDG_DATA_HOME=$home/.local/share XDG_CACHE_HOME=$home/.cache
export XDG_RUNTIME_DIR=$home/run
mkdir -p "$XDG_RUNTIME_DIR" && chmod 700 "$XDG_RUNTIME_DIR"
export XDG_CURRENT_DESKTOP=KDE XDG_SESSION_TYPE=wayland KDE_FULL_SESSION=true
export LIBGL_ALWAYS_SOFTWARE=1

Xvfb :99 -screen 0 "${w}x${h}x24" +extension GLX -nolisten tcp >"$home/xvfb.log" 2>&1 &
xvfb=$!
trap 'kill $xvfb 2>/dev/null || true' EXIT
sleep 1

run() {
  DISPLAY=:99 "$kwin" --x11-display :99 --no-lockscreen --xwayland \
    --width "$w" --height "$h" --socket wayland-shot >"$home/kwin.log" 2>&1 &
  for _ in $(seq 50); do [[ -S $XDG_RUNTIME_DIR/wayland-shot ]] && break; sleep 0.2; done
  export WAYLAND_DISPLAY=wayland-shot QT_QPA_PLATFORM=wayland
  unset DISPLAY
  dbus-update-activation-environment --all
  /usr/lib/x86_64-linux-gnu/libexec/kactivitymanagerd >"$home/kamd.log" 2>&1 &
  sleep 1
  plasmashell >"$home/plasmashell.log" 2>&1 &
  sleep 5
  if [[ $install == 1 ]]; then "$repo/install.sh" >"$home/install.log" 2>&1 || true; fi
  sleep 2
  local app
  for app in "$@"; do $app >/dev/null 2>&1 & sleep 1.5; done
  sleep "${SHOT_WAIT:-10}"
  import -display :99 -window root "$out"
  kill $(jobs -p) 2>/dev/null || true
}

export -f run
export home install repo out kwin w h
dbus-run-session -- bash -c 'run "$@"' _ "$@" 2>"$home/session.log"
[[ -s $out ]] && echo "$out"
