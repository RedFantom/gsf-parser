# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# For license see LICENSE

# UI imports
import Tkinter as tk
import ttk
import tkMessageBox
import tkFileDialog
# General imports
import re
import os
from datetime import datetime
# Own modules
import vars
import parse
import client
import frames
import statistics
import gui

if __name__ == "__main__":
    main_window = gui.main_window()