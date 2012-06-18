from __future__ import division
import os
import pvapi as p
import time
from time import sleep
import wx
import cStringIO

class Panel1(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        # Initialize the driver
        driver = p.PvAPI()

        # Wait for cameras
        print 'Waiting for cameras...'
        while not driver.cameraCount():
            sleep(1)

        # Open the first camera in the list
        camera = p.Camera(driver, driver.cameraList()[0])
        print 'Showing ' + camera.name + ' (' + str(camera.uid) + ').'
        camera.attrEnumSet('PixelFormat', 'Rgb24')

        begin = time.clock()
        image = camera.capture()
        print time.clock() - begin
        image_width = camera.attrUint32Get('Width')
        image_height = camera.attrUint32Get('Height')

        wximage = wx.EmptyImage(image_width, image_height)
        wximage.SetData(image)
        bmp = wx.BitmapFromImage(wximage)
        wx.StaticBitmap(self, -1, bmp, (5, 5))

        
        
        #while 1:
        #    image = camera.capture()
        #    wximage = wx.EmptyImage(image_width, image_height)
        #    wximage.SetData(image)
        #    bmp.SetBitmap(wximage)
        camera.close()

    def forever(self):
        oldtime = time.clock
        while True:
            print time.clock() - oldtime
            oldtime = time.clock()


            
            
app = wx.PySimpleApp()
frame1 = wx.Frame(None, -1, "An image on a panel", size = (800, 600))
Panel1(frame1,-1)
frame1.Show(1)
app.MainLoop()

