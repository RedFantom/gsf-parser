from pynput.keyboard import Listener, Key
from datetime import datetime


start = None


def fprint(string: str):
    print(string)
    with open("measurements.txt", "a") as fo:
        fo.write(string.strip() + "\n")


def timer():
    global start
    if start is None:
        start = datetime.now()
    else:
        elapsed = (datetime.now() - start).total_seconds()
        start = None
        fprint("Measured: {}".format(elapsed))


def callback(key: Key):
    if key == Key.ctrl_l:
        timer()


t = Listener(on_press=callback)
t.run()
