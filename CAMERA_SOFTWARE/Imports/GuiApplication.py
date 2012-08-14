import wx
import time
import MainFrame

class GuiApplication(wx.App):
    def __init__(self, drop, redirect = False):
        self.drop = drop
        wx.App.__init__(self, redirect)
        
    def OnInit(self):
        self.keepGoing = True
        #Initilize GUI
        self.mainFrame = MainFrame.MainFrame(self.drop, self, 'Camera GUI')
        self.settingsFrame = MainFrame.SettingsFrame('Settings', self.drop)
        self.imagePort = self.mainFrame.GetImagePanel()
        return True

    def ShowSelf(self):
        self.mainFrame.Show()

    def MainLoop(self):
        
        if "wxMac" in wx.PlatformInfo:
            # TODO:  Does wxMac implement wxEventLoop yet???
            wx.App.MainLoop()

        else:
            # Create an event loop and make it active.  If you are
            # only going to temporarily have a nested event loop then
            # you should get a reference to the old one and set it as
            # the active event loop when you are done with this one...
            evtloop = wx.EventLoop()
            old = wx.EventLoop.GetActive()
            wx.EventLoop.SetActive(evtloop)

            # This outer loop determines when to exit the application,
            # for this example we let the main frame reset this flag
            # when it closes.
            while self.keepGoing:
                # At this point in the outer loop you could do
                # whatever you implemented your own MainLoop for.  It
                # should be quick and non-blocking, otherwise your GUI
                # will freeze.
                if self.mainFrame:
                    self.mainFrame.Update()
                if self.imagePort:
                    self.imagePort.Update()
                else:
                    self.keepGoing = False
                
                # This inner loop will process any GUI events
                # until there are no more waiting.
                while evtloop.Pending():
                    evtloop.Dispatch()

                # Send idle events to idle handlers.  You may want to
                # throttle this back a bit somehow so there is not too
                # much CPU time spent in the idle handlers.  For this
                # example, I'll just snooze a little...
                time.sleep(0.10)
                self.ProcessIdle()

            wx.EventLoop.SetActive(old)


