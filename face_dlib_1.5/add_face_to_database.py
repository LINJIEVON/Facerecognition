#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 14 03:29:13 2019

@author: linjie
"""

import os,time
import dboperation as dp
import cv2
import face_recognition


trainFilePath = '/mnt/hgfs/share/lfw_funneled/'
cascadesPath = "Cascades/haarcascade_frontalface_alt2.xml"

faceCascade = cv2.CascadeClassifier( cascadesPath ) 
facenum = 0

def AddData(dirname):
    global facenum
    listfiles = os.listdir(dirname)
    if len(listfiles) == 0:
        print('null dir')
        return 0
    for file in listfiles:
        if facenum > 520:
            break
        
        fpath = os.path.join(dirname, file)
        
        if os.path.isdir(fpath):
            AddData(fpath)
        else:
            if os.path.splitext(file)[1] == '.jpg':
                image = cv2.imread(fpath)
                splits = file.split('_')
                name = splits[0] + ' ' + splits[1]
                retvalue = TrainFromFile(image,name)
                if retvalue:
                    facenum += 1
                    print(facenum)
                    break
                
    return 0

minW = 100
minH = 100

def Detection(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(int(minW), int(minH)))
    return rgb,faces  

def TrainFromFile(img,name):

    faceSamples=[]
    knownEncodings = []
    boxes = []
    box = None  
    
    rgb, faces = Detection(img)
    if len(faces) is 0:
        return False
    else: 
        for(x,y,w,h) in faces:
            box = (y, x + w, y + h, x)
        
    for i in range(3):
        faceSamples.append(rgb)
        boxes.append(box)

    for i,face in enumerate(faceSamples):
        # compute the facial embedding for the face
        encoding = face_recognition.face_encodings(face, [boxes[i]])
        knownEncodings.append(encoding[0])

    
    
    faceId = int(time.time()*100)
    identity = int(time.time()*100)
    info = 'test data' + str(facenum)
    faceinfo = dp.FaceInfo(faceId, name, identity, info)

    foption = dp.FileOption()
    foption.WriteFaceInfo(faceinfo)

    ttuple = (faceinfo.faceId, knownEncodings)
    foption.WriteEncodings(ttuple)
    
    return True



if __name__ == '__main__':
    dp.DbConnect()
    AddData(trainFilePath)
    dp.DbRelease()
    print('exit program')
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    