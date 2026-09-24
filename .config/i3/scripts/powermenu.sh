#!/usr/bin/env bash
# Meniu de power pentru i3 (rofi)

options="  Lock\n󰤄  Sleep\n󰍃  Logout\n  Restart\n  Shutdown"

choice=$(echo -e "$options" | rofi -dmenu -i -p "Power" -lines 5)

confirm() {
    [ "$(echo -e "Nu\nDa" | rofi -dmenu -i -p "$1?")" = "Da" ]
}

case "$choice" in
    *Lock)     loginctl lock-session ;;
    *Sleep)    systemctl suspend ;;
    *Logout)   confirm "Logout" && i3-msg exit ;;
    *Restart)  confirm "Restart" && systemctl reboot ;;
    *Shutdown) confirm "Shutdown" && systemctl poweroff ;;
esac
