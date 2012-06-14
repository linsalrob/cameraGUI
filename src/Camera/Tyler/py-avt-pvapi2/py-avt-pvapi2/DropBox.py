#This class is intended to contain any data which must be passed between separate threads.
#Current design is basic and rough, let me know if you have any recommendations on improvement,
#   or better solutions.
#Right now, the DropBox pretty much consists of a set of default values.
import array
import wx

INCOMING_IMAGE_WIDTH = 1360
INCOMING_IMAGE_HEIGHT = 1024
INCOMING_BUFFER_SIZE = INCOMING_IMAGE_WIDTH * INCOMING_IMAGE_HEIGHT * 3

class DropBox:
    def __init__(self, f):
        self.DelayBetweenImageDisplays = 1
        self.NextFileToLoad = f
        self.useFirstFeed = True
        self.firstFeed = wx.EmptyImage
        self.secondFeed = wx.EmptyImage

    def GetNextFeed(self):
        if self.useFirstFeed:
            return self.secondFeed
        return self.firstFeed

    def CompleteFeedTransfer(self):
        self.useFirstFeed = not self.UseFirstFeed
    
    def GetLiveFeed(self):
        if self.useFirstFeed:
            return self.firstFeed
        return self.secondFeed
