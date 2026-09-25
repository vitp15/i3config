#!/usr/bin/env bash
# Meniu de power pentru i3 (rofi), iconite Font Awesome

lock=$'  Lock'
sleep=$'  Sleep'
hibernate=$'  Hibernate'
logout=$'  Logout'
restart=$'  Restart'
shutdown=$'  Shutdown'

choice=$(printf '%s\n' "$shutdown" "$restart" "$sleep" "$hibernate" "$lock" "$logout" \
    | rofi -dmenu -i -p "Power" -lines 6)

confirm() {
    [ "$(printf 'Nu\nDa\n' | rofi -dmenu -i -p "$1?")" = "Da" ]
}

case "$choice" in
    "$lock")      loginctl lock-session ;;
    "$sleep")     systemctl suspend ;;
    "$hibernate")
        if ! err=$(systemctl hibernate 2>&1); then
            rofi -e "Hibernate nu e configurat inca: $err"
        fi ;;
    "$logout")    confirm "Logout" && i3-msg exit ;;
    "$restart")   confirm "Restart" && systemctl reboot ;;
    "$shutdown")  confirm "Shutdown" && systemctl poweroff ;;
esac
