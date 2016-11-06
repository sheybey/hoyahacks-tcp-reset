#!/usr/bin/env python3
try:
    # for Python2
    import Tkinter as tkinter
    import ttk as ttk
except ImportError:
    # for Python3
    from tkinter import *
    import ttk as ttk

import sys

x=tkinter.Tk(screenName=None, baseName=None, className='Tk', useTk=1)
y=ttk.Combobox()
y.set(8)
y.current(newindex=1)
x.mainloop()

'''
listen thread
attack thread
interface thread

connection dictionary
with lock

attack qeueue
with lock
'''
