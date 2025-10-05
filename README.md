- Check instructions for tmux from it's config file
- in .bashrc W in place of w in PS1 to dont show full path in terminal
- use lxappearance to set gtk theme
- rofi-theme-selector - to select theme (rounded-nord-dark for example and alt+a to save it)
- change terminal transparency by its prefferenes
- use arandr to set monitor layout if needed
- create alias android-studio for android-studio to can be open (/opt/android-studio.bin/studio.sh)
- reboot after instalations
- xinput list to see your touchpad and mouse and change in i3/conf with yours
- check if brightness control works (video group given to your user after reboot could work)
- ls /sys/class/power_supply/ to see your battery values and update i3 configuration to use it and corectly display your battery
- change ifname for starting hotspot at .config/polybar/scripts/hootspot-toogle.sh (nmcli device status - to see your ifname for hotspot)
- also for hotspot tou can set your region with sudo iw reg set <RO for example> this will give you ability to use some channels like 149 (script already make this for RO region) to see all regions for 5G (take one that dont have "no IR" iw list to see all channels)


- rofi -show drun: will show .desktop aplications, default is run not drun, some aplications you can find only with drun if they are only .desktop and arent exported in PATH
