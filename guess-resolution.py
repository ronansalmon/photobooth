import cv2 
import json


class PhotoBooth():
  def __init__(self):
  
    # Load default resolution list
    f = open('resolution.json')
    resolution = json.load(f)
    resolution.reverse()
    f.close()

    self.cam = cv2.VideoCapture(0)
    self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    # detect max resolution
    resolutions = []
    for row in resolution:
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, row["W"])
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, row["H"])
        width = self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        resolutions.append( {"width": width, "height": height})

    # set max resolution
    bestres = resolutions.pop(1);
    self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, bestres['width'])
    self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, bestres['height'])

    self.width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    self.height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    
    print("Best resolution: " + str(self.width) + "x" + str(self.height) + "\n")
    
    self.cam.release()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':

  app = PhotoBooth()
