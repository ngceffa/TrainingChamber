import numpy as np
import cv2
import time
import imageio
import matplotlib.pyplot as plt


def find_centroid(image):
	"""Calculate the centroid coordinates
	of the (possibly thresholded) 'image'
	using the first moments from cv2.
    N.B. result follows row-major conventions.
	"""
    # is this row major or column major????
	M = cv2.moments(image)
	cx = int(M['m10'] / M['m00']) # x position of the center
	cy = int(M['m01'] / M['m00']) # y position of the center
	centroid = [cy, cx] # saved as row major, to work easily with numpy
	return centroid

def points_distance(start=[0, 0], stop=[0, 0]):
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


if __name__ == '__main__':
    # test = Camera()
    # test.compute_background()
    path = '/home/ngc/Desktop/test_data'
    image = imageio.imread(path + '/perfectly_thresholded.png')

    centre = find_centroid(image)

    spot = np.zeros((image.shape))
    spot[int(centre[0])-5 : int(centre[0])+5,
        int(centre[1])-5:int(centre[1])+5] = 100

    plt.imshow(image, cmap='gray')
    plt.imshow(spot, alpha = .8, cmap='Reds')
    plt.show()