#!/usr/bin/env bash

HOTSPOT_CONN=$(nmcli -t -f NAME,TYPE connection show --active | grep -E '^Hotspot' | cut -d: -f1)
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if [ -f "$SCRIPT_DIR/.env" ]; then
  export $(grep -Ev '^$|^#' "$SCRIPT_DIR/.env")
else
  echo ".env file not found"
  exit 1
fi

if [ -n "$HOTSPOT_CONN" ]; then
    nmcli connection down "$HOTSPOT_CONN"
else
    nmcli device wifi hotspot ifname wlp3s0 ssid "$HOTSPOT_NAME" password "$HOTSPOT_PASSWORD" band a channel 36
fi

