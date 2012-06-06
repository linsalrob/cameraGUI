'''
Created on Jun 3, 2012

@author: redwards
'''

from pvAPI import *
from ctypes import *
import Image
import StringIO
from pvCodes import *
import wx
from ImageConvert import PilImageToWxBitmap
from AnotherImageViewer import ImageViewer

class Camera(object):
    '''
    A module written by Rob to make it work
    '''

    c = CameraDriver()
    c.initialize()
    uid = c.cameraList()[0].UniqueId
 
    # is the camera connected. If not, we should die!
    print("The camera id is " + str(uid))

    # open the camera
    cam = c_ulong()
    cam = c.cameraOpen(uid)

    error=pvErrors();
    
    app = wx.App()
    iviewer=ImageViewer(app)
    
    # start the camera
    res = c.captureStart(cam)
    if (res == 0):
        sys.stderr.write("Image capture started\n")
    else:
        sys.stderr.write("There was an error starting the stream\n")
        error.printError(res)
        exit(0)
    
    
    res = c.attrEnumSet(cam,"FrameStartTriggerMode","Freerun")
    if (res == 0):
        sys.stderr.write("Starting trigger mode in free run\n")
    else:
        sys.stderr.write("There was an error setting the trigger mode as free run\n")
        error.printError(res)
    
    res = c.attrEnumSet(cam, "PixelFormat", "Rgb24")
    if (res == 0):
        sys.stderr.write("Set the image to rgb24\n")
    else:
        sys.stderr.write("There was an error setting the image mode to rgb24\n")
        error.printError(res)
        
    res = c.attrEnumSet(cam,"AcquisitionMode","Continuous")
    if (res == 0):
        sys.stderr.write("Acquiring images constantly\n")
    else:
        sys.stderr.write("There was an error setting the acquisition mode as continuous\n")
        error.printError(res)

    res = c.commandRun(cam,"AcquisitionStart")
    if (res == 0):
        sys.stderr.write("Collecting images\n")
    else:
        sys.stderr.write("There was an error starting the acquisition\n")
        error.printError(res)
    

    frame = c.captureFrame(cam)
    buffer = frame.ImageBuffer

    imagestr=""
    for i in range(c.getImageSize()):
        imagestr = imagestr + buffer[i]

    im = Image.fromstring('RGB', (frame.Width, frame.Height), imagestr, 'raw')
    #im.show()
    wxIm = PilImageToWxBitmap(im)
    iviewer.showImg(wxIm)

    
    res = c.commandRun(cam,"AcquisitionStop")
    if (res != 0):
        sys.stderr.write("There was an error stopping the acquisition\n")
        error.printError(res)

    c.cameraClose(cam)
    c.uninitialize()
