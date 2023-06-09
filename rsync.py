#!/usr/bin/env python3
# -*- coding: utf8 -*-

import configparser
import traceback
import sys
import os
from libs.lcd1602 import LCD
from time import sleep
import threading
import queue
import signal
import subprocess
import socket
import re


def total_images():
  image_total = 0
  row = 1
  image_path = config['PhotoBooth']['image_path']
  # init message
  lcd_queue.put({"row": row, "text": "Images init"})
  # just for fun
  sleep(3)
  
  while True:
    images = len([name for name in os.listdir(image_path) if os.path.isfile(image_path + name)])
    if image_total != images:
      image_total = images

      """disk usage in human readable format (e.g. '2,1GB')"""
      du = subprocess.check_output(['du','-sh', image_path]).split()[0].decode('utf-8')

      lcd_queue.put({"row": row, "text": "Img: " + str(image_total) + "/" + str(du)})

    sleep(10)


def parseQueue():
  image_path = config['PhotoBooth']['image_path']
  
  lcd = LCD(int(config['LCD1602']['lcd_address'], 16), 
            int(config['LCD1602']['lcd_bus_number']), 
            int(config['LCD1602']['lcd_width']), 
            int(config['LCD1602']['lcd_rows']))
  
  lcd.text("Init...", 1)
  lcd.text("Init...", 2)
    
  while True:
    data = lcd_queue.get()
    lcd.text(data['text'], data['row'])
    sleep(1)


def rsync():
  row = 2
  image_path = config['PhotoBooth']['image_path']
  pipe_path = "/tmp/photobooth_rsync"

  if os.path.exists(pipe_path):
    os.remove(pipe_path)

  os.mkfifo(pipe_path)
  file_rsync = os.open(pipe_path, os.O_RDONLY | os.O_NONBLOCK)

  subprocess.Popen(["/usr/bin/udiskie", "--notify-command", '/usr/bin/bash -c "echo {mount_path} >/tmp/photobooth_rsync"'])

  lcd_queue.put({"row": row, "text": "Ready"})
  while True:
    data = os.read(file_rsync, 1024)

    # wait for USB key
    if (data.decode() != ""):
      usb_path = data.decode().strip()
      if (os.path.exists(usb_path)):
        destination_path = usb_path + '/photobooth'
        lcd_queue.put({"row": row, "text": "USB Key detected"})
        sleep(2)
        
        # start rsync
        command = ['rsync', '-a', '--size-only', '--info=progress2', image_path, destination_path]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf8")

        while True:
            output = process.stdout.readline()
            if not output:
                break

            res = re.split("\s+", output.strip())
            try:
              lcd_queue.put({"row": row, "text": "Copy: " + str(res[1])})
            except:
              pass

        process.communicate()
        lcd_queue.put({"row": row, "text": "Copy: sync.."})
        subprocess.check_output(['/usr/bin/sync'])
        lcd_queue.put({"row": row, "text": "Copy: Ok"})


    sleep(1)

try:
  config = configparser.ConfigParser()
  config.read('config.ini')

  lcd_queue = queue.Queue()
  threadImages = threading.Thread(target=total_images)
  threadLCD = threading.Thread(target=parseQueue)
  threaRsync = threading.Thread(target=rsync)

  threadImages.start()
  threadLCD.start()
  threaRsync.start()

  threadImages.join()
  threadLCD.join()
  threaRsync.join()




except KeyboardInterrupt as e:
  print('KeyboardInterrupt')
  print(e)

  sys.exit(1)


except RuntimeError as e:
  print('RuntimeError')
  print(e)

  sys.exit(1)
except Exception as e:
  print('Exception')
  traceback.print_exc()
  print(e)

  sys.exit(1)

