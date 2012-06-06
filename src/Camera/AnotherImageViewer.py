'''
Created on Jun 4, 2012

@author: redwards
'''
import wx

def scale_bitmap(bitmap, scale):
    image = wx.ImageFromBitmap(bitmap)
    w=image.GetWidth()
    h=image.GetHeight()
    w=w*scale
    h=h*scale
    image = image.Scale(w, h, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result


class Panel(wx.Panel):
    def __init__(self, parent, img):
        super(Panel, self).__init__(parent, -1)
        bitmap = scale_bitmap(img, 0.25)
        self.control = wx.StaticBitmap(self, -1, bitmap)
        self.control.SetPosition((10, 10))

class ImageViewer(object):
    def __init__(self, app):
        #self.app = wx.App()
        self.app = app
        self.frame = wx.Frame(None, -1, 'Prosilica Camera View', size=(350,400))
        
    def showImg(self, img):
        self.panel = Panel(self.frame, img)
        self.frame.Show()
        
        self.app.MainLoop()

    def nextImage(self, img):
        bitmap = scale_bitmap(img, 0.25)
        self.control.SetImage(bitmap)
        self.control.Refresh()
        
    def OnClick(self,event):
        self.panel.Refresh()
 