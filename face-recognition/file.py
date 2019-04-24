#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 21:37:55 2019

@author: linjie
"""

import os, stat
import hashlib
from ruamel import yaml 

faceInfoPath = 'faceinfo.yaml'
trainFilePath = 'trainer/'
faceImagePath = 'dataset/'
permissionPath = 'permission.yaml'
defaultPermission = '202cb962ac59075b964b07152d234b70' #123 md5 twice ''

class FileOption:
    
    def __init__(self):
        self.trainFilePath = trainFilePath
        self.faceInfoPath = faceInfoPath
        self.faceImagePath = faceImagePath
        self.permissionPath = permissionPath
        
        # Storage face info
        if False == os.path.isfile(self.faceInfoPath):
            os.mknod( self.faceInfoPath ,stat.S_IRWXU)
        #Storage trained faces
        if False == os.path.isdir(self.trainFilePath):
            os.mknod( self.trainFilePath ,stat.S_IRWXU)
        #storage face images
        if False == os.path.isdir(self.faceImagePath):
            os.mknod( self.faceImagePath ,stat.S_IRWXU)
            
         # Storage permission
        if False == os.path.isfile(self.permissionPath):
            os.mknod( self.permissionPath ,stat.S_IRWXU)
            self.WriteDefaultPermisssion()
            
    
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
        with open( self.faceInfoPath , 'r') as f: 
            content = yaml.load(f, Loader=yaml.RoundTripLoader)
            if None == content:
                return None
            faceId = str(label)
            if faceId in content:
                name = content[faceId]['name']
                info = content[faceId]['info']
                faceInfo = FaceInfo(faceId, name, info)
                return faceInfo
            else:
                return None
            
    def GetFaceListInfo(self, listinfo):
        with open( self.faceInfoPath , 'r') as f: 
            content = yaml.load(f, Loader=yaml.RoundTripLoader)
            if None == content:
                return None
            for key,value in content.items():
                faceId = key
                name = value['name']
                info = value['info']
                faceInfo = FaceInfo(faceId, name, info)
                listinfo.append(faceInfo)
    
    
    def WriteFaceInfo(self, faceInfo):        
        faceInfo = { str(faceInfo.faceId) : \
                   { 'name' : str(faceInfo.name), 'info' : str(faceInfo.info) } }
        with open( self.faceInfoPath) as f:
            content = yaml.load(f, Loader=yaml.RoundTripLoader)
            content.update(faceInfo)
        with open( self.faceInfoPath, 'w') as f: 
            yaml.dump(content, f, Dumper=yaml.RoundTripDumper)
    
    
    def DeleteFaceInfos(self, labels):
        with open( self.faceInfoPath) as f:
            content = yaml.load(f, Loader=yaml.RoundTripLoader)
            for label in labels:
                faceId = str(label)
                if faceId in content:
                    del content[faceId]
                else:
                    return
        with open(self.faceInfoPath, 'w') as nf:
            yaml.dump(content, nf, Dumper=yaml.RoundTripDumper)
    
    
    def DeleteTrainFiles(self, labels):
        for label in labels:
            file = self.trainFilePath + str(label) + '.yaml'
            if os.path.isfile(file):
                os.remove(file)
    
    
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
        with open( self.permissionPath, 'w') as f:
            content = { 'permission':defaultPermission }
            yaml.dump(content, f, Dumper=yaml.RoundTripDumper)
            
            
            
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
        with open( self.permissionPath, 'w') as f:
            content = { 'permission': md5_new}
            yaml.dump(content, f, Dumper=yaml.RoundTripDumper)
            
        return 0
        
    def GetPermission(self):
        with open( self.permissionPath , 'r') as f: 
            content = yaml.load(f, Loader=yaml.RoundTripLoader)
            if None == content:
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





























