import numpy as np
import matplotlib.pyplot as plt
import cv2
import time


class Camera(object):
    """Stores a cv2.VideoCapture cameara
    and contains the functions to:
    - select the states (aka points in the Ymaze)
    - acquire a background using the median over 1 minute of video
    """
    def __init__(self, num_rois=7, camera_index=0, fps=20) -> None:
        super().__init__()
        self.locations = []
        self.num_rois = num_rois
        self.camera = cv2.VideoCapture(camera_index)
        _, self.snap = self.camera.read()
        self.count = 0
        self.fps = fps
        self.background = np.zeros((self.snap.shape))
    
    def compute_background(self):
        start = time.time()  
        elapsed_time = 0 # total acquisition time
        images = []
        prev_time = 0 # used to define FPS
        _, self.frame = self.camera.read()
        images.append(self.frame)
        while(elapsed_time < 5):
            elapsed_time = time.time() - start
            period = time.time() - prev_time
            if period > 1. / self.fps:
                _, self.frame = self.camera.read()
                images.append(self.frame)
                prev_time = time.time()
        images = np.asarray(images)
        images_merged = np.average(images, axis=3) #because it's a color camera
        self.background = np.median(images_merged, axis=0)

    def live_selection(self):
        self.window = cv2.namedWindow('Snapshot')
        cv2.setMouseCallback('Snapshot', self.select_rois)
        self.user_selection = True
        _, self.frame = self.camera.read()
        while True:
            cv2.imshow('Snapshot', self.frame)
            if cv2.waitKey(1) == 27: 
                break  # esc to quit

    def select_rois(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if (len(self.locations) < 7):
                cv2.circle(self.frame, (x, y), 30, (214, 166, 0), 2)
                cv2.putText(
                    self.frame,
                    str(self.count),
                    (x - 10, y),
                    cv2.FONT_HERSHEY_COMPLEX,
                    .4,
                    (214, 166, 0),
                    )
                self.locations.append([x, y])
                self.count += 1
            if (len(self.locations) == 7):
                response = input(
                    "Are you satisfied with the regions\
                    you have selected? (y/n)")
                if response == "y":
                    print('ESC to close the window')
                else:
                    self.locations = []
                    self.count = 0
                    _, self.frame = self.camera.read()

if __name__ == '__main__':
    test = Camera()
    test.compute_background()