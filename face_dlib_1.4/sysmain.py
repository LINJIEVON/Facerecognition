#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 20:09:27 2019

@author: linjie
"""

from gui import MainWin
import dboperation as dp

#connect to database
dp.DbConnect()

#if no tables exist create it, instead do nothing
dp.CreateTable()

win = MainWin()
win.GuiShow()
del win

#disconnect
dp.DbRelease()

print('exit program')
