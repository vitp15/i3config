#!/usr/bin/env bash
# Lock rapid in stil i3lock-fancy: screenshot blurat + lacat, apoi i3lock
img=$(mktemp --suffix=.png)
trap 'rm -f "$img"' EXIT

import -silent -window root png:- \
    | convert - -scale 20% -blur 0x2 -scale 500% -level 0%,100%,0.6 \
        /usr/share/i3lock-fancy/icons/lock.png -gravity center -composite \
        -define png:compression-level=0 "$img"

i3lock --nofork -i "$img" "$@"
