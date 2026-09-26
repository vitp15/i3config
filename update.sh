#!/bin/bash

YES_FLAG="$1"

sudo apt update

if [[ "$YES_FLAG" == "-y" ]]; then
    sudo apt full-upgrade -y
else
    sudo apt full-upgrade
fi

if [[ "$YES_FLAG" == "-y" ]]; then
    sudo apt autoremove -y
else
    sudo apt autoremove
fi
