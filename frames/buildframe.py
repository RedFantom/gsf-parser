"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from frames.shipstatsframe import ShipStatsFrame
from data.ships import companion_indices
from data.components import components
from parsing.ships import Ship, Component
from widgets import *


class BuildsFrame(ttk.Frame):
    """
    This file is to use the ships.db file found in the folder ships.
    This file contains a pickle of a dictionary that is explained in the
    README file. This also includes the not-enabled Infiltrator class
    ships.
    """

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.window = variables.main_window
        self.major_components = ["PrimaryWeapon", "PrimaryWeapon2", "SecondaryWeapon", "SecondaryWeapon2", "Systems"]
        self.middle_components = ["Engine", "ShieldProjector"]
        self.minor_components = ["Magazine", "Capacitor", "Reactor", "Armor", "Sensor", "Thruster"]
        # Open all required databases
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "ships.db")),
                  "rb") as f:
            # Contains data on the components
            self.ships_data = pickle.load(f)
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "categories.db")),
                  "rb") as f:
            # Contains data on the ships (specifically descriptions and the like)
            self.categories_data = pickle.load(f)
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "companions.db")),
                  "rb") as f:
            # Contains data on the Crew members
            self.companions_data = pickle.load(f)
        # ScrollFrame to contain the component lists (ToggledFrames) and the CrewSelectFrame
        self.components_lists_frame = VerticalScrollFrame(self, canvaswidth=260, canvasheight=315)

        self.ship_select_frame = ShipSelectFrame(self, self.set_ship, self.set_faction)
        self.components_lists = OrderedDict()
        self.faction = "Imperial"
        self.category = "Scout"
        self.ship = Ship("Bloodmark")
        self.character = None
        self.ship_name = None
        # Header above the Components ToggledFrames
        self.components_lists_header_label = ttk.Label(self.components_lists_frame.interior, text="Components",
                                                       justify=tk.LEFT, font=("Calibiri", 12))
        for category in components:
            # Bloodmark is the default around which the widgets are created
            if category not in self.ships_data["Imperial_S-SC4_Bloodmark"]:
                continue
            self.components_lists[category] = \
                ComponentListFrame(
                    self.components_lists_frame.interior, category,
                    self.ships_data["Imperial_S-SC4_Bloodmark"][category], self.set_component,
                    self.toggle_callback)
        self.component_frame = ttk.Frame(self)
        self.current_component = MajorComponentWidget(self.component_frame,
                                                      self.ships_data["Imperial_S-SC4_Bloodmark"]["PrimaryWeapon"][0],
                                                      self.ship, "PrimaryWeapon")
        self.crew_select_frame = CrewListFrame(self.components_lists_frame.interior, self.faction,
                                               self.companions_data[self.faction], self.set_crew_member)
        # Image for on the ShipStats button
        self.ship_stats_image = photo(Image.open(
            os.path.join(get_assets_directory(), "icons", "spvp_targettracker.jpg")).resize((49, 49), Image.ANTIALIAS))
        self.ship_stats_button = ttk.Button(self, text="Show ship statistics", command=self.show_ship_stats,
                                            image=self.ship_stats_image, compound=tk.LEFT)
        self.reset()

    def set_crew_member(self, member):
        """
        Callback to set the crew member in both the database as well as
        in the CrewAbilitiesFrame
        :param member: (faction, category, name)
        """
        print("set_crew_member received member: {0}".format(member))
        print("Looking for companion {0} in category {1}".format(member[2], member[1]))
        value = None
        faction, category, name = member
        self.ship.crew[category] = member
        category_index = companion_indices[category]
        for index, companion in enumerate(self.companions_data[faction][category_index][category]):
            print("Checking companion: {0}".format(companion["Name"]))
            if name == companion["Name"]:
                print("Companion is valid!")
                value = index
                print("Index was {0}, so value set to {1}".format(index, value))
                break
        if value is None:
            raise ValueError()
        member_dict = self.companions_data[faction][category_index][category][value]
        self.current_component.destroy()
        self.current_component = CrewAbilitiesFrame(self.component_frame, member_dict)
        self.current_component.grid_widgets()
        self.grid_widgets()
        self.save_ship_data()

    def set_ship(self, faction, type, ship, ship_object):
        """
        Callback to update the component lists and other widgets to
        match the newly selected ship
        :param faction: faction, str
        :param type: ship type (Scout, Strike etc)
        :param ship: Ship name
        :param ship_object: parsing.ships.Ship instance
        """
        # Close all the open ship category ToggledFrames
        if not self.ship_select_frame.category_frames[faction][type].show.get():
            self.ship_select_frame[faction][type].toggle()

        # Set the data attributes
        self.ship = ship_object
        self.character = self.ship_select_frame.character_tuple

        # Remove component list ToggledFrames from the UI
        for widget in self.components_lists_frame.interior.winfo_children():
            print(widget)
            widget.grid_forget()
            if isinstance(widget, ToggledFrame):
                if widget.show.get():
                    widget.toggle()
        for type in components:
            if type not in self.ship.data:
                # Not all ships have all component types
                print("type not in self.ship.data: {0}".format(type))
                continue
            self.components_lists[type] = ComponentListFrame(
                self.components_lists_frame.interior, type, self.ship.data[type], self.set_component,
                self.toggle_callback)
            if self.ship[type] is None:
                continue
            index = self.ship[type].index
            print("Setting type {0} to index {1}".format(type, index))
            self.components_lists[type].variable.set(index)
        for button in self.ship_select_frame.ship_buttons.values():
            button.config(state=tk.ACTIVE)
        for key in self.ship_select_frame.ship_buttons.keys():
            if ship in key:
                ship = key
                break
        if ship == "Novadive":
            ship = "NovaDive"
        for crew_member in self.ship.crew.values():
            if crew_member is None:
                continue
            faction, category, name = crew_member
            if category == "CoPilot":
                self.crew_select_frame.copilot_variable.set(name)
                self.crew_select_frame.set_crew_member(crew_member)
                continue
            self.crew_select_frame.category_variables[category].set(name)
            self.crew_select_frame.set_crew_member(crew_member)
        self.ship_select_frame.ship_buttons[ship].config(state=tk.DISABLED)
        self.ship_name = ship
        self.grid_widgets()

    def set_component(self, category, component):
        """
        Callback for the Radiobuttons in components list frame to update
        the component set for a certain category on the currently
        selected ship.
        """
        # Remove the current ComponentWidget
        self.current_component.grid_forget()
        self.current_component.destroy()
        print("set_component(%s, %s)" % (category, component))
        # To update the data, we need the index of the component in the list of dictionaries in the category
        indexing = -1
        for index, dictionary in enumerate(self.ships_data[self.ship.ship_name][category]):
            if component == dictionary["Name"]:
                indexing = index
                break
        # Create a tuple of arguments for the new Component widget
        args = (self.component_frame, self.ships_data[self.ship.ship_name][category][indexing], self.ship, category)
        # Create an appropriate ComponentWidget
        if category in self.minor_components:
            self.current_component = MinorComponentWidget(*args)
        elif category in self.middle_components:
            self.current_component = MiddleComponentWidget(*args)
        elif category in self.major_components:
            self.current_component = MajorComponentWidget(*args)
        else:
            # For debugging purposes
            raise ValueError("Component category not found: %s" % category)
        # Create a new Component object
        new_component = Component(self.ships_data[self.ship.ship_name][category][indexing],
                                  indexing,
                                  category)
        # Transfer the upgrades of the currently selected component on the ship to the new Component
        if self.ship[category] is not None:
            new_component.upgrades = self.ship[category].upgrades
        # Check if it is indeed a different component
        if self.ship[category] is None or self.ship[category].name != component:
            # Set the new component
            print("Updating component {} in category {} of ship {}".format(component, category, self.ship.ship_name))
            if self.ship[category] is not None:
                print("Replacing old component '{}' with a new one.".format(self.ship[category].name))
            self.ship[category] = new_component
        # Put the new ComponentWidget in place
        self.current_component.grid_widgets()
        self.current_component.grid(sticky="nswe")
        # Unlock all the upgrade buttons
        for button in self.current_component.upgrade_buttons:
            if isinstance(button, list):
                button[0].config(state=tk.NORMAL)
                button[1].config(state=tk.NORMAL)
                continue
            button.config(state=tk.NORMAL)
        # Save the altered ship
        self.window.characters_frame.characters[self.character]["Ship Objects"][self.ship_name] = self.ship
        self.window.characters_frame.save_button.invoke()

    def grid_widgets(self):
        """
        Puts all the widgets in the correct place for this Frame.
        """
        self.grid_forget_widgets()
        self.ship_select_frame.grid(row=0, column=0, rowspan=2, sticky="nswe", padx=1, pady=1)
        self.ship_select_frame.grid_widgets()
        self.ship_stats_button.grid(row=0, column=1, rowspan=1, sticky="nwe", pady=(6, 5))
        self.components_lists_frame.grid(row=1, column=1, rowspan=1, sticky="nswe", pady=1)
        self.component_frame.grid(row=0, rowspan=2, column=2, sticky="nswe")
        self.current_component.grid(sticky="nswe")
        self.current_component.grid_widgets()
        self.components_lists_header_label.grid(row=0, column=0, sticky="w", pady=5)
        set_row = 1
        for frame in self.components_lists.values():
            frame.grid(row=set_row, column=0, sticky="nswe")
            frame.grid_widgets()
            set_row += 1
        self.crew_select_frame.grid(row=set_row, column=0, sticky="nswe")

    def grid_forget_widgets(self):
        """
        The opposite of grid_widgets. Removes all widgets from the user
        interface if they are displayed.
        """
        self.ship_select_frame.grid_forget()
        self.ship_stats_button.grid_forget()
        self.components_lists_frame.grid_forget()
        self.component_frame.grid_forget()
        self.current_component.grid_forget()
        self.components_lists_header_label.grid_forget()
        for frame in self.components_lists.values():
            frame.grid_forget()

    def show_ship_stats(self):
        """
        Callback for the Show Ship Statistics button. Creates a Frame
        containing a Treeview and showing this Treeview in the place
        of a ComponentWidget on the right.
        """
        if self.ship is None:
            return
        self.grid_forget_widgets()
        self.current_component = ShipStatsFrame(self, self.ship, self.ships_data, self.companions_data)
        self.grid_widgets()
        self.current_component.grid(row=0, rowspan=3, column=2, sticky="nswe")

    def set_faction(self, faction):
        """
        Sets the faction attribute and calls grid_widgets to update the
        ship widgets that are displayed for the appropriate faction.
        """
        self.faction = faction
        self.grid_widgets()

    def save_ship_data(self):
        """
        Saves the modified Ship instance to the CharacterDatabase.
        """
        self.window.characters_frame.characters[self.character]["Ship Objects"][self.ship.name] = self.ship
        self.window.characters_frame.save_button.invoke()

    def reset(self):
        """
        Reset frame to the state it is found in on start-up of the GSF
        Parser. Unloads the character loaded, resets all ToggledFrames.
        """
        self.ship_select_frame.character.set("Choose character")
        self.ship_select_frame.server.set("Choose network")
        for frame in self.components_lists.values():
            frame.toggled_frame.toggle_button.config(state=tk.DISABLED)
        for frame in self.crew_select_frame.category_frames.values():
            frame.toggle_button.config(state=tk.DISABLED)
        for button in self.current_component.upgrade_buttons:
            if isinstance(button, list):
                button[0].config(state=tk.DISABLED)
                button[1].config(state=tk.DISABLED)
                continue
            button.config(state=tk.DISABLED)

    def toggle_callback(self, frame, open):
        """
        Callback for ToggledFrame in order to close all the open frames
        upon opening a new one so only a single frame is open at the
        any given moment.

        """
        if open is False:
            return
        for component_list_frame in self.components_lists.values():
            if component_list_frame.toggled_frame is frame:
                continue
            if bool(component_list_frame.toggled_frame.show.get()) is True:
                print("[BuildFrame] Closing open frame for", component_list_frame.category)
                component_list_frame.toggled_frame.close()
        return
