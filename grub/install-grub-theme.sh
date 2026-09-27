#!/bin/bash
# Install the i3green GRUB theme. Run with sudo.
#   sudo ./grub/install-grub-theme.sh            install / update
#   sudo ./grub/install-grub-theme.sh --uninstall back to the plain menu
set -e

NAME=i3green
SRC="$(cd "$(dirname "$0")" && pwd)/themes/$NAME"
DEST=/boot/grub/themes/$NAME
CONF=/etc/default/grub

if [ "$EUID" -ne 0 ]; then
    echo "Run with sudo: sudo $0 $*" >&2
    exit 1
fi

# set_var KEY VALUE: replace (even if commented out) or append
set_var() {
    if grep -qE "^#?\s*$1=" "$CONF"; then
        sed -i -E "s|^#?\s*$1=.*|$1=\"$2\"|" "$CONF"
    else
        echo "$1=\"$2\"" >> "$CONF"
    fi
}

cp -n "$CONF" "$CONF.bak-before-$NAME" || true

if [ "$1" = "--uninstall" ]; then
    sed -i -E "s|^(GRUB_THEME=.*)|#\1|" "$CONF"
    rm -rf "$DEST"
else
    mkdir -p "$DEST"
    cp -r "$SRC"/. "$DEST"/
    set_var GRUB_THEME "$DEST/theme.txt"
    set_var GRUB_GFXMODE "1920x1080,auto"
    set_var GRUB_GFXPAYLOAD_LINUX "keep"
fi

update-grub
echo
echo "Windows entries in the menu: $(grep -ci "menuentry '.*windows" /boot/grub/grub.cfg)"
echo "Done. Reboot to see it."
