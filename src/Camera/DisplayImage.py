'''

Adapted from online sources, including http://www.blog.pythonlibrary.org/2010/03/26/creating-a-simple-photo-viewer-with-wxpython/

'''

import wx
 
class displayImage(wx.App):
    def __init__(self, redirect=False):
        wx.App.__init__(self, redirect)
        self.frame = wx.Frame(None, title='Prosilica Viewer', pos=(100,300), size=(1360,1024))
        self.panel = wx.Panel(self.frame)
        self.Image = wx.StaticBitmap(self.frame, bitmap=wx.EmptyBitmap(1360,1024))
        #self.panel.Layout()
        self.frame.Show()

    def showImage(self, bmpImg):
        h=bmpImg.GetHeight()
        w=bmpImg.GetWidth()
        print "Image is " + str(h) + " x " + str(w)
        self.Image.SetBitmap(bmpImg)
        self.Image.Refresh()


    def OnClose(self, event):
        self.Destroy()
