import cv2 
import json
import time
import os
import configparser


class PhotoBooth():
  def __init__(self):
    
    # default values
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    self.application = config['PhotoBooth']['application']
    self.image_path = config['PhotoBooth']['image_path']
    self.countdown = int(config['PhotoBooth']['countdown'])
    self.font_thickness = int(config['PhotoBooth']['font_thickness'])
    self.font_scale = int(config['PhotoBooth']['font_scale'])
    self.width = int(config['PhotoBooth']['cam_width'])
    self.height = int(config['PhotoBooth']['cam_height'])
    
    self.cam = cv2.VideoCapture(0)
    self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
    self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
    
    print("Current resolution: " + str(self.width) + "x" + str(self.height) + "\n")

    self.snapshot = False
    self.snapshot_started = 0
    self.snapshot_freeze = False
    self.frame = 0            # live video
    self.font = cv2.FONT_HERSHEY_SIMPLEX
    self.font_color = (0, 0, 0)

    
    self.image_seq = len([name for name in os.listdir(self.image_path) if os.path.isfile(name)])
    
    
  def _text_center(self, text):

      textsize = cv2.getTextSize(text, self.font, self.font_scale, self.font_thickness)[0]
      # get coords based on boundary
      textX = int(self.width/2 - (textsize[0] / 2))
      textY = int(self.height/2 + (textsize[1] / 2))
      return (textX,textY)
    
  def take_snapshot(self):
    if self.snapshot:
      
      display_time = self.countdown - int(time.time() - self.snapshot_started)

      if display_time >= 0:
        # countdown running
        (textX,textY) = self._text_center(str(display_time))
        
        cv2.putText(self.frame, str(display_time), (textX,textY), self.font, self.font_scale, self.font_color, self.font_thickness, cv2.LINE_AA)
      else:
        if self.snapshot_freeze == True:
          # snapshot time
          cv2.imwrite('{}photobooth_{}.{}'.format(self.image_path, self.image_seq, 'png'), img=self.frame)
          self.image_seq += 1
          self.snapshot_freeze = False
          self.snapshot = False
        else:
          if display_time > -3:
            text = "Merci!"
            (textX,textY) = self._text_center(text)
            
            cv2.putText(self.frame, text, (textX,textY), self.font, self.font_scale, self.font_color, self.font_thickness, cv2.LINE_AA)

          
  def _mouse_click(self, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
      if self.snapshot == False:
        # not doing anything yet ? go ahead and shoot
        self.snapshot = True
        self.snapshot_freeze = True
        self.snapshot_started = time.time()
      
  def run(self):

    cv2.namedWindow(self.application, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(self.application, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(self.application, self._mouse_click)
    while True:
      try:
        check, self.frame = self.cam.read()
        self.take_snapshot()
        cv2.imshow(self.application, self.frame)
        
        key = cv2.waitKey(1)
        if key == ord('s'):
          if self.snapshot == False:
            # not doing anything yet ? go ahead and shoot
            self.snapshot = True
            self.snapshot_freeze = True
            self.snapshot_started = time.time()
            

        elif key == ord('q'):
          self.cam.release()
          cv2.destroyAllWindows()
          break
            
      except(KeyboardInterrupt):
        self.cam.release()
        cv2.destroyAllWindows()
        break
    
if __name__ == '__main__':

  app = PhotoBooth()
  app.run()
