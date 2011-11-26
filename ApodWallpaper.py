__author__ = 'ghoti'
#TODO (in order of importance)
#add linkback to apod
#add copyright info if present
#browse previous apod images
#save image locally
#cross platform?

import urllib2
import BeautifulSoup
import tempfile
import ctypes
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
        self.previewsize = 640

        self.CreateWidgets()
        self.frame.Center()
        self.frame.Show()

    def CreateWidgets(self):
        """
        Add our buttons, image handler, and layout design here.  We initially just show a blank image before we download one
        """
        instructions = 'Press \'Download\' to preview the latest APOD'
        img = wx.EmptyImage(640, 500)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.BitmapFromImage(img))

        instructLbl = wx.StaticText(self.panel, label=instructions)
        getButton = wx.Button(self.panel, label='Download/Preview')
        getButton.Bind(wx.EVT_BUTTON, self.download)
        setButton = wx.Button(self.panel, label='Set as Wallpaper')
        setButton.Bind(wx.EVT_BUTTON, self.set)
        quitButton = wx.Button(self.panel, label='Exit')
        quitButton.Bind(wx.EVT_BUTTON, self.quit)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(instructLbl, 0, wx.ALL, 5)
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL, 5)
        self.sizer.Add(getButton, 0, wx.ALL, 5)
        self.sizer.Add(setButton, 0, wx.ALL, 5)
        self.sizer.Add(quitButton, 0, wx.ALL, 5)
        self.mainSizer.Add(self.sizer, 0, wx.ALL, 5)
        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)

        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self.frame)

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
        self.panel.Refresh()

    def set(self, e):
        """
        set the wallpaper with our image.
        """
        if self.gottenpic:
            SPI_SETDESKWALLPAPER = 20
            #fixme.  does not stick on some windows.  requires registry editing methinks.
            #ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, '' , 0)
            ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, self.image , 0)
        else:
            wx.MessageBox('No image to set as background!  Download one first dummy!', 'Error!', wx.OK | wx.ICON_ERROR)

    def quit(self, e):
        """
        a super fancy exiting method.
        """
        wx.Exit()

#the main loop.
if __name__ == '__main__':
    app = Apod()
    app.MainLoop()