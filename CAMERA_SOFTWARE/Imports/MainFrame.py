from __future__ import division
import wx
import os
import sys
import time
import random
import copy
import array
import DropBox
import threading
import serial
from time import sleep
from wx.lib.wordwrap import wordwrap
import cStringIO
import signal

#Constants
WINDOW_SIZE = wx.Size(990, 670)
WINDOW_POSITION = wx.Point(50, 50)
SETTINGS_SIZE = wx.Size(550, 440)
FRAMESCOUNT = 15
MAIN_PANEL_RGB = wx.Colour(150, 150, 150)
PANEL_RGB = wx.Colour(200, 200, 200)
VIEW_PANEL_SIZE = wx.Size(750, 500)
INCOMING_IMAGE_RESOLUTION = wx.Size(1360, 1024)
DEFAULT_FILE_PREFIX = 'default'

#Enumeration
SETTINGS = wx.ID_HIGHEST + 1
STARTSTOP_BUTTON = wx.ID_HIGHEST + 2
DISPLAYHOLD_SLIDER = wx.ID_HIGHEST + 3
FILESPERFOLDER_SLIDER = wx.ID_HIGHEST + 4
QUALITY_SLIDER = wx.ID_HIGHEST + 5
SETTINGS_ACCEPT = wx.ID_HIGHEST + 6
SETTINGS_CANCEL = wx.ID_HIGHEST + 7
SETTINGS_DEFAULT = wx.ID_HIGHEST + 8

def IsNumeric(s):
    '''Checks to see if values of type float have been entered in the appropriate fields.
       If not, returns an error.'''
    try:
        float(s)
        return True
    except ValueError:
        return False

class GPSThread(threading.Thread):
    def __init__(self, frame):
        self.frame = frame
        threading.Thread.__init__(self)
        
    def run(self):
        self.frame.UpdateGPS()

class MainFrame(wx.Frame):
        
    def __init__(self, drop, app, title):
        wx.Frame.__init__(self, None, 1, title=title, size=WINDOW_SIZE, pos=WINDOW_POSITION)
        self.MyApp = app
        self.drop = drop
        self.updatingGPS = False
        self.running = False
        self.settingsVerified = False

        cameraName = 'Waiting...'
  
        # Menu
        fileMenu = wx.Menu()
        helpMenu = wx.Menu()
        about = helpMenu.Append(wx.ID_ABOUT, 'About...\tF1', 'Show about dialog')
        setng = fileMenu.Append(SETTINGS, 'Settings\tAlt-S', 'Open settings window')
        qui = fileMenu.Append(wx.ID_EXIT, 'Exit\tAlt-X', 'Quit this program') 
        self.Bind(wx.EVT_MENU, self.OnQuit, qui)
        self.Bind(wx.EVT_MENU, self.OnSettings, setng)
        self.Bind(wx.EVT_MENU, self.OnAbout, about)

        # Menu Bar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, 'File')
        menuBar.Append(helpMenu, 'Help')
        self.SetMenuBar(menuBar)
        
        # Panels
        mainPanel = wx.Panel(self, pos=wx.Point(0, 0), size=wx.Size(100, 580))
        self.imagePanel = ImageViewPanel(mainPanel, self, drop, wx.Point(230, 45))
        hardwareSettingsPanel = wx.Panel(mainPanel, pos=wx.Point(20, 12), size=wx.Size(200, 208), style=wx.SUNKEN_BORDER)
        fileSettingsPanel = wx.Panel(mainPanel, pos=wx.Point(20, 240), size=wx.Size(200, 335), style=wx.SUNKEN_BORDER)
        runPanel = wx.Panel(mainPanel, pos=wx.Point(240, 10), size=wx.Size(180, 30), style=wx.SUNKEN_BORDER)
        runInfoPanel = wx.Panel(mainPanel, pos=wx.Point(420, 10), size=wx.Size(530, 30), style=wx.SUNKEN_BORDER)
        gpsPanel = wx.Panel(mainPanel, pos=wx.Point(240, 544), size=wx.Size(450, 30), style=wx.SUNKEN_BORDER)
        depthPanel = wx.Panel(mainPanel, pos=wx.Point(700, 544), size=wx.Size(250, 30), style=wx.SUNKEN_BORDER)
        
        # Panel Configurations
        mainPanel.SetBackgroundColour(MAIN_PANEL_RGB) 
        hardwareSettingsPanel.SetBackgroundColour(PANEL_RGB)
        fileSettingsPanel.SetBackgroundColour(PANEL_RGB)
        runPanel.SetBackgroundColour(PANEL_RGB)
        runInfoPanel.SetBackgroundColour(PANEL_RGB)
        gpsPanel.SetBackgroundColour(PANEL_RGB)
        depthPanel.SetBackgroundColour(PANEL_RGB)

        # Hardware Settings Panel
        wx.StaticText(hardwareSettingsPanel, -1, 'Camera Name', wx.Point(25, 20))
        wx.StaticText(hardwareSettingsPanel, -1, 'Display Hold', wx.Point(25, 60))
        wx.StaticText(hardwareSettingsPanel, -1, 'GPS Port', wx.Point(25, 100))
        wx.StaticText(hardwareSettingsPanel, -1, 'Sounder Port', wx.Point(25, 140))
        self.gpsDisplay = wx.StaticText(gpsPanel, -1, 'Waiting for data...', wx.Point(1, 1), wx.Size(348, 48))
        self.depthDisplay = wx.StaticText(depthPanel, -1, 'Waiting for data...', wx.Point(1, 1), wx.Size(348, 48))
        self.cameraNameTextCtrl = wx.TextCtrl(hardwareSettingsPanel, -1, cameraName, wx.Point(25, 36), wx.Size(145, -1))
        self.displayHoldTextCtrl = wx.TextCtrl(hardwareSettingsPanel, -1, '5', wx.Point(25, 76), wx.Size(60, -1))
        self.displayHoldSlider = wx.Slider(hardwareSettingsPanel, DISPLAYHOLD_SLIDER, 5, 0, 10, wx.Point(85, 76), wx.Size(90, -1))
        portChoices = ['COM1','COM2','COM2','COM3','COM4','COM5','COM6','COM7','COM8','COM9','COM10']
        self.gpsPortComboBox = wx.ComboBox(hardwareSettingsPanel, -1, '', wx.Point(25, 116), wx.Size(145, -1), portChoices)
        self.gpsPortComboBox.SetStringSelection('COM7')
        self.sounderPortComboBox = wx.ComboBox(hardwareSettingsPanel, -1, '', wx.Point(25, 156), wx.Size(145, -1), portChoices)
        self.sounderPortComboBox.SetStringSelection('COM8')
       
        # File Settings Panel
        wx.StaticText(fileSettingsPanel, -1, 'Base File Path', wx.Point(25, 20))
        wx.StaticText(fileSettingsPanel, -1, 'File Name Prefix', wx.Point(25, 60))
        wx.StaticText(fileSettingsPanel, -1, 'Files Per Folder', wx.Point(25, 100))
        wx.StaticText(fileSettingsPanel, -1, 'Image Type', wx.Point(25, 140))
        wx.StaticText(fileSettingsPanel, -1, 'Quality', wx.Point(25, 180))   
        self.filePathButton = wx.Button(fileSettingsPanel, -1, 'Select', wx.Point(110, 36), wx.Size(60, 21))
        imageTypeChoices = ['JPEG','TIFF','PNG']
        self.imageTypeComboBox = wx.ComboBox(fileSettingsPanel, -1, '', wx.Point(25, 156), wx.Size(145, -1), imageTypeChoices)
        self.imageTypeComboBox.SetStringSelection('JPEG')
        self.filePathTextCtrl = wx.TextCtrl(fileSettingsPanel, -1, os.getcwd(), wx.Point(25, 36), wx.Size(85, -1))  
        self.fileNamePrefixTextCtrl = wx.TextCtrl(fileSettingsPanel, -1, DEFAULT_FILE_PREFIX, wx.Point(25, 76), wx.Size(145, -1))   
        self.filesPerFolderTextCtrl = wx.TextCtrl(fileSettingsPanel, -1, '500', wx.Point(25, 116), wx.Size(60, -1))
        self.filesPerFolderSlider = wx.Slider(fileSettingsPanel, FILESPERFOLDER_SLIDER, 500, 1, 1000, wx.Point(85, 116), wx.Size(90, -1))        
        self.qualityTextCtrl = wx.TextCtrl(fileSettingsPanel, -1, '75', wx.Point(25, 196), wx.Size(60, -1))
        self.qualitySlider = wx.Slider(fileSettingsPanel, QUALITY_SLIDER, 75, 1, 100, wx.Point(85, 196), wx.Size(90, -1))
        
        self.Bind(wx.EVT_COMBOBOX, self.onSounderPortSelect, self.sounderPortComboBox)

        
        self.Bind(wx.EVT_TEXT, self.AdjustDisplaySlider, self.displayHoldTextCtrl)
        self.Bind(wx.EVT_TEXT, self.AdjustFileSlider, self.filesPerFolderTextCtrl)
        self.Bind(wx.EVT_TEXT, self.AdjustQualitySlider, self.qualityTextCtrl)
        self.Bind(wx.EVT_SLIDER, self.AdjustDisplayTxt, self.displayHoldSlider)
        self.Bind(wx.EVT_SLIDER, self.AdjustFileTxt, self.filesPerFolderSlider)
        self.Bind(wx.EVT_SLIDER, self.AdjustQualityTxt, self.qualitySlider)
        self.Bind(wx.EVT_BUTTON, self.OnDirectory, self.filePathButton)

        self.cameraNameTextCtrl.Disable()

        #Run Panel
        self.startStopButton = wx.Button(runPanel, STARTSTOP_BUTTON, 'Start/Stop', wx.Point(1, 1), wx.Size(175, 25))
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.OnStartStop, self.startStopButton)

            
        #Run Info Panel
        self.runInfoTextCtrl = wx.TextCtrl(runInfoPanel, -1, '', wx.Point(2, 2), wx.Size(522, -1))

        #Create Status Bar
        wx.Frame.CreateStatusBar(self, 2)
        wx.Frame.SetStatusText(self, 'wxCamGui initialized.')

        self.imagePanel.ShowImages()

        self.controls = [self.filePathButton, self.displayHoldSlider, self.filePathTextCtrl, \
            self.filesPerFolderTextCtrl, self.fileNamePrefixTextCtrl, self.displayHoldTextCtrl, \
            self.filesPerFolderSlider, self.gpsPortComboBox, self.sounderPortComboBox, \
            self.imageTypeComboBox, self.qualityTextCtrl, self.qualitySlider]

    def onSounderPortSelect(self, event):
        pass
        #print "changing port"

    def Update(self):
        '''Checks if GPS thread needs updating. If so, start updating thread.'''
        if self.updatingGPS == False:
            self.updatingGPS = True
            self.updateThread = GPSThread(self)
            self.updateThread.start()
        if self.drop.error != None:
            print self.drop.error
        if self.drop.running == False:
            self.cameraNameTextCtrl.SetValue(self.drop.cameraName)
            if self.cameraNameTextCtrl.GetValue() == 'Waiting...':
                self.startStopButton.Disable()
            else:
                self.startStopButton.Enable()
        else:
            self.runInfoTextCtrl.SetValue(self.drop.currentFile)

    def UpdateGPS(self):
        '''Reads in GPS and Depth from respective com7 and com8 ports and displays
           the information on the GUI application.'''
        while 1:
            try: 
            
                ser_gps = serial.Serial(self.gpsPortComboBox.GetStringSelection(), baudrate=9600)
                
                while 1:
                    data_gps = ser_gps.readline()
                    if(data_gps[0] == "$" and data_gps[len(data_gps) - 2] == "\r"):
                        break
                self.drop.gpsData = data_gps
                self.gpsDisplay.SetLabel(data_gps)
                ser_gps.close()

            except:
                guiOn = True
                try:
                    self.gpsDisplay.SetLabel('Waiting for data...!')
                except wx.PyDeadObjectError:
                    pid = os.getpid()
                    os.kill(pid, signal.SIGILL)
                    guiOn = False
                    
                if guiOn:
                    self.drop.gpsData = None
                    self.gpsDisplay.SetLabel('Waiting for data...!')
                
            try:
                ser_dep = serial.Serial(self.sounderPortComboBox.GetStringSelection(), baudrate=9600)
                while 1:
                    data_dep = ser_dep.readline()
                    if(data_dep[0] == "$" and data_dep[len(data_dep) - 2] == "\r"):
                        break
                self.drop.depthData = data_dep
                self.depthDisplay.SetLabel(data_dep)
                ser_dep.close()
                
            except:
                guiOn = True
                try:
                    self.depthDisplay.SetLabel('Waiting for data...') 
                except wx.PyDeadObjectError:
                    guiOn = False
                if guiOn:
                    self.drop.depthData = None
                    self.depthDisplay.SetLabel('Waiting for data...')

        updatingGPS = False

    def VerifySettings(self):
        '''Verifies that settings for display delay value, file path, file name
           prefix, number of files per folder, and image quality  have been set. 
           Otherwise, returns errors.'''
        
        if not IsNumeric(self.displayHoldTextCtrl.GetValue()):
            return 'Error: Please set a main display delay (in seconds).'
        if self.filePathTextCtrl.GetValue() == '':
            return 'Error: No file path set.'
        if self.fileNamePrefixTextCtrl.GetValue() == '':
            return 'Error: No file name prefix set.'
        if not IsNumeric(self.filesPerFolderTextCtrl.GetValue()):
            return 'Error: Please set the number of files to be saved per folder.'
        if not IsNumeric(self.qualityTextCtrl.GetValue()):
            return 'Error: Please set the image quality to save at.'
        self.settingsVerified = True
        return 'No errors'
                 

    def GetImagePanel(self):
        '''Returns image panel'''
        return self.imagePanel

    def OnDirectory(self, e):
        '''Sets the directory to where the files will be saved.'''
        if not self.running:
            self.dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE 
                          | wx.DD_DIR_MUST_EXIST 
                          | wx.DD_CHANGE_DIR
                          )
            if self.dlg.ShowModal() == wx.ID_OK:
                self.filePathTextCtrl.SetValue(self.dlg.GetPath())
                os.chdir(self.dlg.GetPath())
            self.dlg.Destroy()
          
    def OnStartStop(self, e):
        '''Controls when to start/stop saving images and gathering GPS/Depth feed.'''
        
        if self.running == False:
            errorMessage = self.VerifySettings()
                
            if self.settingsVerified:
                self.settingsVerified = False
                result = wx.ID_YES
                if os.path.exists(self.filePathTextCtrl.GetValue()+'\\'+self.fileNamePrefixTextCtrl.GetValue()):
                    dlg = wx.MessageDialog(None, 'The image directory already exists, do you want to overwrite?', 'Warning', wx.YES_NO | wx.ICON_EXCLAMATION)
                    result = dlg.ShowModal()
                    dlg.Destroy()

                if result == wx.ID_YES:
                    self.drop.filesPerFolder = int(self.filesPerFolderTextCtrl.GetValue())
                    self.drop.path = self.filePathTextCtrl.GetValue()
                    self.drop.prefix = self.fileNamePrefixTextCtrl.GetValue()
                    self.drop.quality = int(self.qualityTextCtrl.GetValue())
                    if self.drop.quality > 95 and self.drop.quality < 100:
                        self.drop.quality = 100
                    self.drop.filetype = self.imageTypeComboBox.GetValue()
                    if self.imageTypeComboBox.GetValue() == 'JPEG':
                        self.imagePanel.imageType = wx.BITMAP_TYPE_JPEG
                    elif self.imageTypeComboBox.GetValue() == 'TIFF':
                        self.imagePanel.imageType = wx.BITMAP_TYPE_TIF
                    elif self.imageTypeComboBox.GetValue() == 'PNG':
                        self.imagePanel.imageType = wx.BITMAP_TYPE_PNG
                    self.drop.imageDelay = float(self.displayHoldTextCtrl.GetValue())
                    self.DisableControls()
                    self.running = True
                    self.drop.running = True
            else:
                dlg = wx.MessageDialog(None, errorMessage, 'Error', wx.OK | wx.ICON_EXCLAMATION)
                result = dlg.ShowModal()
                dlg.Destroy()
                #print errorMessage
        else:
            self.running = False
            self.drop.running = False
            self.EnableControls()
                
        

    def EnableControls(self):
        '''Enables the following controls: filePathButton, displayHoldSlider, filePathTextCtrl, 
            filesPerFolderTextCtrl, fileNamePrefixTextCtrl, displayHoldTextCtrl, 
            filesPerFolderSlider, gpsPortComboBox, sounderPortComboBox, 
            imageTypeComboBox, qualityTextCtrl, and qualitySlider.'''
        for x in self.controls:
            x.Enable()

    def DisableControls(self):
        '''Disables the following controls: filePathButton, displayHoldSlider, filePathTextCtrl, 
            filesPerFolderTextCtrl, fileNamePrefixTextCtrl, displayHoldTextCtrl, 
            filesPerFolderSlider, gpsPortComboBox, sounderPortComboBox, 
            imageTypeComboBox, qualityTextCtrl, and qualitySlider.'''        
        for x in self.controls:
            x.Disable()
    
    def OnQuit(self, e):
        '''Closes application.'''
        self.drop.close = True
        time.sleep(1)
        self.Close()
        self.MyApp.settingsFrame.SettingsClose(self)
        
    def OnAbout(self, e):
        '''Provides information about the application.'''
        info = wx.AboutDialogInfo()
        info.Name = "Ocean Real Time Data Collection"
        info.Version = "1.0"
        info.Copyright = "(C) 2012 Edwards Lab"
        info.Description = wordwrap(
            "\"Ocean Real Time Data Collection\" software records photographic imaging "
            "of the seabed, location-based sensing via GPS, and motion-based sensing from "
            "direct interaction with the host vehicle."
            
            "\n\nThis application integrates the data streams from these remote "
            "sensors and displays the information to the user. The data streams "
            "are coordinated and stored for future use.",
            350, wx.ClientDC(self))
        info.WebSite = ("https://github.com/linsalrob/cameraGUI", "Open Source code")
        info.Developers = [ "Edwards Lab" ]
        wx.AboutBox(info)
    
    def AdjustDisplaySlider(self, e):
        '''Adjusts the Display Holder slider to match up with the value entered.'''
        self.displayHoldSlider.SetValue(int(self.displayHoldTextCtrl.GetValue()))
        
    def AdjustQualitySlider(self, e):
        '''Adjusts the Quality slider to match up with the value entered.'''
        self.qualitySlider.SetValue(int(self.qualityTextCtrl.GetValue()))
    
    def AdjustFileSlider(self, e):
        '''Adjusts the Files Per Folder slider to match up with the value entered.'''
        self.filesPerFolderSlider.SetValue(int(self.filesPerFolderTextCtrl.GetValue())) 

    def AdjustQualityTxt(self, e): 
        '''Sets the Quality Value to where the slider is moved.'''
        self.pos2 = self.qualitySlider.GetValue()
        str2 = "%d" % (self.pos2)
        self.qualityTextCtrl.SetValue(str2)
    
    def AdjustDisplayTxt(self, e):    
        '''Sets the Display Holder value to where the slider is moved.'''
        self.pos3 = self.displayHoldSlider.GetValue()
        str3 = "%d" % (self.pos3)
        self.displayHoldTextCtrl.SetValue(str3)
        
    def AdjustFileTxt(self, e):
        '''Sets the Files Per Folder value to where the slider is moved.'''
        self.pos1 = self.filesPerFolderSlider.GetValue()
        str1 = "%d" % (self.pos1)
        self.filesPerFolderTextCtrl.SetValue(str1)
    
    def OnSettings(self, e):
        '''Displays Settings Window.'''
        if not self.running:
            self.MyApp.settingsFrame.ShowSettings(self)

class ImageViewPanel(wx.Panel):
    '''This UI panel includes the main viewscreen, the four additional view screens, and the buttons.
    All of those elements are direct children of this panel.'''
    def __init__(self, parent, mainFrame, drop, pos):
        #Initialization
        self.queueSize = 20 #How many images to leave in the temporary queue
        self.mainFrame = mainFrame
        self.imageType = wx.BITMAP_TYPE_JPEG
        
        wx.Panel.__init__(self, parent, pos=pos, size=VIEW_PANEL_SIZE)
        self.SetBackgroundColour(MAIN_PANEL_RGB)
        largePanel = ImageViewport(self, wx.Point(10, 10), wx.Size(550, 414), 0, style=wx.SUNKEN_BORDER)
        largePanel.isMain = True
        smallPanel1 = ImageViewport(self, wx.Point(570, 10), wx.Size(150, 112), 1, style=wx.SUNKEN_BORDER)
        smallPanel2 = ImageViewport(self, wx.Point(570, 132), wx.Size(150, 112), 2, style=wx.SUNKEN_BORDER)
        smallPanel3 = ImageViewport(self, wx.Point(570, 254), wx.Size(150, 112), 3, style=wx.SUNKEN_BORDER)
        smallPanel4 = ImageViewport(self, wx.Point(570, 376), wx.Size(150, 112), 4, style=wx.SUNKEN_BORDER)

        self.zoomOutBitmap = wx.Bitmap('./Imports/zoomout.png', wx.BITMAP_TYPE_PNG)
        self.zoomInBitmap = wx.Bitmap('./Imports/zoomin.png', wx.BITMAP_TYPE_PNG)
        self.nextBitmap = wx.Bitmap('./Imports/next.png', wx.BITMAP_TYPE_PNG)
        self.prevBitmap = wx.Bitmap('./Imports/prev.png', wx.BITMAP_TYPE_PNG)
        self.contLiveBitmap = wx.Bitmap('./Imports/contlive.png', wx.BITMAP_TYPE_PNG)
        self.contPausedBitmap = wx.Bitmap('./Imports/contpaused.png', wx.BITMAP_TYPE_PNG)
        
        self.nextButton = wx.BitmapButton(self, -1, self.nextBitmap, wx.Point(130, 435), wx.Size(50, 50))
        self.prevButton = wx.BitmapButton(self, -1, self.prevBitmap, wx.Point(10, 435), wx.Size(50, 50))
        self.contButton = wx.BitmapButton(self, -1, self.contPausedBitmap, wx.Point(70, 435), wx.Size(50, 50))
        self.zoomInButton = wx.BitmapButton(self, -1, self.zoomInBitmap, wx.Point(450, 435), wx.Size(50, 50))
        self.zoomOutButton = wx.BitmapButton(self, -1, self.zoomOutBitmap, wx.Point(510, 435), wx.Size(50, 50))
        
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ScrollNext, self.nextButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ScrollPrev, self.prevButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ContinueScroll, self.contButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ZoomIn, self.zoomInButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ZoomOut, self.zoomOutButton)
        
        self.isScrolling = True #Set if, when this panel is updated, it should also be scrolling. Otherwise cleared.
        self.wasRunning = False #Set if, last update, this panel was running. Otherwise cleared. Used to prevent sync issues.
        self.firstCachedImage = 1
        
        self.viewports = [largePanel, smallPanel1, smallPanel2, smallPanel3, smallPanel4]
        self.imageQueue = []
        self.blankBitmap = wx.Bitmap('./imports/blank.jpg', wx.BITMAP_TYPE_JPEG)
        for i in range(self.queueSize):
            self.imageQueue.append(self.blankBitmap)
        self.imageQueue[4] = (copy.copy(self.blankBitmap))
        self.imageQueue[3] = (copy.copy(self.blankBitmap))
        self.imageQueue[2] = (copy.copy(self.blankBitmap))
        self.imageQueue[1] = (copy.copy(self.blankBitmap))
        self.imageQueue[0] = (copy.copy(self.blankBitmap))
        self.queuePos = 4
        self.currentQueue = 4
        
        largePanel.SetImage(copy.copy(self.blankBitmap))
        smallPanel1.SetImage(copy.copy(self.blankBitmap))
        smallPanel2.SetImage(copy.copy(self.blankBitmap))
        smallPanel3.SetImage(copy.copy(self.blankBitmap))
        smallPanel4.SetImage(copy.copy(self.blankBitmap))

        self.drop = drop
        self.nextImage = time.clock() + drop.imageDelay

    def QueueNext(self, i):
        '''Returns the index position of the next image.'''
        if i == (self.queueSize - 1):
            return 0
        else:
            return (i + 1)

    def QueuePrev(self, i):
        '''Returns the index position of the previous image.'''
        if i == 0:
            return (self.queueSize - 1)
        else:
            return (i - 1)

    def DoPaint(self):
        '''Redraws the current window.'''
        self.Refresh(True)
        wx.EVT_PAINT(self, self.OnPaint)

    def ZoomIn(self, e):
        '''Zooms in the center main image.''' 
        self.isScrolling = False
        self.viewports[0].ZoomIn(copy.copy(self.imageQueue[self.currentQueue]))
        self.Refresh(True)
        wx.EVT_PAINT(self, self.OnPaint)

    def ZoomOut(self, e):
        '''Zooms out the center main image.'''
        self.isScrolling = False
        self.viewports[0].ZoomOut(copy.copy(self.imageQueue[self.currentQueue]))
        self.Refresh(True)
        wx.EVT_PAINT(self, self.OnPaint)
        

    def Update(self):
        '''Updates the center main image to the most current feed.
            The images to the right are updated to previous feeds.'''
        if self.drop.running:
            if not self.wasRunning:
                self.wasRunning = True
                self.contButton.SetBitmapLabel(self.contLiveBitmap)
                self.isScrolling = True
            if self.isScrolling:
                img = None
                if time.clock() >= self.nextImage:
                    self.nextImage += self.drop.imageDelay
                    self.RotateImages(None)
        else:
            if self.wasRunning:
                self.wasRunning = False
                self.contButton.SetBitmapLabel(self.contPausedBitmap)

    def ScrollNext(self, e):
        '''Temporarily stops the live feed from displaying on the center panel.
            Also, provides the ability to scroll up to 20 subsequent images.'''

        if self.currentQueue != self.queuePos:
            self.currentQueue = self.QueueNext(self.currentQueue)
            self.SetImagesOnQueue()
            self.isScrolling = False
            self.isLiveFeed = False

    def ScrollPrev(self, e):
        '''Temporarily stops the live feed from showing on the center panel.
            Also, provides the ability to scroll down to 20 preceding images.'''
        if self.currentQueue != (self.QueueNext(self.queuePos)):
            self.currentQueue = self.QueuePrev(self.currentQueue)
            self.SetImagesOnQueue()
            self.isScrolling = False
            self.isLiveFeed = False

    def ContinueScroll(self, e):
        '''Continues displaying the live feed on the center image panel.'''        
        self.isScrolling = True
        self.isLiveFeed = True
        self.nextImage = time.clock() + self.drop.imageDelay
        self.currentQueue = copy.copy(self.queuePos)
        self.SetImagesOnQueue()

    #This method should probably be eliminated on integration
    def ShowImages(self):
        for x in self.viewports:
            x.ShowImage()

    def OnPaint(self, e):
        '''Provides a paint object to redraw all or part of the window.'''
        dc = wx.PaintDC(self)
    
    def RotateImages(self, e):
        '''The center image is moved to the top right panel.
            The images on the right panels are moved to shifted down to subsequent panels.'''
        for i in range(5)[:0:-1]:
            self.viewports[i].SetImage(self.viewports[i - 1].img)
        nextfile = self.drop.GetNextFile()
        if nextfile:
            #print nextfile
            img = wx.Bitmap(self.drop.GetNextFile(), self.imageType)
            self.queuePos = self.QueueNext(self.queuePos)
            self.currentQueue = copy.copy(self.queuePos)
            self.imageQueue[self.QueuePrev(self.queuePos)] = copy.copy(img)
            self.viewports[0].SetImage(img)
            self.Refresh(True)
            wx.EVT_PAINT(self, self.OnPaint)

    def SetImagesOnQueue(self):
        '''Manually sets the queue of images. This is not called during normal running, but instead when it is continued after pausing.'''
        images = []
        i = copy.copy(self.currentQueue)
        fillBlanks = False
        #Get Images
        for x in range(5):
            if i == self.QueueNext(self.queuePos):
                if fillBlanks:
                    images.append(copy.copy(self.blankBitmap))
                else:
                    images.append(copy.copy(self.imageQueue[i]))
                    fillBlanks = True
            else:
                images.append(copy.copy(self.imageQueue[i]))
                i = self.QueuePrev(i)
        #Place Images
        for x in range(5):
            self.viewports[x].SetImage(images[x])
        self.Refresh()
        wx.EVT_PAINT(self, self.OnPaint)
        

class ImageViewport(wx.Panel):
    '''This panel is an individual viewport: Either the large center image, or one of the four side images.'''
    def __init__(self, parent, pos, size, ident, style=0):
        wx.Panel.__init__(self, parent, pos=pos, size=size, style=style)
        self.SetBackgroundColour(PANEL_RGB)
        self.x = pos.Get()[0]
        self.y = pos.Get()[1]
        self.width = size.Get()[0] - 4
        self.height = size.Get()[1] - 4
        self.scale = 1
        self.displayX = 0
        self.displayY = 0
        self.hasMoved = False #Set if this image has been zoomed in or out on, or recentered since being shown. Otherwise, cleared.
        self.isMain = False #Set if this is the center image, otherwise cleared
        self.leftIsDown = False #NOTE: Left/right refer to mouse buttons.
        self.id = ident
        
        wx.EvtHandler.Bind(self, wx.EVT_LEFT_DOWN, self.LeftDown, self)
        wx.EvtHandler.Bind(self, wx.EVT_LEFT_UP, self.LeftUp, self)
        wx.EvtHandler.Bind(self, wx.EVT_ERASE_BACKGROUND, self.EraseBackground)

    def LeftDown(self, e):
        '''Executes on left mouse down.'''
        parent = wx.Window.GetParent(self)
        if self.isMain:
            x = e.GetPosition()[0]
            y = e.GetPosition()[1]
            x = x - (self.width / 2)
            y = y - (self.width / 2)
            self.TransposeImage(parent.imageQueue[parent.currentQueue], x, y)
            parent.DoPaint()
            e.Skip()
        else:
            for i in range(self.id):
                parent.currentQueue = parent.QueuePrev(parent.currentQueue)
            parent.SetImagesOnQueue()
            parent.isLiveFeed = False
            parent.isScrolling = False
            e.Skip()
            
    def LeftUp(self, e):
        '''Executes on left mouse up.'''
        if self.isMain:
            leftIsDown = False

    def SetImage(self, image):
        '''Sets the given image to this viewport.'''
        temp = image.ConvertToImage()        
        temp.Rescale(self.width, self.height)
        self.img = wx.BitmapFromImage(temp)
        self.scale = 1
        self.hasMoved = False

    def ZoomIn(self, image):
        '''Zoom the current image in. Should only be called on the main port.'''
        self.scale += 0.2 # Lower value zooms in less each click, greater value zooms in more each click.
        temp = image.ConvertToImage()
        #If the image has been previously moved, retain the center
        #NOTE: Currently retains top left, need to modify to retain center
        if self.hasMoved:
            self.CompleteZoom(image, temp, retainCenter=True, zoomingIn=True)
        else:
            self.CompleteZoom(image, temp)

    def ZoomOut(self, image):
        '''Zoom the current image out. Should only be called on the main port.'''
        if self.scale > 1:
            self.scale -= 0.2
            temp = image.ConvertToImage()
            if self.hasMoved:
                self.CompleteZoom(image, temp, retainCenter=True, zoomingIn=False)
            else:
                self.CompleteZoom(image, temp)

    def TransposeImage(self, image, x, y):
        temp = image.ConvertToImage()
        self.CompleteZoom(image, temp, x, y)
        self.hasMoved = True

    def CompleteZoom(self, image, temp, xDelta= -1, yDelta= -1, retainCenter=False, zoomingIn=False):
        if self.scale == 1:
            self.SetImage(image)
        else:
            #Find the new source image dimensions            
            imgwidth = self.width * self.scale
            imgheight = self.height * self.scale

            #Retain center if needed
            if retainCenter:
                oldWidth = 0
                oldHeight = 0
                if zoomingIn:
                    oldWidth = self.width * (self.scale - 0.2)
                    oldHeight = self.height * (self.scale - 0.2)
                else:
                    oldWidth = self.width * (self.scale + 0.2)
                    oldHeight = self.height * (self.scale + 0.2)
                xDelta = (imgwidth - oldWidth) / 2
                yDelta = (imgheight - oldHeight) / 2
            
            #Set deltas
            if xDelta == -1:
                self.displayX = (imgwidth - self.width) / 2
            else:
                self.displayX += xDelta
            if yDelta == -1:
                self.displayY = (imgheight - self.height) / 2
            else:
                self.displayY += yDelta
            #Enforce Bounds
            if self.displayX < 0:
                self.displayX = 0
            elif self.displayX > imgwidth - self.width:
                self.displayX = imgwidth - self.width
            if self.displayY < 0:
                self.displayY = 0
            elif self.displayY > imgheight - self.height:
                self.displayY = imgheight - self.height

            #Make and set image
            imgrect = wx.Rect(self.displayX, self.displayY, self.width, self.height)
            temp.Rescale(imgwidth, imgheight)
            temp = temp.GetSubImage(imgrect)
            self.img = wx.BitmapFromImage(temp)

    def ShowImage(self):
        wx.EVT_PAINT(self, self.OnPaint)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.img, 0, 0)

    def EraseBackground(self, e):
        pass

class SettingsFrame(wx.Frame):
    
    def __init__(self, title, drop):
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title=title, size=SETTINGS_SIZE, style= wx.CAPTION)
        self.drop = drop
        
        #Configurations of panels in Settings
        settingsPanel = wx.Panel(self, size=wx.Size(0, 0), pos=wx.Point(500, 500))
        innerSettingsPanel = wx.Panel(settingsPanel, size=wx.Size(510, 340), pos=wx.Point(10, 10), style=wx.SUNKEN_BORDER)
        acceptSettingsPanel = wx.Panel(settingsPanel, size=wx.Size(300, 35), pos=wx.Point(220, 360), style=wx.SUNKEN_BORDER)
        settingsPanel.SetBackgroundColour(MAIN_PANEL_RGB)
        innerSettingsPanel.SetBackgroundColour(PANEL_RGB)
        acceptSettingsPanel.SetBackgroundColour(PANEL_RGB)







    
        #Frame Rate Setting
        wx.StaticText(innerSettingsPanel, -1, 'Frame Rate', wx.Point(25, 22))
        self.frameRateTextCtrl = wx.TextCtrl(innerSettingsPanel, -1, str(self.drop.frameRate), wx.Point(200, 20), wx.Size(200, -1))

        self.line1 = wx.StaticLine(innerSettingsPanel, -1, pos=wx.Point(25, 54), size=wx.Size(375,1))
        
        #Exposure Mode Setting
        wx.StaticText(innerSettingsPanel, -1, 'Exposure Mode', wx.Point(25, 72))
        self.exposureModeComboBox = wx.ComboBox(innerSettingsPanel, -1, self.drop.exposureMode, wx.Point(200, 70), wx.Size(200, -1))
    
        #Exposure Value Setting
        wx.StaticText(innerSettingsPanel, -1, 'Exposure Value', wx.Point(25, 102))
        self.exposureValueTextCtrl = wx.TextCtrl(innerSettingsPanel, -1, '', wx.Point(200, 100), wx.Size(100, -1))
        self.exposureValueSlider = wx.Slider(innerSettingsPanel, -1, 50, 1, 100, wx.Point(300, 100), wx.Size(100, -1))

        self.line2 = wx.StaticLine(innerSettingsPanel, -1, pos=wx.Point(25, 134), size=wx.Size(375,1))
    
        #Gain Mode Choices Setting
        wx.StaticText(innerSettingsPanel, -1, 'Gain Mode', wx.Point(25, 152))
        self.gainModeComboBox = wx.ComboBox(innerSettingsPanel, -1, self.drop.gainMode, wx.Point(200, 150), wx.Size(200, -1))
        
        #Gain Value Setting
        wx.StaticText(innerSettingsPanel, -1, 'Gain Value', wx.Point(25, 182))
        self.gainValueTextCtrl = wx.TextCtrl(innerSettingsPanel, -1, '', wx.Point(200, 180), wx.Size(100, -1))
        self.gainValueSlider = wx.Slider(innerSettingsPanel, -1, 50, 1, 100, wx.Point(300, 180), wx.Size(100, -1))

        self.line3 = wx.StaticLine(innerSettingsPanel, -1, pos=wx.Point(25, 214), size=wx.Size(375,1))
    
        #White Balance Mode Setting
        wx.StaticText(innerSettingsPanel, -1, 'White Balance Mode', wx.Point(25, 232))
        self.whitebalModeComboBox = wx.ComboBox(innerSettingsPanel, -1, self.drop.whitebalMode, wx.Point(200, 230), wx.Size(200, -1))

        self.line4 = wx.StaticLine(innerSettingsPanel, -1, pos=wx.Point(25, 264), size=wx.Size(375,1))
       
        #Packet Size Setting
        wx.StaticText(innerSettingsPanel, -1, 'Packet Size', wx.Point(25, 282))
        self.packetSizeTextCtrl = wx.TextCtrl(innerSettingsPanel, -1, '', wx.Point(200, 280), wx.Size(100, -1))
        self.packetSizeSlider = wx.Slider(innerSettingsPanel, -1, 50, 1, 100, wx.Point(300, 280), wx.Size(100, -1))
        
        self.acceptSettingsButton = wx.Button(acceptSettingsPanel, SETTINGS_ACCEPT, 'Accept', wx.Point(0, 0), wx.Size(99, 33))            
        self.cancelSettingsButton = wx.Button(acceptSettingsPanel, SETTINGS_CANCEL, 'Cancel', wx.Point(99, 0), wx.Size(99, 33))
        self.defaultSettingsButton = wx.Button(acceptSettingsPanel, SETTINGS_DEFAULT, 'Default', wx.Point(198, 0), wx.Size(99, 33))

        self.Bind(wx.EVT_TEXT, self.AdjustExposureValueSlider, self.exposureValueTextCtrl)
        self.Bind(wx.EVT_SLIDER, self.AdjustExposureValueTxt, self.exposureValueSlider)
        self.Bind(wx.EVT_TEXT, self.AdjustGainValueSlider, self.gainValueTextCtrl)
        self.Bind(wx.EVT_SLIDER, self.AdjustGainValueTxt, self.gainValueSlider)
        self.Bind(wx.EVT_TEXT, self.AdjustPacketSizeSlider, self.packetSizeTextCtrl)
        self.Bind(wx.EVT_SLIDER, self.AdjustPacketSizeTxt, self.packetSizeSlider)
        
        self.Bind(wx.EVT_BUTTON, self.OnAcceptSettings, self.acceptSettingsButton)
        self.Bind(wx.EVT_BUTTON, self.OnCancelSettings, self.cancelSettingsButton)
        self.Bind(wx.EVT_BUTTON, self.OnDefaultSettings, self.defaultSettingsButton)
    
    def OnAcceptSettings(self, e):
        '''Accepts and adjusts the camera Settings.'''
        self.drop.frameRate = int(self.frameRateTextCtrl.GetValue())
        self.drop.exposureMode = self.exposureModeComboBox.GetValue()
        self.drop.exposureValue = int(self.exposureValueTextCtrl.GetValue())
        self.drop.gainMode = self.gainModeComboBox.GetValue()
        self.drop.gainValue = int(self.gainValueTextCtrl.GetValue())
        self.drop.whitebalMode = self.whitebalModeComboBox.GetValue()
        self.drop.packetSize = int(self.packetSizeTextCtrl.GetValue())
        
        self.Hide()
    
    def OnCancelSettings(self, e):
        '''Cancels the Settings.'''
        self.Hide()

    def OnDefaultSettings(self, e):
        '''Sets the settings to the camera default values.'''
        
        self.drop.exposureMode = 'Manual'
        self.exposureModeComboBox.SetValue(self.drop.exposureMode)
        
        self.drop.exposureValue = 15000
        self.exposureValueTextCtrl.SetValue(str(self.drop.exposureValue))
        
        self.drop.gainMode = 'Manual'
        self.gainModeComboBox.SetValue(self.drop.gainMode)
        
        self.drop.gainValue = 0
        self.gainValueTextCtrl.SetValue(str(self.drop.gainValue))
        
        self.drop.whitebalMode = 'Manual'
        self.whitebalModeComboBox.SetValue(self.drop.whitebalMode)
        
        self.drop.packetSize = 1500
        self.packetSizeTextCtrl.SetValue(str(self.drop.packetSize))
        
        #self.Hide()
        
    def ShowSettings(self,e):
        '''Shows Settings window.'''

        if self.drop.isCameraAttached == True:
            self.Show()
            if self.drop.running == False:
                
                self.exposureModeComboBox.Clear()
                for x in self.drop.exposureModeRange.split(','):
                    self.exposureModeComboBox.Append(x)
                self.exposureModeComboBox.SetStringSelection(self.drop.exposureMode)
                
                self.exposureValueTextCtrl.SetLabel(str(self.drop.exposureValue))
                self.exposureValueSlider.SetMin(int(self.drop.exposureValueRange.split(',')[0]))
                self.exposureValueSlider.SetMax(int(self.drop.exposureValueRange.split(',')[1]))
                self.exposureValueSlider.SetValue(self.drop.exposureValue)

                self.gainModeComboBox.Clear()
                for x in self.drop.gainModeRange.split(','):
                    self.gainModeComboBox.Append(x)
                self.gainModeComboBox.SetStringSelection(self.drop.gainMode)

                self.gainValueTextCtrl.SetLabel(str(self.drop.gainValue))
                self.gainValueSlider.SetMin(int(self.drop.gainValueRange.split(',')[0]))
                self.gainValueSlider.SetMax(int(self.drop.gainValueRange.split(',')[1]))
                self.gainValueSlider.SetValue(self.drop.gainValue)

                self.whitebalModeComboBox.Clear()
                for x in self.drop.whitebalModeRange.split(','):
                    self.whitebalModeComboBox.Append(x)
                self.whitebalModeComboBox.SetStringSelection(self.drop.whitebalMode)

                self.packetSizeTextCtrl.SetLabel(str(self.drop.packetSize))
                self.packetSizeSlider.SetMin(int(self.drop.packetSizeRange.split(',')[0]))
                self.packetSizeSlider.SetMax(int(self.drop.packetSizeRange.split(',')[1]))
                self.packetSizeSlider.SetValue(self.drop.packetSize)
        else:
            self.Hide()
    
    def SettingsClose(self,e):
        '''Closes Setting window.'''
        self.Close()

    def AdjustExposureValueSlider(self, e):
        '''Adjusts the Exposure slider to match up with the value entered.'''
        self.exposureValueSlider.SetValue(int(self.exposureValueTextCtrl.GetValue()))

    def AdjustExposureValueTxt(self, e): 
        '''Sets the Expsoure Value to where the slider is moved.'''
        self.pos2 = self.exposureValueSlider.GetValue()
        str2 = "%d" % (self.pos2)
        self.exposureValueTextCtrl.SetValue(str2)
        
    def AdjustGainValueSlider(self, e):
        '''Adjusts the Gain slider to match up with the value entered.'''
        self.gainValueSlider.SetValue(int(self.gainValueTextCtrl.GetValue()))

    def AdjustGainValueTxt(self, e): 
        '''Sets the Gain Value to where the slider is moved.'''
        self.pos2 = self.gainValueSlider.GetValue()
        str2 = "%d" % (self.pos2)
        self.gainValueTextCtrl.SetValue(str2)

    def AdjustPacketSizeSlider(self, e):
        '''Adjusts the Gain slider to match up with the value entered.'''
        self.packetSizeSlider.SetValue(int(self.packetSizeTextCtrl.GetValue()))

    def AdjustPacketSizeTxt(self, e): 
        '''Sets the Gain Value to where the slider is moved.'''
        self.pos2 = self.packetSizeSlider.GetValue()
        str2 = "%d" % (self.pos2)
        self.packetSizeTextCtrl.SetValue(str2)
