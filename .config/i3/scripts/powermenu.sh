#!/usr/bin/env bash
# Meniu de power pentru i3 (rofi), iconite Font Awesome

lock=$'  Lock'
sleep=$'  Sleep'
deep=$'  Deep sleep'
sleephib=$'  Sleep → Hibernate (2h)'
hibernate=$'  Hibernate'
logout=$'  Logout'
restart=$'  Restart'
shutdown=$'  Shutdown'

choice=$(printf '%s\n' "$shutdown" "$restart" "$sleep" "$deep" "$sleephib" "$hibernate" "$lock" "$logout" \
    | rofi -dmenu -i -p "Power" -lines 8)

run_or_err() {
    local name=$1; shift
    if ! err=$("$@" 2>&1); then
        rofi -e "$name nu e configurat inca: $err"
    fi
}

case "$choice" in
    "$lock")      loginctl lock-session ;;
    "$sleep")     systemctl suspend ;;
    "$deep")
        # set-mem-sleep: helper root (sudoers NOPASSWD); revine singur pe s2idle dupa trezire
        if sudo -n /usr/local/sbin/set-mem-sleep deep 2>/dev/null; then
            systemctl suspend
        else
            rofi -e "Deep sleep nu e configurat inca (lipseste set-mem-sleep)"
        fi ;;
    "$sleephib") run_or_err "Sleep → Hibernate" systemctl suspend-then-hibernate ;;
    "$hibernate") run_or_err "Hibernate" systemctl hibernate ;;
    "$logout")    i3-msg exit ;;
    "$restart")   systemctl reboot ;;
    "$shutdown")  systemctl poweroff ;;
esac
