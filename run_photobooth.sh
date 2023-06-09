#!/bin/bash

DIR="$( dirname -- "${BASH_SOURCE[0]}"; )";
cd ${DIR}

export DISPLAY=:0.0

xset -dpms
xset s noblank
xset s off
xset -display :0 s off -dpms

source  ~/photobooth/bin/activate
while true; do
  python photobooth.py
  sleep 2
done

