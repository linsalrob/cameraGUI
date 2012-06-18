# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 15:17:31 2011

True Camera API that binds to the underlying DLL PvAPI.dll
This is the result of a lot of blood, sweat, and pain.

Not all functions are implemented, but example in example.py 
demonstrates successful initialization of the camera, captures a frame,
and then shuts down the driver engine.

@author: coryli

PLEASE SEE: https://bitbucket.org/Cixelyn/py-avt-pvapi/downloads

"""


from ctypes import *
from time import sleep
import logging
import sys


class CameraInfoEx(Structure):
    """Struct that holds information about the camera"""
    
    _fields_ = [
    ("StructVer", c_ulong),
    ("UniqueId", c_ulong),
    ("CameraName", c_char * 32),
    ("ModelName", c_char * 32),
    ("PartNumber", c_char * 32),
    ("SerialNumber", c_char * 32),
    ("FirmwareVersion", c_char * 32),
    ("PermittedAccess", c_long),
    ("InterfaceId", c_ulong),
    ("InterfaceType", c_int)
    ]

class Frame(Structure):
    """Struct that holds the frame and other relevant information"""

    
    _fields_ = [
    ("ImageBuffer", POINTER(c_char)),
    ("ImageBufferSize", c_ulong),
    ("AncillaryBuffer", c_void_p),
    ("AncillaryBufferSize", c_ulong),
    ("Context", c_void_p * 4),
    ("_reserved1", c_ulong * 8),

    ("Status", c_int),
    ("ImageSize", c_ulong),
    ("AncillarySize", c_ulong),
   
    ("Width", c_ulong),
    ("Height", c_ulong),
    
    ("RegionX", c_ulong),
    ("RegionY", c_ulong),
    
    ("Format", c_uint),
    
    ("BitDepth", c_ulong),
    ("BayerPattern", c_int),
    
    ("FrameCount", c_ulong),
    ("TimestampLo", c_ulong),
    ("TimestampHi", c_ulong),
    ("_reserved2", c_ulong * 32)    
    ]
    
    def __init__(self, size):
        self.ImageBuffer = create_string_buffer(size)
        self.ImageBufferSize = size
        self.AncillaryBuffer = 0
        self.AncillaryBufferSize = 0



class CameraDriver:
    """The main class that drives the camera"""

    def __init__(self):
        self.imageSize = 0
        #self.dll = windll.LoadLibrary("PvAPI.dll")
        ## the cdll is the mac version of windll
        
        ## the 32-bit version of the API
        #self.dll = cdll.LoadLibrary("/Users/redwards/Desktop/AVT_GigE_SDK/bin-pc/x86/libPvAPI.dylib")
        
        ## the 64 bit version of the API(prefered)
        #/Users/redwards/Desktop/AVT_GigE_SDK/bin-pc/x64/libPvAPI.dylib
        self.dll = cdll.LoadLibrary("C:/Users/Owner/Desktop/py-avt-pvapi2/py-avt-pvapi2/PvAPI/Windows/x86/PvAPI.dll")
        
    def getImageSize(self):
        return self.imageSize;

    def version(self):
        """Returns a tuple of the driver version"""
        pMajor = c_int()
        pMinor = c_int()
        self.dll.PvVersion(byref(pMajor), byref(pMinor))
        return (pMajor.value, pMinor.value)
        
    def initialize(self):
        """Initializes the camera.  Call this first before anything"""
        logging.info("Driver Loaded")
        result = self.dll.PvInitialize()
        sleep(1)
        return result
    
    def cameraCount(self):
        """Returns the number of attached cameras"""
        return self.dll.PvCameraCount()

    def uninitialize(self):
        """Uninitializes the camera interface"""
        logging.info("Driver Unloaded")
        result = self.dll.PvUnInitialize()
        return result
    
    def cameraOpen(self, uniqueId):
        """Opens a particular camera. Returns the camera's handle"""
        logging.info("Opening Camera")
        camera = c_ulong()
        res = self.dll.PvCameraOpen(uniqueId, 4, byref(camera))
        if (res != 0):
            sys.stderr.write("There was an error opening the camera.\n")
            sys.stderr.write("The response from the camera was " + str(res) + "\n")
            sys.stderr.write("Please check PvAPI.h to figure out what that should be\n")
            sys.exit(0)
        
        # figure out how big the image should be 
        self.imageSize = self.attrUint32Get(camera, "TotalBytesPerFrame")
        
        return camera
    
    def cameraClose(self, camera):
        """Closes a camera given a handle"""
        logging.info("Closing Camera")
        self.dll.PvCameraClose(camera)


    def cameraList(self):
        """Returns a list of all attached cameras as CameraInfoEx"""
        var = (CameraInfoEx * 10)()
        self.dll.PvCameraListEx(byref(var), 1, None, sizeof(CameraInfoEx))
        return var
        
    def captureStart(self, handle):
        """Begins Camera Capture"""
        return self.dll.PvCaptureStart(handle)
    
    def captureEnd(self, handle):
        """Ends Camera Capture"""
        return self.dll.PvCaptureEnd(handle)
        
    def captureFrame(self, handle):
        """Function that loads up a frame buffer,
        then waits for said frame buffer to be filled"""
        
        sys.stderr.write("Creating frame of size " + str(self.imageSize) + "\n")
        frame = Frame(self.imageSize)
        res = self.dll.PvCaptureQueueFrame(handle, byref(frame), None)
        if (res != 0):
            sys.stderr.write("There was an error setting the frame " + str(res))
            sys.exit()
        
        res = self.dll.PvCaptureWaitForFrameDone(handle, byref(frame), 600000)
        if (res != 0):
            sys.stderr.write("There was an error getting the frame " + str(res))
            sys.exit()
             
        return frame
    
    def attrEnumSet(self, handle, param, value):
        """Set a particular enum attribute given a param and value."""
        return self.dll.PvAttrEnumSet(handle, param, value)
        
    def commandRun(self, handle, command):
        """Runs a particular command valid in the Camera and Drive Attributes"""
        return self.dll.PvCommandRun(handle, command)
    
    def attrList(self, handle):
        """
        Gets a list of attributes form the camera.
        This does not work at the moment, as I need to figure out
        how to pass in a mutable array and get the result back.
        
        """
        
        sys.stderr.write("This function does not work yet!!")
        exit(0)
        
        listPtr = create_string_buffer(30)
        listLength = c_uint()

        res = self.dll.PvAttrList(handle, byref(listPtr), byref(listLength));
        print("Result was " + str(res))
        if (self.dll.PvAttrList(handle, byref(listPtr), byref(listLength)) == 0):
            print("The list has " + str(listLength.value) + " elements")
            #for j in range(listLength.value-1):
                #print(" j : " + listPtr[j])
        else:
            print("Error getting the list")
        
        
        
    def attrUint32Get(self, handle, name):
        """Returns a particular integer attribute"""
        val = c_uint()
        self.dll.PvAttrUint32Get(handle, name, byref(val))
        return val.value
        
        


