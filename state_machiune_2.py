
import numpy as np
import ymaze_utility_functions as utils



class DiscreteStates(object):
    """Refactored Region class"""
    def  __init__(self, loc, locs, threshold=20):
        """Find better names maybe
        loc = 2D vector
        locs = 2D vector or 2N vectors"""
        super().__init__()
        self.location = loc
        self.locations = locs
        self.threshold = threshold # used to determine a transition
                                   # it removes ambiguity.
        n_distances = utils.points_distance(loc, self.locations)
        self.initial_state = np.argmin(n_distances)
        self.location = self.locations[self.initial_state] #stantig state
        # cancel after testing:
        print('Starting in state ', self.state)
        print('Located in', self.location)
        print('From the barycenter found in', self.location)
    
    def get_state(self, point):
        # add the computation of the next closest state!
        """Find the minimal distance between the locations
        and the given point. Store the index in self.state"""
        if point == [-1, -1]:
            pass # do nothing if larva centre is not properly found
        else:\
            # instantaneous distance between now and the previous state-point
            my_distance = utils.points_distance(point, self.location)
            # distances between now and all state-points
            n_distances = utils.points_distance(point, self.locations)
            closest = np.amin(n_distances)
            if ((my_distance - self.threshold) > closest
            and closest != my_distance):
                self.state = np.argmin(n_distances)
                self.location = self.locations[self.state]
