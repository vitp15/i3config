#!/bin/bash
sudo apt update -y
sudo apt upgrade -y
sudo apt autoremove -y
sudo apt install git -y
sudo apt install vim -y
sudo apt install python3 -y
sudo apt install python3-pip -y
sudo apt install tmux -y
sudo apt install software-properties-common apt-transport-https curl -y
sudo apt install iw -y

# google-chrome installation, and brave instalation
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo rm google-chrome-stable_current_amd64.deb
sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
sudo curl -fsSLo /etc/apt/sources.list.d/brave-browser-release.sources https://brave-browser-apt-release.s3.brave.com/brave-browser.sources
sudo apt update -y
sudo apt install brave-browser -y

# install vs code and android studio
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -y
sudo add-apt-repository "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main" -y
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EB3E94ADBE1229CF
sudo add-apt-repository ppa:maarten-fonville/android-studio -y
sudo apt update -y
sudo apt install code -y
sudo apt install android-studio -y

sudo apt install snap -y
sudo snap install figma-linux

# nvm for code
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
source ~/.bashrc

# dbeaver
sudo snap install dbeaver-ce

# docker install
# Add Docker's official GPG key:
sudo apt-get update -y
sudo apt-get install ca-certificates -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
# sudo snap install docker # docker-compose exist for me only after this
sudo systemctl start docker

