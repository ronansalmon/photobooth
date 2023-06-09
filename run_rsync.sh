#!/bin/bash

source  ~/photobooth/bin/activate
DIR="$( dirname -- "${BASH_SOURCE[0]}"; )";
cd ${DIR}

while true; do
  python rsync.py
  sleep 2
done

