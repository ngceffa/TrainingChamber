import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":

    def funbc(weight):
        print(weight)
        if weight < 0:
            weight = 0
            print(weight)
        if weight > 1:
            weight = 1
            print(weight)
        if weight == 1:
            print(weight)
        return weight

    w = funbc(-10)
    # current = new.copy() #so, do I really need to pass "current" then?
	# if current.shape !=  new.shape: # should be impossible	current = new
	# else:
	# 	current = cv2.addWeighted(new,weight,current,1-weight,0)
	# return current