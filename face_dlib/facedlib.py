#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 00:33:14 2019

@author: linjie
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 19:54:04 2019

@author: linjie
"""

import numpy as np
import cv2
import os, stat
import face_recognition
#import _pickle as pickle #_pickle is cPickle, fast than pickle
import pickle


CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4

# Define camera farame size
frame_width = 640
frame_height = 480

# Define camera device 
camera  = 0

# Define number of training sample
samplingtimes = 3

# Define cascades xml path
cascadesPath = "Cascades/haarcascade_frontalface_alt2.xml"
#cascadesPath = "Cascades/haarcascade_frontalface_default.xml"

# Define encodings path
encodingsPath = "encodings.pickle"


font = cv2.FONT_HERSHEY_SIMPLEX

cam = cv2.VideoCapture( camera )

retval = cam.isOpened()
if retval != True:
    print("Error: camera open failed!")
    exit()
cam.set( CV_CAP_PROP_FRAME_WIDTH, frame_width)     # set Width 
cam.set( CV_CAP_PROP_FRAME_HEIGHT, frame_height)   # set Height

# Define min window size to be recognized as a face
minW = 200
minH = 200
#minW = 0.1*cam.get(CV_CAP_PROP_FRAME_WIDTH)
#minH = 0.1*cam.get(CV_CAP_PROP_FRAME_HEIGHT)

resize = (330,330)

faceCascade = cv2.CascadeClassifier( cascadesPath ) 

isFirstTrain = True
dataset = None

if False == os.path.isfile(encodingsPath):
    print("\nError: "+encodingsPath+" not exist and creat it.")
    os.mknod( encodingsPath ,stat.S_IRWXU)
elif os.path.getsize( encodingsPath ):
    isFirstTrain = False
    print('begin')
    dataset = pickle.loads(open( encodingsPath, "rb").read())
    print('end')

    
def detection():
    ret, img = cam.read()
    
    #img = cv2.flip(img, 0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(int(minW), int(minH)))
    
    return img, rgb, faces


def getDataAndTrain():
    global isFirstTrain
    count = 0
    faceSamples=[]
    ids = []
    knownEncodings = []
    boxes = []
    
    cv2.destroyWindow("video")
    # For each person, enter one numeric face id
    #face_id = input('Enter user id, end press <return> \n:')
    face_id = '005'
    
    img, rgb, faces = detection()
    cv2.imshow('video', img)
    print("\n [INFO] Initializing face capture. Look the camera and wait ...")
    while(True):
        img, rgb, faces = detection()
        # OpenCV returns bounding box coordinates in (x, y, w, h) order
        # but we need them in (top, right, bottom, left) order, so we
        # need to do a bit of reordering
        #boxes = [(y, x + w, y + h, x) for (x, y, w, h) in faces]
        box = ()
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
            box = (y, x + w, y + h, x)
            count += 1
            #rgb = cv2.resize(rgb[y:y+h,x:x+w], resize, interpolation = cv2.INTER_CUBIC)
            # Save the captured image into the datasets folder
            #cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
            faceSamples.append(rgb)
            boxes.append(box)
            ids.append(face_id)
            break
             
        if count >= samplingtimes:
            break   
    cv2.imshow('video', img)
    
    print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
     
    for i,face in enumerate(faceSamples):
        # compute the facial embedding for the face
        encoding = face_recognition.face_encodings(face, [boxes[i]])
        knownEncodings.append(encoding)
    if isFirstTrain is False:
        for known in knownEncodings:
            dataset['encodings'].append(known)
            dataset['names'].append(ids[0])
        f = open(encodingsPath, 'wb')
        f.write(pickle.dumps(dataset))
        f.close()
    else:
        data = {"encodings": knownEncodings, "names": ids}
        f = open(encodingsPath, "wb")
        f.write(pickle.dumps(data))
        f.close()
    
    # Print the numer of faces trained and end program
    print("\n [INFO] {0} faces trained.".format(len(np.unique(ids))))



def faceRecognition():
    global isFirstTrain
    if isFirstTrain:
        print("Error: No face model exist")
        return
    
    box = []
    encoding = []
    while True:
        img, rgb, faces = detection()
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            #rgb = cv2.resize(rgb[y:y+h,x:x+w], resize, interpolation = cv2.INTER_CUBIC)
            box.append( (y, x + w, y + h, x) )
            encoding = face_recognition.face_encodings(rgb, box)
            break
        if len(encoding) > 0:
            break
    
    for i,known in enumerate(dataset["encodings"]):
        #print(encoding)
        distance = face_recognition.face_distance(np.array(known), np.array(encoding))
        print('name: ' +dataset['names'][i] + '\ndistance: ' + str(distance))
        print(i)

while(True):
    
    img,gray,faces = detection()
    for(x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
    cv2.imshow('video', img)
    
    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    elif k== 110:   # Press 'n'
        #for i in range(100):
        getDataAndTrain()
            #print(i)
    elif k== 114:   # Press 'r'
        faceRecognition()
        
# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        