# Headless Plasma 6.8 for theme screenshots. Pinned to an Arch Linux Archive
# snapshot so rebuilds give the same Plasma version.
# Needs the host's /dev/dri passed in: without a GPU node KWin 6.8 cannot
# render with OpenGL and its screenshot plugin crashes.
FROM archlinux:base

ARG ARCH_DATE=2026/11/14
RUN echo "Server=https://archive.archlinux.org/repos/${ARCH_DATE}/\$repo/os/\$arch" > /etc/pacman.d/mirrorlist \
 && pacman -Syyuu --noconfirm \
 && pacman -S --noconfirm --needed \
      kwin plasma-workspace plasma-desktop breeze kactivitymanagerd qt6-wayland \
      xorg-xwayland mesa vulkan-swrast noto-fonts \
      konsole dolphin spectacle imagemagick libcap \
 && pacman -Scc --noconfirm \
 # Docker drops CAP_SYS_NICE from the bounding set; with the file cap kwin cannot exec.
 && setcap -r /usr/bin/kwin_wayland \
 && useradd -m -u 1000 shot

USER shot
WORKDIR /repo
