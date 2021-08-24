
from region import Region
import numpy as np
from region import Roi


def roi_distance(start=[0, 0], stop=[0, 0]):
    """Find the distance between two positions
    or between a position and an array if positions.
    """
    start = np.asarray(start)
    stop = np.asarray(stop)
    if start.shape == stop.shape:
        return np.linalg.norm(start - stop)
    else:
        distance = np.zeros((stop.shape[0], 2))
        repeated = np.ones_like(stop) * start
        for row in range(repeated.shape[0]):
            distance[row] = np.linalg.norm(repeated[row] - stop[row])
        return distance

class StateMachine:

	def __init__(self, initial, locs):
		self.initial = initial
		self.locs = locs
		self.state =\
			Initializer(self.initial, self.locs).starting_point(self.initial)

	def on_input(self, input):
		self.prevnumber = self.state.mynumber
		if input == [-1, -1]: #if tracker lost larva, keep previous state
					try:
							self.prevnumber
					except NameError:
							return 0, 0, 0
					else:
							return self.prevnumber,\
									self.prevnumber,\
									self.prevnumber
		else:
			self.state = self.state.on_input(input)
			self.number = self.state.getState(input)
			self.nextnum = self.state.getnextclosestState(input)
			return self.prevnumber, self.number, self.nextnum

class Initializer(Region):
	def starting_point(self, input):
		states = {0 : Zero(self.locs[0], self.locs),
					1 : One(self.locs[1], self.locs),
					2 : Two(self.locs[2], self.locs),
					3: Three(self.locs[3], self.locs),
					4: Four(self.locs[4], self.locs),
					5: Five(self.locs[5], self.locs),
					6: Six(self.locs[6], self.locs)}
		state = self.getState(input)
		return states[state]

class Zero(Region):
	mynumber = 0 # never used ?	
	def on_input(self, input):
		if input != [-1,-1]:
			states = {0 : self,
						1 : One(self.locs[1],self.locs),
						2 : Two(self.locs[2],self.locs),
						3: Three(self.locs[3],self.locs),
						4: Four(self.locs[4],self.locs),
						5: Five(self.locs[5],self.locs),
						6: Six(self.locs[6], self.locs)}
			transition = self.processPoint(input)
			state = self.getState(input)
			if transition == True:
				return states[state]
			else:
				return self # if no transition, stay in Zero

class One(Region):
	mynumber = 1
	def on_input(self, input):
		if input != [-1,-1]:
			states = {0 : Zero(self.locs[0],self.locs), 1 : self, 2 : Two(self.locs[2],self.locs), 3: Three(self.locs[3],self.locs), 4: Four(self.locs[4],self.locs), 5: Five(self.locs[5],self.locs), 6: Six(self.locs[6], self.locs)}
			transition = self.processPoint(input)
			state = self.getState(input)
			if transition == True:
				return states[state]
			else:
				return self

class Two(Region):
	mynumber = 2
	def on_input(self, input):
		if input != [-1,-1]:
			states = {0 : Zero(self.locs[0], self.locs), 1 : One(self.locs[1],self.locs), 2 : self, 3: Three(self.locs[3],self.locs), 4: Four(self.locs[4],self.locs), 5: Five(self.locs[5],self.locs), 6: Six(self.locs[6], self.locs)}
			transition = self.processPoint(input)
			state = self.getState(input)
			if transition == True:
				return states[state]
			else:
				return self

class Three(Region):
	mynumber = 3
	def on_input(self, input):
		if input != [-1,-1]:
			states = {0 : Zero(self.locs[0], self.locs), 1 : One(self.locs[1],self.locs), 2 : Two(self.locs[2],self.locs), 3: self, 4: Four(self.locs[4],self.locs), 5: Five(self.locs[5],self.locs), 6: Six(self.locs[6], self.locs)}
			transition = self.processPoint(input)
			state = self.getState(input)
			if transition == True:
				return states[state]
			else:
				return self
	
class Four(Region):
	mynumber = 4
	def on_input(self, input):
		if input != [-1,-1]:
			states = {0 : Zero(self.locs[0], self.locs), 1 : One(self.locs[1],self.locs), 2 : Two(self.locs[2],self.locs), 3: Three(self.locs[3],self.locs), 4: self, 5: Five(self.locs[5],self.locs), 6: Six(self.locs[6], self.locs)}
			transition = self.processPoint(input)
			state = self.getState(input)
			if transition == True:
				return states[state]
			else:
				return self

class Five(Region):
	mynumber = 5
	def on_input(self, input):
		if input != [-1,-1]:
			states = {0 : Zero(self.locs[0], self.locs), 1 : One(self.locs[1],self.locs), 2 : Two(self.locs[2],self.locs), 3: Three(self.locs[3],self.locs), 4: Four(self.locs[4],self.locs), 5: self, 6: Six(self.locs[6], self.locs)}
			transition = self.processPoint(input)
			state = self.getState(input)
			if transition == True:
				return states[state]
			else:
				return self

class Six(Region):
	mynumber = 6
	def on_input(self, input):
		if input !=[-1,-1]:
			states = {0 : Zero(self.locs[0], self.locs), 1 : One(self.locs[1],self.locs), 2 : Two(self.locs[2],self.locs), 3: Three(self.locs[3],self.locs), 4: Four(self.locs[4],self.locs), 5: Five(self.locs[5],self.locs), 6: self}
			transition = self.processPoint(input)
			state = self.getState(input)
			if transition == True:
				return states[state]
			else:
				return self

# states = np.asarray((
# 	[10,10],
# 	[20, 20],
# 	[-10, -10],
# 	[40,40],
# 	[35,35],
# 	[20,10],
# 	[8, -20]))
# test = StateMachine([0,0], states)
# print(test.state)
# print(test.state.mynumber)
# test.on_input([40,20])
# print(test.state)
# print(test.state.mynumber)

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
        # self.transition_flag = False # start with no transition detected
        # self.state = self.get_state(self.location)
        n_distances = roi_distance(loc, self.locations)
        self.initial_state = np.argmin(n_distances)
        self.location = self.locations[self.initial_state] #stantig state
        print('Starting in state ', self.state)
        print('Located in', self.location)
        print('From the barycenter found in', self.location)
    
    def get_state(self, point):
        """Find the minimal distance between the locations
        and the given point. Store the index in self.state"""
        if point == [-1, -1]:
            pass # do nothing if larva centre is not properly found
        else:\
            # instantaneous distance between now and the previous state-point
            my_distance = roi_distance(point, self.location)
            # distances between now and all state-points
            n_distances = roi_distance(point, self.locations)
            closest = np.amin(n_distances)
            if ((my_distance - self.threshold) > closest
            and closest != my_distance):
                self.state = np.argmin(n_distances)