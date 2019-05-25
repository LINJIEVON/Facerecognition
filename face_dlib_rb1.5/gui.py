#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 19:05:58 2019

@author: linjie
"""
#import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
from core import FaceCore, MyThread
from dboperation import FileOption, FaceInfo
from error import Error


threadCount = 0
console = None


class MainWin:
    def __init__(self):
        self.menuTextState = False
        self.facecore = FaceCore()
        self.image = None
        self.isRuningRecognize = False
        
    def GuiShow(self):
        self.message = ''
        win = tk.Tk()
        win.title('Face-Recognition')
        win.geometry('640x650')
        win.minsize(640,650)
        #win.maxsize(640,650)
        win.protocol('WM_DELETE_WINDOW',    lambda:self.CallBack(win))
    
        frametop = tk.Frame( win, padx = 1, pady = 2, bg = 'snow')
        frametop.pack(fill = tk.X)
                
        tk.Frame(height = 1, bg = 'gray').pack(fill = tk.X)
        
        framemid = tk.Frame( win)
        framemid.pack(fill = tk.X)
        
        tk.Frame(height = 1, bg = 'gray').pack(fill = tk.X)
        
        framebottom = tk.Frame( win)
        framebottom.pack(fill = tk.X)
     
        self.btmenu = tk.Button( frametop, text = 'menu', command = lambda:self.MenuShow(win), bg = 'steelblue')
        self.btmenu.pack(side = tk.LEFT)
        
# =============================================================================
#         btrecg = tk.Button( frametop, text = 'recognition', bg = 'steelblue'\
#                                 , command = lambda:self.FaceRecognition(win) )
#         btrecg.pack(side = tk.RIGHT)
# =============================================================================
        btrecg = tk.Button( frametop, text = 'recognition', bg = 'steelblue'\
                        , command = lambda:MyThread(self.FaceRecognition, win).start())
        btrecg.pack(side = tk.RIGHT)
        
        # Video control
        self.videocanvas  = tk.Canvas( framemid, height = 480, bg = 'white')
        self.videocanvas.pack(fill = tk.X)
    
        self.outtext = tk.Text( framebottom)
        self.outtext.insert( tk.END, 'Ready...\n')
        self.outtext.config(state = tk.DISABLED)
        self.outtext.propagate(False)
        self.outtext.pack(expand = True, fill = tk.BOTH)
        global console
        console = self.outtext
        
        scroll = ttk.Scrollbar(self.outtext, cursor = 'arrow')
        scroll.pack(side = tk.RIGHT, fill = tk.Y)
        #'self.scrol['command'] = self.outtext.yview'  is same as next
        scroll.config(command = self.outtext.yview)
        self.outtext.config(yscrollcommand = scroll.set)
        
        #clear text
        self.menuText = tk.Menu( self.outtext, tearoff = False)
        self.menuText.add_command( label = '    Clear console             Ctrl+L'\
                                  , command = self.ConsoleClear)
        self.menuText.add_separator()                           #cut-off rule(fen ge xian)
        self.outtext.bind( '<Button-3>', self.TextMenuShow)
        self.outtext.bind( '<Button-1>', self.TextMenuClose)
        
        win.bind('<Key>', self.handlerAdaptor( self.ConsoleShow, win = win))
        
        retvalue = self.facecore.FaceInit()
        if retvalue < 0:
             messagebox.showerror(title = Error().GetError(retvalue), message = 'Initialize camera failed!', parent = win)
             win.destroy()
             return -1
        self.ShowFrame()
        win.mainloop()     
        
    def CallBack(self, win):
        if 0 == threadCount:
            win.destroy()
        
        
    def ConsoleShow(self, event, win):
        key = event.keysym
        self.message = 'press key' + ' ' + key + '\n' 
        
        self.outtext.config(state = tk.NORMAL)
        self.outtext.insert( tk.END, self.message)
        self.outtext.see(tk.END)
        self.outtext.config(state = tk.DISABLED)
        
        if 'r' == key:
            MyThread(self.FaceRecognition, win).start()
        if 'm' == key:
            self.MenuShow(win)
        if 'Escape' == key: #Esc
            self.CallBack(win)
        
    def ConsoleClear(self, event = None): #if no 'None',will get one error,when running
        self.outtext.config(state = tk.NORMAL)
        self.outtext.delete( 0.0, tk.END)
        self.outtext.config(state = tk.DISABLED)
        self.menuTextState = False
    
    def TextMenuShow(self, event):
        if self.menuTextState:
            self.menuText.unpost()
            self.menuTextState = False
        else:
            self.menuText.post( event.x_root, event.y_root)
            self.menuTextState = True
        
    def TextMenuClose(self, event):
        if self.menuTextState:
            self.menuText.unpost()
            self.menuTextState = False
            
    def MenuShow(self, parent, event = None): 
        #parent.wm_attributes('-type', 'splash')
        Verify(self.facecore, parent).Verify()

  
        
    def handlerAdaptor(self, fun, **kwds):
        return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)
        
    def ShowFrame(self):
        img, faces = self.facecore.Detection()
        self.facecore.DrawRectangle(img, faces)
        img = Image.fromarray( img ) #.resize((100, 100))
        
        #1.This should be a PhotoImage or BitmapImage, or a compatible object (such as the PIL PhotoImage). 
        #2.The application must keep a reference to the image object. (very important)
        self.image = ImageTk.PhotoImage(image = img)
        self.videocanvas.create_image(0, 0, image = self.image, anchor = tk.NW)
        self.videocanvas.after(10, self.ShowFrame)
        
        
    def FaceRecognition(self, win):
        if self.isRuningRecognize:
            return
        self.isRuningRecognize = True
        global threadCount
        threadCount += 1
        dicResult = {} 
        self.facecore.FaceRecognition(dicResult)
        string  = 'Name: ' + dicResult['faceinfo'].name + '\n\nIdentity: ' + dicResult['faceinfo'].identity
        #messagebox.showinfo(title = 'Recognize result', message = string, parent = win)
        Popup('Recognize result', string, 1500,  win)
        threadCount -= 1
        self.isRuningRecognize = False
        
    def __del__(self):
        print('destroy object MainWin')


def WriteConsole(content):
    if console is None:
        return
    console.config(state = tk.NORMAL)
    console.insert( tk.END, content + '\n')
    console.see(tk.END)
    console.config(state = tk.DISABLED)


class Verify:
    
    def __init__(self, facecore, wparent):
        self.facecore = facecore
        self.wparent = wparent
        self.menugui = MenuGui(wparent, facecore)
        
        
    
    def Verify(self):
        self.root = tk.Toplevel() 
        self.root.title('Enter permission')
        self.root.wm_attributes('-topmost', 1)
        self.root.config(bg = 'whitesmoke')
        
        width = 270
        height = 70
        
        #get parent window posiotion
        px = self.wparent.winfo_x()  
        py = self.wparent.winfo_y()
        
        #get parent window width/height
        pwidth = self.wparent.winfo_width()
        pheight = self.wparent.winfo_height()
        
        #offset
        
        dx = (pwidth - width) / 2
        dy = (pheight - height) / 2
        
        self.root.geometry("%dx%d+%d+%d" % (width, height, px + dx, py + dy))

  
        self.inputstr = tk.StringVar(self.root) 
        entry = tk.Entry(self.root, textvariable = self.inputstr, show = '*', highlightcolor = 'deepskyblue')  
        entry.pack(fill = tk.X, padx = 5, pady = 5)
        entry.focus_set()
        entry.bind('<Return>', self.PermissionVerify)
        btn1 = tk.Button(self.root, text='Ok', command = self.PermissionVerify)     
        btn2 = tk.Button(self.root, text='Cancel', command = self.MenuCancel)   
    
        btn2.pack(side='right',pady = 2)
        btn1.pack(side='right', padx = 5, pady = 2)
    
        #self.root.mainloop()

    def PermissionVerify(self, event = None):
        permission = self.inputstr.get()
        if 0 == len(permission):
            self.MenuCancel()
            self.facecore.CvPrint('Permission error!')
            #messagebox.showerror(title = 'Error', message = 'Permission error!')
            Popup('Error', 'Permission is null!', 1000, self.wparent)
        else:
            retvalue = FileOption().VerifyPermission(permission)
            if retvalue >= 0:
                self.MenuCancel()
                self.menugui.GuiShow()
            else:
                self.MenuCancel()
                WriteConsole('Permission verify failure')
                #messagebox.showerror(title = Error().GetError(retvalue), message = 'Permission error!')
                Popup(Error().GetError(retvalue), 'Permission error!', 1000, self.wparent)
                
        
    def MenuCancel(self):
        self.root.destroy()
        
        
    def __del__(self):
        print('destroy object Verify')
    





class MenuGui:
    
    def __init__(self, wparent, facecore):
        self.topWin = None
        self.wparent = wparent
        self.facecore = facecore
        self.isTraning = False
        
    def GuiShow(self):
        
        self.topWin = tk.Toplevel()
        self.topWin.title('Menu')
        width = 640
        height = 500
        
        dx = self.wparent.winfo_x()
        dy = self.wparent.winfo_y()
        self.topWin.geometry("%dx%d+%d+%d" % (width, height, dx, dy))
        self.topWin.minsize(width, height)
        self.topWin.maxsize(width, height)
        #self.topWin.wm_attributes('-type', 'splash')
        
        self.topWin.protocol('WM_DELETE_WINDOW',    lambda:self.CallBack(self.topWin))
        
        frame = tk.Frame(self.topWin)
        frame.pack(fill = tk.BOTH, expand = True)
        
        #-------------------------- topWin ----------------------------
        
        frame_left1 = tk.Frame(frame, highlightthickness = 1, highlightbackground = 'gray'\
                               , bg = 'white', width = 150)
        frame_left1.pack(side = tk.LEFT,fill = tk.BOTH, padx = 5, pady = 5)
        frame_left1.propagate(False) #Setting to True means that the geometry of the parent component is determined by the child component (the default) and vice versa
        
        frame_left2 = tk.Frame(frame, highlightthickness = 1, highlightbackground = 'gray'\
                               , highlightcolor = 'gray', bg = 'white', )
        frame_left2.pack(side = tk.LEFT, fill = tk.BOTH, expand = True, pady = 5)
        
        #-------------------------- frame_left1 ( function menu )----------------------------
        
        self.labels = []
        options = [' Management', ' New face', ' Change permission']
        for item in options:
            label_left = tk.Label(frame_left1, text = item, bg = 'white', anchor = tk.W)
            label_left.pack(fill = tk.X)
            label_left.bind('<Button-1>',self.handlerAdaptor(self.lbChangeBackGround, index = options.index(item)))
            self.labels.append(label_left)
        self.labels[0].config(bg = 'deepskyblue')
          
        #-------------------------- frame_left2 ----------------------------
        
        self.listFrames = []
        
        frame_left2_1 = tk.Frame(frame_left2, bg = 'white', padx = 5, pady = 5)
        frame_left2_1.propagate(False)
        frame_left2_1.pack(fill = tk.BOTH, expand = True)
        self.listFrames.append(frame_left2_1)
        
        frame_left2_2 = tk.Frame(frame_left2, bg = 'white', padx = 5, pady = 5)
        frame_left2_2.propagate(False)
        self.listFrames.append(frame_left2_2)
        
        frame_left2_3 = tk.Frame(frame_left2, bg = 'white', padx = 5, pady = 5)
        frame_left2_3.propagate(False)
        self.listFrames.append(frame_left2_3)

        #-------------------------- frame_left2_1 ( face list )----------------------------
        frame_left2_1_1 = tk.Frame(frame_left2_1)
        frame_left2_1_1.pack(fill = tk.BOTH, expand = True)
        s = ttk.Style()
        s.configure('Treeview', rowheight = 25)
        
        self.table = ttk.Treeview(frame_left2_1_1, show = 'headings', selectmode='extended')
        self.table.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        self.table.config(columns = ('label','name','identity','note'))
        self.table.heading('label', text = 'label')
        self.table.column('label', width = '20')
        self.table.heading('name', text = 'name')
        self.table.column('name', width = '10')
        self.table.heading('identity', text = 'identity')
        self.table.column('identity', width = '20')
        self.table.heading('note', text = 'note')
        self.table.column('note', width = '30') 
        #self.table['show'] = 'headings'
        #self.table.column("#0", width = 0)

        scrollbar = ttk.Scrollbar(frame_left2_1_1)
        scrollbar.pack(side = tk.LEFT, fill = tk.Y)
        scrollbar.config(command = self.table.yview)
        self.table.config(yscrollcommand = scrollbar.set)
        
        
        serch_frame = tk.Frame(frame_left2_1, bg = 'white')
        serch_frame.pack(fill = tk.X)
        serch_frame.config(pady = 5)
        serchlabel = tk.Label(serch_frame, text = 'Serch: ', anchor = tk.E, bg = 'white')
        serchlabel.pack(side = tk.LEFT)
        vcmd = self.topWin.register(self.SerchByIdentity)
        serchentry = tk.Entry(serch_frame, validate="key", validatecommand = (vcmd, '%P'), highlightcolor = 'deepskyblue')
        serchentry.pack(side = tk.RIGHT, fill = tk.X, expand = True)
        
        
        
        button_frame = tk.Frame(frame_left2_1, height = 40, bg = 'white', pady = 2\
                                , highlightthickness = 1, highlightbackground = 'gray')
        #button_frame.propagate(False)
        button_frame.pack(fill = tk.X)
        
        button_f1 = tk.Button(button_frame, text = 'Cancel', command = self.UnSelectTable)
        button_f1.pack(side = tk.RIGHT, padx = 2)
        button_f2 = tk.Button(button_frame, text = 'Delete', command = self.DeleteTableItems)
        button_f2.pack(side = tk.RIGHT, padx = 2)
        button_f3 = tk.Button(button_frame, text = 'Delete all', command = lambda: self.DeleteTableItems(True))
        button_f3.pack(side = tk.RIGHT, padx = 2)      
    
        #fill the table
        self.RefreshTable()

        #-------------------------- frame_left2_2 ( new face )----------------------------
        
        fram_2_2_base1 = tk.Frame(frame_left2_2, bg = 'white'\
                                   ,highlightthickness = 1, highlightbackground = 'gray', highlightcolor = 'gray')
        fram_2_2_base1.propagate(False)
        fram_2_2_base1.pack(fill = tk.BOTH, expand = True)
        frame_2_2_base = tk.Frame(fram_2_2_base1, bg = 'white', width = 350, height = 400, pady = 20\
                                  ,padx = 50)
        frame_2_2_base.propagate(False)
        frame_2_2_base.pack()
        
        frame_2_2_1 = tk.Frame(frame_2_2_base, bg = 'white')
        #frame_2_2_1.propagate(False)
        frame_2_2_1.pack(fill = tk.X, pady = 10)
        self.inputText1 = tk.Entry(frame_2_2_1, width = 20, highlightcolor = 'deepskyblue')
        self.inputText1.pack(side = tk.RIGHT)
        labelText1 = tk.Label(frame_2_2_1, bg = 'white', text ='Name: ', anchor = tk.E)
        labelText1.pack(side = tk.RIGHT)
        
        frame_2_2_1 = tk.Frame(frame_2_2_base, bg = 'white')
        #frame_2_2_1.propagate(False)
        frame_2_2_1.pack(fill = tk.X, pady = 10)
        self.inputText2 = tk.Entry(frame_2_2_1, width = 20, highlightcolor = 'deepskyblue')
        self.inputText2.pack(side = tk.RIGHT)
        labelText2 = tk.Label(frame_2_2_1, bg = 'white', text ='Identity: ', anchor = tk.E)
        labelText2.pack(side = tk.RIGHT)
        
        frame_2_2_2 = tk.Frame(frame_2_2_base, bg = 'white')
        #frame_2_2_2.propagate(False)
        frame_2_2_2.pack(fill = tk.X, pady = 10)
        self.inputText3 = tk.Text(frame_2_2_2, width = 23, height = 5, wrap = tk.WORD, highlightcolor = 'deepskyblue')
        self.inputText3.pack(side = tk.RIGHT)
        labelText3 = tk.Label(frame_2_2_2, bg = 'white', text ='Note: ', anchor = tk.NE)
        labelText3.pack(side = tk.RIGHT, fill = tk.Y)
        
        frame_2_2_base2 = tk.Frame(frame_left2_2, bg = 'white', pady = 2\
                                   ,highlightthickness = 1, highlightbackground = 'gray')
        #frame_2_2_4.propagate(False)
        frame_2_2_base2.pack(side = tk.BOTTOM, fill = tk.X, pady = 5)
        button_f21 = tk.Button(frame_2_2_base2, text = 'Clear', command = self.ClearFaceInput)
        button_f21.pack(side = tk.RIGHT, padx = 2)
# =============================================================================
# 
#         button_f22 = tk.Button(frame_2_2_base2, text = 'Train', width = 5, command = lambda:MyThread(self.CreateNewFaceTest).start() )
# =============================================================================
        button_f22 = tk.Button(frame_2_2_base2, text = 'Train', width = 5, command = lambda:MyThread(self.CreateNewFace).start() )
        button_f22.pack(side = tk.RIGHT, padx = 2)
# =============================================================================
#         button_f22 = tk.Button(frame_2_2_base2, text = 'Train', width = 5, command = self.CreateNewFace)
#         button_f22.pack(side = tk.RIGHT, padx = 2)
# =============================================================================
        button_f23 = tk.Button(frame_2_2_base2, text = 'Trainfromfile', width = 10, command = self.CreatNewFaceFromFile )
        button_f23.pack(side = tk.LEFT, padx = 2)
        
        
        
              
        
        #-------------------------- frame_left2_3 (change permission)----------------------------
        
        frame_2_3_base1 = tk.Frame(frame_left2_3, bg = 'white'\
                                   ,highlightthickness = 1, highlightbackground = 'gray', highlightcolor = 'gray')
        frame_2_3_base1.propagate(False)
        frame_2_3_base1.pack(fill = tk.BOTH, expand = True)
        frame_2_3_base = tk.Frame(frame_2_3_base1, bg = 'white', width = 300, height = 400, pady = 20)
        frame_2_3_base.propagate(False)
        frame_2_3_base.pack()
        
        frame_2_3_1 = tk.Frame(frame_2_3_base, bg = 'white')
        #frame_2_3_1.propagate(False)
        frame_2_3_1.pack(fill = tk.X, pady = 10)
        self.inputTextOld = tk.Entry(frame_2_3_1, show = '*', highlightcolor = 'deepskyblue')
        self.inputTextOld.pack(side = tk.RIGHT)
        labelText1 = tk.Label(frame_2_3_1, bg = 'white', text ='old permission: ', anchor = tk.E)
        labelText1.pack(side = tk.RIGHT)
        
        frame_2_3_2 = tk.Frame(frame_2_3_base, bg = 'white')
        #frame_2_3_2.propagate(False)
        frame_2_3_2.pack(fill = tk.X, pady = 10)
        self.inputTextNew = tk.Entry(frame_2_3_2, show = '*', highlightcolor = 'deepskyblue')
        self.inputTextNew.pack(side = tk.RIGHT)
        labelText1 = tk.Label(frame_2_3_2, bg = 'white', text ='new permission: ', anchor = tk.E)
        labelText1.pack(side = tk.RIGHT)

        
        frame_2_3_3 = tk.Frame(frame_2_3_base, bg = 'white')
        #frame_2_3_3.propagate(False)
        frame_2_3_3.pack(fill = tk.X, pady = 10)
        self.inputTextRepeat = tk.Entry(frame_2_3_3, show = '*', highlightcolor = 'deepskyblue')
        self.inputTextRepeat.pack(side = tk.RIGHT)
        labelText1 = tk.Label(frame_2_3_3, bg = 'white', text ='repeat: ', anchor = tk.E)
        labelText1.pack(side = tk.RIGHT)

        
        frame_2_3_base2 = tk.Frame(frame_left2_3, bg = 'white', pady = 2\
                                   ,highlightthickness = 1, highlightbackground = 'gray')
        #frame_2_2_4.propagate(False)
        frame_2_3_base2.pack(side = tk.BOTTOM, fill = tk.X, pady = 5)
        button_f21 = tk.Button(frame_2_3_base2, text = 'Cancel', command = self.CancelResetPermission)
        button_f21.pack(side = tk.RIGHT, padx = 2)
        button_f22 = tk.Button(frame_2_3_base2, text = 'Change', width = 5, command = self.ChangePermission)
        button_f22.pack(side = tk.RIGHT, padx = 2)
        
           
    def CallBack(self, win):
        if threadCount is 0:
            win.destroy()
        
    def handlerAdaptor(self, fun, **kwds):
        return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)
    
    def lbChangeBackGround(self, event, index):
        for i,item in enumerate(self.labels):
            if index == i:
                item.config(bg = 'deepskyblue')
                self.listFrames[i].pack(fill = tk.BOTH, expand = True)
                if i == 1:
                    self.inputText1.focus_set()
                elif i == 2:
                    self.inputTextOld.focus_set()
            else:
                item.config(bg = 'white')
                self.listFrames[i].pack_forget()
    
    
    def CreateNewFace(self, event = None):
        if self.isTraning:
            return
        self.isTraning = True
        global threadCount
        threadCount += 1
        
        name = self.inputText1.get()
        if 0 == len(name):
            name = 'unspecified'
        
        identity = self.inputText2.get()
        if 0 == len(identity):
            identity = 'unspecified'
        
        note = self.inputText3.get(0.0, tk.END)
        if 0 == len(note):
            note = 'unspecified'
        note = note.replace('\n', ' ')

        faceInfo  = FaceInfo('unspecified', name, identity, note)
        messagebox.showinfo(title = 'INFO', message = 'Look the camera and wait ...', parent = self.topWin)
        retvalue = self.facecore.TrainFromCamera(faceInfo)
        faceInfo = [faceInfo]
        if retvalue >= 0:
            Popup('Info', '1 faces trained', 1500, self.topWin)
            #messagebox.showinfo(title = 'INFO', message = '1 faces trained.', parent = self.topWin)
            self.RefreshTable(faceInfo)
        else:
             Popup(Error().GetError(retvalue), 'Add new face failure!', 1500, self.topWin)
            #messagebox.showerror(title = Error().GetError(retvalue), message = 'Add new face failure!'\
              #                  , parent = self.topWin)
        threadCount -= 1
        self.isTraning = False
        
        
    def CreatNewFaceFromFile(self):
        dirname = filedialog.askdirectory(initialdir = "/home/pi/Desktop",title = "Select one filedir",parent = self.topWin)
        #dirname = filedialog.askopenfilename()
        if len(dirname) <= 2:
            return
        print(dirname)

        progressbar = Progressbar(self.topWin)
        retvalue, faceInfos, faillist= self.facecore.TrainFromFile(dirname, progressbar)
        if retvalue < 0:
            progressbar.Release()
            Popup(Error().GetError(retvalue), 'Not find image!', 1500, self.topWin)
        else:
            add = len(faceInfos)
            fail = len(faillist)
            self.RefreshTable(faceInfos)
            for info in faillist:
                WriteConsole(info)
            info = str(add) + ' faces added successfully,' + str(fail) + ' faces added  failed,view console'
            messagebox.showinfo(title = 'Info', message = info, parent = self.topWin)
        
        

    
    def CreateNewFaceTest(self, event = None):
        count = 2019001
        for i in range(500):
            count += i
            print(count)
            faceInfo  = FaceInfo('unspecified', 'linjie', str(count), 'test')
            self.facecore.TrainFromCamera(faceInfo)
            self.RefreshTable(faceInfo)
        
        
    def ClearFaceInput(self):
        self.inputText1.delete(0, tk.END)
        self.inputText2.delete(0, tk.END)
        self.inputText3.delete(0.0, tk.END)
    
    
    def RefreshTable(self, faceInfos = None):
        
        if None != faceInfos:
            for faceInfo in faceInfos:
                self.table.insert('',tk.END, values = (faceInfo.faceId, faceInfo.name, faceInfo.identity, faceInfo.info))
        else:
            faceInfos = []
            self.fileObject = FileOption()
            self.fileObject.GetFaceAllInfo(faceInfos)
            for item in faceInfos:
                self.table.insert('',tk.END, values = (item.faceId, item.name, item.identity, item.info))
                
        
    def DeleteTableItems(self, deleteAll = False):
        faceIds = []
        obids = []
        if deleteAll is False:
            for item in self.table.selection():
                values = self.table.item(item, 'values')
                faceIds.append(values[0])
                obids.append(item)
                #self.table.delete(item)
                #print(values[0])
        else:
            items = self.table.get_children()
            for item in items:
                values = self.table.item(item, 'values')
                faceIds.append(values[0])
                obids.append(item)
                #self.table.delete(item)
                #print(values[0])
        if len(faceIds) == 0:
            return
        retvalue = messagebox.askokcancel(title = 'Info', message = 'Whether to delete the selected '\
                                          +str( len(faceIds) )+' faces', parent = self.topWin)
        if retvalue:
            for item in obids:
                self.table.delete(item)
            self.facecore.DeleteFaces(faceIds)
            Popup('Info', str( len(faceIds) ) + ' faces deleted successfully', 1000, self.topWin)
    
    
    def SerchByIdentity(self, content):
        #print(content)
        #clear table
        items = self.table.get_children()
        for item in items:
            self.table.delete(item)
        #refill table        
        faceInfos = FileOption().GetFaceListInfo(content)
        if faceInfos is not None:
            for item in faceInfos:
                    self.table.insert('',tk.END, values = (item.faceId, item.name, item.identity, item.info))
        
        return True
            
            
    
    def UnSelectTable(self):
        self.table.selection_remove(self.table.selection())
    
    
    def ChangePermission(self, event = None):
        oldp = self.inputTextOld.get()
        newp = self.inputTextNew.get()
        repp = self.inputTextRepeat.get()
        if newp != repp:
            messagebox.showerror(title = 'Error', message = 'Repeat permission error', parent = self.topWin)
        else: 
            retvalue = FileOption().WritePermission(oldp, newp)
            if retvalue is 0:
                messagebox.showinfo(title = 'Info', message = 'Change permission success!', parent = self.topWin)
                self.CancelResetPermission()
            elif retvalue < 0:
                messagebox.showerror(title = Error().GetError(retvalue), message = 'Old permission error', parent = self.topWin)
            
    
    def CancelResetPermission(self):
        self.inputTextOld.delete(0,tk.END)
        self.inputTextNew.delete(0,tk.END)
        self.inputTextRepeat.delete(0,tk.END)
    
            
    def __del__(self):
        print('destroy object MenuGui')

# =============================================================================
#         listBox = tk.Listbox(frame1_left1, selectbackground = 'deepskyblue', highlightcolor = '#000000')
#         listBox.pack(fill = tk.X, expand = True)
#         #print(listBox.config())
#         for item in [' Management',' New face',' Change permission']:
#             listBox.insert(tk.END, item)
# =============================================================================

class Popup:
    def __init__(self, title, content, time, wparent):
        self.title = title
        self.content = content
        self.time = time
        self.wparent = wparent
        self.widget = tk.Tk()
        self.widget.title(self.title)
        self.widget.wm_attributes('-topmost', 1)
        #self.win.wm_attributes('-type', 'splash')

        width = 300
        height = 100
        
        px = self.wparent.winfo_x() 
        py = self.wparent.winfo_y()
        
        
        pw = self.wparent.winfo_width() 
        ph = self.wparent.winfo_height() 
        
        dx = (pw - width) / 2
        dy = (ph - height) / 2
        
        #print(width)
        #print(height)
        #self.widget.geometry("%dx%d+%d+%d" % (width, height, px, py))
        self.widget.geometry("%dx%d+%d+%d" % (width, height, dx + px, dy + py))

        message = tk.Message(self.widget, text = self.content, width = width)
        message.pack(fill = tk.BOTH, expand = True)
       
        self.widget.after(time, self.widget.destroy)
        
        self.widget.mainloop()
        
    def __del__(self):
        pass
    
class Progressbar:
    def __init__(self, wparent):
        self.wparent = wparent
        self.widget = tk.Toplevel()
        self.widget.wm_attributes('-topmost', 1)
        self.widget.wm_attributes('-type', 'splash')
        self.maximumstr = ''
        
        width = 350
        height = 50
        
        px = self.wparent.winfo_x() 
        py = self.wparent.winfo_y()
        
        
        pw = self.wparent.winfo_width() 
        ph = self.wparent.winfo_height() 
        
        dx = (pw - width) / 2
        dy = (ph - height) / 2

        self.widget.geometry("%dx%d+%d+%d" % (width, height, dx + px, dy + py))
        
        self.text = tk.StringVar()
        self.text.set('Processing progress (0/0)')
        self.label = tk.Label(self.widget,  textvariable = self.text)       
        self.label.pack()
        
        self.progressbar = ttk.Progressbar(self.widget, orient="horizontal", length = 300, mode="determinate")
        self.progressbar.pack()
        
        #self.widget.mainloop()
    
    def SetProgressBarValue(self, initvalue, maximum):
        self.progressbar['value'] = initvalue
        self.progressbar['maximum'] = maximum
        self.maximumstr = str(maximum)
    
    def Update(self, value):
        self.progressbar['value'] = value
        self.progressbar.update()
        self.text.set('Processing progress ('+str(value)+'/'+self.maximumstr+')')
    
    def Release(self):
        self.widget.destroy()
    




if __name__ == '__main__':
    win = MainWin()
    win.GuiShow()
    del win
    print('exit program')
        
        


























