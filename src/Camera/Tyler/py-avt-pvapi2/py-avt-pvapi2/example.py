import sys
import wx
sys.path.append("C:\\openCV2.3\\build\\Python\\2.7\\Lib\\site-packages")

import os
import pvapi as p
from time import sleep


# Initialize the driver
driver = p.PvAPI()

# Wait for cameras
print 'Waiting for cameras...'
while not driver.cameraCount():
    sleep(1)

# Open the first camera in the list
camera = p.Camera(driver, driver.cameraList()[0])
print 'Showing ' + camera.name + ' (' + str(camera.uid) + ').'

#camera.attrEnumSet('PixelFormat', 'Bayer8')
camera.attrEnumSet('PixelFormat', 'Rgb24')

# Set the exposure time to ~ 10ms
#camera.attrUint32Set('ExposureValue', 10000)



#while True:
image = camera.capture()
     #cv2.imshow('Camera', image)
#misc.imsave('outfile.jpg', image)
     #cv2.waitKey(1)
     
        
camera.close()

