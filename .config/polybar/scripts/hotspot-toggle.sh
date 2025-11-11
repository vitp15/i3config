#!/usr/bin/env bash

HOTSPOT_CONN=$(nmcli -t -f NAME,TYPE connection show --active | grep -E '^Hotspot' | cut -d: -f1)

if [ -f .env ]; then
  export $(grep -Ev '^$|^#' .env)
else
  echo ".env file not found"
  exit 1
fi

if [ -n "$HOTSPOT_CONN" ]; then
    nmcli connection down "$HOTSPOT_CONN"
else
    nmcli device wifi hotspot ifname wlp0s20f3 ssid "$HOTSPOT_NAME" password "$HOTSPOT_PASSWORD" band a channel 36
fi

