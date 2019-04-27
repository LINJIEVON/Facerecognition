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
from PIL import Image, ImageTk
from core import FaceCore, MyThread
from dboperation import FileOption


threadCount = 0

class MainWin:
    def __init__(self):
        self.menuTextState = False
        self.facecore = FaceCore()
        self.image = None
        
    def GuiShow(self):
        self.message = ''
        win = tk.Tk()
        win.title('Face-Recognition')
        win.geometry('640x650')
        win.minsize(640,650)
        win.protocol('WM_DELETE_WINDOW',    lambda:self.CallBack(win))
    
        frametop = tk.Frame( win, padx = 1, pady = 2, bg = 'snow')
        frametop.pack(fill = tk.X)
                
        tk.Frame(height = 1, bg = 'gray').pack(fill = tk.X)
        
        framemid = tk.Frame( win)
        framemid.pack(fill = tk.X)
        
        tk.Frame(height = 1, bg = 'gray').pack(fill = tk.X)
        
        framebottom = tk.Frame( win)
        framebottom.pack(fill = tk.X)
    
        btmenu = tk.Button( frametop, text = 'menu', command = self.MenuShow, bg = 'steelblue')
        btmenu.pack(side = tk.LEFT)
        
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
        self.outtext.insert( tk.END, 'Init ...\n')
        self.outtext.config(state = tk.DISABLED)
        self.outtext.propagate(False)
        self.outtext.pack(expand = True, fill = tk.BOTH)
        
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
        
        retvalue = self.facecore.FaceInit(console = self.outtext)
        if retvalue < 0:
             messagebox.showerror(title = 'Error', message = 'Camera not found !', parent = win)
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
            self.FaceRecognition(win)
        if 'm'== key:
            self.MenuShow()
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
            
    def MenuShow(self, event = None): 
        Verify(self.facecore).Verify()
  
        
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
        global threadCount
        threadCount += 1
        dicResult= self.facecore.FaceRecognition()
        if len(dicResult) <= 0:
            messagebox.showerror(title = 'Error', message = self.facecore.errorMessage, parent = win)
        else:  
            string  = 'name: ' + dicResult['name'] + '\nconfidence: ' + dicResult['distance'] 
            messagebox.showinfo(title = 'Recognize thr result', message = string, parent = win)
        threadCount -= 1
        
    def __del__(self):
        print('destroy object MainWin')






class Verify:
    
    def __init__(self, facecore):
        self.facecore = facecore
        self.menugui = MenuGui()
        
        
    
    def Verify(self):
        self.root = tk.Tk(className='Enter permission') 
        self.root.geometry('270x70')  
        self.root.wm_attributes('-topmost', 1)
        
        self.inputstr = tk.StringVar(self.root) 
        entry = tk.Entry(self.root, textvariable = self.inputstr, show = '*')  
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
            self.facecore.CvPrint('Permission error!')
            messagebox.showerror(title = 'Error', message = 'Permission error!')
        else:
            retvalue = FileOption().VerifyPermission(permission)
            if retvalue >= 0:
                self.MenuCancel()
                self.menugui.GuiShow(tk.Toplevel(), self.facecore)
            else:
                self.facecore.CvPrint('Permission error!')
                messagebox.showerror(title = 'Error', message = 'Permission error!')
                self.root.destroy()
        
    def MenuCancel(self):
        self.root.destroy()
        
        
    def __del__(self):
        print('destroy object Verify')
    





class MenuGui:
    
    def __init__(self):
        self.topWin = None
        self.facecore = None
        self.autoMessage = None
        
    def GuiShow(self, master, facecore):
        
        self.topWin = master
        self.facecore = facecore
        
        self.topWin.title('Menu')
        self.topWin.geometry('600x500')
        self.topWin.minsize(500,400)
        self.topWin.protocol('WM_DELETE_WINDOW',    lambda:self.CallBack(self.topWin))
        
        self.facecore.SetParentWidget(self.topWin)
        
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
        
        self.table = ttk.Treeview(frame_left2_1_1, show = 'headings', selectmode='extended')
        self.table.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        self.table.config(columns = ('label','name','note'))
        self.table.heading('label', text = 'label')
        self.table.column('label', width = '20')
        self.table.heading('name', text = 'name')
        self.table.column('name', width = '10')
        self.table.heading('note', text = 'note')
        self.table.column('note', width = '30')        
        #self.table['show'] = 'headings'
        #self.table.column("#0", width = 0)

        scrollbar = ttk.Scrollbar(frame_left2_1_1)
        scrollbar.pack(side = tk.LEFT, fill = tk.Y)
        scrollbar.config(command = self.table.yview)
        self.table.config(yscrollcommand = scrollbar.set)
        
        
        button_frame = tk.Frame(frame_left2_1, height = 40, bg = 'white', pady = 2\
                                , highlightthickness = 1, highlightbackground = 'gray')
        #button_frame.propagate(False)
        button_frame.pack(fill = tk.X, pady = 5)
        
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
        self.inputText1 = tk.Entry(frame_2_2_1)
        self.inputText1.pack(side = tk.RIGHT)
        labelText1 = tk.Label(frame_2_2_1, bg = 'white', text ='Name: ', anchor = tk.E)
        labelText1.pack(side = tk.RIGHT)
        
        frame_2_2_2 = tk.Frame(frame_2_2_base, bg = 'white')
        #frame_2_2_2.propagate(False)
        frame_2_2_2.pack(fill = tk.X, pady = 10)
        self.inputText2 = tk.Text(frame_2_2_2, width = 20, height = 5, wrap = tk.WORD)
        self.inputText2.pack(side = tk.RIGHT)
        labelText1 = tk.Label(frame_2_2_2, bg = 'white', text ='Note: ', anchor = tk.NE)
        labelText1.pack(side = tk.RIGHT, fill = tk.Y)
        
        frame_2_2_base2 = tk.Frame(frame_left2_2, bg = 'white', pady = 2\
                                   ,highlightthickness = 1, highlightbackground = 'gray')
        #frame_2_2_4.propagate(False)
        frame_2_2_base2.pack(side = tk.BOTTOM, fill = tk.X, pady = 5)
        button_f21 = tk.Button(frame_2_2_base2, text = 'Clear', command = self.ClearFaceInput)
        button_f21.pack(side = tk.RIGHT, padx = 2)
        button_f22 = tk.Button(frame_2_2_base2, text = 'Train', width = 5, command = lambda:MyThread(self.CreateNewFace).start() )
        button_f22.pack(side = tk.RIGHT, padx = 2)
# =============================================================================
#         button_f22 = tk.Button(frame_2_2_base2, text = 'Train', width = 5, command = self.CreateNewFace)
#         button_f22.pack(side = tk.RIGHT, padx = 2)
# =============================================================================
              
        
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
        self.inputTextOld = tk.Entry(frame_2_3_1, show = '*')
        self.inputTextOld.pack(side = tk.RIGHT)
        labelText1 = tk.Label(frame_2_3_1, bg = 'white', text ='old permission: ', anchor = tk.E)
        labelText1.pack(side = tk.RIGHT)
        
        frame_2_3_2 = tk.Frame(frame_2_3_base, bg = 'white')
        #frame_2_3_2.propagate(False)
        frame_2_3_2.pack(fill = tk.X, pady = 10)
        self.inputTextNew = tk.Entry(frame_2_3_2, show = '*')
        self.inputTextNew.pack(side = tk.RIGHT)
        labelText1 = tk.Label(frame_2_3_2, bg = 'white', text ='new permission: ', anchor = tk.E)
        labelText1.pack(side = tk.RIGHT)

        
        frame_2_3_3 = tk.Frame(frame_2_3_base, bg = 'white')
        #frame_2_3_3.propagate(False)
        frame_2_3_3.pack(fill = tk.X, pady = 10)
        self.inputTextRepeat = tk.Entry(frame_2_3_3, show = '*')
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
        global threadCount
        threadCount += 1
        name = self.inputText1.get()
        if 0 == len(name):
            name = 'unspecified'
        note = self.inputText2.get(0.0, tk.END)
        if 0 == len(note):
            note = 'null'
        faceInfo = self.facecore.TrainFromCamera(name, note)
        self.RefreshTable(faceInfo)
        threadCount -= 1
        
    def ClearFaceInput(self):
        self.inputText1.delete(0, tk.END)
        self.inputText2.delete(0.0, tk.END)
    
    def RefreshTable(self, faceId = None):
        self.fileObject = FileOption()
        if None != faceId:
            faceInfo = self.fileObject.GetFaceInfo(faceId)
            self.table.insert('',tk.END, values = (faceInfo.faceId, faceInfo.name, faceInfo.info))
        else:
            faceInfos = []
            self.fileObject.GetFaceListInfo(faceInfos)
            for item in faceInfos:
                self.table.insert('',tk.END, values = (item.faceId, item.name, item.info))
                
        
    def DeleteTableItems(self, deleteAll = False):
        faceIds = []
        obids = []
        if False == deleteAll:
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
        retvalue = messagebox.askokcancel(title = 'Info', message = 'Whether to delete the selected '\
                                          +str( len(faceIds) )+' faces', parent = self.topWin)
        if retvalue:
            for item in obids:
                self.table.delete(item)
            self.facecore.DeleteFaces(faceIds)
            
            
    
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
            if 0 == retvalue:
                messagebox.showinfo(title = 'Info', message = 'Change permission success!', parent = self.topWin)
                self.CancelResetPermission()
            elif -1 == retvalue:
                messagebox.showinfo(title = 'Error', message = 'Old permission rrror', parent = self.topWin)
            
    
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
        





if __name__ == '__main__':
    win = MainWin()
    win.GuiShow()
    del win
    print('exit program')
        
        


























