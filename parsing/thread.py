"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom

Module offers a Thread import that is either a Process or a Thread,
depending on the setting determined by the user. Process may increase
performance of the whole GSF Parser by delegating tasks normally
executed in Threads to Processes, side-stepping the GIL.

The amount of Threads/Processes in the GSF Parser is rather high. Each
Thread has its own specific task that requires the lowest latency
possible. If no low-latency actions are required, a Thread is not used.

parsing.realtime.RealTimeParser

    self: Thread or Process
        Requires to run in a Thread to prevent slowing down the
        Tkinter.Tk.mainloop that runs in the MainThread. Runs the
        screen parsing and file parsing loop. The file parsing loop
        runs a LogStalker.

    pynput.keyboard.Listener: Thread
    pynput.mouse.Listener: Thread

parsing.pointer.PointerParser

    self: Thread or Process
        Requires to run in a Thread because a minimum latency between
        recording a mouse click and processing it is required.

    pynput.mouse.Listener: Thread

parsing.rgb.RGBController

    self: Thread or Process
        Runs in a Thread to prevent slowing down the RealTimeParser.
        # TODO: Determine if this is really necessary

    rgbkeyboards.Controller: Thread
        Runs in a Thread because it executes events on the RGB lighting
        asynchronously with the other code.

parsing.timer.TimerParser

    self: Thread or Process
        Requires to run in a Thread because a minimum latency between
        recording a keypress or mouse click and processing them is
        required.

    pynput.mouse.Listener: Thread
    pynput.keyboard.Listener: Thread

Other Thread usages in the GSF Parser (including the networking classes
as well as the Simulator tool) are meant to prevent slowing down the
Tkinter.Tk.mainloop that is running in MainThread. They do not require
to be moved to Processes.

While the Tkinter mainloop supports execution of arbitrary tasks using
the Tkinter.Tk.after function, this is not nearly as fast as simply
running a separate Thread, despite CPython having a GIL, because the
mainloop performing arbitrary tasks pauses the mainloop for much longer
at a time, reducing responsiveness.
"""
# Project Modules
from variables import settings


if settings["screen"]["multi"] is True:  # Processes enabled
    from multiprocessing import Process as Thread, Queue, Lock
else:  # Processes disabled, Threads used
    from threading import Thread, Lock
    from queue import Queue, Empty
    Queue.Empty = Empty
