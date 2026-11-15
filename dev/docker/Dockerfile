# Headless Plasma for theme screenshots, pinned to a Debian snapshot so
# rebuilds give the same packages.
# Plasma 6.3 rather than 6.8: without a GPU node, KWin 6.8's nested backends
# need EGL and exit, and its virtual backend crashes in the screenshot plugin.
# 6.3's nested X11 backend renders with llvmpipe inside Xvfb.
FROM debian:trixie

ARG SNAPSHOT=20261114T000000Z
RUN echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/${SNAPSHOT} trixie main" > /etc/apt/sources.list \
 && rm -f /etc/apt/sources.list.d/* \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      kwin-wayland plasma-workspace plasma-desktop breeze kactivitymanagerd \
      xwayland xvfb imagemagick konsole dolphin plasma-integration \
      fonts-noto-core dbus-x11 libcap2-bin \
 && rm -rf /var/lib/apt/lists/* \
 # Docker drops CAP_SYS_NICE from the bounding set; with the file cap kwin cannot exec.
 && setcap -r /usr/bin/kwin_wayland \
 && useradd -m -u 1000 shot

USER shot
WORKDIR /repo
