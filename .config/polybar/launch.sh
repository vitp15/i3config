#!/usr/bin/env bash

killall -q polybar
killall -q stalonetray
killall -q nm-applet

stalonetray --edge bottom --align right --icon-size 24 --geometry 1x1-0-0 &
nm-applet >/dev/null 2>&1 &
polybar mybar >> /tmp/polybar.log
