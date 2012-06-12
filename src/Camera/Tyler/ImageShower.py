import wx
import os
import time
import random
import copy
from threading import Thread    

class ImageViewPanel(wx.Panel):
    def __init__(self, parent, drop):
        self.queueSize = 20
        
        wx.Panel.__init__(self, parent, pos = wx.Point(0, 0), size = wx.Size(1200,600))
        largePanel = ImageViewport(self, wx.Point(50,50), wx.Size(300,300))
        largePanel.isMain = True
        smallPanel1 = ImageViewport(self, wx.Point(375,50), wx.Size(75,75))
        smallPanel2 = ImageViewport(self, wx.Point(375,150), wx.Size(75,75))
        smallPanel3 = ImageViewport(self, wx.Point(375,250), wx.Size(75,75))
        
        nextButton = wx.Button(self, -1, 'NEXT', wx.Point(175,400), wx.Size(100,25))
        prevButton = wx.Button(self, -1, 'PREV', wx.Point(50,400), wx.Size(100,25))
        contButton = wx.Button(self, -1, 'CONTINUE', wx.Point(50,450), wx.Size(100,25))
        zoomInButton = wx.Button(self, -1, 'ZOOM IN', wx.Point(50,500), wx.Size(100,25))
        zoomOutButton = wx.Button(self, -1, 'ZOOM OUT', wx.Point(175,500), wx.Size(100,25))
        
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ScrollNext, nextButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ScrollPrev, prevButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ContinueScroll, contButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ZoomIn, zoomInButton)
        wx.EvtHandler.Bind(self, wx.EVT_BUTTON, self.ZoomOut, zoomOutButton)
        
        self.isScrolling = True
        
        self.viewports = [largePanel, smallPanel1, smallPanel2, smallPanel3]
        self.imageQueue = []
        self.blankBitmap = wx.Bitmap('test1.jpg', wx.BITMAP_TYPE_JPEG)
        for i in range(self.queueSize):
            self.imageQueue.append(self.blankBitmap)
        img1 = wx.Bitmap('smile.jpg', wx.BITMAP_TYPE_JPEG)
        img2 = wx.Bitmap('test2.jpg', wx.BITMAP_TYPE_JPEG)
        img3 = wx.Bitmap('test3.jpg', wx.BITMAP_TYPE_JPEG)
        img4 = wx.Bitmap('test4.jpg', wx.BITMAP_TYPE_JPEG)
        self.imageQueue[3] = (copy.copy(img1))
        self.imageQueue[2] = (copy.copy(img2))
        self.imageQueue[1] = (copy.copy(img3))
        self.imageQueue[0] = (copy.copy(img4))
        self.queuePos = 3
        self.currentQueue = 3
        largePanel.SetImage(img1)
        smallPanel1.SetImage(img2)
        smallPanel2.SetImage(img3)
        smallPanel3.SetImage(img4)

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
        ImageViewport(self, wx.Point(0,0), wx.Size(1200,600))
        wx.EVT_PAINT(self, self.OnPaint)

    def ZoomIn(self, e):
        self.isScrolling = False
        self.viewports[0].ZoomIn(copy.copy(self.imageQueue[self.currentQueue]))
        ImageViewport(self, wx.Point(0,0), wx.Size(1200,600))
        wx.EVT_PAINT(self, self.OnPaint)

    def ZoomOut(self, e):
        self.isScrolling = False
        self.viewports[0].ZoomOut(copy.copy(self.imageQueue[self.currentQueue]))
        ImageViewport(self, wx.Point(0,0), wx.Size(1200,600))
        wx.EVT_PAINT(self, self.OnPaint)

    def Update(self):
        if self.isScrolling:
            if time.clock() >= self.nextImage:
                self.nextImage += self.drop.DelayBetweenImageDisplays
                #This parameter needs cleaned up on integration!
                self.RotateImages(None)

    def ScrollNext(self, e):
        if self.currentQueue != self.queuePos:
            self.currentQueue = self.QueueNext(self.currentQueue)
            self.SetImagesOnQueue()
            self.isScrolling = False

    def ScrollPrev(self, e):
        if self.currentQueue != (self.QueueNext(self.queuePos)):
            self.currentQueue = self.QueuePrev(self.currentQueue)
            self.SetImagesOnQueue()
            self.isScrolling = False

    def ContinueScroll(self, e):
        self.isScrolling = True
        self.nextImage = time.clock() + self.drop.DelayBetweenImageDisplays
        self.currentQueue = copy.copy(self.queuePos)
        self.SetImagesOnQueue()

    #This method should probably be eliminated on integration
    def ShowImages(self):
        for x in self.viewports:
            x.ShowImage()

    def OnPaint(self,e):
        dc = wx.PaintDC(self)
        for x in self.viewports:
            x.Paint(dc)
    
    def RotateImages(self, e):
        for i in range(4)[:0:-1]:
            self.viewports[i].SetImage(self.viewports[i-1].img)
        img = wx.Bitmap(self.drop.NextFileToLoad, wx.BITMAP_TYPE_JPEG)
        self.queuePos = self.QueueNext(self.queuePos)
        self.currentQueue = copy.copy(self.queuePos)
        self.imageQueue[self.queuePos] = copy.copy(img)
        self.viewports[0].SetImage(img)
        #This panel is written in order to invalidate the images below it. This solution is not clean,
        #so we should keep our eyes out for another solution.
        ImageViewport(self, wx.Point(0,0), wx.Size(1200,600))
        wx.EVT_PAINT(self, self.OnPaint)

    def SetImagesOnQueue(self):
        images = []
        i = copy.copy(self.currentQueue)
        fillBlanks = False
        #Get Images
        for x in range(4):
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
        for x in range(4):
            self.viewports[x].SetImage(images[x])
        ImageViewport(self, wx.Point(0,0), wx.Size(1200,600))
        wx.EVT_PAINT(self, self.OnPaint)
        

class ImageViewport(wx.Panel):
    def __init__(self, parent, pos, size):
        wx.Panel.__init__(self, parent, pos = pos, size = size)
        self.x = pos.Get()[0]
        self.y = pos.Get()[1]
        self.width = size.Get()[0]
        self.height = size.Get()[1]
        self.scale = 1
        self.displayX = 0
        self.displayY = 0
        self.hasMoved = False
        self.isMain = False
        self.leftIsDown = False
        
        wx.EvtHandler.Bind(self, wx.EVT_LEFT_DOWN, self.LeftDown, self)
        wx.EvtHandler.Bind(self, wx.EVT_LEFT_UP, self.LeftUp, self)

    def LeftDown(self, e):
        if self.isMain:
            x = e.GetPosition()[0]
            y = e.GetPosition()[1]
            x = x - (self.width/2)
            y = y - (self.width/2)
            self.TransposeImage(wx.Window.GetParent(self).imageQueue[wx.Window.GetParent(self).currentQueue], x, y)
            wx.Window.GetParent(self).DoPaint()
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
            self.CompleteZoom(temp, retainCenter = True, zoomingIn = True)
        else:
            self.CompleteZoom(temp)

    def ZoomOut(self, image):
        if self.scale > 1:
            self.scale -= 0.2
            temp = image.ConvertToImage()
            if self.hasMoved:
                self.CompleteZoom(temp, retainCenter = True, zoomingIn = False)
            else:
                self.CompleteZoom(temp)

    def TransposeImage(self, image, x, y):
        temp = image.ConvertToImage()
        self.CompleteZoom(temp, x, y)
        self.hasMoved = True

    def CompleteZoom(self, temp, xDelta = -1, yDelta = -1, retainCenter = False, zoomingIn = False):
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

    def Paint(self, dc):
        dc.DrawBitmap(self.img, 0, 0)

class MouseState:
    pass

class TestApp(wx.App):        
    def OnInit(self):
        self.keepGoing = True
        return True

    def MainLoop(self):

        self.filenames = ['smile.jpg','test2.jpg','test3.jpg','test4.jpg']
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

            # This outer loop determines when to exit the application,
            # for this example we let the main frame reset this flag
            # when it closes.
            while self.keepGoing:
                # At this point in the outer loop you could do
                # whatever you implemented your own MainLoop for.  It
                # should be quick and non-blocking, otherwise your GUI
                # will freeze.

                if time.clock() >= self.nextimage:
                    self.index += 1
                    if self.index > 3:
                        self.index = 0
                    drop.NextFileToLoad = self.filenames[self.index]
                    self.nextimage = time.clock() + random.randint(1,5)
                
                self.myframe.Update()
                
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

class Drop:
    pass

drop = Drop()
app = TestApp()
app.drop = drop
drop.DelayBetweenImageDisplays = 3
drop.NextFileToLoad = 'test1.jpg'
frame = wx.Frame(None, pos = wx.Point(0,0), size = wx.Size(1200,600))
panel = ImageViewPanel(frame, drop)
app.myframe = panel
frame.Show()
panel.ShowImages()
app.MainLoop()

