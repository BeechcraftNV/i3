#!/bin/bash
# setup-debian.sh

echo "Installing required packages for i3 config..."
sudo apt update && sudo apt install -y \
  i3 i3blocks feh picom xss-lock i3lock rofi dex \
  network-manager-gnome flameshot x11-xserver-utils
