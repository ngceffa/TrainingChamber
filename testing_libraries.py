import numpy as np
import matplotlib.pyplot as plt
import cv2
import imageio

def Centroid(cnt):
	"""Calculate the centroid vector
	of the image 'cnt'
	using the first moments
	"""
	M = cv2.moments(cnt)
	cx = int(M['m10'] / M['m00']) # x position of the center
	cy = int(M['m01'] / M['m00']) # y position of the center
	centroid = [cx, cy]
	return centroid

def FindLarva(img):
	"""Calculate the contours
	and use them to compute the centroid
	"""
	_, contours, _ = cv2.findContours(
		img, # input image
		cv2.RETR_TREE, # contour retrieaval mode
		# (this searches for all contour and organizes them in a hierarchy)
		cv2.CHAIN_APPROX_NONE # contour approximation method -> none by default
		)
	# retrieve the areas for each countour
	areas = []
	for contour in contours:
		areas.append(cv2.contourArea(contour))
	# calculate the centroid
	if len(areas) >= 1:
		larva = contours[np.argmax(areas)]
		centroid = Centroid(larva)
	else:
		centroid = [-1, -1] # fake centroid if no larva is found (?)
							# it seems to act like a flag
	return centroid

if __name__ == "__main__":

    path = '/home/ngc/Desktop/test_data'

    larva = imageio.imread(path + '/perfectly_thresholded.png')

    center = FindLarva(larva)
    print(center)

    # current = new.copy() #so, do I really need to pass "current" then?
	# if current.shape !=  new.shape: # should be impossible	current = new
	# else:
	# 	current = cv2.addWeighted(new,weight,current,1-weight,0)
	# return current