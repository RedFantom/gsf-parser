# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE
import Tkinter as tk
import ttk
import webbrowser
from widgets import *

class resources_frame(ttk.Frame):
    def __init__(self, root_frame, main_window):
        ttk.Frame.__init__(self, root_frame)
        self.frame = vertical_scroll_frame(self, canvasheight=280)
        self.frame.grid(column=0, row=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
        self.main_window = main_window
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        resources = ["GSF: A starting point",
                     "Stasiepedia",
                     "Despon's GSF School",
                     "Thranta Squadron Event Calendar",
                     "Dulfy GSF New Player Guide",
                     "Dulfy Ships and Components Guide",
                     "GSF Forums on SWTOR.com",
                     "GSF Discord Server"
                    ]
        resources_descriptions = {
            "GSF: A starting point":"A guide by comprehensive Pyril with information ranging from the interface to"+\
                                    "the components and controls. Originally created for Thranta Squadron, but useful"+\
                                    "for and available to everyone.",
            "Stasiepedia":"A very extensive guide to everything there is in GSF, including advisory builds for every"+\
                          "ship. Written in 2014, but still up-to-date due to the lack of updates for GSF. A trusted"+\
                          "source of information for many Veteran pilots.",
            "Despon's GSF School":"A YouTube channel with videos about important topics within GSF and a very"+\
                                  "experienced host. After throwing various types of event to help Rookies learn how"+\
                                  "to play GSF, he has started this YouTube channel, and with success.",
            "Thranta Squadron Event Calendar":"An interactive calendar containing all events of the GSF community on"+\
                                              "different servers. This calendar is being kept up-to-date with the GSF"+\
                                              "forums and it includes times in UTC and server locations.",
            "Dulfy GSF New Player Guide":"A guide for new players by the popular resource site Dulfy.",
            "Dulfy Ships and Components Guide":"An in-depth guide on ships and components by the popular resource site Dulfy.",
            "GSF Forums on SWTOR.com":"A place where subscribers who play GSF gather and discuss all sorts of things including events.",
            "GSF Discord Server":"A voice server created by Dakhath for anyone playing GSF for the Discord platform."
        }
        resources_links = {
            "GSF: A starting point": "https://www.thrantasquadron.tk/guide",
            "Stasiepedia": "http://www.swtor.com/community/showthread.php?t=729222",
            "Despon's GSF School": "https://www.youtube.com/channel/UCWTo5N9w5J_9OeqCvKfWMbQ/",
            "Thranta Squadron Event Calendar": "https://www.thrantasquadron.tk/my-calendar",
            "Dulfy GSF New Player Guide": "http://dulfy.net/2013/11/15/swtor-galactic-starfighter-new-player-guide/",
            "Dulfy Ships and Components Guide": "http://dulfy.net/2013/11/11/swtor-galactic-starfighter-ships-and-components-guide/",
            "GSF Forums on SWTOR.com": "http://www.swtor.com/community/forumdisplay.php?f=419",
            "GSF Discord Server": "https://www.reddit.com/r/swtor/comments/5dbi93/i_made_a_discord_server_for_anyone_still_playing/"
        }
        self.resource_labels = []
        self.resource_description_labels = {}
        set_row = 0
        print "[DEBUG] Creating labels"
        self.label_style = ttk.Style()
        self.label_style.configure("Resource.TLabel", foreground = "#0000EE")
        for resource in resources:
            resource_label = ttk.Label(self.frame.interior, text = resource,style="Resource.TLabel")
            link = lambda x: (lambda y: self.open_link(x))
            resource_label.bind("<Button-1>", link(resources_links[resource]))
            resource_description = ttk.Label(self.frame.interior, text = resources_descriptions[resource],
                                             justify=tk.LEFT, wraplength = 780)
            resource_label.grid(column=0, row=set_row,sticky = tk.N+tk.S+tk.W, padx = 5)
            resource_description.grid(column=0, row=set_row + 1, sticky = tk.N+tk.S+tk.W+tk.E, padx = 5)
            self.resource_labels.append(resource_label)
            self.resource_description_labels[resource_label] = resource_description
            set_row+=2
        self.help_label = ttk.Label(self, text = "Help", font = ("Calibri", 12))
        self.explanation_label = ttk.Label(self, text = "In this tab you can find links to all sorts of "+\
                                                                       "useful resources for SWTOR: GSF. Just click "+\
                                                                       "the text highlighted in blue to open the "+\
                                                                       "resource in your default browser.\n\nIf you "+\
                                                                       "have created a resource and would like it to "+\
                                                                       "be added to this list, please e-mail RedFantom "+\
                                                                       "at redfantom@outlook.com",
                                           justify = tk.LEFT, wraplength = 780)
        self.separator.grid(column=0, row=1, sticky=tk.N+tk.S+tk.W+tk.E, columnspan=2, pady=10)
        self.help_label.grid(column = 0, row=2, sticky =tk.N+tk.S+tk.W, pady=5)
        self.explanation_label.grid(column = 0, row=3, sticky = tk.N+tk.S+tk.W+tk.E)

    @staticmethod
    def open_link(link):
        webbrowser.open(str(link))