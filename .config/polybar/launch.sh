#!/usr/bin/env bash

killall -q polybar
killall -q stalonetray
killall -q nm-applet

while pgrep -u $UID -x polybar >/dev/null; do sleep 1; done

stalonetray --edge bottom --align right --icon-size 24 --geometry 1x1-0-0 &
nm-applet >/dev/null 2>&1 &

polybar --reload mybar >> /tmp/polybar.log &
if [[ $(polybar -m | grep "HDMI-1: ") ]]; then
	polybar --reload secondmonitorbar >> /tmp/polybar.log &
fi
