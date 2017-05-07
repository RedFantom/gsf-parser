# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import unittest
import gui
import Tkinter as tk
import variables
import tkMessageBox
import os
from tools import utilities


class TestUI(unittest.TestCase):
    def setUp(self):
        self.window = gui.MainWindow()

        def messagebox(title, message):
            pass

        with open(os.path.join(utilities.get_assets_directory(), "logs", "CombatLog.txt")) as log:
            self.lines = log.readlines()
            try:
                os.makedirs((os.path.expanduser("~") + "\\Documents\\Star Wars - The Old Republic\\CombatLogs").
                            replace("\\", "/"))
            except OSError:
                pass
            with open((os.path.expanduser("~") + "\\Documents\\Star Wars - The Old Republic\\CombatLogs\\").
                               replace("\\", "/") + "combat_2017-02-26_12_00_00_000000.txt", "w") as target_log:
                target_log.writelines(self.lines)
        tkMessageBox.showerror = messagebox
        tkMessageBox.showinfo = messagebox

    def tearDown(self):
        variables.FLAG = False
        self.window.update()
        self.window.destroy()

    def test_instances(self):
        self.assertIsInstance(self.window, tk.Tk)
        for item in self.window.children.values():
            self.assertIsInstance(item, tk.Widget)

    def test_main_window(self):
        self.window.update()

    def test_notebook(self):
        self.window.notebook.select(self.window.file_tab_frame)
        self.window.update()
        self.window.notebook.select(self.window.graphs_frame)
        self.window.update()
        self.window.notebook.select(self.window.realtime_tab_frame)
        self.window.update()
        self.window.notebook.select(self.window.share_tab_frame)
        self.window.update()
        self.window.notebook.select(self.window.resources_frame)
        self.window.update()
        self.window.notebook.select(self.window.settings_tab_frame)
        self.window.update()

    def test_file_adding(self):
        self.window.file_select_frame.refresh_button.invoke()
        self.window.update()
        self.assertEqual(self.window.file_select_frame.file_box.get(0), "All CombatLogs")
        self.assertEqual(self.window.file_select_frame.file_box.get(1), "2017-02-26   12:00")

    def test_custom_color_toplevel(self):
        self.window.settings_frame.event_scheme_custom_button.invoke()
        self.window.update()
        self.assertIsInstance(self.window.settings_frame.color_toplevel, tk.Toplevel)
        self.window.update()
        self.window.settings_frame.color_toplevel.destroy()

    '''
    def test_realtime_parsing_button(self):
        self.window.update()
        self.window.update()
        self.window.realtime_frame.start_parsing_button.invoke()
        self.window.update()
        self.assertTrue(self.window.realtime_frame.stalker_obj.is_alive())
        self.assertEqual(self.window.realtime_frame.watching_stringvar.get(),
                         "Watching: combat_2017-02-26_12_00_00_000000.txt")
        self.window.realtime_frame.start_parsing_button.invoke()
        time.sleep(5)
        self.assertFalse(self.window.realtime_frame.stalker_obj.is_alive())
        self.window.update()
    '''

    def test_graphs_frame(self):
        graphs = ("play", "dmgd", "dmgt", "hrec", "enem", "critluck", "hitcount", "spawn", "match", "deaths")
        self.window.notebook.select(self.window.graphs_frame)
        self.window.graphs_frame.update_button.invoke()
        self.window.update()
        for graph in graphs:
            self.window.graphs_frame.type_graph.set(graph)
            self.window.graphs_frame.update_button.invoke()
            self.window.update()
            for graph in graphs:
                self.window.graphs_frame.type_graph.set(graph)
                self.window.graphs_frame.update_button.invoke()
                self.window.update()

    def test_settings_frame(self):
        self.window.notebook.select(self.window.settings_tab_frame)
        self.window.settings_frame.save_settings_button.invoke()
        self.window.settings_frame.discard_settings_button.invoke()
        self.window.settings_frame.default_settings_button.invoke()
        for widget in self.window.settings_frame.children.values():
            if isinstance(widget, tk.Radiobutton):
                widget.select()
            if isinstance(widget, tk.Button):
                widget.invoke()
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, "value")
