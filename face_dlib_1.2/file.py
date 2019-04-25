#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 21:37:55 2019

@author: linjie
"""

import os, stat
import hashlib
import pickle

faceImagePath = 'dataset/'
faceInfoPath = 'faceinfo/faceinfo.pickle'
encodingsPath = 'encodings/encodings.pickle'
permissionPath = 'permission.pickle'
defaultPermission = '202cb962ac59075b964b07152d234b70' #123 md5 twice ''

class FileOption:
    
    def __init__(self):
        self.encodingsPath = encodingsPath
        self.faceInfoPath = faceInfoPath
        self.faceImagePath = faceImagePath
        self.permissionPath = permissionPath
    
    def BuildPaths(self):
        # Storage face info
        if False == os.path.isfile(self.faceInfoPath):
            os.mknod( self.faceInfoPath ,stat.S_IRWXU)
            with open(self.faceInfoPath, "wb") as f:
                f.write(pickle.dumps({}))
            
        #Storage trained faces
        if False == os.path.isfile(self.encodingsPath):
            os.mknod( self.encodingsPath ,stat.S_IRWXU)
            with open(self.encodingsPath, "wb") as f:
                f.write(pickle.dumps({}))
            
        #storage face images
        if False == os.path.isdir(self.faceImagePath):
            os.mkdir( self.faceImagePath ,stat.S_IRWXU)
            
         # Storage permission
        if False == os.path.isfile(self.permissionPath):
            os.mknod( self.permissionPath ,stat.S_IRWXU)
            self.WriteDefaultPermisssion()
            
    # Not used
    def GetTrainFiles(self, list_names):
        count = 0
        listfiles = os.listdir(self.trainFilePath)
        if len(listfiles) == 0:
            list_names = []
            return 0
        for file in listfiles:
            fpath = os.path.join(self.trainFilePath, file)
            if os.path.isdir(fpath):
                count += self.GetPathFiles(list_names)
            else:
                if os.path.splitext(file)[1] == '.yaml':  
                    list_names.append(self.trainFilePath + file)
                    count += 1
                    #print(self.trainFilePath + file)
                    #print(file)
        return count
    
    def GetFaceInfo(self, label):
        dicInfos = pickle.loads(open( self.faceInfoPath, "rb").read())
        if not dicInfos:
            return None
        faceId = str(label)
        if faceId in dicInfos:
            name = dicInfos[faceId]['name']
            info = dicInfos[faceId]['info']
            faceInfo = FaceInfo(faceId, name, info)
            return faceInfo
        else:
            return None
            
    def GetFaceListInfo(self, listinfo):
        dicInfos = pickle.loads(open( self.faceInfoPath, "rb").read())
        if not dicInfos:
            return None
        for key,value in dicInfos.items():
            faceId = key
            name = value['name']
            info = value['info']
            faceInfo = FaceInfo(faceId, name, info)
            listinfo.append(faceInfo)
    
    def WriteFaceInfo(self, faceInfo):
        dicInfos = pickle.loads(open( self.faceInfoPath, "rb").read())
        dicInfos[ str(faceInfo.faceId) ] = { 'name' : str(faceInfo.name), 'info' : str(faceInfo.info) } #Change if it exist,instead add
        #dicInfos.setdefault(key,value)     #if it exist,it does not change ,instead add
        with open(self.faceInfoPath, "wb") as f:
            f.write(pickle.dumps(dicInfos))
    
    
    def DeleteFaceInfos(self, labels):
        dicInfos = pickle.loads(open( self.faceInfoPath, "rb").read())
        for label in labels:
            faceId = str(label)
            if faceId in dicInfos:
                del dicInfos[faceId]
        with open(self.faceInfoPath, "wb") as f:
            f.write(pickle.dumps(dicInfos))
    
    
    def LoadDataset(self):
        dataset = pickle.loads(open( encodingsPath, "rb").read())
        if not dataset:
            return None
        return dataset
        
    
    def WriteEncodings(self, dataset):
        if dataset is not None:
            with open(encodingsPath, "wb") as f:
                f.write(pickle.dumps(dataset))
    
    
    def DeleteFaceImages(self, label):
        faceId = str(label)
        listfiles = os.listdir(self.faceImagePath)
        if len(listfiles) == 0:
            return None
        for file in listfiles:
            fpath = os.path.join(self.faceImagePath, file)
            if os.path.isdir(fpath):
                self.GetPathFiles(faceId)
            else:
                print(os.path.split(file)[1])
                if faceId in os.path.split(file)[1]:  
                    os.remove(file)
    
    
    
    def WriteDefaultPermisssion(self):
        content = { 'permission':defaultPermission }
        with open(self.permissionPath, "wb") as f:
            f.write(pickle.dumps(content))
            
            
            
    def WritePermission(self, old, new):
        
        prep = self.GetPermission()
        
        md5 = hashlib.md5()
        old = old.encode(encoding='utf-8')
        md5.update(old)
        md5_old = md5.hexdigest()
        if prep != md5_old:
            return -1
        
        md5 = hashlib.md5()
        new = new.encode(encoding='utf-8')
        md5.update(new)
        md5_new = md5.hexdigest()
        
        content = { 'permission': md5_new}
        with open(self.permissionPath, "wb") as f:
            f.write(pickle.dumps(content))
            
        return 0
    
        
    def GetPermission(self):
        content = pickle.loads(open( self.permissionPath, "rb").read())
        if not content:
            return None
        return content['permission']
    
    
    def VerifyPermission(self, permission):
        md5 = hashlib.md5()
        permission = permission.encode(encoding='utf-8')
        md5.update(permission)
        md5_per = md5.hexdigest()

        prep = self.GetPermission()
        if md5_per == prep:
            return 0
        else:
            return -1
        
        

        
class FaceInfo:
    
    def __init__(self, faceId, name, info):
        self.name = name
        self.info = info
        self.faceId = faceId
        

if __name__ == "__main__": 
    pass





























