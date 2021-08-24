from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
from statemachine import StateMachine
from statemachine import Initializer
from statemachine import Zero
from statemachine import One
from statemachine import Two
from statemachine import Three
from statemachine import Four
from statemachine import Five
from statemachine import Six
from lightsvalvesobject_longterm import LightsValves
import random
import RPi.GPIO as GPIO
from collections import Counter
from collections import deque
from BakCreator import BakCreator
from BakCreator import FIFO

def ExponentialFilter(current, new, weight):
	"""Create a "filtered" version of the current image.

	First check if the weight is between 0 and 1.
	If negative: it's 0.
	If >1: it's 1.

	Then use cv2 AddWeighted if current has same shape as new.
	Otherwise just copy the image (current becomes new).
	"""
	# the last thing is not super clear...
	# also... is this actualyl a "filter"?
	if weight < 0:
		weight = 0
	if weight > 1:
		weight = 1
	if weight == 1:
		current = new.copy() 
	if current.shape !=  new.shape: 
		current = new
	else:
		current = cv2.addWeighted(new, weight, current, 1-weight,0)
		# linear blending  of new (with weight 'weight')
		# and current (with weight '1-weight')
		# and constant term 0.
		# Formula:
		# result = (weight_1 x Image_1) + (weight_2 x Image_2) + constant
	return current

def readImage(cap):
	# check the cap class!
	""" Read an image from cap ('capture') class in cv2"""
	#im = camera.capture(cap, format = 'bgr') # ? rewriting on the same?
	im = cap.array
	im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) # depending on the camera NB
	return im

def displacement(new, prev):
	"""Calculate the distance between two 2D vectors.
	new = 'current' 2D vectror
	prev = 'previous' 2D vector
	"""
	xi = prev[0]
	xf = new[0]
	yi = prev[1]
	yf = new[1]
	return(np.sqrt((xi - xf)**2 + (yf - yi)**2))

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

def FindLarva_2(img): # compacted function
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

def FindLarva(img):
	"""Calculate the contours and use them to compute the centroid"""
	# _, contours, _ = cv2.findContours(
	# 	img, # input image
	# 	cv2.RETR_TREE, # contour retrieaval mode
	# 	# (this searches for all contour and organizes them in a hierarchy)
	# 	cv2.CHAIN_APPROX_NONE # contour approximation method -> none by default
	# 	)

	# Neil/Rey: on Pi's with Buster, 
	# it's 2 arguments not 3
	# so (contours,_) 
	# not (_, contours, _)
	# I think this is the correct one for us:
	contours, _ = cv2.findContours(
		img, # input image
		cv2.RETR_TREE, # contour retrieaval mode
		# (this searches for all contour and organizes them in a hierarchy)
		cv2.CHAIN_APPROX_NONE # contour approximation method -> none by default
		)
	length = int(len(contours)) # int is redundant
	areas = []
	for i in range(0, length):
		if length > 0: # always satisfyed... ?
			area = cv2.contourArea(contours[i])
			areas.append(area)
		else:
			break

	# I would rather do:
	# for contour in contours:
	# 	areas.append(cv2.contourArea(contour))

	if len(areas) >= 1:
		largestCont = np.amax(areas) # should be always the fist one,
									 # thanks to cv2.RETR_TREE hierarchy (?)
									 # CHECK THIS!

		loc = areas.index(largestCont)
		larva = contours[loc]

		centroid = Centroid(larva)
		return centroid
	else:
		centroid = [-1, -1] # fake centroid if no larva is found (?)
							# it seems to act like a flag
		return centroid

# here the actual program starts
##################################CAMERA INITIALIZATION#######################
# Raspberry Pi variables
ir = 13
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(ir,GPIO.OUT)
GPIO.output(ir,GPIO.HIGH)

# Camera
resx = 300
resy = 300
camera = PiCamera()
camera.resolution = (resx, resy)
camera.framerate = 20

#getting the first frame
rawCapture = PiRGBArray(camera, size=(resx,resy))
rawCapture_0 = PiRGBArray(camera, size=(resx,resy))

current = readImage(rawCapture_0)

resetfilter = 1
weight = 0.2
im_multiplier = 10
fgthreshold = 20

y0 = 65
y1 = 360
x0 = 165
x1 = 460
############################################################################################
################################REGION SELECTION INITIALIZATION#############################
locs = []
def selectRegions(event, x, y, flags, param):
	if event == cv2.EVENT_LBUTTONDOWN:
		cv2.circle(image, (x,y), 100, (0, 255, 0), 3)
		region = [x,y]
		locs.append(region)

number_of_regions = 7

cv2.namedWindow('Frame')
cv2.setMouseCallback('Frame', selectRegions)

for frame in camera.capture_continuous(
	rawCapture,
	format = 'bgr',
	use_video_port = True
	):
	image = frame.array
	cv2.imshow('Frame', image)
	key= cv2.waitKey(1) & 0xFF
	rawCapture.truncate(0)
	if len(locs) == number_of_regions:
		response = input(
			"Are you satisfied with the regions you have selected? (yes/no)")
		if response == "yes":
			break
		if response == "no":
			locs = []
	if key == ord('q'):
		break
############################################################################################
################################STATE MACHINE INITIALIZATION################################
initial = locs[0]
statemachine = StateMachine(initial,locs)

############################################################################################
####################################GPIO INITIALIZATION#####################################
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

red = 12
ir = 13
v1 = 4
v2 = 17
v3 = 27
v4 = 22
v5 = 5
v6= 6
GPIO.setup(red, GPIO.OUT)
GPIO.setup(ir, GPIO.OUT)
GPIO.setup(v1, GPIO.OUT)
GPIO.setup(v2, GPIO.OUT)
GPIO.setup(v3, GPIO.OUT)
GPIO.setup(v4, GPIO.OUT)
GPIO.setup(v5, GPIO.OUT)
GPIO.setup(v6, GPIO.OUT)

lightsvalves = LightsValves(red,ir,v1,v2,v3,v4,v5,v6)
lightsvalves.offall()

############################################################################################
###################################EXPERIMENT###############################################


########BUILD UP BACKGROUND IMAGE####################################

fps = 10 #frame rate
rawCapture = PiRGBArray(camera, size=(resx,resy))
rawCapture_0 = PiRGBArray(camera, size=(resx,resy))
frame_0 = readImage(rawCapture_0)
Ims = deque()               #set up FIFO data structure for video frames
Ims.append(frame_0)
N = 1              #N keeps track of how many frames have gone by
window = 60        #sets the length of the window over which mean is calculated

print('Building Background')

for frame in camera.capture_continuous(
	rawCapture,
	format = 'bgr',
	use_video_port = True
	):
    im = frame.array
    im=cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    if N == fps:            #add a new frame to kernel each second
            Ims.append(im)
            N = 1
    if len(Ims)==window:
            bgim = np.median(Ims, axis=0).astype(dtype = np.uint8)
            break
    N +=1
    cv2.imshow('background', im)
    key= cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if key == ord('q'):
	    break

print("Background Built")

##### Read in data file #####

with open('scheme_longterm.txt', 'r') as f:
    scheme = f.read().splitlines()
f.close()
setupname = scheme[1]
date = scheme[3]
ptnumber = int(scheme[5])
ptnumberstring = str(ptnumber)
timeofday = scheme[7]
naivetime = int(scheme[9])
testtime = int(scheme[11])
trainreps = int(scheme[13])
rewardwhen = scheme[15]
repetitions = int(scheme[17])+1
trainingtype = scheme[19]
phasedtraining = scheme[21]
longerairtraining = scheme[23]
co2offduringtrain = scheme[25]
spacedtrainingperset = int(scheme[27])
spacedtrainingreps = int(scheme[29])


filepath = "/home/pi/shared/"
filepath_vid= "/home/pi/videos/"

parameterfile = filepath + setupname + "_" + date + "_" + timeofday + "_parameters.txt"
with open(parameterfile,'w') as filehandle:
	filehandle.writelines("%s\n" % place for place in scheme)

if trainingtype == "N":
	filenamestring = setupname+"_"+date+"_"+timeofday+"_"+"PT"+ptnumberstring+"_"
	videonamestring = setupname+"_"+date+"_"

if trainingtype == "R":
	filenamestring = setupname+"_"+date+"_"+timeofday+"_"+reciprocal+"_"+"PT"+ptnumberstring+"_"
	videonamestring = setupname+"_"+date+"_"+reciprocal+"_"

if trainingtype == "P":
	filenamestring = setupname+"_"+date+"_"+timeofday+"_"+"PT"+ptnumberstring+"_"+"PhaseShifted"+phasedtraining+"_"
	videonamestring = setupname+"_"+date+"_"+"PhaseShifted"+phasedtraining+"_"

if trainingtype == "S":
	filenamestring = setupname+"_"+date+"_"+timeofday+"_"+"spaced_"+"PT"+ptnumberstring+"_"
	videonamestring = setupname+"_"+date+"_"


lightsvalves.offall()

##### Naive Runs #####

print("naive runs start")
print("naive time = " + str(naivetime)) 
blocknumber = 0
blocknumberstring = str(blocknumber)
naivefilename = filenamestring + blocknumberstring + "_naive.txt"
naivefilenameall = filenamestring + blocknumberstring + "_naive_all.txt"
naivefilenameall_vid = filenamestring + blocknumberstring + "_naive_all.h264"
naivefilenamepath = filepath + naivefilename
naivefilenamepathall = filepath + naivefilenameall
naivefilenamepathall_vid = filepath_vid + naivefilenameall_vid
naivefile = []
naiveall = []
naiveframe = []
valvelog = []
valvelogname = filenamestring + blocknumberstring + "_naive_valvelog.txt"
valvelogpath = filepath + valvelogname

naivepercent = 0

naivefilenamepath_positionframe = filepath + filenamestring + blocknumberstring + "_naive_positionframe.txt"
positionframefile = []

rawCapture = PiRGBArray(camera, size=(resx,resy))

bgCreate = BakCreator(stacklen = 60, alpha = 0.02, bgim=bgim)  #create an instance of the background update class
#loading = True								#variable to load up FIFO queues
#use_init = True								#use the background built initially

camera.start_recording(naivefilenamepathall_vid)
starttime = time.time()
framecount = 0
prev_pos = [0,0]
odorontime = [0]
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	newRaw = frame.array
	new = cv2.cvtColor(newRaw, cv2.COLOR_BGR2GRAY)
	fgim = cv2.subtract(new,bgim)
	_,fgthresh = cv2.threshold(fgim, fgthreshold, 255, cv2.THRESH_BINARY)
	fgthresh = cv2.morphologyEx(fgthresh, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
	fgthresh = cv2.morphologyEx(fgthresh, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
	bgim = bgCreate.run(new,fgthresh)
	maggot = FindLarva(fgthresh)
        disp = displacement(prev_pos,maggot)
        prev_state, curr_state, nextclosest_state = statemachine.on_input(maggot)
	framecount = camera.frame.index
	timestamp = time.time()- starttime
	lightsvalves.run_test_noreward(prev_state, curr_state, nextclosest_state, naivefile, naiveall, starttime, framecount,maggot,odorontime, valvelog)
        positionframefile.append([maggot,framecount,timestamp])
        prev_pos = maggot
	cv2.circle(new,tuple(maggot), 2, (0,0,255),-1)
	cv2.imshow('experiment', new)
	cv2.imshow('background image',bgim)
	key = cv2.waitKey(1) & 0xff
	rawCapture.truncate(0)
	if key == ord('q'):
		break
	looptime = time.time()
	elapsedtime = looptime - starttime
	if elapsedtime > naivetime:
		break
camera.stop_recording()

with open(naivefilenamepath,'w') as filehandle: #decision list (0,1)
	filehandle.writelines("%s\n" % place for place in naivefile)
with open(valvelogpath,'w') as filehandle: #valvelog 
	filehandle.writelines("%s\n" % place for place in valvelog)
with open(naivefilenamepathall,'w') as filehandle: #decision list descriptive
	filehandle.writelines("%s\n" % place for place in naiveall)
with open(naivefilenamepath_positionframe,'w') as filehandle: #larva position at each timestamp
	filehandle.writelines("%s\n" % place for place in positionframefile)

print("naive runs done")


##### Training/Testing Runs #####

for i in range(1,repetitions):

	lightsvalves.offall()
	print("training start, " + str(ptnumber) + " reps")
	if trainingtype == "N":
		if co2offduringtrain == "Y":
		        print("CO2 off during training")
			lightsvalves.co2offduringtraining(ptnumber)
		else:
			print("CO2 reward training")
			lightsvalves.training(ptnumber,trainreps,rewardwhen)

	if trainingtype == "R":
                print("air reward training")
                lightsvalves.reciprocal_pretrain(ptnumber)

	if trainingtype == "S":
		print("Spaced training: 2x reward, wait 15 minute; repeat 5x")
		lightsvalves.spacedtraining(ptnumber, spacedtrainingperset, spacedtrainingreps)

	if trainingtype == "P":
		if phasedtraining == "CO2First":
			print("Phase Shifted Reward Training:")
			print("CO2 on 0-15 s, red light on 7.5 - 22.5 s")
			lightsvalves.phasetrain_co2first(ptnumber)
		if phasedtraining == "LightFirst":
			print("Phase Shifted Reward Training:")
			print("CO2 on 0-15 s, red light on 22.5 - 7.5 s")
			lightsvalves.phasetrain_airfirst(ptnumber)

	if trainingtype == "L":
		if longerairtraining == "Paired":
			print("Paired longer air time Reward Training:")
			print("CO2 on 0-15 s, red light on 15-30 s")
			lightsvalves.longerairpaired(ptnumber)
		if longerairtraining == "Unpaired":
			print("Unpaired longer air time Reward Training:")
			print("CO2 on 0-15 s, red light on 60-75 s")
			lightsvalves.longerairunpaired(ptnumber)
		if longerairtraining == "DoubleCO2":
			print("longer air time Reward Training with 2 CO2 pulses:")
			print("CO2 on 0-15 s, red light on 15-30 s, CO2 on 30-45 s")
			lightsvalves.longerairtwoco2(ptnumber)
	
	
	print("training finished")

	print("block " + str(i))	
	lightsvalves.offall()
	GPIO.output(ir,GPIO.HIGH)
	rawCapture = PiRGBArray(camera, size=(resx,resy))
	rawCapture_0 = PiRGBArray(camera, size=(resx,resy))
	current = readImage(rawCapture_0)
	fgthreshold = 20
	initial = locs[0]
	statemachine = StateMachine(initial,locs)

	
	blocknumber = i
	blocknumberstring = str(blocknumber)
        testfilename = filenamestring + blocknumberstring + "_test.txt"
        testfilenameall = filenamestring + blocknumberstring + "_test_all.txt"
	testfilename_vid = filenamestring + blocknumberstring + "_test.h264"

	testfile = []
	testfileall = []
        positionframefile = []
        valvelog = []
        
	testfilenamepath = filepath + testfilename
	testfilenamepath_vid = filepath_vid + testfilename_vid
        testfilenamepathall = filepath + testfilenameall
        testfilenamepath_positionframe = filepath + filenamestring + blocknumberstring + "_test_positionframe.txt"

        valvelogname = filenamestring + blocknumberstring + "_test_valvelog.txt"
        valvelogpath = filepath + valvelogname

        
	print("test for seconds = " + str(testtime))

	fps = 10 #frame rate
	rawCapture = PiRGBArray(camera, size=(resx,resy))
	rawCapture_0 = PiRGBArray(camera, size=(resx,resy))
	frame_0 = readImage(rawCapture_0)
	Ims = deque()                   #set up FIFO data structure for video frames
	Ims.append(frame_0)
	N = 1                           #N keeps track of how many frames have gone by
	window = 60                     #sets the length of the window over which mean is calculated
        bgim = None

	print('Building Test Background')

	for frame in camera.capture_continuous(rawCapture, format = 'bgr', use_video_port = True):
	    im = frame.array
	    im=cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
	    if N == fps:            #add a new frame to kernel each second
	            Ims.append(im)
	            N = 1
	    if len(Ims)==window:
	            bgim = np.median(Ims, axis=0).astype(dtype = np.uint8)
	            break
	    N +=1
	    cv2.imshow('background', im)
	    key= cv2.waitKey(1) & 0xFF
	    rawCapture.truncate(0)
	    if key == ord('q'):
		    break

	print("Test Background Built")

	bgim_init = bgim
	bgCreate = BakCreator(stacklen = 60, alpha = 0.02, bgim=bgim_init)  #create an instance of the background update class

	rawCapture = PiRGBArray(camera, size=(resx,resy))
	camera.start_recording(testfilenamepath_vid)
 	starttime = time.time()
 	framecount = 0
 	prev_pos = [0,0]
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		newRaw = frame.array
		new = cv2.cvtColor(newRaw, cv2.COLOR_BGR2GRAY)
                fgim = cv2.subtract(new,bgim)
		_,fgthresh = cv2.threshold(fgim, fgthreshold, 255, cv2.THRESH_BINARY)
		fgthresh = cv2.morphologyEx(fgthresh, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
		fgthresh = cv2.morphologyEx(fgthresh, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
		bgim = bgCreate.run(new,fgthresh)
		maggot = FindLarva(fgthresh)
		disp = displacement(prev_pos,maggot)
		prev_state, curr_state, nextclosest_state = statemachine.on_input(maggot)
                framecount = camera.frame.index
                timestamp = time.time() - starttime
                lightsvalves.run_test_noreward(prev_state, curr_state, nextclosest_state, testfile, testfileall, starttime,framecount,maggot,odorontime, valvelog)
                positionframefile.append([maggot,framecount,timestamp])
                prev_pos = maggot
                cv2.circle(new,tuple(maggot), 2, (0,0,255),-1)
                cv2.imshow('experiment', new)
                key = cv2.waitKey(1) & 0xff
                rawCapture.truncate(0)
                if key == ord('q'):
                    break
		looptime = time.time()
		elapsedtime = looptime - starttime
		if elapsedtime > testtime:
			break
	camera.stop_recording()

	with open(testfilenamepath,'w') as filehandle:
		filehandle.writelines("%s\n" % place for place in testfile)
	with open(testfilenamepathall,'w') as filehandle:
		filehandle.writelines("%s\n" % place for place in testfileall)
	with open(testfilenamepath_positionframe,'w') as filehandle:
                filehandle.writelines("%s\n" % place for place in positionframefile)
        with open(valvelogpath,'w') as filehandle: #valvelog 
                filehandle.writelines("%s\n" % place for place in valvelog)

	print("test done")
	print("block = " + blocknumberstring)
	
print("finished")
GPIO.output(ir,GPIO.LOW)
lightsvalves.offall()

