#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 01:57:06 2019

@author: linjie
"""

import dboperation as dp
import numpy as np


dp.DbConnect()
dp.CreateTable()

fp = dp.FileOption()

array = np.arange(384).reshape(3,128)
ttuple = ('123456', array)

#fp.WriteEncodings(ttuple)

fp.DeleteEncoding('123456')

fp.LoadDataset()

dp.DbRelease()





for i in range(3):
    print(i)







# =============================================================================
# 
# import pickle
# from ruamel import yaml
# 
# 
# info = {'221': 'li','age':12}
# info2 = {'222': 'zl','age':15}
# infos = []
# infos.append(info)
# infos.append(info2)
# with open('test.pickle', "wb") as f:
#     pickle.dump(infos, f)
# 
# data = pickle.loads(open('test.pickle', "rb").read())
# 
# if '221' in data:
#     print(data[1]['name'])
# =============================================================================


# =============================================================================
# def WriteFaceInfo(faceId, name, info):        
#     faceInfo = { faceId : \
#                { 'name' : name, 'info' : info } }
#     with open('test.yaml') as f:
#         content = yaml.load(f, Loader=yaml.RoundTripLoader)
#         content.update(faceInfo)
#     with open('test.yaml', 'w') as f: 
#         yaml.dump(content, f, Dumper=yaml.RoundTripDumper)
#         
# 
# WriteFaceInfo('1', 'lili', 'info1')  
# WriteFaceInfo('2', 'kaiwen', 'info2')
#   
# with open('test.yaml' , 'r') as f: 
#     content = yaml.load(f, Loader=yaml.RoundTripLoader)
#     print(content)
# =============================================================================
    
    
    

# =============================================================================
# with open(encodingsPath, "wb") as f:
#                 f.write(pickle.dumps(dataset))
# =============================================================================
