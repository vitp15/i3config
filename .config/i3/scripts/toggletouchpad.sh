#!/usr/bin/env bash
# Porneste/opreste touchpad-ul (libinput). Gaseste singur dispozitivul "Touchpad".
dev=$(xinput list --name-only | grep -m1 -i 'touchpad' | sed 's/^∼ //')
[ -z "$dev" ] && exit 1
if [ "$(xinput list-props "$dev" | awk -F: '/Device Enabled/{gsub(/[[:space:]]/,"",$2); print $2}')" = "1" ]; then
    xinput disable "$dev" && notify-send -t 1500 "Touchpad" "Oprit" 2>/dev/null
else
    xinput enable "$dev" && notify-send -t 1500 "Touchpad" "Pornit" 2>/dev/null
fi
