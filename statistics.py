# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import Tkinter as tk
import ttk
import tkMessageBox
import tkFileDialog
# General imports
import re
import glob
import os
# Own modules
import vars
import parse
import client
import abilities

class statistics:
    def folder_statistics(self):
        self.file_list = []
        for file_name in os.listdir(os.getcwd()):
            if file_name.endswith(".txt"):
                self.file_list.append(file_name)

        total_ddealt = 0
        total_dtaken = 0
        total_hrecvd = 0
        total_selfdmg = 0
        total_timeplayed = 0
        avg_criticalluck = None
        avg_matchtime = None
        mostplayedship = None
        match_count = 0

        razor_count = 0
        legion_count = 0
        decimus_count = 0
        bloodmark_count = 0
        sting_count = 0
        blackbolt_count = 0
        mangler_count = 0
        dustmaker_count = 0
        jurgoran_count = 0
        imperium_count = 0
        quell_count = 0
        rycer_count = 0

        criticalnumber = 0
        criticaltotal = 0
        file_object = open(self.file_list[0], "r")
        lines = file_object.readlines()
        player_name = parse.determinePlayerName(lines)
        file_object.close()
        for name in self.file_list:
            file_object = open(name, "r")
            lines = file_object.readlines()
            player_numbers = parse.determinePlayer(lines)
            file_cube, match_timings, spawn_timings = parse.splitter(lines, player_numbers)
            for matrix in file_cube:
                match_count += 1
                for spawn in matrix:
                    ships_possible = parse.determineShip(spawn)
                    if len(ships_possible) == 1:
                        if ships_possible[0] == "Razorwire":
                            razor_count += 1
                        elif ships_possible[0] == "Legion":
                            legion_count += 1
                        elif ships_possible[0] == "Decimus":
                            decimus_count += 1
                        elif ships_possible[0] == "Bloodmark":
                            bloodmark_count += 1
                        elif ships_possible[0] == "Sting":
                            sting_count += 1
                        elif ships_possible[0] == "Blackbolt":
                            blackbolt_count += 1
                        elif ships_possible[0] == "Mangler":
                            mangler_count += 1
                        elif ships_possible[0] == "Dustmaker":
                            dustmaker_count += 1
                        elif ships_possible[0] == "Jurgoran":
                            jurgoran_count += 1
                        elif ships_possible[0] == "Imperium":
                            imperium_count += 1
                        elif ships_possible[0] == "Quell":
                            quell_count += 1
                        elif ships_possible[0] == "Rycer":
                            rycer_count += 1
            # Then get the useful information out of the matches
            (abilitiesdict, damagetaken, damagedealt, selfdamage, healingreceived, enemies,
             criticalcount, criticalluck, hitcount, enemydamaged, enemydamaget, match_timings,
             spawn_timings) = parse.parse_file(file_cube, player_numbers, match_timings, spawn_timings)
            for list in damagetaken:
                for number in list:
                    total_ddealt += number
            for list in damagedealt:
                for number in list:
                    total_dtaken += number
            for list in healingreceived:
                for number in list:
                    total_hrecvd += number
            for list in selfdamage:
                for number in list:
                    total_selfdmg += number
            for list in criticalluck:
                for number in list:
                    criticalnumber += 1
                    criticaltotal += number
            file_object.close()
        start_time = False
        previous_time = None
        for datetime in match_timings:
            if start_time == False:
                previous_time = datetime
                continue
            else:
                total_timeplayed += datetime - previous_time
                previous_time = datetime
                continue
        (total_timeplayed_minutes, total_timeplayed_seconds) = divmod(total_timeplayed, 60)
        return total_ddealt, total_dtaken, total_hrecvd, total_selfdmg, total_timeplayed_minutes


    def match_statistics(self, match):
        # match needs to be a matrix containing strings with each list being a spawn
        total_ddealt = 0
        total_dtaken = 0

        for spawn in match:
            print "Something"

    def spawn_statistics(self, spawn):
        (abilitiesdict, damagetaken, damagedealt, healingreceived, selfdamage, enemies, criticalcount,
         criticalluck, hitcount, ships_list, enemydamaged, enemydamaget) = parse.parse_spawn(spawn, vars.player_numbers)
        abilities_string = ""
        events_string = ""
        enemies_string = ""
        statistics_string = ""
        ship_components = []
        comps = ["Primary", "Secondary", "Engine", "Shield", "System"]
        for key in abilitiesdict:
            abilities_string += key + "\n"
            if key in abilities.components:
                ship_components.append(key)
        for component in ship_components:
            if component in abilities.primaries:
                if "Rycer" in ships_list:
                    if comps[0] == "Primary":
                        comps[0] = component
                    else:
                        comps[0] += "/" + component
                else:
                    comps[0] = component
            elif component in abilities.secondaries:
                if "Quell" in ships_list:
                    if comps[1] == "Secondary":
                        comps[1] = component
                    else:
                        comps[1] += "/" + component
                else:
                    comps[1] = component
            elif component in abilities.engines:
                comps[2] = component
            elif component in abilities.shields:
                comps[3] = component
            elif component in abilities.systems:
                comps[4] = component
            else:
                tkMessageBox.showinfo("WHAT?!", "DID GSF GET AN UPDATE?!")
        if "Primary" in comps:
            del comps[comps.index("Primary")]
        if "Secondary" in comps:
            del comps[comps.index("Secondary")]
        if "Engine" in comps:
            del comps[comps.index("Engine")]
        if "Shield" in comps:
            del comps[comps.index("Shield")]
        if "System" in comps:
            del comps[comps.index("System")]

        statistics_string = (str(damagedealt) + "\n" + str(damagetaken) + "\n" +
                             str(selfdamage) + "\n" + str(healingreceived) + "\n" + 
                             str(hitcount) + "\n" + str(criticalcount) + "\n" +
                             str(criticalluck) + "%" + "\n")
        enemies_string = "Enemy \tDamage dealt to you\tDamage taken\n\n"
        for enemy in enemies:
            enemies_string += enemy[8:] + "\t\t" + str(enemydamaged[enemy]) + "\t\t" + str(enemydamaget[enemy]) + "\n"
        return abilities_string, events_string, enemies_string, statistics_string, ships_list, comps
        

