from __future__ import division
import wx
import os
import sys
import time
import random
import copy
import array
import DropBox
import pvapi as p
from time import sleep
import cStringIO

MAIN_PANEL_RGB = wx.Colour(150,150,150)
PANEL_RGB = wx.Colour(200,200,200)
VIEW_PANEL_SIZE = wx.Size(750, 540)
INCOMING_IMAGE_RESOLUTION = wx.Size(1360, 1024)

driver = p.PvAPI()

class ImageViewPanel(wx.Panel):
    def __init__(self, parent, drop):
        self.queueSize = 20
        
        wx.Panel.__init__(self, parent, pos = wx.Point(0, 0), size = VIEW_PANEL_SIZE)
        self.SetBackgroundColour(MAIN_PANEL_RGB)
        largePanel = ImageViewport(self, wx.Point(10,10), wx.Size(550,414), 0, style=wx.SUNKEN_BORDER)
        largePanel.isMain = True
        smallPanel1 = ImageViewport(self, wx.Point(570,10), wx.Size(150,112), 1, style=wx.SUNKEN_BORDER)
        smallPanel2 = ImageViewport(self, wx.Point(570,132), wx.Size(150,112), 2, style=wx.SUNKEN_BORDER)
        smallPanel3 = ImageViewport(self, wx.Point(570,254), wx.Size(150,112), 3, style=wx.SUNKEN_BORDER)
        smallPanel4 = ImageViewport(self, wx.Point(570,376), wx.Size(150,112), 4, style=wx.SUNKEN_BORDER)
        
        nextButton = wx.Button(self, -1, 'NEXT', wx.Point(130,435), wx.Size(50,50))
        prevButton = wx.Button(self, -1, 'PREV', wx.Point(10,435), wx.Size(50,50))
        contButton = wx.Button(self, -1, 'CONTINUE', wx.Point(70,435), wx.Size(50,50))
        zoomInButton = wx.Button(self, -1, 'ZOOM IN', wx.Point(450,435), wx.Size(50,50))
        zoomOutButton = wx.Button(self, -1, 'ZOOM OUT', wx.Point(510,435), wx.Size(50,50))
        
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ScrollNext, nextButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ScrollPrev, prevButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ContinueScroll, contButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ZoomIn, zoomInButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ZoomOut, zoomOutButton)
        
        self.isScrolling = True
        self.isLiveFeed = True
        self.firstCachedImage = 1
        
        self.viewports = [largePanel, smallPanel1, smallPanel2, smallPanel3, smallPanel4]
        self.imageQueue = []
        self.blankBitmap = wx.Bitmap('blank.jpg', wx.BITMAP_TYPE_JPEG)
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
        self.nextImage = time.clock() + drop.DelayBetweenImageDisplays

    def QueueNext(self, i):
        if i == (self.queueSize - 1):
            return 0
        else:
            return (i + 1)

    def QueuePrev(self, i):
        if i == 0:
            return (self.queueSize - 1)
        else:
            return (i - 1)

    def DoPaint(self):
        self.Refresh(True)
        wx.EVT_PAINT(self, self.OnPaint)

    def ZoomIn(self, e):
        self.isScrolling = False
        self.viewports[0].ZoomIn(copy.copy(self.imageQueue[self.currentQueue]))
        self.Refresh(True)
        wx.EVT_PAINT(self, self.OnPaint)

    def ZoomOut(self, e):
        self.isScrolling = False
        self.viewports[0].ZoomOut(copy.copy(self.imageQueue[self.currentQueue]))
        self.Refresh(True)
        wx.EVT_PAINT(self, self.OnPaint)
        

    def Update(self):
        if self.isScrolling:
            img = None
            if self.isLiveFeed: #If live feed is running, get it and store it
                img = drop.firstFeed
                self.imageQueue[self.queuePos] = copy.copy(img)
                self.viewports[0].SetImage(img)
            if time.clock() >= self.nextImage:
                self.nextImage += self.drop.DelayBetweenImageDisplays
                if self.isLiveFeed:
                    self.RotateImages(1, None)
                else:
                    self.RotateImages(0, None)
        self.Refresh(True)
        wx.EVT_PAINT(self, self.OnPaint)

    def ScrollNext(self, e):
        if self.currentQueue != self.queuePos:
            self.currentQueue = self.QueueNext(self.currentQueue)
            self.SetImagesOnQueue()
            self.isScrolling = False
            self.isLiveFeed = False

    def ScrollPrev(self, e):
        if self.currentQueue != (self.QueueNext(self.queuePos)):
            self.currentQueue = self.QueuePrev(self.currentQueue)
            self.SetImagesOnQueue()
            self.isScrolling = False
            self.isLiveFeed = False

    def ContinueScroll(self, e):
        self.isScrolling = True
        self.isLiveFeed = True
        self.nextImage = time.clock() + self.drop.DelayBetweenImageDisplays
        self.currentQueue = copy.copy(self.queuePos)
        self.SetImagesOnQueue()

    #This method should probably be eliminated on integration
    def ShowImages(self):
        for x in self.viewports:
            x.ShowImage()

    def OnPaint(self,e):
        dc = wx.PaintDC(self)
    
    def RotateImages(self, x, e):
        for i in range(5)[:x:-1]:
            self.viewports[i].SetImage(self.viewports[i-1].img)
        img = wx.Bitmap(self.drop.NextFileToLoad, wx.BITMAP_TYPE_JPEG)
        self.queuePos = self.QueueNext(self.queuePos)
        self.currentQueue = copy.copy(self.queuePos)
        todelete = self.imageQueue[self.QueuePrev(self.queuePos)]
        self.imageQueue[self.QueuePrev(self.queuePos)] = copy.copy(img)
        self.viewports[x].SetImage(img)
        self.Refresh(True)
        wx.EVT_PAINT(self, self.OnPaint)

    def SetImagesOnQueue(self):
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
    def __init__(self, parent, pos, size, ident, style = 0):
        wx.Panel.__init__(self, parent, pos = pos, size = size, style=style)
        self.SetBackgroundColour(PANEL_RGB)
        self.x = pos.Get()[0]
        self.y = pos.Get()[1]
        self.width = size.Get()[0] - 5
        self.height = size.Get()[1] - 5
        self.scale = 1
        self.displayX = 0
        self.displayY = 0
        self.hasMoved = False
        self.isMain = False
        self.leftIsDown = False
        self.id = ident
        
        wx.EvtHandler.Bind(self, wx.EVT_LEFT_DOWN, self.LeftDown, self)
        wx.EvtHandler.Bind(self, wx.EVT_LEFT_UP, self.LeftUp, self)
        wx.EvtHandler.Bind(self, wx.EVT_ERASE_BACKGROUND, self.EraseBackground)

    def LeftDown(self, e):
        parent = wx.Window.GetParent(self)
        if self.isMain:
            x = e.GetPosition()[0]
            y = e.GetPosition()[1]
            x = x - (self.width/2)
            y = y - (self.width/2)
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
        if self.isMain:
            leftIsDown = False

    def SetImage(self, image):
        temp = image.ConvertToImage()        
        temp.Rescale(self.width, self.height)
        self.img = wx.BitmapFromImage(temp)
        self.scale = 1
        self.hasMoved = False

    def ZoomIn(self, image):
        self.scale += 0.2
        temp = image.ConvertToImage()
        #If the image has been previously moved, retain the center
        #NOTE: Currently retains top left, need to modify to retain center
        if self.hasMoved:
            self.CompleteZoom(image, temp, retainCenter = True, zoomingIn = True)
        else:
            self.CompleteZoom(image, temp)

    def ZoomOut(self, image):
        if self.scale > 1:
            self.scale -= 0.2
            temp = image.ConvertToImage()
            if self.hasMoved:
                self.CompleteZoom(image, temp, retainCenter = True, zoomingIn = False)
            else:
                self.CompleteZoom(image, temp)

    def TransposeImage(self, image, x, y):
        temp = image.ConvertToImage()
        self.CompleteZoom(image, temp, x, y)
        self.hasMoved = True

    def CompleteZoom(self, image, temp, xDelta = -1, yDelta = -1, retainCenter = False, zoomingIn = False):
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
                    oldWidth = self.width * (self.scale-0.2)
                    oldHeight = self.height * (self.scale-0.2)
                else:
                    oldWidth = self.width * (self.scale+0.2)
                    oldHeight = self.height * (self.scale+0.2)
                xDelta = (imgwidth-oldWidth)/2
                yDelta = (imgheight-oldHeight)/2
            
            #Set deltas
            if xDelta == -1:
                self.displayX = (imgwidth-self.width)/2
            else:
                self.displayX += xDelta
            if yDelta == -1:
                self.displayY = (imgheight-self.height)/2
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

class MouseState:
    pass

class TestApp(wx.App):        
    def OnInit(self):
        self.keepGoing = True
        
        self.camera = p.Camera(driver, driver.cameraList()[0])
        print 'Showing ' + self.camera.name + ' (' + str(self.camera.uid) + ').'
        self.camera.attrEnumSet('PixelFormat', 'Rgb24')

        
        return True

    def MainLoop(self):

        self.filenames = ['test1.jpg','test2.jpg','test3.jpg','test4.jpg','test5.jpg']
        self.index = 0
        random.seed()
        self.nextimage = time.clock() + random.randint(1,5)
        
        if "wxMac" in wx.PlatformInfo:
            # TODO:  Does wxMac implement wxEventLoop yet???
            wx.App.MainLoop()

        else:
            # Create an event loop and make it active.  If you are
            # only going to temporarily have a nested event loop then
            # you should get a reference to the old one and set it as
            # the active event loop when you are done with this one...
            evtloop = wx.EventLoop()
            old = wx.EventLoop.GetActive()
            wx.EventLoop.SetActive(evtloop)

            oldtime = time.clock()
            counter = 0
            totaltime = 0
            
            # This outer loop determines when to exit the application,
            # for this example we let the main frame reset this flag
            # when it closes.
            while self.keepGoing:
                # At this point in the outer loop you could do
                # whatever you implemented your own MainLoop for.  It
                # should be quick and non-blocking, otherwise your GUI
                # will freeze.
                print time.clock() - oldtime
                oldtime = time.clock()
                
                image = self.camera.capture()
                image_width = self.camera.attrUint32Get('Width')
                image_height = self.camera.attrUint32Get('Height')
                wximage = wx.EmptyImage(image_width, image_height)
                wximage.SetData(image)
                bmp = wx.BitmapFromImage(wximage)
                drop.firstFeed = wx.EmptyBitmap(1360, 1024)
                
                if time.clock() >= self.nextimage:
                    self.index += 1
                    if self.index > 3:
                        self.index = 0
                    drop.NextFileToLoad = self.filenames[self.index]
                    #self.nextimage = time.clock() + random.randint(1,1)
                    self.nextimage = time.clock() + 0.75
                if self.myframe:
                    self.myframe.Update()
                else:
                    self.keepGoing = False
                
                # This inner loop will process any GUI events
                # until there are no more waiting.
                while evtloop.Pending():
                    evtloop.Dispatch()

                # Send idle events to idle handlers.  You may want to
                # throttle this back a bit somehow so there is not too
                # much CPU time spent in the idle handlers.  For this
                # example, I'll just snooze a little...
                time.sleep(0.10)
                self.ProcessIdle()

            wx.EventLoop.SetActive(old)


print 'Waiting for cameras...'
while not driver.cameraCount():
    sleep(1)

drop = DropBox.DropBox('test1.jpg')
app = TestApp(False)
frame = wx.Frame(None, pos = wx.Point(0,0), size = VIEW_PANEL_SIZE)
panel = ImageViewPanel(frame, drop)
app.myframe = panel
frame.Show()
panel.ShowImages()
app.MainLoop()
