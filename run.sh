#!/bin/bash

xset -dpms
xset s noblank
xset s off
xset -display :0 s off -dpms


source  ~/photobooth/bin/activate
python photobooth.py

