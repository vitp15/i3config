#!/usr/bin/env bash
# Lock rapid in stil i3lock-fancy: screenshot blurat + lacat, apoi i3lock
img=$(mktemp --suffix=.png)
trap 'rm -f "$img"' EXIT

import -silent -window root png:- \
    | convert - -scale 20% -blur 0x2 -scale 500% -level 0%,100%,0.6 \
        /usr/share/i3lock-fancy/icons/lock.png -gravity center -composite \
        -define png:compression-level=0 "$img"

# Inainte de sleep/hibernate, xss-lock (--transfer-sleep-lock) asteapta sa inchidem
# XSS_SLEEP_LOCK_FD abia dupa ce ecranul e blocat; altfel sistemul intra in sleep
# fortat dupa timeout, cu lock-ul pe jumatate desenat.
if [[ -e /dev/fd/${XSS_SLEEP_LOCK_FD:--1} ]]; then
    kill_i3lock() { pkill -xu "$EUID" "$@" i3lock; }
    trap 'kill_i3lock; rm -f "$img"' TERM INT

    # fara --nofork: i3lock se detaseaza abia dupa ce a blocat ecranul
    i3lock -i "$img" "$@" {XSS_SLEEP_LOCK_FD}<&-
    exec {XSS_SLEEP_LOCK_FD}<&-

    while kill_i3lock -0; do sleep 0.5; done
else
    trap 'kill %%' TERM INT
    i3lock --nofork -i "$img" "$@" &
    wait
fi
