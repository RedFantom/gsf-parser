"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mb
from tkinter.filedialog import askopenfilename
from widgets import VerticalScrollFrame
# Tools
from parsing.guiparsing import get_gui_profiles
from parsing.gsfinterface import GSFInterface
from toplevels.cartelfix import CartelFix
from tools import simulator
# Miscellaneous
import os
import variables


class ToolsFrame(ttk.Frame):
    """
    This frame contains widgets to control various tools included with the GSF Parser.

    Tool available:
    - CartelFix
    - Simulator
    """

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.grid_propagate(False)
        self.interior_frame = VerticalScrollFrame(self, canvasheight=370)
        self.description_label = ttk.Label(
            self, text="In this frame you can find various tools to improve your GSF and GSF Parser experience. These "
                       "tools are not actively supported.", font=("Calibri", 11), wraplength=780)
        """
        CartelFix
        """
        self.separator_one = ttk.Separator(self.interior_frame.interior, orient=tk.HORIZONTAL)
        self.cartelfix = None
        self.cartelfix_heading_label = ttk.Label(self.interior_frame.interior, text="CartelFix", font=("Calibri", 12))
        self.cartelfix_description_label = ttk.Label(
            self.interior_frame.interior, justify=tk.LEFT, wraplength=780,
            text="The Cartel Market Gunships do not properly switch the icon of their Railguns, which can be really "
                 "annoying. This utility automatically places an overlay on top of the game, so you can use your "
                 "Railguns as you would with non-Cartel Market ships. Game mode must be set to \"Fullscreen "
                 "(Windowed)\" or \"Windowed\".")
        self.cartelfix_faction = tk.StringVar()
        self.cartelfix_first = tk.StringVar()
        self.cartelfix_second = tk.StringVar()
        self.cartelfix_faction_dropdown = ttk.OptionMenu(self.interior_frame.interior, self.cartelfix_faction,
                                                         "Choose faction", "Imperial",
                                                         "Republic")
        self.cartelfix_first_dropdown = ttk.OptionMenu(self.interior_frame.interior, self.cartelfix_first,
                                                       "Choose railgun", "Slug Railgun",
                                                       "Ion Railgun", "Plasma Railgun")
        self.cartelfix_second_dropdown = ttk.OptionMenu(self.interior_frame.interior, self.cartelfix_second,
                                                        "Choose railgun", "Slug Railgun",
                                                        "Ion Railgun", "Plasma Railgun")
        self.cartelfix_gui_profile = tk.StringVar()
        self.cartelfix_gui_profile_dropdown = ttk.OptionMenu(self.interior_frame.interior, self.cartelfix_gui_profile,
                                                             *tuple(get_gui_profiles()))
        self.cartelfix_button = ttk.Button(self.interior_frame.interior, text="Open CartelFix",
                                           command=self.open_cartel_fix)
        """
        Simulator
        """
        self.separator_three = ttk.Separator(self.interior_frame.interior, orient=tk.HORIZONTAL)
        self.simulator_heading_label = ttk.Label(self.interior_frame.interior, text="CombatLog Creation Simulator",
                                                 font=("Calibri", 12))
        self.simulator_description_label = ttk.Label(
            self.interior_frame.interior, justify=tk.LEFT, wraplength=780,
            text="Small tool simulate the CombatLog creation. This is used during development to debug real-time "
                 "parsing and runs in its own thread so it can run alongside the GSF Parser. Once you have started it, "
                 "you cannot cancel the process.")
        self.simulator_file_label = ttk.Label(self.interior_frame.interior, text="No file selected...")
        self.simulator_file_selection_button = ttk.Button(
            self.interior_frame.interior, text="Select file", command=self.set_simulator_file)
        self.simulator_file = None
        self.simulator_button = ttk.Button(
            self.interior_frame.interior, text="Start simulator", command=self.start_simulator, state=tk.DISABLED)
        self.simulator_thread = None

    def start_simulator(self):
        """
        Start a CombatLog Simulator file for the file found in the widget
        """
        if self.simulator_thread is not None:
            self.simulator_thread.exit_queue.put(True)
            self.simulator_thread = None
            self.simulator_button.config(text="Start simulator")
            return
        self.simulator_thread = simulator.Simulator(self.simulator_file,
                                                    output_directory=variables.settings["parsing"]["path"])
        self.simulator_thread.start()
        self.simulator_button.config(text="Stop simulator")

    def set_simulator_file(self):
        file_name = askopenfilename()
        self.simulator_file = file_name
        self.simulator_button.config(state=tk.NORMAL)
        self.simulator_file_label.config(text=os.path.basename(file_name))

    def open_cartel_fix(self):
        """
        Open a CartelFix overlay with the data given by the widgets.
        Also determines the correct icons to use and calculates the
        correct position for the CartelFix.
        """
        # If a CartelFix is running, then the CartelFix should be closed, as this callback also provides
        # functionality for closing an open CartelFix
        if self.cartelfix:
            self.cartelfix.listener.stop()
            self.cartelfix.listener.join()
            self.cartelfix.destroy()
            self.cartelfix_button.config(text="Open CartelFix")
            self.cartelfix = None
            return
        # Perform checks to determine if the options entered are valid
        options = ["Slug Railgun", "Ion Railgun", "Plasma Railgun"]
        first = self.cartelfix_first.get()
        second = self.cartelfix_second.get()
        faction = self.cartelfix_faction.get()
        if first == second:
            mb.showerror("Error", "Please choose two different railguns, not two the same railguns.")
            return
        if first not in options or second not in options:
            mb.showerror("Error", "Please select the railguns")
            raise ValueError("Error", "Unkown railgun found: {0}, {1}".format(first, second))
        # Determine the icons for the Railguns
        # TODO: Change into dictionary operation
        if faction == "Imperial":
            if first == "Slug Railgun":
                first = generate_icon_path("spvp.imp.gunship.sweapon.03.jpg")
            elif first == "Ion Railgun":
                first = generate_icon_path("spvp.imp.gunship.sweapon.02.jpg")
            elif first == "Plasma Railgun":
                first = generate_icon_path("spvp.imp.gunship.sweapon.04.jpg")
            if second == "Slug Railgun":
                second = generate_icon_path("spvp.imp.gunship.sweapon.03.jpg")
            elif second == "Ion Railgun":
                second = generate_icon_path("spvp.imp.gunship.sweapon.02.jpg")
            elif second == "Plasma Railgun":
                second = generate_icon_path("spvp.imp.gunship.sweapon.04.jpg")
        elif faction == "Republic":
            if first == "Slug Railgun":
                first = generate_icon_path("spvp.rep.gunship.sweapon.03.jpg")
            elif first == "Ion Railgun":
                first = generate_icon_path("spvp.rep.gunship.sweapon.01.jpg")
            elif first == "Plasma Railgun":
                first = generate_icon_path("spvp.rep.gunship.sweapon.04.jpg")
            if second == "Slug Railgun":
                second = generate_icon_path("spvp.rep.gunship.sweapon.03.jpg")
            elif second == "Ion Railgun":
                second = generate_icon_path("spvp.rep.gunship.sweapon.01.jpg")
            elif second == "Plasma Railgun":
                second = generate_icon_path("spvp.rep.gunship.sweapon.04.jpg")
        else:
            raise ValueError("Unknown faction value found: {0}".format(faction))
        # Determine coordinates
        gui_profile = GSFInterface(self.cartelfix_gui_profile.get() + ".xml")
        x, y = gui_profile.get_secondary_icon_coordinates()
        scale = gui_profile.get_element_scale(gui_profile.get_element_object("FreeFlightShipAmmo"))
        # Open CartelFix
        self.cartelfix = CartelFix(variables.main_window, first, second, (x, y), scale)
        self.cartelfix_button.config(text="Close CartelFix")
        self.cartelfix.start_listener()

    def grid_widgets(self):
        self.description_label.grid(row=0, column=0, columnspan=10, sticky="w")
        self.interior_frame.grid(row=1, column=0, columnspan=10, sticky="nswe", pady=5, padx=5)
        self.separator_one.grid(row=1, column=0, columnspan=10, pady=5, sticky="we")
        self.cartelfix_heading_label.grid(row=3, column=0, columnspan=10, sticky="we")
        self.cartelfix_description_label.grid(row=4, column=0, columnspan=10, sticky="we")
        self.cartelfix_faction_dropdown.grid(row=5, column=0, columnspan=2, sticky="we")
        self.cartelfix_first_dropdown.grid(row=5, column=2, columnspan=1, sticky="we")
        self.cartelfix_second_dropdown.grid(row=5, column=3, columnspan=2, sticky="we")
        self.cartelfix_gui_profile_dropdown.grid(row=5, column=5, sticky="we")
        self.cartelfix_button.grid(row=5, column=6, columnspan=4, sticky="we")
        self.separator_three.grid(row=10, columnspan=10, sticky="we", pady=5)
        self.simulator_heading_label.grid(row=11, columnspan=10, sticky="w")
        self.simulator_description_label.grid(row=12, columnspan=10, sticky="w")
        self.simulator_file_label.grid(row=13, column=0, columnspan=2, sticky="w")
        self.simulator_file_selection_button.grid(row=13, column=2, sticky="we")
        self.simulator_button.grid(row=13, column=3, sticky="we")
        self.separator_six.grid(row=22, column=0, columnspan=10, sticky="we", pady=5)
