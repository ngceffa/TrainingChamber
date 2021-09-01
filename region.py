import numpy as np


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


class Region(object):
	"""Basic object to manipulate regions on the image (?)"""

	def __init__(self, loc, locs):
		"""I suppose the locations are:
		2D vector
		2D or 2N vector
		"""
		self.loc = loc #location of this region
		self.locs = locs #location of all regions

	def getNeighbors(self):
		"""Cannot really understand what this is doing"""
		i = self.locs.index(self.loc)
		del self.locs[i]
		return self.locs #(???) maybe save in a self variable?

	def distance(self, a, b): # a is the location of larva;
							  # b is other point or vector of points
		"""Calculate the distance between larva location a
		and vector b, that can be a single location
		or a series of locations (lenght 2N) """
		a = np.asarray(a)
		b = np.asarray(b)
		if a.shape == b.shape:
			# calculate distance
			displacement = a - b
			return np.sqrt(np.dot(displacement, displacement))
		else:
			# if using "vector of points", then a 2N vector
			A = np.ones_like(b) * a
			displacement = A - b
			c = []
			for i in displacement: 
				distance = (np.sqrt(np.dot(i, i)))
				c.append(distance)
			return np.array(c)

	def processPoint(self, x):
		"""Return a transition flag"""
		hyst = 10 # cutoff for considering a "transition"
		neighbors = self.locs 
		mydist = self.distance(x, self.loc)
		ndist = self.distance(x, neighbors)
		closest = np.amin(ndist)
		# so, if the new position (minus a threshold value)
		# is farther awayn then the closest, report a transition;
		# this all depends on the meaning of loc and locs in the __init__
		if abs(mydist-hyst) > closest and closest != mydist:
			transition = True
		else:
			transition = False
		return transition

	def getState(self, x): #gets current state of the larva
		neighbors = self.locs # useless to just copy the attribute
		ndist = self.distance(x, neighbors)
		closest = np.amin(ndist)
		ndist_list = np.ndarray.tolist(ndist)
		state = ndist_list.index(closest)
		return state
	
	def get_state(self, x):
		"""Compacted the previous method"""
		ndist = self.distance(x, self.locs)
		self.state = np.argmin(ndist)
	
	def getnextclosestState(self,x): #gets state larva is closest to
		neighbors = self.locs
		ndist = self.distance(x,neighbors)
		closest = np.amin(ndist)
		m, sm = float('inf'), float('inf')
		for x in ndist:
			if x <= m:
				m, sm = x, m
			elif x < sm:
                                sm = x
		ndist_list = np.ndarray.tolist(ndist)
		state = ndist_list.index(sm)



class Roi(object):
    """Refactored Region class"""
    def  __init__(self, loc, locs, threshold=20):
        """Find better names maybe
        loc = 2D vector
        locs = 2D vector or 2N vectors"""
        super().__init__()
        self.location = loc
        self.locations = locs
        self.threshold = 20 # used to determine a transitoin
        self.transition_flag = False # start with no transition detected
        self.state = 0
    
    def process_point(self, point):
        """Search for transition.
        If there is one, put transition flag to True"""
        my_distance = roi_distance(point, self.location)
        n_distances = roi_distance(point, self.locations)
        closest = np.amin(n_distances)
        if (my_distance - self.threshold) > closest and closest != my_distance:
            self.transition_flag = True
        else: self.transition_flag = False
    
    def get_state(self, point):
        """Find the minimal distance between the locations
        and the given point. Store the index in self.state"""
        n_distances = roi_distance(point, self.locations)
        self.state = np.argmin(n_distances)


if __name__ == '__main__':

	loc = [0, 0]
	locs = np.asarray(([0, 0], [1 , 1], [-1, -1], [10, 10]))
	reg = Region(loc, locs)
	ciao = reg.getnextclosestState([5,5])
	print(ciao)