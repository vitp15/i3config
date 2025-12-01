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
sudo usermod -aG video $USER
sudo apt install xinput -y
sudo apt install compton -y
sudo apt install rofi -y
sudo apt install blueman -y
sudo apt install copyq -y

sudo apt install imagemagick -y
sudo apt install i3lock -y
git clone https://github.com/meskarune/i3lock-fancy.git
cd i3lock-fancy
sudo make install
cd ..
sudo rm -r i3lock-fancy

git clone https://github.com/lr-tech/rofi-themes-collection.git
cd rofi-themes-collection
cp themes/* ~/.local/share/rofi/themes/ -r
cd ..
sudo rm -r rofi-themes-collection

sudo iw reg set RO
