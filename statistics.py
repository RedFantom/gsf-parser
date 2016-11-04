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
import decimal
# Own modules
import vars
import parse
import client
import abilities
import parse

def check_gsf(file_name):
    file_obj = open(file_name, "r")
    for line in file_obj:
        if "@" not in line:
            file_obj.close()
            return True
        else:
            continue
    file_obj.close()
    return False


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
            file_object.close()
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

        total_abilitiesdict = {}
        total_damagetaken = 0
        total_damagedealt = 0
        total_healingrecv = 0
        total_selfdamage = 0
        total_enemies = []
        total_criticalcount = 0
        total_hitcount = 0
        total_shipsdict = {}
        total_enemydamaged = {}
        total_enemydamaget = {}

        ships_uncounted = 0

        for spawn in match:
            (abilitiesdict, damagetaken, damagedealt, healingreceived, selfdamage, enemies, criticalcount,
             criticalluck, hitcount, ships_list, enemydamaged, enemydamaget) = parse.parse_spawn(spawn, vars.player_numbers)
            total_abilitiesdict.update(abilitiesdict)
            total_damagetaken += damagetaken
            total_damagedealt += damagedealt
            total_healingrecv += healingreceived
            total_selfdamage += selfdamage
            for enemy in enemies:
                total_enemies.append(enemy)
            total_criticalcount += criticalcount
            total_hitcount += hitcount
            for key, value in enemydamaged.iteritems():
                if key in total_enemydamaged:
                    total_enemydamaged[key] += value
                else:
                    total_enemydamaged[key] = value
            for key, value in enemydamaget.iteritems():
                if key in total_enemydamaget:
                    total_enemydamaget[key] += value
                else:
                    total_enemydamaget[key] = value
            abilities_string = ""
            statistics_string = "" 
            events_string = "Events is not available for a whole match"
            if len(ships_list) != 1:
                ships_uncounted += 1
            for ship in ships_list:
                if ship in total_shipsdict:
                    total_shipsdict[ship] += 1
                else:
                    total_shipsdict[ship] = 1
        for (ability, count) in total_abilitiesdict.iteritems():
            abilities_string = abilities_string + ability.strip() + "\n"
        try:
            total_criticalluck = decimal.Decimal(float(total_criticalcount) / float(total_hitcount))
            total_criticalluck = round(total_criticalluck * 100, 2)
        except ZeroDivisionError:
            total_criticalluck = 0
        statistics_string = (str(total_damagedealt) + "\n" + str(total_damagetaken) + "\n" +
                             str(total_selfdamage) + "\n" + str(total_healingrecv) + "\n" + 
                             str(total_hitcount) + "\n" + str(total_criticalcount) + "\n" +
                             str(total_criticalluck) + "%" + "\n" + str(len(match) -1) + "\n")
        for enemy in total_enemies:
            print "[DEBUG] " + enemy + "\t" + str(total_enemydamaged[enemy])
        return abilities_string, events_string, statistics_string, total_shipsdict, total_enemies, total_enemydamaged, total_enemydamaget

    def spawn_statistics(self, spawn):
        (abilitiesdict, damagetaken, damagedealt, healingreceived, selfdamage, enemies, criticalcount,
         criticalluck, hitcount, ships_list, enemydamaged, enemydamaget) = parse.parse_spawn(spawn, vars.player_numbers)
        abilities_string = ""
        events_string = ""
        enemies_string = ""
        statistics_string = ""
        ship_components = []
        comps = ["Primary", "Secondary", "Engine", "Shield", "System"]
        events = []
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
                             str(criticalluck) + "%" + "\n" + "-\n")
        return abilities_string, events_string, statistics_string, ships_list, comps, enemies, enemydamaged, enemydamaget

        

