#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 19:06:26 2019

@author: linjie
"""
import sqlite3
import hashlib
import numpy as np
import io
import pickle

defaultPermission = '202cb962ac59075b964b07152d234b70' #123 md5 twice ''

#databese
database = 'database/face.db'

connect = None
cursor = None

def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)

# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)


def DbConnect():
    global connect, cursor
    connect = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
    with connect:
        cursor = connect.cursor()
        print('Open database successfully')
        return 0
    print('Open database failed')
    return -1



def DbRelease():
    if connect is not None:
        cursor.close()
        connect.close()
        print('database closed')



def CreateTable():
    # Create table
    try:
        cursor.execute('create table faceencode (face_id text, face_data array)')
        connect.commit()
    except sqlite3.OperationalError:
            print('tabel faceencode has exist')
    try:
        cursor.execute('create table faceinfo (face_id text, face_name text, note text)')
        connect.commit()
    except sqlite3.OperationalError:
            print('tabel faceinfo has exist')
            
    



class FileOption:
    
    def __init__(self):
        self.conn = connect
        self.cur = cursor
        
    
    def LoadDataset(self):
        dataset = []
        rdatas = self.cur.execute('select * from dataset')
        if not rdatas:
            return None
        for item in rdatas:
           #print(type(item))
           dataset.append(item)
            
        return dataset 
        
    
    def WriteEncodings(self, datatuple):
        if self.cur is not None:
            self.cur.execute('insert into faceencode (face_id,face_data) values (?,?)',(datatuple[0], datatuple[1]))
            self.conn.commit()
        else:
            return
    
    
    def DeleteEncoding(self, faceIds):
        if self.cur is not None:
            for faceId in faceIds:  
                self.cur.execute('delete from faceencode where face_id=?', (faceId,))
                self.conn.commit()
        else:
            return 

            
            
    def GetFaceInfo(self, faceId):
        if self.cur is not None:
            rinfos = self.cur.execute('select * from faceInfo where face_id=?', (faceId,))
            for item in rinfos:
                name = item[1]
                info = item[2]
                faceInfo = FaceInfo(faceId, name, info)            
                return faceInfo
            return None
        else:
            return None

            
    def GetFaceListInfo(self, listinfo):
        if self.cur is not None:
            rinfos = self.cur.execute('select * from faceInfo')
            for item in rinfos:
                faceId = item[0]
                name = item[1]
                info = item[2]
                faceInfo = FaceInfo(faceId, name, info)
                listinfo.append(faceInfo)
        else:
            return None
        
    
    def WriteFaceInfo(self, faceInfo):
        if self.cur is not None:
            self.cur.execute('insert into faceinfo (face_id,face_name,note) values (?,?,?)'\
                             ,(faceInfo.faceId, faceInfo.face_name, faceInfo.info))
            self.conn.commit()
    
    
    def DeleteFaceInfos(self, faceIds):
        if self.cur is not None:
            for faceId in faceIds:  
                self.cur.execute('delete from faceinfo where face_id=?', (faceId,))
                self.conn.commit()
        else:
            return 
        
        
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
    
    
    def __del__(self):
        pass
    
   
    
class FaceInfo:
    
    def __init__(self, faceId, name, info):
        self.name = name
        self.info = info
        self.faceId = faceId
    
    def __del__(self):
        pass
    
    
    
    
    
    
    
    
    
    
    
    
    


if __name__ == "__main__": 
    pass

