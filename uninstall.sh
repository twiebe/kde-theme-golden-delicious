#!/usr/bin/env bash
# Put back the settings install.sh changed, as they were before the first
# install (install.sh records them), and remove the theme's files. Without
# that record (installed by an older install.sh) it switches to Breeze Dark.
# Your backups stay (see restore.sh).
# Usage: ./uninstall.sh [--layout] [-y | --yes]
#   --layout  also put back the panels from before the first install with
#             --layout (or reset them to the global theme's, if not recorded)
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

orig=$state/golden-delicious/original
unset_mark=__unset__
[[ -f $orig/values ]] && have_orig=1 || have_orig=0
[[ -d $orig/panels ]] && have_panels=1 || have_panels=0
value() {  # kind key...: the recorded value of that line, empty if none
  local kind=$1; shift
  awk -F'\t' -v k="$kind" -v a="${1:-}" -v b="${2:-}" -v c="${3:-}" \
    '$1 == k && $2 == a && (b == "" || $3 == b) && (c == "" || $4 == c) { print $NF; exit }' "$orig/values"
}

if [[ $yes == 0 ]]; then
  echo "This removes the Golden Delicious theme for your user. It will:"
  if [[ $have_orig == 1 ]]; then
    echo "  - put back the settings you had before the first install: global"
    echo "    theme, colors, icons, Plasma style, window decoration and buttons,"
    echo "    blur, GTK theme and buttons, GNOME's button layout"
  else
    echo "  - switch to Breeze Dark with Breeze's window buttons (your settings"
    echo "    from before the install were not recorded)"
  fi
  if [[ $layout == 1 && $have_panels == 1 ]]; then
    echo "  - put back the panels you had before the first install with --layout"
  elif [[ $layout == 1 ]]; then
    echo "  - reset your panels to the global theme's default"
  else
    echo "  - leave your panels as they are"
  fi
  echo "  - stop and remove the app icon tiles service"
  echo "  - remove golden-delicious.css from gtk-3.0 and gtk-4.0"
  echo "  - take back the Flatpak access to the GTK config install.sh gave"
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

# Global theme first: it resets colors, icons, Plasma style and decoration to
# its own, the recorded values below then win over that.
if [[ $have_orig == 1 ]]; then
  lnf=$(value kcfg kdeglobals KDE LookAndFeelPackage)
  [[ -z $lnf || $lnf == "$unset_mark" ]] && lnf=org.kde.breeze.desktop
else
  lnf=org.kde.breezedark.desktop
fi
reset=()
[[ $layout == 1 && $have_panels == 0 ]] && reset=(--resetLayout)
log "Switching the global theme back to $lnf"
plasma-apply-lookandfeel -a "$lnf" "${reset[@]}"

if [[ $have_orig == 1 ]]; then
  log "Putting back your settings from before the install"
  # kde-gtk-config writes both GTK versions: first, so the values below win.
  gtk=$(value kcfg "$config/gtk-3.0/settings.ini" Settings gtk-theme-name)
  [[ -n $gtk && $gtk != "$unset_mark" ]] &&
    qdbus6 org.kde.kded6 /modules/gtkconfig org.kde.GtkConfig.setGtkTheme "$gtk" >/dev/null 2>&1 || true
  while IFS=$'\t' read -r kind a b c d; do
    case $kind in
      kcfg)  # file group key value
        if [[ $d == "$unset_mark" ]]; then
          kwriteconfig6 --file "$a" --group "$b" --key "$c" --delete
          continue
        fi
        case "$a/$b/$c" in
          # These need applying, not just writing.
          kdeglobals/General/ColorScheme) plasma-apply-colorscheme "$d" >/dev/null 2>&1 ||
            kwriteconfig6 --file "$a" --group "$b" --key "$c" "$d" ;;
          plasmarc/Theme/name) plasma-apply-desktoptheme "$d" >/dev/null 2>&1 ||
            kwriteconfig6 --file "$a" --group "$b" --key "$c" "$d" ;;
          *) kwriteconfig6 --file "$a" --group "$b" --key "$c" "$d" ;;
        esac ;;
      dconf)  # path value ('' when it was not set)
        if [[ -z $b ]]; then dconf reset "$a"; else dconf write "$a" "$b"; fi ;;
    esac
  done <"$orig/values"
else
  log "Window buttons back to Breeze's"
  kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnLeft --delete
  kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnRight --delete
  gsettings reset org.gnome.desktop.wm.preferences button-layout 2>/dev/null || true
  for v in 3.0 4.0; do
    [[ -f $config/gtk-$v/settings.ini ]] &&
      kwriteconfig6 --file "$config/gtk-$v/settings.ini" --group Settings --key gtk-decoration-layout --delete
  done
  qdbus6 org.kde.kded6 /modules/gtkconfig org.kde.GtkConfig.setGtkTheme Breeze 2>/dev/null || true
fi
qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true

# Panels as they were before an install with --layout replaced them. The shell
# writes its config on exit, so it has to be down while they go back.
if [[ $layout == 1 && $have_panels == 1 ]]; then
  log "Putting back your panels"
  if systemctl --user -q is-active plasma-plasmashell.service 2>/dev/null; then
    systemctl --user stop plasma-plasmashell.service
    cp -a "$orig/panels/." "$config/"
    systemctl --user start plasma-plasmashell.service
  else
    kquitapp6 plasmashell >/dev/null 2>&1 || true
    cp -a "$orig/panels/." "$config/"
    (setsid plasmashell >/dev/null 2>&1 &)
  fi
fi

# App icon tiles.
log "Removing the app icon tiles service"
systemctl --user disable --now golden-delicious-tiles.path golden-delicious-tiles.service 2>/dev/null || true
rm -f "$config/systemd/user/golden-delicious-tiles."{service,path}
systemctl --user daemon-reload 2>/dev/null || true

log "Removing golden-delicious.css from the GTK config"
for v in 3.0 4.0; do
  rm -f "$config/gtk-$v/golden-delicious.css"
  if [[ -f $config/gtk-$v/gtk.css ]]; then
    # Also when it ended up on kde-gtk-config's line (no final newline there).
    sed -i "s/@import 'golden-delicious.css';//; /^$/d" "$config/gtk-$v/gtk.css"
  fi
done

# Flatpak: take back only the read access to the GTK config that install.sh
# gave, not one you had before (and the blocks an older uninstall.sh wrote).
# `flatpak override --nofilesystem` would not undo it but forbid the folders.
overrides=$data/flatpak/overrides/global
gtks=()
for v in 3 4; do
  [[ $have_orig == 1 && $(value flatpak-fs "xdg-config/gtk-$v.0") == 1 ]] || gtks+=("$v")
done
if [[ -f $overrides && ${#gtks[@]} -gt 0 ]]; then
  log "Taking back the Flatpak access to the GTK config"
  vs=$(IFS=; echo "${gtks[*]}")
  sed -i -E "/^filesystems=/{:a;s/([=;])!?xdg-config\/gtk-[$vs]\.0(:ro)?(;|$)/\1/;ta;/^filesystems=$/d}" "$overrides"
fi
if [[ $have_orig == 1 && $(value flatpak-app org.gtk.Gtk3theme.Breeze) == 0 ]]; then
  log "Removing the Breeze GTK theme for Flatpak apps (install.sh added it)"
  flatpak uninstall --user -y --noninteractive org.gtk.Gtk3theme.Breeze >/dev/null 2>&1 || true
fi

# The theme's files, and the record of your settings (it's been used now).
log "Deleting the theme's files"
rm -rf "${data:?}"/aurorae/themes/golden-delicious "${data:?}"/plasma/desktoptheme/golden-delicious \
  "${data:?}"/plasma/look-and-feel/golden-delicious "${data:?}"/icons/golden-delicious \
  "${data:?}"/icons/golden-delicious-apps "${data:?}"/color-schemes/GoldenDelicious.colors \
  "${data:?}"/golden-delicious "${orig:?}"

echo
echo "Golden Delicious is removed. Log out and back in once so every app picks"
echo "up the change. Backups of your old config are still in"
echo "$state/golden-delicious/backups (see restore.sh)."
