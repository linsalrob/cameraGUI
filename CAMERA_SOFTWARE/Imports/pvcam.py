import sys
import os
import pvapi as p
import time
import datetime
import thread
from threading import Thread
import Image

class PVCam():   
    def __init__(self, drop):
        self.drop = drop
       
      
    def MainLoop(self):
        
        driver = p.PvAPI()
        # Wait for cameras
        while not driver.cameraCount():
            time.sleep(1)
        self.drop.isCameraAttached = True
        self.camera = p.Camera(driver, driver.cameraList()[0])

        self.drop.cameraName = self.camera.name
        fps = self.drop.frameRate
        self.drop.isCameraAttached = True

        self.save_default_values()
        self.set_drop_values()
        self.read_drop_values()
        image_str = None
        self.camera.captureStart()
        while True:
            
            if self.drop.running == False:
                self.drop.SetNextFile(None)
                fps = 1/float(self.drop.frameRate)
                filenum = 1
                foldernum = 0
                if not image_str == None:
                    image_str =None
                    self.set_drop_values()

            else:
                # Set camera values equal to the dropbox settings
                if image_str == None:
                    self.camera.captureEnd()
                    result = self.camera.attrEnumSet('ExposureMode', str(self.drop.exposureMode))
                    if result != 0:
                        print "Couldn't set exposure mode"
                        raise
                    result = self.camera.attrUint32Set('ExposureValue',self.drop.exposureValue)
                    if result != 0:
                        print "Couldn't set exposure value"
                        raise
                    result = self.camera.attrEnumSet('GainMode', str(self.drop.gainMode))
                    if result != 0:
                        print "Couldn't set gain mode"
                        raise
                    result = self.camera.attrUint32Set('GainValue',self.drop.gainValue)
                    if result != 0:
                        print "Couldn't set gain value"
                        raise
                    result = self.camera.attrEnumSet('WhitebalMode', str(self.drop.whitebalMode))
                    if result != 0:
                        print "Couldn't set white balance mode"
                        raise
                    self.camera.captureEnd()
                    result = self.camera.attrUint32Set('PacketSize', self.drop.packetSize)
                    if result != 0:
                        print "Couldn't set packet size"
                        raise
                    self.camera.captureStart()
                    
                

                start_time = time.time()
                # Capture the image data off the camera
                image_str = self.camera.capture()
                timestamp = datetime.datetime.now()
                gpsData = self.drop.gpsData
                depthData = self.drop.depthData

                if filenum ==1:
                    if not os.path.isdir(self.drop.path + '\\' + self.drop.prefix):
                        os.makedirs(self.drop.path + '\\' + self.drop.prefix)
                if filenum%self.drop.filesPerFolder == 1:
                    foldernum += 1
                    foldername = self.drop.prefix + '_' + format(foldernum, '04d')
                    if not os.path.isdir(self.drop.path + '\\' + self.drop.prefix + '\\' + foldername):
                        os.makedirs(self.drop.path + '\\' + self.drop.prefix + '\\' + foldername)       

                filename_img = self.drop.path+'\\'+self.drop.prefix+'\\'+foldername+'\\' +self.drop.prefix+'_'+format(filenum,'06d')+'.'+self.drop.filetype                
                filename_dat = self.drop.path+'\\'+self.drop.prefix+'\\'+foldername+'\\' +self.drop.prefix+'_'+format(filenum,'06d')+'.bin'
                try:
                    t1.join()
                    t2.join()
                except:
                    pass

                # Create a thread to save the image data and a thread to save the bin file
                t1 = Thread(target=self.save_image, args=(image_str,filename_img,self.drop.filetype,self.drop.quality,self.camera.height,self.camera.width,self.camera.channels)).start()         
                t2 = Thread(target=self.save_data, args=(timestamp,gpsData,depthData,filename_dat)).start()

                self.drop.currentFile = filename_img
                filenum += 1
                # Wait for enough to have elapsed to equal the frame rate
                if fps > (time.time() - start_time):
                    time.sleep(fps - (time.time() - start_time))
                
            if self.drop.close == True:
                break   
        self.camera.close()
        self.write_drop_values()



    def save_image(self,image_str,filename,filetype,qual,height,width,channels,*args):
        im = Image.fromstring('RGB',(width,height),image_str)
        if filetype == 'JPEG':
            im.save(filename,filetype,quality=qual)
        else:
            im.save(filename,filetype)
        self.drop.SetNextFile(filename)

    def save_data(self,t,data_gps,data_dep,filename,*args):
        FILE = open(filename,"w")
        FILE.write(data_gps)
        FILE.write(t.strftime('%I:%M:%S %p').lstrip('0') + data_dep)
        FILE.write(t.strftime('%d/%m/%Y').lstrip('0').ljust(256-len(data_gps)-len(t.strftime('%I:%M:%S %p'))-len(data_dep), '0'))
        FILE.close()

    def set_drop_values(self):
        self.drop.exposureMode = self.camera.attrEnumGet('ExposureMode')
        self.drop.exposureModeRange = self.camera.attrRangeEnum('ExposureMode')
        self.drop.exposureValue = self.camera.attrUint32Get('ExposureValue')
        self.drop.exposureValueRange = self.camera.attrRangeUint32('ExposureValue')
        self.drop.gainMode = self.camera.attrEnumGet('GainMode')
        self.drop.gainModeRange = self.camera.attrRangeEnum('GainMode')
        self.drop.gainValue = self.camera.attrUint32Get('GainValue')
        self.drop.gainValueRange = self.camera.attrRangeUint32('GainValue')
        self.drop.whitebalMode = self.camera.attrEnumGet('WhitebalMode')
        self.drop.whitebalModeRange = self.camera.attrRangeEnum('WhitebalMode')
        self.drop.packetSize = self.camera.attrUint32Get('PacketSize')
        self.drop.packetSizeRange = self.camera.attrRangeUint32('PacketSize')

    def save_default_values(self):
        self.drop.defaultexposureMode = self.camera.attrEnumGet('ExposureMode')
        self.drop.defaultexposureValue = self.camera.attrUint32Get('ExposureValue')
        self.drop.defaultgainMode = self.camera.attrEnumGet('GainMode')
        self.drop.defaultgainValue = self.camera.attrUint32Get('GainValue')
        self.drop.defaultwhitebalMode = self.camera.attrEnumGet('WhitebalMode')
        self.drop.defaultpacketSize = self.camera.attrUint32Get('PacketSize')

    def write_drop_values(self):
        FILE = open('settings.ini','w')
        FILE.write('ExposureMode='+self.drop.exposureMode+"\n")
        FILE.write('ExposureValue='+str(self.drop.exposureValue)+"\n")
        FILE.write('GainMode='+self.drop.gainMode+"\n")
        FILE.write('GainValue='+str(self.drop.gainValue)+"\n")
        FILE.write('WhitebalMode='+self.drop.whitebalMode+"\n")
        FILE.write('PacketSize='+str(self.drop.packetSize)+"\n")
        FILE.close()

    def read_drop_values(self):
        settings = {}
        if os.path.exists('settings.ini'):
            FILE = open('settings.ini','r')
            for line in FILE:
                settings[line.split('=')[0]] = line.split('=')[1].rstrip()
            self.drop.exposureMode = settings['ExposureMode']
            self.drop.exposureValue = int(settings['ExposureValue'])
            self.drop.gainMode = settings['GainMode']
            self.drop.gainValue = int(settings['GainValue'])
            self.drop.whitebalMode = settings['WhitebalMode']
            self.drop.packetSize = int(settings['PacketSize'])

