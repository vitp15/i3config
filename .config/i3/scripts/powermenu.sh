#!/usr/bin/env bash
# Meniu de power pentru i3 (rofi), iconite Font Awesome

lock=$'  Lock'
sleep=$'  Sleep'
sleephib=$'  Sleep → Hibernate (2h)'
hibernate=$'  Hibernate'
logout=$'  Logout'
restart=$'  Restart'
shutdown=$'  Shutdown'

choice=$(printf '%s\n' "$shutdown" "$restart" "$sleep" "$sleephib" "$hibernate" "$lock" "$logout" \
    | rofi -dmenu -i -p "Power" -lines 7)

run_or_err() {
    local name=$1; shift
    if ! err=$("$@" 2>&1); then
        rofi -e "$name nu e configurat inca: $err"
    fi
}

case "$choice" in
    "$lock")      loginctl lock-session ;;
    "$sleep")     systemctl suspend ;;
    "$sleephib")  run_or_err "Sleep → Hibernate" systemctl suspend-then-hibernate ;;
    "$hibernate") run_or_err "Hibernate" systemctl hibernate ;;
    "$logout")    i3-msg exit ;;
    "$restart")   systemctl reboot ;;
    "$shutdown")  systemctl poweroff ;;
esac
