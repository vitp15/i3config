#!/usr/bin/env bash

HOTSPOT_CONN=$(nmcli -t -f NAME,TYPE connection show --active | grep -E '^Hotspot' | cut -d: -f1)

if [ -n "$HOTSPOT_CONN" ]; then
    nmcli connection down "$HOTSPOT_CONN"
else
    nmcli device wifi hotspot ifname wlp3s0 ssid "Internet" password "qwer2341" band a channel 36
fi

