#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 19:54:04 2019

@author: linjie
"""

import numpy as np
import cv2
import os, stat


CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4

# Define camera farame size
frame_width = 640
frame_height = 480

# Define camera device 
camera  = 0

# Define number of training sample
samplingtimes = 10

# Define cascades xml path
cascadesPath = "../Cascades/haarcascade_frontalface_alt2.xml"
#cascadesPath = "Cascades/haarcascade_frontalface_default.xml"

# Define trainer path
trainFile = "trainer/trainer.yaml"

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

faceCascade = cv2.CascadeClassifier( cascadesPath ) 

isFirstTrain = True

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer2 = cv2.face.LBPHFaceRecognizer_create()

if False == os.path.isfile(trainFile):
    print("\nError: "+trainFile+" not exist and creat it.")
    os.mknod( trainFile ,stat.S_IRWXU)
elif os.path.getsize( trainFile ):
    isFirstTrain = False
    print('begin')
    recognizer.read( trainFile )
    print('end')

    
def detection():
    ret, img = cam.read()
    
    #img = cv2.flip(img, 0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(int(minW), int(minH)))
    
    return img, gray, faces


def getDataAndTrain():
    global isFirstTrain
    count = 0
    faceSamples=[]
    ids = []
    
    cv2.destroyWindow("video")
    # For each person, enter one numeric face id
    face_id = input('Enter user id, end press <return> \n:')
    face_name = input('Enter user name, end press <return>\n:')
    
    img, gray, faces = detection()
    cv2.imshow('video', img)
    print("\n [INFO] Initializing face capture. Look the camera and wait ...")
    
    facenum = 0
    while True:
        while(True):
            img, gray, faces = detection()
            
            for (x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
                count += 1
                #if (w-x)*(h-y) < 330*330:
                    #img = cv2.resize(gray[y:y+h,x:x+w],(330,330),interpolation = cv2.INTER_CUBIC)
                # Save the captured image into the datasets folder
                #cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
                faceSamples.append(gray[y:y+h,x:x+w])
                #ids.append(face_id)
                ids.append(int(face_id))
                print(count)
                 
            if count >= samplingtimes:
                break
        count = 0    
        #cv2.imshow('video', img)
        
        print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
        
        if isFirstTrain:
            recognizer.train(faceSamples, np.array( ids))
            isFirstTrain = False
        else:
            recognizer.update(faceSamples, np.array( ids))      # Add new model if not exist,otherwise update existent model 
        recognizer.setLabelInfo(ids[0],str(face_name))
        #Save the model into trainer/trainer.yml
        #recognizer.write( trainFile )
        recognizer.save( trainFile)
    
        face_id = int(face_id) + 1
        facenum += 1
        if facenum > 10:
            break
    
    #fs.release()    
    # Print the numer of faces trained and end program
    print("\n [INFO] {0} faces trained.".format(len(np.unique(ids))))

def faceRecognition():
    global isFirstTrain
    if isFirstTrain:
        print("Error: No face model exist")
        return
    img, gray, faces = detection()
    #To shrink an image recommend use INTER_AREA
    #To enlarge an image recommend use INTER_CUBIC() or INTER_LINEAR
    #cv2.resize()
    for(x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
 
        # Check if confidence is less them 100 ==> "0" is perfect match
        if (confidence < 100):
            id = str(id)
            name = recognizer.getLabelInfo( int(id) )
            confidence = "  {0}%".format(round(100 - confidence))
        else:
            id = "unknown"
            name = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))
         
        print("id:"+id+" name: "+name+" confidence:"+confidence+"")
        #cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        #cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1) 

while(True):
    
    img,gray,faces = detection()
    for(x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
    cv2.imshow('video', img)
    
    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    elif k== 110:   # Press 'n'
        getDataAndTrain()
    elif k== 114:   # Press 'r'
        faceRecognition()
        
# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        