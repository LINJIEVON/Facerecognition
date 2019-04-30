#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 21:28:37 2019

@author: linjie
"""

class Error:
    
    def __init__(self):
        self.errors = {-101:'CONNECT_CURSOR_NONE',\
                -102:'IDENTITY_REPEAT',\
                -103:'OLD_PERMISSION_ERROR',\
                -104:'PERMISSION_ERROR',\
                -201:'NO_CAMERA_DEVICE_FOUND',\
                -202:'CAMERA_OPEN_FAILED',\
                -203:'NO_FACE_DETECH',\
                -204:'NO_FACE_MODEL'
                }
    
    def GetError(self, errorNum):
        return self.errors.get(int(errorNum), 'Bad errorNum')