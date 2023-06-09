# Description
Really light photobooth. Auto detect max resolution of the first webcam and take a picture on 's' or left mouse click.


# source
resolution.json from https://en.wikipedia.org/wiki/List_of_common_resolutions

# install
```bash
virtualenv photobooth
source ~/photobooth/bin/activate 
pip install opencv-python
```

detect resolution and codec
```bash

apt install v4l-utils
v4l2-ctl --device /dev/video0 --list-formats-ext
```

# running photobooth
```bash
source ~/photobooth/bin/activate 
# detect best resolution and edit config.ini with thoses values
python guess-resolution.py

# kick off app
python photobooth.py
```

# running lcd/rsync
```bash
source ~/photobooth/bin/activate 

python rsync.py
```


