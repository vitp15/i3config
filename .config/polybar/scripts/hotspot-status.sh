#!/usr/bin/env bash

if nmcli -t -f NAME,TYPE connection show --active | grep -q "^Hotspot"; then
    echo "%{F#4bb393}"
else
    echo ""
fi

