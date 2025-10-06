- Check instructions for tmux from it's config file (.tmux.conf)
- in .bashrc W in place of w in PS1 to dont show full path in terminal
- use lxappearance to set gtk theme
- rofi-theme-selector - to select theme (rounded-nord-dark for example and alt+a to save it)
- change terminal transparency by its prefferenes
- use arandr to set monitor layout if needed
- reboot after instalations
- xinput list to see your touchpad and mouse and change in i3/conf with yours
- check if brightness control works (video group given to your user after reboot could work)
- ls /sys/class/power_supply/ to see your battery values and update i3 configuration to use it and corectly display your battery
- change ifname for starting hotspot at .config/polybar/scripts/hootspot-toogle.sh (nmcli device status - to see your ifname for hotspot)
- also for hotspot you can set your region with sudo iw reg set <RO for example> this will give you ability to use some channels like 149 (script already make this for RO region) to see all regions for 5G (take one that dont have "no IR" iw list to see all channels)
- if problems with hotspot (maybe from 802.1 used in Regie:) they maybe because of not existing routes in iptables to forward network from cable to wifi/hotspot) you can solve them like this:
    ```
    ip link # to see your specific channels (example for enp2s0 (eth) and wlp3s0 (wifi/hotspot))
    sudo iptables -t nat -A POSTROUTING -o enp2s0 -j MASQUERADE
    sudo iptables -A FORWARD -i wlp3s0 -o enp2s0 -j ACCEPT
    sudo iptables -A FORWARD -i enp2s0 -o wlp3s0 -m state --state ESTABLISHED,RELATED -j ACCEP
    # to save this configuration to be persistent after restart too:
    sudo apt install iptables-persistent -y
    sudo netfilter-persistent save
    ```
