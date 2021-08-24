import numpy as np
import cv2
from collections import deque


class BakCreator:

	def __init__(self, stacklen, alpha, bgim):

		self.stacklen = stacklen
		self.alpha = alpha     #alpha = percent change
		self.bgim = bgim      #initialize bgim with initial background image
		self.Ims = FIFO(self.stacklen, 'Ims')
		self.Tims = FIFO(10, 'Tims')
		self.updatetime = 0

	def orStack(self,stack):
		if stack:
			if len(stack)==1:
			    print("Premature Stack")
			    return stack[0]
			else:
				a = stack[0]
				for i in range(len(stack)-1):
					or_i = cv2.bitwise_or(a,stack[i+1])
					a = or_i	
				return or_i
		else:
			print("Problem wih orStack: input stack is empty")

	def makeORStack(self):
		self.timsOR = self.orStack(self.Tims)
		print("Initial OR stack created")

	def update(self,newIm,fgthresh):
		self.Ims.add(newIm)
		self.Tims.add(fgthresh)
		if self.Ims.loading == False:
			self.bgim = np.median(self.Ims.stack,axis=0).astype(dtype = np.uint8)

	def run(self,newIm,fgthresh):
		if self.Tims.loading:
			self.Tims.add(fgthresh)
		else:
			self.timsOR = self.orStack(self.Tims.stack)
			numNewPix = cv2.countNonZero(
                cv2.bitwise_and(fgthresh,cv2.bitwise_not(self.timsOR)))
			if numNewPix > (self.alpha*cv2.countNonZero(fgthresh)):
				self.update(newIm,fgthresh)
				self.updatetime = 0
			else:
				self.updatetime += 1
		return self.bgim

class Background(object):
    """Store and calculate the background"""
    def __init__(self, stack_length, alpha, initial_background):
        super().__init__()
        self.stacklen = stack_length
        self.alpha = alpha     #alpha = percent change
        self.background_image = initial_background
        self.images = Fifo(self.stacklen, 'images')
        self.buffer = Fifo(10, 'buffer')
        self.update_time = 0


class FIFO: # first in first out ?
	def __init__(self,maxlength,name):
		self.maxlength = maxlength
		self.name = name
		self.stack = deque()
		self.loading = True
	def getLength(self):
		return len(self.stack)
	def add(self,im):
		length = self.getLength()
		if length < self.maxlength:
			self.stack.append(im)
		else:
			self.loading = False
			self.stack.popleft()
			self.stack.append(im)
	
class Fifo(object):
    def __init__(self, max_length, name):
        super().__init__()
        self.max_length = max_length
        self.name = name
        self.stack = deque()
        self.loading = True
    def add(self, image):
        length = len(self.stack)
        if length < self.max_length:
            self.stack.append(image)
        else:
            self.loading = False
            self.stack.popleft()
            self.stack.append(image)
