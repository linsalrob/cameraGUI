'''
Created on Jun 4, 2012

@author: redwards
'''
import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, "Prosilica viewer", size = (1360, 1024))

    def showImage(self, img):
        self.bitmap = wx.Bitmap(img)
        wx.EVT_PAINT(self, self.OnPaint)

        self.Centre()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bitmap, 1360, 1024)

class ImageViewer(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True
