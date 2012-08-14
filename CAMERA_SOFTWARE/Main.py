import os, sys
sys.path.append("./Imports") 
import sys
import threading
import GuiApplication
import MainFrame
import DropBox
import pvcam

drop = DropBox.DropBox()
app = GuiApplication.GuiApplication(drop, False)
cam = pvcam.PVCam(drop)

class CameraThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        cam.MainLoop()

class GUIThread(threading.Thread):
    def __init(self):
        threading.Thread.__init__(self)

    def run(self):
        app.mainFrame.Show()
        app.MainLoop()

os.chdir(os.getcwd())

thread1 = GUIThread()
thread2 = CameraThread()
thread2.start()
thread1.run()
