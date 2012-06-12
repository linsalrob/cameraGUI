#!/usr/bin/env python
import wx
import os
from pvAPI import *
import thread
import time

#p = CameraDriver()

#Global Constants
WINDOW_SIZE = wx.Size(1000, 580)
WINDOW_POSITION = wx.Point(50, 50)
SETTINGS_SIZE = wx.Size(550, 440)
MAIN_PANEL_RGB = wx.Colour(150, 150, 150)
PANEL_RGB = wx.Colour(200, 200, 200)

#Enumeration
SETTINGS = wx.ID_HIGHEST + 1
STARTSTOP_BUTTON = wx.ID_HIGHEST + 2
DISPLAYHOLD_SLIDER = wx.ID_HIGHEST + 3
FILESPERFOLDER_SLIDER = wx.ID_HIGHEST + 4
QUALITY_SLIDER = wx.ID_HIGHEST + 5
SETTINGS_ACCEPT = wx.ID_HIGHEST + 6
SETTINGS_CANCEL = wx.ID_HIGHEST + 7

images = "JPG (*.jpg)|*.jpg"

class MyApp(wx.App):
   
    def OnInit(self):
       frame = MyFrame()
       frame.Show()
       self.SetTopWindow(frame)
       return True

class MyFrame(wx.Frame):
   
    title = "Title"
    
    def __init__(self):
        wx.Frame.__init__(self, None, 1, self.title, size=WINDOW_SIZE, pos=WINDOW_POSITION)
        
        #Create Menu
        fileMenu = wx.Menu()
        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_ABOUT, 'About...\tF1', 'Show about dialog')
        setng = fileMenu.Append(SETTINGS, 'Settings\tAlt-S', 'Open settings window')
        qui = fileMenu.Append(wx.ID_EXIT, 'Exit\tAlt-X', 'Quit this program')
        self.Bind(wx.EVT_MENU, self.OnQuit, qui)
        self.Bind(wx.EVT_MENU, self.OnSettings, setng)
       
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, 'File')
        menuBar.Append(helpMenu, 'Help')
        self.SetMenuBar(menuBar)

        #Create Panels
        mainPanel = wx.Panel(self, pos=wx.Point(0, 0), size=wx.Size(100, 580))
        hardwareSettingsPanel = wx.Panel(mainPanel, pos=wx.Point(20, 20), size=wx.Size(200, 200), style=wx.SUNKEN_BORDER)
        fileSettingsPanel = wx.Panel(mainPanel, pos=wx.Point(20, 240), size=wx.Size(200, 240), style=wx.SUNKEN_BORDER)
        runPanel = wx.Panel(mainPanel, pos=wx.Point(240, 15), size=wx.Size(180, 30), style=wx.SUNKEN_BORDER)
        runInfoPanel = wx.Panel(mainPanel, pos=wx.Point(440, 15), size=wx.Size(320, 30), style=wx.SUNKEN_BORDER)
        mainImagePanel = wx.Panel(mainPanel, pos=wx.Point(240, 60), size=wx.Size(520, 340), style=wx.SUNKEN_BORDER)
        previousImagesPanel = wx.Panel(mainPanel, pos=wx.Point(780, 20), size=wx.Size(180, 460), style=wx.SUNKEN_BORDER)
        gpsPanel = wx.Panel(mainPanel, pos=wx.Point(240, 420), size=wx.Size(520, 30), style=wx.SUNKEN_BORDER)
        depthPanel = wx.Panel(mainPanel, pos=wx.Point(240, 450), size=wx.Size(520, 30), style=wx.SUNKEN_BORDER)
        mainPanel.SetBackgroundColour(MAIN_PANEL_RGB)
        hardwareSettingsPanel.SetBackgroundColour(PANEL_RGB)
        fileSettingsPanel.SetBackgroundColour(PANEL_RGB)
        runPanel.SetBackgroundColour(PANEL_RGB)
        runInfoPanel.SetBackgroundColour(PANEL_RGB)
        mainImagePanel.SetBackgroundColour(PANEL_RGB)
        previousImagesPanel.SetBackgroundColour(PANEL_RGB)
        gpsPanel.SetBackgroundColour(PANEL_RGB)
        depthPanel.SetBackgroundColour(PANEL_RGB)

        #Hardware Settings Panel
        wx.StaticText(hardwareSettingsPanel, -1, 'Camera Name', wx.Point(25, 20))
        wx.StaticText(hardwareSettingsPanel, -1, 'Display Hold', wx.Point(25, 60))
        wx.StaticText(hardwareSettingsPanel, -1, 'GPS Port', wx.Point(25, 100))
        wx.StaticText(hardwareSettingsPanel, -1, 'Sounder Port', wx.Point(25, 140))
        cameraNameTextCtrl = wx.TextCtrl(hardwareSettingsPanel, -1, '', wx.Point(25, 36), wx.Size(145, -1))
        self.displayHoldTextCtrl = wx.TextCtrl(hardwareSettingsPanel, -1, '5', wx.Point(25, 76), wx.Size(60, -1))
        self.displayHoldSlider = wx.Slider(hardwareSettingsPanel, DISPLAYHOLD_SLIDER, 5, 1, 10, wx.Point(85, 76), wx.Size(90, -1))
        
        gpsPortComboBox = wx.ComboBox(hardwareSettingsPanel, -1, '', wx.Point(25, 116), wx.Size(145, -1))
        sounderPortComboBox = wx.ComboBox(hardwareSettingsPanel, -1, '', wx.Point(25, 156), wx.Size(145, -1))
        
        #File Settings Panel
        wx.StaticText(fileSettingsPanel, -1, 'Base File Path', wx.Point(25, 20))
        wx.StaticText(fileSettingsPanel, -1, 'File Name Prefix', wx.Point(25, 60))
        wx.StaticText(fileSettingsPanel, -1, 'Files Per Folder', wx.Point(25, 100))
        wx.StaticText(fileSettingsPanel, -1, 'Image Type', wx.Point(25, 140))
        wx.StaticText(fileSettingsPanel, -1, 'Quality', wx.Point(25, 180))
        self.filePathTextCtrl = wx.TextCtrl(fileSettingsPanel, -1, '', wx.Point(25, 36), wx.Size(85, -1))     
        filePathButton = wx.Button(fileSettingsPanel, -1, 'Select', wx.Point(110, 36), wx.Size(60, 21))
        
        self.fileNamePrefixTextCtrl = wx.TextCtrl(fileSettingsPanel, -1, '', wx.Point(25, 76), wx.Size(145, -1))   
        self.Bind(wx.EVT_TEXT, self.SetFilePrefix, self.fileNamePrefixTextCtrl)
        
        self.filesPerFolderTextCtrl = wx.TextCtrl(fileSettingsPanel, -1, '500', wx.Point(25, 116), wx.Size(60, -1))
        self.filesPerFolderSlider = wx.Slider(fileSettingsPanel, FILESPERFOLDER_SLIDER, 500, 1, 1000, wx.Point(85, 116), wx.Size(90, -1))

        imageTypeChoices = ['.jpg']
        imageTypeComboBox = wx.ComboBox(fileSettingsPanel, -1, '', wx.Point(25, 156), wx.Size(145, -1), imageTypeChoices)
        
        self.qualityTextCtrl = wx.TextCtrl(fileSettingsPanel, -1, '50', wx.Point(25, 196), wx.Size(60, -1))
        self.qualitySlider = wx.Slider(fileSettingsPanel, QUALITY_SLIDER, 50, 1, 99, wx.Point(85, 196), wx.Size(90, -1))
       
        self.Bind(wx.EVT_SLIDER, self.OnSliders)
        self.Bind(wx.EVT_BUTTON, self.OnDirectory, filePathButton)

        #Run Panel
        startStopButton = wx.Button(runPanel, STARTSTOP_BUTTON, 'Start/Stop', wx.Point(0, 0), wx.Size(175, 25))

        #Run Info Panel
        runInfoTextCtrl = wx.TextCtrl(runInfoPanel, -1, '', wx.Point(2, 2), wx.Size(312, -1))

        #Create Status Bar
        wx.Frame.CreateStatusBar(self, 2)
        wx.Frame.SetStatusText(self, 'wxCamGui initialized.')        
        
    def SetFilePrefix(self, e):
        dlg = wx.FileDialog(
            self, defaultDir=os.getcwd(),
            defaultFile=self.fileNamePrefixTextCtrl,
             wildcard=images,
              style=wx.SAVE)
     
    def OnDirectory(self, e):
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
        pass #IMPLEMENTATION REQUIRED
    
    def OnQuit(self, e):
        self.Close()
        
    def OnAbout(self, e):
        pass #IMPLEMENTATION REQUIRED
    
    def OnSliders(self, e):
        self.pos1 = self.filesPerFolderSlider.GetValue()
        str1 = "%d" % (self.pos1)
        self.filesPerFolderTextCtrl.SetValue(str1)
        self.pos2 = self.qualitySlider.GetValue()
        str2 = "%d" % (self.pos2)
        self.qualityTextCtrl.SetValue(str2)
        self.pos3 = self.displayHoldSlider.GetValue()
        str3 = "%d" % (self.pos3)
        self.displayHoldTextCtrl.SetValue(str3)
    
    def OnSettings(self, e):
        SettingsFrame('Settings').Show()
    
    def _DeclareEventTable(self):
        pass #IMPLEMENTATION REQUIRED 

class SettingsFrame(wx.Frame):
    
    def __init__(self, title):
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title=title, size=SETTINGS_SIZE)
        
        settingsPanel = wx.Panel(self, size=wx.Size(0, 0), pos=wx.Point(500, 500))
        innerSettingsPanel = wx.Panel(settingsPanel, size=wx.Size(510, 340), pos=wx.Point(10, 10), style=wx.SUNKEN_BORDER)
        acceptSettingsPanel = wx.Panel(settingsPanel, size=wx.Size(200, 35), pos=wx.Point(320, 360), style=wx.SUNKEN_BORDER)
        settingsPanel.SetBackgroundColour(MAIN_PANEL_RGB)
        innerSettingsPanel.SetBackgroundColour(PANEL_RGB)
        acceptSettingsPanel.SetBackgroundColour(PANEL_RGB)
    
        wx.StaticText(innerSettingsPanel, -1, 'Frame Rate', wx.Point(25, 22))
        wx.StaticText(innerSettingsPanel, -1, 'Frame Start Trigger Mode', wx.Point(25, 52))
        wx.StaticText(innerSettingsPanel, -1, 'Exposure Mode', wx.Point(25, 82))
        wx.StaticText(innerSettingsPanel, -1, 'Exposure Value', wx.Point(25, 112))
        wx.StaticText(innerSettingsPanel, -1, 'Gain Mode', wx.Point(25, 142))
        wx.StaticText(innerSettingsPanel, -1, 'Gain Value', wx.Point(25, 172))
        wx.StaticText(innerSettingsPanel, -1, 'White Balance Mode', wx.Point(25, 202))
        wx.StaticText(innerSettingsPanel, -1, 'Pixel Format', wx.Point(25, 232))
        wx.StaticText(innerSettingsPanel, -1, 'Packet Size', wx.Point(25, 262))
    
        frameRateTextCtrl = wx.TextCtrl(innerSettingsPanel, -1, '', wx.Point(200, 20), wx.Size(200, -1))
        frameStartTriggerModeChoices = ['FreeRun', 'SyncIn1', 'SyncIn2', 'FixedRate', 'Software']
        #Size 5
        frameStartTriggerModeComboBox = wx.ComboBox(innerSettingsPanel, -1, '', wx.Point(200, 50), wx.Size(200, -1), frameStartTriggerModeChoices)
    
        exposureModeChoices = ['Manual', 'Auto', 'AutoOnce', 'External']
        #Size 4
        exposureModeComboBox = wx.ComboBox(innerSettingsPanel, -1, '', wx.Point(200, 80), wx.Size(200, -1), exposureModeChoices)
        exposureValueTextCtrl = wx.TextCtrl(innerSettingsPanel, -1, '', wx.Point(200, 110), wx.Size(200, -1))
    
        gainModeChoices = ['Manual', 'Auto', 'AutoOnce']
        #Size 3
        gainModeComboBox = wx.ComboBox(innerSettingsPanel, -1, '', wx.Point(200, 140), wx.Size(200, -1), gainModeChoices)
        gainValueTextCtrl = wx.TextCtrl(innerSettingsPanel, -1, '', wx.Point(200, 170), wx.Size(200, -1))
    
        whitebalModeChoices = ['Manual', 'Auto', 'AutoOnce']
        #Size 3
        whitebalModeComboBox = wx.ComboBox(innerSettingsPanel, -1, '', wx.Point(200, 200), wx.Size(200, 1), whitebalModeChoices)
    
        pixelFormatChoices = ['Mono8', 'Mono16', 'Bayer8', 'Bayer16', \
                              'Rgb24', 'Bgr24', 'Yuv411', 'Yuv422', \
                              'Yuv444', 'Rgba32', 'Bgra32', 'Rgb48', \
                              'Mono12Packed', 'Bayer12Packed']
        #Size 14
        pixelFormatComboBox = wx.ComboBox(innerSettingsPanel, -1, '', wx.Point(200, 230), wx.Size(200, -1), pixelFormatChoices)
        packetSizeTextCtrl = wx.TextCtrl(innerSettingsPanel, -1, '', wx.Point(200, 260), wx.Size(200, -1))
        
        acceptSettingsButton = wx.Button(acceptSettingsPanel, SETTINGS_ACCEPT, 'Accept', wx.Point(0, 0), wx.Size(99, 33))            
        cancelSettingsButton = wx.Button(acceptSettingsPanel, SETTINGS_CANCEL, 'Cancel', wx.Point(99, 0), wx.Size(99, 33))
        self.Bind(wx.EVT_MENU, self.OnAcceptSettings, acceptSettingsButton)
        self.Bind(wx.EVT_MENU, self.OnCancelSettings, cancelSettingsButton)
    
    def OnAcceptSettings(self, e):
        # forward the slider change events to the image window
        # note: self.images = NAME_OF_IMAGE_CLASS
        frameRateTextCtrl
        frameStartTriggerModeComboBox
        exposureModeComboBox
        exposureValueTextCtrl
        gainModeComboBox
        gainValueTextCtrl
        whitebalModeComboBox
        pixelFormatComboBox
        packetSizeTextCtrl.Bind(wx.EVT_TEXT, self.images.OnScrollRed)
    
    def OnCancelSettings(self, e):
        pass #IMPLEMENTATION REQUIRED
    
    def _DeclareEventTable(self):
        pass #IMPLEMENTATION REQUIRED
    
    def OnQuit(self, e):
        self.Close()

def WaitForCamera():
    print 'Waiting for a camera'
    while not p.cameraCount():
        print '.'
        time.sleep(2.5)
    print '\n'

if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()
