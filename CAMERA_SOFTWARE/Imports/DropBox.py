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
    def __init__(self):
        self.imageDelay = 2
        self.nextFile1 = None
        self.nextFile2 = None
        self.useFirstFeed = True
        self.isReady = False
        self.running = False
        self.isCameraAttached = False

        self.cameraName = 'Waiting...'      
        self.frameRate = 10
        self.frameStartTriggerMode = 'Waiting...'
        self.exposureMode = 'Waiting...'
        self.exposureModeRange = 'Waiting...'
        self.exposureValue = 'Waiting'
        self.gainMode = 'Waiting...'
        self.gainValue = 0
        self.whitebalMode = 'Waiting...'
        self.pixelFormat = 'Waiting...'
        self.packetSize = 0
        self.close = False

        self.currentFile = ''

        self.error = None

    def SetNextFile(self, f):
        if f == None:
            self.isReady = False
        else:
            self.isReady = True
            if self.useFirstFeed:
                self.nextFile2 = f
                self.useFirstFeed = False
            else:
                self.nextFile1 = f
                self.useFirstFeed = True

    def GetNextFile(self):
        if self.isReady:
            if self.useFirstFeed:
                return self.nextFile1
            else:
                return self.nextFile2
        else:
            return None
