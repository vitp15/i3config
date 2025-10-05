#!/usr/bin/env bash

if nmcli -t -f NAME,TYPE connection show --active | grep -q "^Hotspot"; then
	nmcli connection down Hotspot
else
    nmcli device wifi hotspot ifname wlo1 ssid "Hotspot 5G" password "12345678" band a channel 149
fi

