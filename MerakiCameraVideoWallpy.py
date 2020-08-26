import tkinter as tk
from tkinter import font  as tkfont
import cv2
from PIL import Image, ImageTk
import requests
import json
import datetime
import time
import threading
import os
import numpy as np

baseUrl = "https://api.meraki.com/api/v0/devices/"
baseUrlPt2 = "/camera/video/settings"
XCiscoMerakiAPIKey =  "your api key goes here"
headers = {'X-Cisco-Meraki-API-Key':XCiscoMerakiAPIKey}
data = '{"externalRtspEnabled":true}'
activeWindow = None
fullscreen = True
serialList = ["serialnumber 1","serialnumber 2"] # 4 digit codes should be "-" seperated, can be as many as you want

# You need at least one Meraki MV camera and access to
# the Meraki API to make this work
#
# - CONTROLS -
# n - next
# l - last
# m - return to menu
# s - take a screenshot
#
# I know the controls are weird, this is because I was
# origionaly going to use an infrared remote with this
# as I explained on my website that sadly never happended
# but I never changed the controlls back to something
# better. Feel free to if you want to though
#
# Copyright 2020 sckzor

# Permission to use, copy, modify, and/or distribute this
# software for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission
# notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE
# USE OR PERFORMANCE OF THIS SOFTWARE.
#
# Packages needed
# - opencv-python
# - requests
# - numpy
# - pillow



def GetURL(serial):
    retry = 0
    camUrl = baseUrl + serial + baseUrlPt2
    print(camUrl)
    response = requests.put(camUrl, headers=headers,data=data)
    while retry < 6:
        if response.status_code == 200:
            jsonResponse = json.loads(response.content.decode('utf-8'))
            print(jsonResponse)
            retry = 0
            break
        else:
            print(response.status_code)
            retry += 1
    return(jsonResponse["rtspUrl"])

class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(StartPage)
        geom = self.geometry()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        self.overrideredirect(fullscreen)
        self.geometry('%dx%d+0+0' % (w, h))
        #self.config(bg="lavender")

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.pack_forget()

        self._frame = new_frame
        self._frame.pack()


class StartPage(tk.Frame):
    def __init__(self, master):
        global activeWindow
        activeWindow = 0
        self.selected = 3
        def nextItem():
            if self.selected == 0:
                live.config(fg="black")
                self.selected =1
                snapshots.config(fg="tomato")
            elif self.selected == 1:
                snapshots.config(fg="black")
                self.selected = 2
                videoWall.config(fg="tomato")
            elif self.selected == 2:
                videoWall.config(fg="black")
                self.selected = 3
                shutdown.config(fg="tomato")
            elif self.selected == 3:
                shutdown.config(fg="black")
                self.selected = 0
                live.config(fg="tomato")

        def lastItem():
            if self.selected == 0:
                live.config(fg="black")
                self.selected = 3
                shutdown.config(fg="tomato")
            elif self.selected == 1:
                snapshots.config(fg="black")
                self.selected = 0
                live.config(fg="tomato")
            elif self.selected == 2:
                videoWall.config(fg="black")
                self.selected = 1
                snapshots.config(fg="tomato")
            elif self.selected == 3:
                shutdown.config(fg="black")
                self.selected = 2
                videoWall.config(fg="tomato")

        def enterItem():
            if self.selected == 0:
                master.switch_frame(PageOne)
            if self.selected == 1:
                master.switch_frame(PageTwo)
            if self.selected == 2:
                master.switch_frame(PageThree)
            if self.selected == 3:
                quit()


        def key(event):
            if event.keysym == 'Escape':
                pass
            if event.keysym == 'Return':
                enterItem()
            if event.char == 'n':
                nextItem()
            if event.char == 's':
                try:
                    takeScreenshot()
                except:
                    pass
            if event.char == 'l':
                lastItem()


        tk.Frame.__init__(self, master)
        self.master.config(bg='SystemButtonFace')

        #self.master.config(bg="lavender")
        live = tk.Label(self, text="Live Video", font=("Arial Bold", 120), anchor = tk.N)
        live.grid(column=0, row=0)
        live.config(fg="black")

        videoWall = tk.Label(self, text="Video Wall", font=("Arial Bold", 120), anchor = tk.N)
        videoWall.grid(column=0, row=2)
        videoWall.config(fg="black")

        snapshots = tk.Label(self, text="Snapshots", font=("Arial Bold", 120), anchor = tk.N)
        snapshots.grid(column=0, row=1)
        snapshots.config(fg="black")

        shutdown = tk.Label(self, text="Shutdown", font=("Arial Bold", 120), anchor = tk.N)
        shutdown.grid(column=0, row=3)
        shutdown.config(fg="black")

        if activeWindow == 0:
            self.bind_all('<Key>', key)




class PageOne(tk.Frame):

    def __init__(self, master):
        self.serList = serialList
        self.numCams = len(self.serList)
        self.outputPath = "screenshots/"
        self.curCam = 0
        self.cap = cv2.VideoCapture(GetURL(self.serList[0]))
        tk.Frame.__init__(self, master)

        self.videoLoop()
    def videoLoop(self):
        global activeWindow
        activeWindow = 2

        def menu():
            self.master.switch_frame(StartPage)
        def nextStream():
            if self.curCam + 1 != self.numCams:
                self.cap = cv2.VideoCapture(GetURL(self.serList[self.curCam+1]))
                self.curCam = self.curCam + 1
            else:
                self.cap = cv2.VideoCapture(GetURL(self.serList[0]))
                self.curCam = 0
        def lastStream():
            if curCam != 0:
                self.cap = cv2.VideoCapture(GetURL(self.serList[self.curCam-1]))
                self.curCam = self.curCam - 1
            else:
                self.cap = cv2.VideoCapture(GetURL(self.serList[self.numCams-1]))
                self.curCam = self.numCam - 1
        def takeScreenshot():
            ts = datetime.datetime.now()
            filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
            path = os.path.sep.join((self.outputPath, filename))
            _, frame = self.cap.read()
            cv2.imwrite(path, frame)
            print(filename)

        lmain = tk.Label(self)
        lmain.grid(column=0, row=0)
        def key(event):
            if event.keysym == 'Escape':
                pass
            if event.char == 'n':
                nextStream()
            if event.char == 's':
                takeScreenshot()
            if event.char == 'l':
                lastStream()
            if event.char == 'm':
                menu()
        def showFrame():
            _, frame = self.cap.read()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
            if activeWindow == 2:
                self.bind_all('<Key>', key)
            lmain.after(10, showFrame)

        showFrame()
        self.pack()
        lmain.pack()


class PageTwo(tk.Frame):
    def __init__(self, master):
        global activeWindow
        activeWindow = 4
        self.files = os.listdir("screenshots")
        self.dir = "screenshots/"
        self.file = 0
        def nextImage():
            if self.file == len(self.files) -1:
                self.file = 0
                load = Image.open(self.dir+self.files[self.file])
                render = ImageTk.PhotoImage(load)
                img.configure(image=render)
                img.image = render
                img.pack()
            elif self.file != len(self.files)-1:
                self.file +=1
                load = Image.open(self.dir+self.files[self.file])
                render = ImageTk.PhotoImage(load)
                img.configure(image=render)
                img.image = render
                img.pack()

        def lastImage():
            if self.file == 0:
                self.file = len(self.files) -1
                load = Image.open(self.dir+self.files[self.file])
                render = ImageTk.PhotoImage(load)
                img.configure(image=render)
                img.image = render
                img.pack()

            elif self.file != 0:
                self.file -= 1
                load = Image.open(self.dir+self.files[self.file])
                render = ImageTk.PhotoImage(load)
                img.configure(image=render)
                img.image = render
                img.pack()
        def menu():
            master.switch_frame(StartPage)

        def key(event):
            if event.char == 'n':
                nextImage()
            if event.char == 'l':
                lastImage()
            if event.char == 'm':
                menu()

        tk.Frame.__init__(self, master)
        self.master = master
        self.pack(expand=1)

        load = Image.open(self.dir+self.files[self.file])
        render = ImageTk.PhotoImage(load)
        img = tk.Label(self, image=render)
        img.image = render
        img.place(x=0, y=0)
        if activeWindow == 4:
            self.bind_all('<Key>', key)
        img.pack()

        self.pack()

class PageThree(tk.Frame):
    def __init__(self, master):
        self.serList = serialList
        self.numCams = len(self.serList)
        self.caps = []
        for ser in self.serList:
            self.caps.append(cv2.VideoCapture(GetURL(ser)))
        tk.Frame.__init__(self, master)
        black = cv2.VideoCapture("black.mp4")
        ret, blackf = black.read()
        blackr = cv2.resize(blackf,(500,500),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
        self.black = blackr

        self.videoLoop()
    def videoLoop(self):
        global activeWindow
        activeWindow = 6

        def menu():
            self.master.switch_frame(StartPage)

        lmain = tk.Label(self)
        lmain.grid(column=0, row=0)
        def key(event):
            if event.char == 'm':
                menu()

        def showFrame():
            imgs = []
            for cap in self.caps:
                _, frame = cap.read()
                b = cv2.resize(frame,(500,500),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
                imgs.append(b)

            both = imgs[0]
            blackRow =  np.concatenate((self.black, self.black), axis=1)
            blackRow =  np.concatenate((blackRow, self.black), axis=1)

            if len(imgs) == 1:
                both = np.concatenate((imgs[0], self.black), axis=1)
                both = np.concatenate((both, self.black), axis=1)
                both = np.concatenate((both, blackRow), axis=0)
            if len(imgs) == 2:
                both = np.concatenate((imgs[0], imgs[1]), axis=1)
                both = np.concatenate((both, self.black), axis=1)
                both = np.concatenate((both, blackRow), axis=0)
            if len(imgs) == 3:
                both = np.concatenate((imgs[0], imgs[1]), axis=1)
                both = np.concatenate((both, imgs[2]), axis=1)
                both = np.concatenate((both, blackRow), axis=0)
            if len(imgs) == 4:
                both = np.concatenate((imgs[0], imgs[1]), axis=1)
                both = np.concatenate((both, imgs[2]), axis=1)
                both2 = np.concatenate((imgs[3], self.black), axis=1)
                both2 = np.concatenate((both2, self.black), axis=1)
                both = np.concatenate((both, both2), axis=0)
            if len(imgs) == 5:
                both = np.concatenate((imgs[0], imgs[1]), axis=1)
                both = np.concatenate((both, imgs[2]), axis=1)
                both2 = np.concatenate((imgs[3], imgs[4]), axis=1)
                both2 = np.concatenate((both2, self.black), axis=1)
                both = np.concatenate((both, both2), axis=0)
            if len(imgs) == 6:
                both = np.concatenate((imgs[0], imgs[1]), axis=1)
                both = np.concatenate((both, imgs[2]), axis=1)
                both2 = np.concatenate((imgs[3], imgs[4]), axis=1)
                both2 = np.concatenate((both2, imgs[5]), axis=1)
                both = np.concatenate((both, both2), axis=0)

            cv2image = cv2.cvtColor(both, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
            lmain.configure(anchor=tk.NE)
            if activeWindow == 6:
                self.bind_all('<Key>', key)
            lmain.after(10, showFrame)

        showFrame()
        self.pack()
        lmain.pack()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
