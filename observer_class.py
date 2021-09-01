import numpy as np
import ymaze_utility_functions as utils
# from picamera.array import PiRGBArray
# from picamera import PiCamera
import time
import cv2

class Observer(object):
    """Control the camera; can loop through continuous acquisitions,
    while finding the larva position
    and assigning it to a discrete set of states (seven states)
    defined by the user.
    """
    def __init__(
        self,
        fps=20,
        resolution=[512, 512], #width, height
        threshold = 20,
        regions= {}, # points defining the discrete states
        ):
        """Give:
        - fps = frames per second
        - resolution = [rows, cols], in pixels
        - threshold = minimal distance between current and next position
            (if smaller that this, it's not considered as real transitio)
        - regions = dict, where the larva is
        """
        super().__init__()
        self.fps = fps
        # self.camera = PiCamera(resolution = resolution, framerate = fps)
        # self.camera.capture(self.image).array
        self.threshold = threshold
        self.regions = regions
        self.previous_state = 0
        self.state = 0
        self.spot = [-1, -1] # positions are all positive integers.
        # this acts as an extra flag to signal that the larva was not found
        self.mean_background = 0
        self.found_flag = False
        # the regions are numbered according to a hard-coded convention
        # it makes it easier to identify where the larva is.
        # see schematics for explanation
        regions_keys = [0, 1, 2, 3, 5, 7, 9]
        for key in regions_keys:
            self.regions[key] = [0, 0]

    def compute_background(
        self,
        time_window=60
        ):
        """Calculate the background
        taking images for 'time_window' seconds
        """
        now = time.time()
        start = now
        elapsed = now
        prev_image_time = now
        image_time = now

        self.background = []

        while elapsed < time_window:
            if(image_time - prev_image_time >= 1 / self.fps):
                self.camera.capture(self.image).array
                self.background.append(self.image)
                prev_image_time = time.time()
            now = time.time()
            image_time = now - prev_image_time
            elapsed = now - start
        
        self.background = np.asarray(self.background)
        self.mean_background = np.average(self.background, axis=0)

    def define_states(self):
        """User can define the 7 states by clicking"""
        self.window = cv2.namedWindow('Select discrete states')
        cv2.setMouseCallback('Select discrete states', self.select_rois)
        self.user_selection = True
        self.camera.capture(self.image).array
        while True:
            cv2.imshow('Select discrete states', self.image)
            if cv2.waitKey(1) == 27: 
                break  # esc to quit

    def select_rois(
        self,
        event,
        x,
        y,
        flags,
        param
        ):
        """Allow the user to click and deine the points
        corresponding to the discrete states.
        It should be following the indications
        found in the figure in Amanda's thesis"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if (len(self.regions) < 7):
                cv2.circle(self.frame, (x, y), 30, (214, 166, 0), 2)
                cv2.putText(
                    self.frame,
                    str(self.count),
                    (x - 10, y),
                    cv2.FONT_HERSHEY_COMPLEX,
                    .4,
                    (214, 166, 0),
                    )
                self.regions.append([y, x]) #row major, as numpy
                self.count += 1
            if (len(self.regions) == 7):
                response = input(
                    "Are you satisfied with the regions\
                    you have selected? (y/n)")
                if response == "y":
                    print('ESC to close the window')
                else:
                    self.regions = []
                    self.count = 0
                    self.camera.capture(self.image).array

    def find_larva(
        self,
        lowpass_kernel=np.ones((5, 5)),
        highpass_kernel=np.ones((3, 3))
        ):
        """Find larva's centroid"""
        self.camera.capture(self.image).array
        self.image = cv2.subtract(self.image, self.mean_background)
        # threshold, then low-pass, then high-pass
        _, self.thresholded = cv2.threshold(
            self.image,
            self.threshold,
            255,
            cv2.THRESH_BINARY
            )
        self.thresholded = cv2.morphologyEx(
            self.thresholded,
            cv2.MORPH_CLOSE,
            lowpass_kernel
            )
        self.thresholded = cv2.morphologyEx(
            self.thresholded,
            cv2.MORPH_OPEN,
            highpass_kernel 
            )
        # find the contours. We assume the only one
        # (or at lest the largest one) is the larva
        self.contours, _ = cv2.findContours(
            self.thresholded, # input image
            cv2.RETR_TREE, # contour retrieaval mode
            cv2.CHAIN_APPROX_NONE # contour approximation method
		)
        areas = []
        for contour in self.contours:
            areas.append(cv2.contourArea(contour))
        # calculate the centroid
        if len(areas) >= 1:
            self.larva = self.contours[np.argmax(areas)]
            self.spot = utils.Centroid(self.larva)
            self.found_flag = True
        else:
            self.spot = [-1, -1]
            self.found_flag = False

    def get_state(self):
        """Find the minimal distance between the locations
        and the given point. Store the index in self.state"""
        # TO BE TESTED
        if self.spot == [-1, -1]:
            pass # do nothing if larva centre is not properly found
        else:
            # instantaneous distance between now and the previous state-point
            my_distance = utils.points_distance(
                self.spot,
                self.regions[self.state]
                )
            # distances between now and all state-points
            n_distances = utils.points_distance(
                self.spot,
                self.regions
                )
            closest = np.amin(n_distances)
            if ((my_distance - self.threshold) > closest
            and closest != my_distance):
                self.previous_state = self.state # keep track of previous state
                self.state = self.regions[
                    list(
                        self.regions.keys()[
                            np.argmin(n_distances)
                            ]
                        )
                    ]
        
        # the state can be signalled to the trainer
    
    def monitor_transition(self):
        """This is where the transition
        between the discrete states is computed.
        The hardcoded numbers follow a naming logic explained in schematics.
        For now, the important transitions are just after a decision
        (to eventually give immediate reward/punishment)
        and the ones after reaching a new circle
        (to change the flows)
        """
        if self.state == self.previous_state:
            pass
        else:
            transition = self.regions[self.state]\
                       - self.regions[self.previous_state]
        # actually from now on are computations to be done externally
            if np.abs(transition <= 3):
                # choice has been mane.
                # eventually punish or reward accordingly
                # and change flows
                # using from "manipulation_classes.py"
                if transition == -1:
                    print('going away from the center')
                if transition == -2:
                    print('going away from the center')
                if transition == -3:
                    print('going away from the center')
                else:
                    print('going away from the center')
            else:
                # do something to the valves
                if transition == 4:
                    print('going to bottom right circle')
                if transition == 5:
                    print('going to top circle')
                if transition == 6:
                    print('going to bottom left circle')

if __name__ == '__main__':
    test = Observer()