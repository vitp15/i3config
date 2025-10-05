#!/usr/bin/env bash

INCREMENT=${1:-5}

current=$(pactl get-sink-volume @DEFAULT_SINK@ | grep -oP '\d+%' | head -1 | tr -d '%')

new_volume=$((current + INCREMENT))

if [ "$new_volume" -gt 100 ]; then
    new_volume=100
fi

pactl set-sink-volume @DEFAULT_SINK@ ${new_volume}%

