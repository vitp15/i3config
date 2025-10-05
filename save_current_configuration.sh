#!/bin/bash
cp -r ~/.config/i3/* .config/i3
cp -r ~/.config/polybar/* .config/polybar
cp -r ~/.tmux/* .tmux
cp ~/.tmux.conf .tmux.conf

# to dont push hotspot password
git restore --staged .config/polybar/scripts/hotspot-toggle.sh
