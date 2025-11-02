import cv2 
import json
import time
import os
import configparser
import multiprocessing as mp
import copy
from tkinter import Tk, messagebox

class PhotoBooth():
  def __init__(self):
    
    # default values
    config = configparser.ConfigParser()
    config.read('config.ini')

    self.mouse_down_since = 0
    self.application = config['PhotoBooth']['application']
    self.image_path = config['PhotoBooth']['image_path']
    self.countdown = int(config['PhotoBooth']['countdown'])
    self.font_thickness = int(config['PhotoBooth']['font_thickness'])
    self.font_scale = int(config['PhotoBooth']['font_scale'])
    self.width = int(config['PhotoBooth']['cam_width'])
    self.height = int(config['PhotoBooth']['cam_height'])
    self.display_width = int(config['PhotoBooth']['display_width'])
    self.display_height = int(config['PhotoBooth']['display_height'])
    self.crope = int(config['PhotoBooth']['crope'])
    self.crope_x = int(config['PhotoBooth']['crope_x'])
    self.crope_y = int(config['PhotoBooth']['crope_y'])
    self.crope_h = int(config['PhotoBooth']['crope_h'])
    self.crope_w = int(config['PhotoBooth']['crope_w'])
    self.cam_device = int(config['PhotoBooth']['cam_device'])
    self.cam_codec = config['PhotoBooth']['cam_codec']
    self.cam = cv2.VideoCapture(self.cam_device)
    self.cam.release()
    print("Current resolution: " + str(self.width) + "x" + str(self.height) + "\n")

    self.snapshot = False
    self.snapshot_started = 0
    self.snapshot_freeze = False
    self.font = cv2.FONT_HERSHEY_SIMPLEX
    self.font_color = (0, 255, 0)

    self.image_seq = len([name for name in os.listdir(self.image_path) if os.path.isfile(self.image_path + name)])
    
    print('Init seq: ' + str(self.image_seq))
    
    self.frame_queue = mp.Queue()
    self.stop_event = mp.Event()
    self.snapshot_event = mp.Event()
    self.process = None
    self.frame = False
    self.frame_org = False
    
  def start(self):
    self.process = mp.Process(target=self.read_frame, args=(self.frame_queue, self.stop_event))
    self.process.start()
    
  def stop(self):
    if self.process is not None:
      self.process.terminate()
      self.process.join()
    if self.cam.isOpened():
      self.cam.release()
    cv2.destroyAllWindows()
    
    
  def read_frame(self, frame_queue, stop_event):
    need_init = True
    while not stop_event.is_set():
      if self.snapshot_event.is_set():
        self.cam.release()
        time.sleep(0.5)
        need_init = True
      else:
        if need_init:
          self.cam = cv2.VideoCapture(self.cam_device)
          self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*self.cam_codec))
          self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.display_width)
          self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.display_height)
          need_init = False

        ret, frame = self.cam.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        if self.crope == 1:
          img = frame[self.crope_y:self.crope_y+self.crope_h, self.crope_x:self.crope_x+self.crope_w]
          frame_queue.put(img)
        else:
          frame_queue.put(frame)
        
      
  def _text_center(self, text):
    # text centered vertiacally and horizontally
    textsize = cv2.getTextSize(text, self.font, self.font_scale, self.font_thickness)[0]
    # get coords based on boundary
    if self.crope == 1:
      textX = int(self.crope_w/2 - (textsize[0] / 2))
      textY = int(self.crope_h/2 + (textsize[1] / 2))
    else:
      textX = int(self.display_width/2 - (textsize[0] / 2))
      textY = int(self.display_height/2 + (textsize[1] / 2))
    return (textX,textY)
    
  def take_snapshot(self):
    display_time = self.countdown - int(time.time() - self.snapshot_started)
    if self.snapshot:

      if display_time >= 0:
        # countdown running
        (textX,textY) = self._text_center(str(display_time))
        
        cv2.putText(self.frame, str(display_time), (textX,textY), self.font, self.font_scale, self.font_color, self.font_thickness, cv2.LINE_AA)
      else:
        if self.snapshot_freeze == True:

          self.snapshot_event.set()
          # make sure read_frame pause
          time.sleep(0.2)
          try:
            # change resolution for screenshot
            self.cam.release()
            self.cam = cv2.VideoCapture(self.cam_device)
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*self.cam_codec))
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

            ret, full_frame = self.cam.read()
            full_frame = cv2.rotate(full_frame, cv2.ROTATE_180) if ret else None
            
            # snapshot time
            cv2.imwrite('{}photobooth_{}.{}'.format(self.image_path, self.image_seq, 'png'), img=full_frame)
            
            self.cam.release()
            print("{}photobooth_{}.{}".format(self.image_path, self.image_seq, 'png'))

          finally:
            self.snapshot_event.clear()
            self.image_seq += 1
            self.snapshot_freeze = False
            self.snapshot = False
            # make sure read_frame resume
            time.sleep(0.5)
    else:
      if display_time > -5:
        text = "Merci!"
        (textX,textY) = self._text_center(text)
        
        cv2.putText(self.frame, text, (textX,textY), self.font, self.font_scale, self.font_color, self.font_thickness, cv2.LINE_AA)

          
  def _mouse_click(self, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
      self.mouse_down_since = int(time.time())

    if event == cv2.EVENT_LBUTTONUP:
      if int(time.time() - self.mouse_down_since) > 6:
        # someone wants to clean up everything ?
        self.mouse_down_since = 0
        root = Tk()
        root.withdraw()  # Masquer la fenêtre principale
        response = messagebox.askyesno("Cleaning up", "Voulez vous effacer toutes les images déjà enregistrée ?")      
        root.grab_set()

        if response == True:
          for fichier in os.listdir(self.image_path):
            chemin_fichier = os.path.join(self.image_path, fichier)
            if os.path.isfile(chemin_fichier):
              os.remove(chemin_fichier)
        root.destroy()

      else:
        if self.snapshot == False:
          # not doing anything yet ? go ahead and shoot
          self.snapshot = True
          self.snapshot_freeze = True
          self.snapshot_started = time.time()
        
  def show(self):

    # start in full screen mode
    cv2.namedWindow(self.application, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(self.application, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(self.application, self._mouse_click)

    while True:
      try:
        if not self.frame_queue.empty():
          self.frame_org = self.frame_queue.get()

        # use the last virgin frame
        self.frame = copy.copy(self.frame_org)
        self.take_snapshot()
        try:
          cv2.imshow(self.application, self.frame)
        except:
          pass

        key = cv2.waitKey(1)
        if key == ord('s'):
          if self.snapshot == False:
            # not doing anything yet ? go ahead and shoot
            self.snapshot = True
            self.snapshot_freeze = True
            self.snapshot_started = time.time()
            

        elif key == ord('q'):
          self.stop()
          break

      except KeyboardInterrupt:
        self.stop()
        break
    
if __name__ == '__main__':

  app = PhotoBooth()
  app.start()
  app.show()
