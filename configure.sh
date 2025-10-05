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

sudo apt update -y
sudo apt upgrade -y
sudo apt autoremove -y
sudo apt install polybar -y
sudo apt install feh -y
sudo apt install lxappearance -y
sudo apt install arandr -y
sudo apt install pulseaudio pulseaudio-utils pavucontrol -y
sudo apt install stalonetray -y
sudo apt install brightnessctl -y
sudo apt install xinput -y
sudo apt install compton -y
sudo apt install rofi -y

