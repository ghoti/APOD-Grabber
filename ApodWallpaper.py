__author__ = 'ghoti'
#TODO (in order of importance)
#add linkback to apod
#add copyright info if present
#browse previous apod images
#save image locally
#cross platform?
import BeautifulSoup
import ctypes
import datetime
import tempfile
import urllib2
import wx

class Apod(wx.App):
    """
    initialize our app.  draw a fancy frame, make some buttons
    """
    def __init__(self, redirect=False):
        self.gottenpic = False
        wx.App.__init__(self, redirect)
        #we've disabled the maximize button here, it makes things unpretty
        self.frame = wx.Frame(None, title="Apod Wallpaper Grabber",
            style=wx.SYSTEM_MENU | wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX)
        self.panel = wx.Panel(self.frame)

        #this is the max size of the preview image to be shown, we will scale anything
        #bigger than this down to this size
        self.previewsize = 600

        self.CreateWidgets()
        self.frame.Center()
        self.frame.Show()

    def CreateWidgets(self):
        """
        Add our buttons, image handler, and layout design here.  We initially just show a blank image before we download one
        """
        instructions = 'Press \'Download\' to preview the latest (today\'s) Astronomy Picture of the Day.  http://apod.nasa.gov/apod/'
        picdate = ''
        img = wx.EmptyImage(600, 640)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ALIGN_CENTER, wx.BitmapFromImage(img))
        self.picdateCtrl = wx.StaticText(self.panel, label=picdate)

        instructLbl = wx.StaticText(self.panel, label=instructions)
        
        getButton = wx.Button(self.panel, label='Download/Preview')
        getButton.Bind(wx.EVT_BUTTON, self.download)
        self.setButton = wx.Button(self.panel, label='Set as Wallpaper')
        self.setButton.Bind(wx.EVT_BUTTON, self.set)
        quitButton = wx.Button(self.panel, label='Exit')
        quitButton.Bind(wx.EVT_BUTTON, self.quit)
        #previousButton = wx.Button()
        #nextButton = wx.Button()

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(instructLbl, 0, wx.ALIGN_CENTRE, 5)
        self.mainSizer.Add(self.picdateCtrl, 0, wx.ALIGN_CENTER, 5)
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL, 5)

#        self.sizer2.Add(previousButton, 0, wx.ALL, 5)
#        self.sizer2.Add(nextButton, 0, wx.ALL, 5)
#        self.mainSizer.Add(self.sizer2, 0, wx.ALIGN_CENTRE, 5)

        self.sizer.Add(getButton, 0, wx.ALL, 5)
        self.sizer.Add(self.setButton, 0, wx.ALL, 5)
        self.sizer.Add(quitButton, 0, wx.ALL, 5)
        self.mainSizer.Add(self.sizer, 0, wx.ALL, 5)
        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)

        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self.frame)
        self.setButton.Disable()
        self.panel.Layout()
    def download(self, e):
        """
        download the latest image using magic
        """
        url = 'http://apod.nasa.gov/apod/'
        try:
            page = urllib2.urlopen(url).read()
        except urllib2.HTTPError:
            wx.MessageBox('There was an error in downloading the image from APOD', 'Error!', wx.OK | wx.ICON_ERROR)
            return
        #this saved me from regex hell
        picsoup = BeautifulSoup.BeautifulSoup(page)
        pic = picsoup.findAll('img')[0]
        #fixme.  if the url ever changes, or anything odd pops up, this will not work
        picurl = url + str(pic)[10:].split(' ')[0][:-1]

        try:
            #fixme.  opening and closing 2 files for the same data is stupid.
            img = urllib2.urlopen(picurl).read()
            #fixme.  handle multiple image types.
            with tempfile.TemporaryFile(mode='wb', suffix='.jpg') as f:
                f.write(img)
                f.close()
                with open(f.name, 'ab') as t:
                    t.write(img)
                    t.close()
                self.preview(f.name)
                
        except urllib2.HTTPError:
            wx.MessageBox('There was an error in downloading or saving the image from APOD', 'Error!', wx.OK | wx.ICON_ERROR)
            return

    def preview(self, img):
        """
        Show the iage in our preview spot.
        """
        newpic = wx.Image(img, wx.BITMAP_TYPE_ANY)
        W = newpic.GetWidth()
        H = newpic.GetHeight()

        if W > H:
            NewW = self.previewsize
            NewH = self.previewsize * H / W
        else:
            NewH = self.previewsize
            NewW = self.previewsize * W / H
        newpic = newpic.Scale(NewW, NewH)

        self.imageCtrl.SetBitmap(wx.BitmapFromImage(newpic))
        #enable the set button if we downloaded anything.
        self.gottenpic = True
        self.image = img
        self.setButton.Enable()
        self.panel.Refresh()

    def set(self, e):
        """
        set the wallpaper with our image.
        """
        SPI_SETDESKWALLPAPER = 20
        #fixme.  does not stick on some windows.  requires registry editing methinks.
        #ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, '' , 0)
        ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, self.image , 0)

    def quit(self, e):
        """
        a super fancy exiting method.
        """
        wx.Exit()

#the main loop.
if __name__ == '__main__':
    app = Apod()
    app.MainLoop()