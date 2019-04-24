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


CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4

# Define cascades xml path
cascadesPath = "Cascades/haarcascade_frontalface_alt2.xml"
#cascadesPath = "Cascades/haarcascade_frontalface_default.xml"

# Define trainer path
trainFileBasePath = 'trainer/'

# Define number of training sample
samplingtimes = 5

font = cv2.FONT_HERSHEY_SIMPLEX

threadLock = threading.Lock()

limitsize = (330,330)

radius = 2
neighbors =  8  

DevicePath0 = '/dev/video0'
DevicePath1 = '/dev/video1'

class CvCore(object):
    
    # devNum is usb camera device
    def __init__(self, devNum = None, frameWidth = 640, frameHeight = 480):
        # Define camera farame size
        self.camera = devNum
        self.frame_width = frameWidth
        self.frame_height = frameHeight
           
        self.cam = None
        self.console = None
        self.parentWidget = None
        
        self.threadNum = 2
        
        self.recognizers = []
        self.recognizerCount = 0
        self.tempRecognizerCount = 0
        
        self.trainFiles = []
        self.trainFilesCount = 0
        
        self.recogResults = []
        self.errorMessage = ""
    
    def CvInit(self, console = None):
        
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
        
        # Define min window size to be recognized as a face
        self.minW = 200
        self.minH = 200
        #self.minW = 0.1*self.cam.get(CV_CAP_PROP_FRAME_WIDTH)
        #self.minH = 0.1*self.cam.get(CV_CAP_PROP_FRAME_HEIGHT)
        
        self.faceCascade = cv2.CascadeClassifier( cascadesPath ) 

        string = 'camera ' + str( self.camera ) + ' open success !\n' + \
                'frame width: ' + str( self.cam.get(CV_CAP_PROP_FRAME_WIDTH) ) + '\n'\
                'frame height: ' + str( self.cam.get(CV_CAP_PROP_FRAME_HEIGHT) )
        self.CvPrint(string)
        
        #MyThread(self.RecgInit).start()
        self.RecognizerInit()
        #MyThread(self.RecognizerInit).start()
        
        return 0
    
    def Detection(self):
        if None == self.cam:
            self.CvPrint('Error: camera is not open')
            self.Message(2, 'Error', 'camera is not open')
            return
        ret, img = self.cam.read()
    
        #img = cv2.flip(img, 0)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
        faces = self.faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(int( self.minW ), int( self.minH )))

        return gray,faces   
    
    def DetectionToShow(self):
        if None == self.cam:
            self.CvPrint('Error: camera is not open')
            self.Message(2, 'Error', 'camera is not open')
            return
        #while True:
        ret, img = self.cam.read()
    
        #img = cv2.flip(img, 0)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces = self.faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(int( self.minW ), int( self.minH )))
        
        for(x,y,w,h) in faces:
            #cv2.imwrite("dataset/User." + str(1) + '.' + str(1) + ".jpg", gray[y:y+h,x:x+w])
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                
        return img   
    
    def TrainFromCamera(self, name, info):
        if None == self.cam:
            self.CvPrint('Error: camera is not open')
            self.Message(2, 'Error', 'camera is not open')
            return
        count = 0
        faceSamples=[]
        ids = []
        
        string = "\n [INFO] Initializing face capture. Look the camera and wait ..."
        self.Message(0, 'info', string)
        self.CvPrint(string)
        
        while True:
            face_id = random.getrandbits(31)
            retvalue, index = self.FindRecognizer(str(face_id))
            if 'not found'== retvalue[0]:
                break
        
        recognizer = cv2.face.LBPHFaceRecognizer_create(radius, neighbors)
        while(True):
            gray, faces = self.Detection()
            
            for (x,y,w,h) in faces:
                count += 1
                # Save the captured image into the datasets folder
                #cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
                gray = cv2.resize(gray[y:y+h,x:x+w], limitsize, interpolation=cv2.INTER_CUBIC)
                #cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray)
                faceSamples.append(gray)
                ids.append( int( face_id ) )
                print(count)
                 
            if count >= samplingtimes:
                break
        
        string = "\n [INFO] Training faces. It will take a few seconds. Wait ..."
        #self.Message(0, 'info', string)
        self.CvPrint(string)
        
        recognizer.train(faceSamples, np.array( ids))
        
        saveName = trainFileBasePath + str(face_id) + '.yaml'
        
        #Save the model into 'trainer/' dir
        recognizer.write(saveName)
        
        faceInfo = FaceInfo(faceId = face_id, name = name, info = info)
        self.AddNewFace(faceInfo, saveName)
        
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
        
        self.tempRecognizerCount = self.recognizerCount     # Refill the trainFile counter
        
        #print(self.tempRecognizerCount)
        if 0 >= self.tempRecognizerCount:
            self.errorMessage = 'No face model exist'
            self.CvPrint('Error: No face model exist')
            return {}
            
        detected = False
        gray = None
        faces = None
        while True:
            gray, faces = self.Detection()
            for (x,y,w,h) in faces:
                gray = cv2.resize(gray[y:y+h,x:x+w], limitsize, interpolation=cv2.INTER_CUBIC)
                #cv2.imwrite("dataset/User.recognition.jpg", gray)
                detected = True
            if detected:
                break
            
        threads = []
        #start =time.time()
        for i in range(self.threadNum):
            thread = MyThread(self.Recognition, gray)
            thread.start()
            threads.append(thread)
        
        for th in threads:
            th.join()
        #end =time.time()
        #print('Running time: %s Seconds'%(end-start))
         
        self.recogResults.sort(key = lambda k: k[1]) #sort by value
        if len(self.recogResults) ==0:
            string = 'Error: The recognizer return an empty list, Try again!'
            self.CvPrint(string)
            self.errorMessage = string
            return {}
        #print(self.recogResults)
        final = self.recogResults[0]
        
        label = final[0]
        confidence = final[1]
        self.recogResults.clear()
        
        faceInfo = FileOption().GetFaceInfo(label)
        
        # Check if confidence is less them 100 ==> "0" is perfect match
        if (confidence < 100):
            confidence = "  {0}%".format(round(100 - confidence))
        else:
            faceInfo.name = 'unknown'
            faceInfo.info = 'unknown'
            confidence = '0%'
        
        entity = Entity(faceInfo.faceId, faceInfo.name, faceInfo.info, confidence)
        string2 = '\nid: ' + faceInfo.faceId + entity.eToString()
        self.CvPrint(string2)
        
        return {'name' : faceInfo.name, 'confidence' : confidence}
        
        #cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        #cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)
            
    def Recognition(self, gray):
        while True:
            threadLock.acquire()
            index = self.tempRecognizerCount -1
            self.tempRecognizerCount -= 1
            threadLock.release()
            
            if 0 > index:
                break
            
            recognizer = self.recognizers[index][1]
            result = {}
           
            id, confidence = recognizer.predict(gray)
     
            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence < 100):
                result = ( str(id) , confidence)
            else:
                result = ( str(id) , 100)
           
            self.recogResults.append(result)
            #print(index)
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
        
        
    def RecognizerInit(self):
        trainFiles = []
        foption = FileOption()
        self.trainFilesCount = foption.GetTrainFiles(trainFiles)
        if 0 == self.trainFilesCount:
            return
        
        for i in range(self.threadNum):
            MyThread(self.SubRecgInit, trainFiles).start()
        #MyThread(self.WaitRelease).start()
     
        
    def SubRecgInit(self, trainFiles):
        while True:
            threadLock.acquire()
            index = self.trainFilesCount -1
            self.trainFilesCount -= 1
            if index >= 0:
                self.recognizerCount += 1
            threadLock.release()
            
            if index < 0:
                break
            file = trainFiles[index]
            label = file.split('.')[0].split('/')[1]
            recg  = cv2.face.LBPHFaceRecognizer_create(radius, neighbors)
            recg.read(file)
            self.recognizers.append( (label, recg) )
            #print(str(index) + ' ' + label)
        self.CvPrint('RecognizerInit finished!')
       
        
    def WaitRelease(self):
        while self.trainFilesCount >= 0:
            time.sleep(2)
        self.trainFiles.clear()
        self.CvPrint('trainFiles list cleard')
        
    
    
    def AddNewFace(self, faceInfo, filePath):
        #Write to faceinfo file
        foption = FileOption()
        foption.WriteFaceInfo(faceInfo)
        #print(faceInfo.info)
        
         #Add new trained face to recognizer 
        recg = cv2.face.LBPHFaceRecognizer_create(radius, neighbors)
        recg.read(filePath)
        self.recognizers.append( (faceInfo.faceId, recg) )
        self.recognizerCount += 1
        
        
        
    def DeleteFaces(self, faceIds = []):
        count = 0
        foption = FileOption()
        for faceId in faceIds:
            self.DeleteOneRecognizer(faceId)
            self.CvPrint('deleted face:' + faceId)
            count += 1
        foption.DeleteFaceInfos(faceIds)
        foption.DeleteTrainFiles(faceIds)
        self.CvPrint('Deleted ' +str(count)+ ' faces success!')
        
            
        
    
    def FindRecognizer(self, label): # label type is str
        for item in self.recognizers:
            if str(label) == str(item[0]):
                return item, self.recognizers.index(item)
        return ('not found',''),-1
    
    
    def DeleteOneRecognizer(self, label):
        retvalue, index= self.FindRecognizer(label)
        if 'not found' != retvalue[0]:
            del self.recognizers[index]
            print(self.recognizerCount)
            self.recognizerCount -= 1
            
            
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
    




if __name__ == '__main__':
    pass


# =============================================================================
# while(True):
#     
#     img,gray,faces = detection()
#     for(x,y,w,h) in faces:
#         cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
#     cv2.imshow('video', img)
#     
#     k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
#     if k == 27:
#         break
#     elif k== 110:   # Press 'n'
#         getDataAndTrain()
#     elif k== 114:   # Press 'r'
#         faceRecognition()
#         
# # Do a bit of cleanup
# print("\n [INFO] Exiting Program and cleanup stuff")
# cam.release()
# cv2.destroyAllWindows()
#         
# =============================================================================

#fs = cv2.FileStorage( testFile, cv2.FileStorage_READ | cv2.FileStorage_FORMAT_YAML | cv2.FileStorage_WRITE)# | cv2.FileStorage_FORMAT_YAML | cv2.FileStorage_APPEND)
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        