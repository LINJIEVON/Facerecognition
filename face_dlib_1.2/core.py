#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 19:54:04 2019

@author: linjie
"""
import os, time
import numpy as np
import cv2
import random
import threading
import tkinter as tk
from tkinter import messagebox
from file import FileOption,FaceInfo
import face_recognition
#when run in raspberry open the annotation
#import opblas


CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4

# Define cascades xml path
cascadesPath = "Cascades/haarcascade_frontalface_alt2.xml"
#cascadesPath = "Cascades/haarcascade_frontalface_default.xml"

# Define trainer path
encodingsPath = 'encodings/encodings.pickle'

# Define number of training sample
samplingtimes = 3

font = cv2.FONT_HERSHEY_SIMPLEX

threadLock = threading.Lock()

DevicePath0 = '/dev/video0'
DevicePath1 = '/dev/video1'

#when run in raspberry open the annotation
#Resolve conflicts between openblas and applications
#opblas.set_num_threads(1)

class FaceCore(object):
    
    # devNum is usb camera device
    def __init__(self, devNum = None, frameWidth = 640, frameHeight = 480):
        # Define camera farame size
        self.camera = devNum
        self.frame_width = frameWidth
        self.frame_height = frameHeight
           
        self.cam = None
        self.console = None
        self.parentWidget = None
        
        self.threadNum = 4
        
        self.dataset = None
        self.knownsCount = 0
        self.tempKnownsCount = 0
        
        self.recogResults = []
        
        self.errorMessage = ""
        
        self.capImages = None
        self.capSwitch = False
    
    def FaceInit(self, console = None):
        
        self.console = console
        
        if None != self.cam:
            return
        if None == self.camera:
            if os.path.exists(DevicePath0):
                self.camera = 0
            elif os.path.exists(DevicePath1):
                self.camera = 1
            else:
                self.CvPrint('No Camera found')
                return -1
                
        
        self.cam = cv2.VideoCapture( self.camera )
        
        retval = self.cam.isOpened()
        if retval != True:
            self.CvPrint('Error: camera open failed!')
            return -1
            
        self.cam.set( CV_CAP_PROP_FRAME_WIDTH, self.frame_width)     # set Width 
        self.cam.set( CV_CAP_PROP_FRAME_HEIGHT, self.frame_height)   # set Height
        
        # Get all encoded face data
        self.dataset = FileOption().LoadDataset()
        if self.dataset is not None: 
            self.knownsCount = len( self.dataset['ids'] ) / samplingtimes
            self.tempKnownsCount = self.knownsCount
        
        
        # Define min window size to be recognized as a face
        self.minW = 200
        self.minH = 200
        #self.minW = 0.1*self.cam.get(CV_CAP_PROP_FRAME_WIDTH)
        #self.minH = 0.1*self.cam.get(CV_CAP_PROP_FRAME_HEIGHT)
        
        self.faceCascade = cv2.CascadeClassifier( cascadesPath ) 

        string = 'camera ' + str( self.camera ) + ' open success !\n' + \
                'frame width: ' + str( self.cam.get(CV_CAP_PROP_FRAME_WIDTH) ) + '\n'\
                'frame height: ' + str( self.cam.get(CV_CAP_PROP_FRAME_HEIGHT) ) + '\n'\
                'face num: ' + str( self.knownsCount )
                
        self.CvPrint(string)
        
        return 0
    
    def Detection(self):
        if None == self.cam:
            self.CvPrint('Error: camera is not open')
            self.Message(2, 'Error', 'camera is not open')
            return
        ret, img = self.cam.read()
    
        #img = cv2.flip(img, 0)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
        faces = self.faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(int( self.minW ), int( self.minH )))
        if self.capSwitch and len(faces) > 0:
            retvalue = self.capImages.Put(rgb, faces)
            if retvalue < 0:
                self.capSwitch = False
        return rgb,faces  
    
 
    def DrawRectangle(self, img, faces):
        for(x,y,w,h) in faces:
            #cv2.imwrite("dataset/User." + str(1) + '.' + str(1) + ".jpg", gray[y:y+h,x:x+w])
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
    
    
    
    def TrainFromCamera(self, name, info):
        if None == self.cam:
            self.CvPrint('Error: camera is not open')
            self.Message(2, 'Error', 'camera is not open')
            return
        
        count = 0
        faceSamples=[]
        ids = []
        knownEncodings = []
        boxes = []
        
        string = "\n [INFO] Initializing face capture. Look the camera and wait ..."
        self.Message(0, 'info', string)
        self.CvPrint(string)
        
        while True:
            face_id = random.getrandbits(31)
            retvalue = self.IsIdExist(str(face_id))
            if retvalue < 0:
                break
        
        self.capSwitch = True
        self.capImages = DetImages(samplingtimes)
        while self.capSwitch:
            time.sleep(0.2)
            
        while True:
            rgb, faces = self.capImages.Get()
            if faces is None:
                break
            for(x,y,w,h) in faces:
                # OpenCV returns bounding box coordinates in (x, y, w, h) order
                # but we need them in (top, right, bottom, left) order, so we
                # need to do a bit of reordering
                #boxes = [(y, x + w, y + h, x) for (x, y, w, h) in faces]
                box = (y, x + w, y + h, x)
                count += 1
                faceSamples.append(rgb)
                boxes.append(box)
                ids.append(face_id)
                break
                 
            if count >= samplingtimes:
                break
        
        if 0 == len(faceSamples):
            string = "\n [INFO] No faces deteched, Training faces failed!"
            self.Message(0, 'info', string)
            self.CvPrint(string)
            
        for i,face in enumerate(faceSamples):
            # compute the facial embedding for the face
            encoding = face_recognition.face_encodings(face, [boxes[i]])
            knownEncodings.append(encoding)
            
        if self.dataset is not None:
            for i in range(samplingtimes):
                self.dataset['encodings'].append(knownEncodings[i])
                self.dataset['ids'].append(ids[i])
        else:
            self.dataset = {"encodings": knownEncodings, "ids": ids}
        
        faceInfo = FaceInfo(faceId = face_id, name = name, info = info)
        self.AddNewFace(faceInfo)
        
        # Print the numer of faces trained and end program
        string = "\n [INFO] {0} faces trained.".format(len(np.unique(ids)))
        self.Message(0, 'info', string)
        self.CvPrint(string)
        
        return face_id
        

    def FaceRecognition(self):
        if None == self.cam:
            self.errorMessage = 'camera is not open'
            self.CvPrint('Error: camera is not open')
            return {}
        
        self.tempKnownsCount = self.knownsCount     # Refill the counter
        self.recogResults.clear()   #empty the result list
        
        #print(self.tempRecognizerCount)
        if 0 >= self.tempKnownsCount:
            self.errorMessage = 'No face model exist'
            self.CvPrint('Error: No face model exist')
            return {}
        
        self.capSwitch = True
        self.capImages = DetImages(1)
        
        while self.capSwitch:
            time.sleep(0.1)
            
        encoding = None
        rgb, faces = self.capImages.Get()
        if faces is None:
            self.errorMessage = 'No face deteched'
            self.CvPrint('Error: No face deteched')
            return {}
        for(x,y,w,h) in faces:
            box = (y, x + w, y + h, x)
            encoding = face_recognition.face_encodings(rgb, [box])
            
        threads = []
        #start =time.time()
        for i in range(self.threadNum):
            thread = MyThread(self.Recognition, encoding)
            thread.start()
            threads.append(thread)
        
        for th in threads:
            th.join()
            
        #end =time.time()
        #print('Running time: %s Seconds'%(end-start))
         
        self.recogResults.sort(key = lambda k: k[0]) #sort by value
        if len(self.recogResults) ==0:
            string = 'Error: The recognizer return an empty list, Try again!'
            self.CvPrint(string)
            self.errorMessage = string
            return {}
        #print(self.recogResults)str(face_id)
        final = self.recogResults[0]
        
        label = final[1]
        distance = final[0]
        
        faceInfo = FileOption().GetFaceInfo(label)
        
        entity = Entity(faceInfo.faceId, faceInfo.name, faceInfo.info, distance)
        string2 = '\nid: ' + faceInfo.faceId + entity.eToString()
        self.CvPrint(string2)
    
        return {'name' : faceInfo.name, 'distance' : str(distance)}
        
        #cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        #cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)
            
    def Recognition(self, encoding):
        while True:
            threadLock.acquire()
            index = self.tempKnownsCount -1
            self.tempKnownsCount -= 1
            threadLock.release()
            
            if 0 > index:
                break
            
            index =  int(index * samplingtimes)
            
            distance0 = face_recognition.face_distance(np.array(self.dataset['encodings'][index]), np.array(encoding))
            distance1 = face_recognition.face_distance(np.array(self.dataset['encodings'][index + 1]), np.array(encoding))
            distance2 = face_recognition.face_distance(np.array(self.dataset['encodings'][index + 2]), np.array(encoding))
           
            distance = (distance0[0] + distance1[0] + distance2[0]) / samplingtimes
            result = (distance, self.dataset['ids'][index])
            self.recogResults.append(result)
            #print(threading.currentThread().ident)
       
        
    def Message(self, priority, title, content):
        if 2 == priority:
            messagebox.showerror(title = title, message = content, parent = self.parentWidget)
        else:
            messagebox.showinfo(title = title, message = content, parent = self.parentWidget)
    
    
    def GetRecognitionMessage(self):
        return self.recogmsg.eToString()
    
    
    def ConsoleWrite(self, content):
        message = content+ '\n'
        self.console.config(state = tk.NORMAL)
        self.console.insert( tk.END, message)
        self.console.see(tk.END)
        self.console.config(state = tk.DISABLED)
      
        
    def CvPrint(self, content):
        if None != self.console:
            self.ConsoleWrite(content)
        print(content)
        
    
    def AddNewFace(self, faceInfo):
        #Write to faceinfo file
        foption = FileOption()
        foption.WriteFaceInfo(faceInfo)
        #print(faceInfo.info)
        
        #write to encodings file
        FileOption().WriteEncodings(self.dataset)
        
        #Synchronization variable value
        self.knownsCount += 1
        self.tempKnownsCount = self.knownsCount
    
    def IsIdExist(self, label): # label type is str
        if self.dataset is not None:
            for i,item in enumerate(self.dataset['ids']):
                #print(str(label) + ' ' + str(item))
                if str(label) == str(item):
                    return i
        return -1
    
    
    def DeleteFaces(self, labels):
        foption = FileOption()
        foption.DeleteFaceInfos(labels)
        for label in labels:
            index = self.IsIdExist(label)
            if index >= 0:
                for i in range(samplingtimes):
                    del self.dataset['encodings'][index]
                    del self.dataset['ids'][index]
                    
                self.knownsCount -= 1
                self.tempKnownsCount = self.knownsCount
                foption.WriteEncodings(self.dataset)
                
        self.CvPrint('Deleted ' +str( len(labels) )+ ' faces success!')
                   
    def SetParentWidget(self, parent):
        del self.parentWidget
        self.parentWidget = None
        self.parentWidget = parent
        
    
   
        
    def __del__(self):
        print('destroy object CvCore')
        if None != self.cam:
            if self.cam.isOpened():
                self.cam.release()
        



class Entity(object):
    
    def __init__(self, eId, eName, eInfo, eConfidence = None):
        self.id = eId
        self.name = eName
        self.info = eInfo
        self.confidence = eConfidence
        
    def eToString(self):
        string = '\nName: ' + self.name + '\n'\
                'Confidence: ' + str(self.confidence) + '\n'\
                'Info: ' + self.info
        return string
    
    def __del__(self):
        print('destroy object Entity')




class MyThread (threading.Thread):
    def __init__(self, func, *args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
            
    def run(self):
        argNum = len(self.args)
        if 0 == argNum:
            self.func()
        elif 1 == argNum:
            self.func(self.args[0])
        elif 2 == argNum:
            self.func(self.args[0], self.args[1])
            
                       
class DetImages:
    
    def __init__(self, size = 3):
        self.size = size
        self.detImages = []
    
    def Put(self, img, box):
        if self.size > len(self.detImages):
            self.detImages.append( (img,box) )
            return 0
        else:
            return -1
    
    def Get(self):
        if len(self.detImages) > 0: 
            item = self.detImages.pop()
            return item[0], item[1]
        else:
            return None, None
    
    def SetEmpty(self):
        if len(self.detImages) > 0:
            self.detImages.clear()




if __name__ == '__main__':
    pass


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        