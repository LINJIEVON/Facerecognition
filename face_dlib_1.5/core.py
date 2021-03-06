#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 19:54:04 2019

@author: linjie
"""
import os, time
import cv2
import random
import threading
from tkinter import messagebox
from dboperation import FileOption,FaceInfo
import gui
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

Unkown = 0.4

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
        
        self.threadNum = 4
        
        self.dataset = None
        self.knownsCount = 0
        
        self.recogResults = []
        
        self.capImages = None
        self.capSwitch = False
    
    def FaceInit(self):

        if self.camera is None:
            if os.path.exists(DevicePath0):
                self.camera = 0
            elif os.path.exists(DevicePath1):
                self.camera = 1
            else:
                self.CvPrint('No Camera found')
                return -201
                
        
        self.cam = cv2.VideoCapture( self.camera )

        if self.cam.isOpened() is False:
            self.CvPrint('Error: camera open failed!')
            return -202
            
        self.cam.set( CV_CAP_PROP_FRAME_WIDTH, self.frame_width)     # set Width 
        self.cam.set( CV_CAP_PROP_FRAME_HEIGHT, self.frame_height)   # set Height
        
        # Get all encoded face data
        self.dataset = FileOption().LoadDataset()
        if self.dataset is not None: 
            self.knownsCount = len(self.dataset)
        
        
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
    
    
    def DetectionFromImage(self, img):
    
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
        faces = self.faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100))
        return rgb,faces  
    
    
    def GetImageDirs(self, dirname, imagedirs):

        listfiles = os.listdir(dirname)
        if len(listfiles) == 0:
            self.CvPrint('null dir')
            return -205
        for file in listfiles:
            fpath = os.path.join(dirname, file)
            
            if os.path.isdir(fpath):
                self.GetImageDirs(fpath, imagedirs)
            else:
                if os.path.splitext(file)[1] == '.jpg':
                    imagedirs.append((fpath, file))
        return 0
    
    
    def TrainFromFile(self, dirname, progressbar):
        faillist = []
        faceInfos = []
        imagedirs = []
        box = None  
        retvalue = self.GetImageDirs(dirname, imagedirs)
        if retvalue < 0:
            return retvalue, [], []
        progressbar.SetProgressBarValue(0, len(imagedirs))

        for i,item in enumerate(imagedirs):
            imagepath = item[0]
            fname = item[1]
            infos = fname.split('_')
            #print(infos)
            if len(infos) == 3:
                img = cv2.imread(imagepath)
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                faces = self.faceCascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(100, 100))
                
                if len(faces) is 0:
                        progressbar.Update(i+1)
                        faillist.append(fname)
                        continue
                else: 
                    for(x,y,w,h) in faces:
                        box = (y, x + w, y + h, x)
                        
                faceSamples=[]
                knownEncodings = []
                boxes = []
                for j in range(samplingtimes):
                    faceSamples.append(rgb)
                    boxes.append(box)
                    
                for k,face in enumerate(faceSamples):
                    # compute the facial embedding for the face
                    encoding = face_recognition.face_encodings(face, [boxes[k]])
                    knownEncodings.append(encoding[0])
                
                while True:
                    faceId = random.getrandbits(31)
                    retvalue = self.IsIdExist(str(faceId))
                    if retvalue < 0:
                        break
                
                name = infos[0].replace('-',' ')
                identity = infos[1]
                note = infos[2].split('.')[0].replace('-',' ')
                faceInfo = FaceInfo(faceId, name, identity, note)
                retvalue = self.AddNewFace(faceInfo, knownEncodings)
                if retvalue < 0:
                    faillist.append(fname)
                else:
                    faceInfos.append(faceInfo)
                
            else:
                faillist.append(fname)
            progressbar.Update(i+1)
        progressbar.Release()
        return 0, faceInfos, faillist
        
        
        
    
    
    def TrainFromCamera(self, faceInfo):
        if self.cam.isOpened is False:
            self.CvPrint('Error: camera is not open')
            #self.Message(2, 'Error', 'camera is not open')
            return -202 
        
        count = 0
        faceSamples=[]
        knownEncodings = []
        boxes = []
        
        string = "\n [INFO] Initializing face capture."
        #self.Message(0, 'info', string)
        self.CvPrint(string)
        
        while True:
            faceId = random.getrandbits(31)
            retvalue = self.IsIdExist(str(faceId))
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
                break
                 
            if count >= samplingtimes:
                break
        
        if len(faceSamples) is 0:
            string = "\n [INFO] No faces deteched, Training faces failed!"
            #self.Message(0, 'info', string)
            self.CvPrint(string)
            return -203
        
        for i,face in enumerate(faceSamples):
            # compute the facial embedding for the face
            encoding = face_recognition.face_encodings(face, [boxes[i]])
            knownEncodings.append(encoding[0])

        
        faceInfo.faceId = faceId
        retvalue = self.AddNewFace(faceInfo, knownEncodings)
        if retvalue < 0:
            return retvalue
        
        # Print the numer of faces trained and end program
        string = "\n [INFO] 1 faces trained."
        #self.Message(0, 'info', string)
        self.CvPrint(string)
        
        return 0
        

    def FaceRecognition(self, result):
        if self.cam.isOpened is False:
            self.CvPrint('Error: camera is not open')
            #self.Message(2, 'Error', 'camera is not open')
            return -202 
        
        self.recogResults.clear()   #empty the result list
        
        #print(self.tempRecognizerCount)
        if 0 >= self.knownsCount:
            self.errorMessage = 'No face model exist'
            self.CvPrint('Error: No face model exist')
            return -204
        
        self.capSwitch = True
        self.capImages = DetImages(1)
        
        while self.capSwitch:
            time.sleep(0.1)
            
        encoding = None
        rgb, faces = self.capImages.Get()
        
        for(x,y,w,h) in faces:
            box = (y, x + w, y + h, x)
            encoding = face_recognition.face_encodings(rgb, [box])
            
        threads = []
        
        if self.knownsCount < 4*2:
            self.threadNum = 1
            taskNum = self.knownsCount
        else:
            taskNum = int(self.knownsCount / 4)
            
        for i in range(self.threadNum):
            start = i*taskNum
            end = (i+1)*taskNum
            if (i + 1) == self.threadNum and end < self.knownsCount:
                end = self.knownsCount
            thread = MyThread(self.Recognition, encoding[0], start, end)
            thread.start()
            threads.append(thread)
        
        for th in threads:
            th.join()
            
        if len(self.recogResults) > 0:
            self.recogResults.sort(key = lambda k: k[0]) #sort by value
            final = self.recogResults[0]
        
            label = final[1]
            distance = final[0]
            faceInfo = FileOption().GetFaceInfo(label)
        else:
            distance = 1.0
            faceInfo = FileOption().UnkownFaceInfo()
            
        string2 = faceInfo.eToString() + '\nDistance: ' + str(distance)
        self.CvPrint(string2)
        result.update({'faceinfo' : faceInfo, 'distance' : str(distance)}) 
        
        return 0
        
        #cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        #cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)
         
        
        
    def Recognition(self, encoding, start, end):
        for i in range(start, end):
            distances = face_recognition.face_distance(self.dataset[i][1], encoding)
            distance = (distances[0] + distances[1] + distances[2]) / samplingtimes
            #print(self.dataset[i][0] + ' ' + str(distance))
            if distance < Unkown:
                result = (distance, self.dataset[i][0])
                self.recogResults.append(result)
            #print(threading.currentThread().ident)
       
        
    def Message(self, priority, title, content):
        if 2 == priority:
            messagebox.showerror(title = title, message = content, parent = self.parentWidget)
        else:
            messagebox.showinfo(title = title, message = content, parent = self.parentWidget)
    
        
    def CvPrint(self, content):
        gui.WriteConsole(content)
        print(content)
        
    
    def AddNewFace(self, faceInfo, encodings):
        #Write to faceinfo file
        foption = FileOption()
        retvalue = foption.WriteFaceInfo(faceInfo)
        if retvalue < 0:
            return retvalue
        #print(faceInfo.info)
        
        #write to encodings file
        ttuple = (faceInfo.faceId, encodings)
        foption.WriteEncodings(ttuple)
        
        #Add new face to menory
        datatuple = (faceInfo.faceId, encodings)
        self.dataset.append(datatuple)
        
        #Synchronization variable value
        self.knownsCount += 1
        
        return 0
    
    def IsIdExist(self, label): # label type is str
        if self.dataset is not None:
            for i,item in enumerate(self.dataset):
                #print(str(label) + ' ' + str(item))
                if str(label) == str(item[0]):
                    return i
        return -1
    
    
    def DeleteFaces(self, labels):
        foption = FileOption()
        foption.DeleteFaceInfos(labels)
        foption.DeleteEncoding(labels)
        for label in labels:
            index = self.IsIdExist(label)
            if index >= 0:
                del self.dataset[index]
                    
                self.knownsCount -= 1
                
        self.CvPrint('Deleted ' +str( len(labels) )+ ' faces success!')
                   
    
   
        
    def __del__(self):
        print('destroy object CvCore')
        if None != self.cam:
            if self.cam.isOpened():
                self.cam.release()
        


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
        elif 3 == argNum:
            self.func(self.args[0], self.args[1], self.args[2])
            
                       
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


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        