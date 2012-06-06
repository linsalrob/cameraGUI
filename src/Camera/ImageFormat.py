'''
Created on Jun 4, 2012

@author: redwards

Take an image and get its format. Perhaps saving the string

'''


from pvAPI import *
from ctypes import *

class ImageFormat(object):
    c = CameraDriver()
    c.initialize()
    uid = c.cameraList()[0].UniqueId
    
    # is the camera connected. If not, we should die!
    print("The camera id is " + str(uid))
    
    # open the camera
    cam = c_ulong()
    cam = c.cameraOpen(uid)
    
    res = c.captureStart(cam)
    if (res == 0):
        sys.stderr.write("Image capture started\n")
    else:
        sys.stderr.write("There was an error starting the stream: " + str(res) + "\n")
        exit(0)
    
    
    res = c.attrEnumSet(cam,"FrameStartTriggerMode","Freerun")
    if (res == 0):
        sys.stderr.write("Started free run mode\n")
    else:
        sys.stderr.write("There was an error setting the trigger mode as free run" + str(res) + "\n")
    
    res = c.attrEnumSet(cam,"AcquisitionMode","Continuous")
    if (res == 0):
        sys.stderr.write("Started continuous acquisition\n")
    else:
        sys.stderr.write("There was an error setting the acquisition mode as continuous" + str(res) + "\n")
    
    
    res = c.commandRun(cam,"AcquisitionStart")
    if (res == 0):
        sys.stderr.write("Started acquiring frames\n")
    else:
        sys.stderr.write("There was an error starting the acquisition" + str(res) + "\n")
    
    for i in range(5):
        frame = c.captureFrame(cam)
        print "Status\t" + str(frame.Status)
        print "Format\t " + str(frame.Format)
        print "ImageSize\t " + str(frame.ImageSize)
    print "\n\n"
    print "AncillarySize\t " + str(frame.AncillarySize)
    print "Width\t " + str(frame.Width)
    print "Height\t " + str(frame.Height)
    print "RegionX\t " + str(frame.RegionX)
    print "RegionY\t " + str(frame.RegionY)
    print "Format\t " + str(frame.Format)
    print "BitDepth\t " + str(frame.BitDepth)
    print "BayerPattern\t " + str(frame.BayerPattern)
    print "FrameCount\t " + str(frame.FrameCount)
    print "TimestampLo\t " + str(frame.TimestampLo)
    print "TimestampHi\t " + str(frame.TimestampHi)
    print "_reserved2\t " + str(frame._reserved2) + "\n"
    print "Buffer " + repr(frame.ImageBuffer) + "\n\n"
    
    res = c.commandRun(cam,"AcquisitionStop")
    c.cameraClose(cam)
    c.uninitialize()
    
    
    
    
