#!/bin/bash
cp -r update.sh restart.sh shutdown.sh ~/.
cp -r .config/* ~/.config
mkdir ~/.fonts -p
cp -r .fonts/* ~/.fonts
mkdir ~/.tmux -p
cp -r .tmux/* ~/.tmux
mkdir ~/wallpapers -p
cp -r wallpapers/* ~/wallpapers
cp .tmux.conf ~/.tmux.conf
