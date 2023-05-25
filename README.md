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

# running
```bash
source ~/photobooth/bin/activate 
# detect best resolution and edit config.ini with thoses values
python guess-resolution.py

# kick off app
python photobooth.py
```
