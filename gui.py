#!/usr/bin/env python3
try:
    # for Python2
    from Tkinter import * 
except ImportError:
    # for Python3
    from tkinter import *

class App(TK.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
myapp = App()

myapp.master.title("My Do-Nothing Application")
myapp.master.maxsize(1000, 400)
myapp.mainloop()