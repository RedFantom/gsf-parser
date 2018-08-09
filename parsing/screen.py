"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
from functools import partial
# Project Modules
from parsing.filehandler import FileHandler
from parsing.parser import Parser
from parsing.shipstats import ShipStats

POWER_MODES = {
    "F1": "Power to Weapons",
    "F2": "Power to Shields",
    "F3": "Power to Engines",
    "F4": "Balanced Power"
}

SPEED_DEF = "Engine_Speed_Modifier_at_Default_Power"
SPEED_MAX = "Engine_Speed_Modifier_at_Max_Power"
SPEED_MIN = "Engine_Speed_Modifier_at_Min_Power"

DAMAGE_DEF = "Weapon_Damage_Modifier_at_Default_Power"
DAMAGE_MAX = "Weapon_Damage_Modifier_at_Max_Power"
DAMAGE_MIN = "Weapon_Damage_Modifier_at_Min_Power"

SHIELDS_DEF = "Shield_Strength_Modifier_at_Default_Power"
SHIELDS_MAX = "Shield_Strength_Modifier_at_Max_Power"
SHIELDS_MIN = "Shield_Strength_Modifier_at_Min_Power"

ICON_SPEED_INC = "spvp_increaseenginepowerefficiency"
ICON_SPEED_DCR = "spvp_enginespeed"

ICON_WEAPON_INC = "spvp_weaponpowerregeneration"
ICON_WEAPON_DCR = "spvp_weaponpowerregeneration_upside_down"

ICON_SHIELDS_INC = "spvp_shieldpowerregeneration"
ICON_SHIELDS_DCR = "spvp_shieldpowerregeneration_upside_down"

POWER_MODE_ICONS = {
    "F1": "spvp_weaponpower",
    "F2": "spvp_shieldpower",
    "F3": "spvp_enginepower",
    "F4": "spvp_balancedpower",
}

POWER_MODE_CATEGORIES = {
    "F1": "dmgd_pri",
    "F2": "shield",
    "F3": "engine",
    "F4": "system"
}


class ScreenParser(object):
    """
    Parser that can create TimeView events from screen parsing data

    These events are built from specific screen parsing events that are
    recorded in the screen parsing data dictionary.
    """

    @staticmethod
    def build_spawn_events(file_name: str, match: datetime, spawn: datetime, events: list, player_name: str) -> list:
        """
        Build a new set of events to insert into a TimeView

        This new set of events includes all the screen parsing data that
        can be represented in a TimeView.
        """
        screen_data = FileHandler.get_spawn_dictionary(None, file_name, match, spawn)
        if screen_data is not None and not isinstance(screen_data, str):
            print("[ScreenParser] Processing spawn: {}/{}/{}".format(file_name, match, spawn))
            orig = len(events)
            events = ScreenParser._build_spawn_events(events, screen_data, player_name)
            print("[ScreenParser] Built {} new events.".format(len(events) - orig))
        return sorted(events, key=lambda e: e["time"].timestamp())

    @staticmethod
    def _build_spawn_events(events: list, screen_data: dict, player_name: str) -> list:
        """Extend the given events list with new screen parsing events"""
        if "ship" not in screen_data or screen_data["ship"] is None:
            print("[ScreenParser] Failed to fetch ship for this spawn")
            ship = None
        else:
            ship = ShipStats(screen_data["ship"], None, None)
        if "keys" in screen_data and len(screen_data["keys"]) != 0:
            print("[ScreenParser] Building key events")
            events.extend(ScreenParser._build_key_events(screen_data["keys"], player_name, ship))
        if "distance" in screen_data and len(screen_data["distance"]) != 0:
            print("[ScreenParser] Building tracking effects")
            events = ScreenParser._build_tracking_effects(events, screen_data, ship)
        return events

    @staticmethod
    def _build_tracking_effects(events: list, screen_data: dict, ship: ShipStats):
        """Determine tracking penalty for each primary weapon event"""
        active_ids = Parser.get_player_id_list(events)
        distance = screen_data["distance"]
        primary = "PrimaryWeapon"
        for i, event in enumerate(events):
            if "custom" in event and event["custom"] is True:
                continue
            if "Primary Weapon Swap" in event["ability"] and event["self"] is True:
                primary = "PrimaryWeapon2" if primary == "PrimaryWeapon" else "PrimaryWeapon"
                continue
            ctg = Parser.get_event_category(event, active_ids)
            if ctg != "dmgd_pri":
                continue
            key = min(distance.keys(), key=lambda k: abs((k - event["time"]).total_seconds()))
            if abs((key - event["time"]).total_seconds()) > 0.5:
                continue
            if primary not in ship:
                continue
            tracking = ship[primary]["trackingAccuracyLoss"] * (distance[key] / 10) * 100
            del events[i]
            event["effects"] = (
                ("", "Tracking", "Penalty", "-{:.0f}%".format(tracking), "", "spvp_improvedfiringarctrackingbonus"),
            )
            events.append(event)
        return events

    @staticmethod
    def _build_key_events(key_data: dict, player_name: str, ship: ShipStats) -> list:
        """Build a list of key event dictionaries"""
        events = list()
        states = {"mode": "F4"}
        for time, (key, state) in key_data.items():
            if "F" in key and len(key) == 2 and state is True:
                if states["mode"] == key:
                    continue
                states["mode"] = key
                print("[ScreenParser] Power mode switch: {}".format(key))
                events.append(ScreenParser.create_power_mode_event(player_name, time, key, ship))
                continue
            elif key == "space":
                if key not in states:
                    states[key] = (True, time)
                elif state is True and states[key][0] is True:
                    continue
                elif state is True and states[key][0] is False:
                    states[key] = (True, time)
                else:  # state is False and states[key][0] is True
                    start, end = states[key][1], time
                    events.append(ScreenParser.create_boost_event(player_name, start, end, ship))
                    states[key] = (False, time)
        while None in events:
            events.remove(None)
        return events

    @staticmethod
    def create_boost_event(name: str, start: datetime, end: datetime, ship: ShipStats):
        """Create a boost event"""
        duration = (end - start).total_seconds()
        if duration < 0.2:
            return None
        return {
            "time": start,
            "source": name,
            "target": name,
            "ability": "Engine Boost",
            "effect": "ApplyEffect: Speed Increased",
            "effects": ((
                "", "Speed", "Increased",
                "for {:.1f}s".format(duration),
                "{:.0f}%".format(ship["Ship"]["Booster_Speed_Multiplier"] * 100),
                "spvp_enginespeed"
            ),) if ship is not None else None,
            "custom": True,
            "self": True,
            "crit": False,
            "type": Parser.LINE_ABILITY,
            "icon": "spvp_enginespeed",
            "amount": "{:.1f}s".format(duration),
            "category": "engine"
        }

    @staticmethod
    def create_power_mode_event(player_name: str, time: datetime, power_mode: str, ship: ShipStats):
        """Create a new power mode event"""
        return {
            "time": time,
            "source": player_name,
            "target": player_name,
            "target": player_name,
            "ability": POWER_MODES[power_mode],
            "effect": "ApplyEffect: ChangePowerMode",
            "effects": ScreenParser._build_power_mode_effects(ship, power_mode),
            "custom": True,
            "self": True,
            "crit": False,
            "type": Parser.LINE_ABILITY,
            "icon": POWER_MODE_ICONS[power_mode],
            "amount": 0,
            "category": POWER_MODE_CATEGORIES[power_mode]
        }

    @staticmethod
    def _build_power_mode_effects(ship: ShipStats, mode: str):
        """Build a tuple of power mode effects to display in TimeView"""
        if ship is None:
            return None
        get_mod = partial(ScreenParser._get_power_modifier, ship)
        if mode == "F1":
            return (
                ("", "Power", "Weapons", "Damage Increased", get_mod(DAMAGE_MAX), ICON_WEAPON_INC),
                ("", "Power", "Shields", "Capacity Decreased", get_mod(SHIELDS_MIN), ICON_SHIELDS_DCR),
                ("", "Power", "Engines", "Speed Decreased", get_mod(SPEED_MIN), ICON_SPEED_DCR),
            )
        elif mode == "F2":
            return (
                ("", "Power", "Shields", "Capacity Increased", get_mod(SHIELDS_MAX), ICON_SHIELDS_INC),
                ("", "Power", "Engines", "Speed Decreased", get_mod(SPEED_MIN), ICON_SPEED_DCR),
                ("", "Power", "Weapons", "Damage Decreased", get_mod(DAMAGE_MIN), ICON_WEAPON_DCR)
            )
        elif mode == "F3":
            return (
                ("", "Power", "Engines", "Speed Increased", get_mod(SPEED_MAX), ICON_SPEED_INC),
                ("", "Power", "Weapons", "Damage Decreased", get_mod(DAMAGE_MIN), ICON_WEAPON_DCR),
                ("", "Power", "Shields", "Capacity Decreased", get_mod(SHIELDS_MIN), ICON_SHIELDS_DCR)
            )
        elif mode == "F4":
            return (
                ("", "Power", "Weapons", "Normalized", get_mod(DAMAGE_DEF), ICON_WEAPON_DCR),
                ("", "Power", "Shields", "Normalized", get_mod(SHIELDS_DEF), ICON_SHIELDS_DCR),
                ("", "Power", "Engines", "Normalized", get_mod(SPEED_DEF), ICON_SPEED_DCR)
            )
        return None

    @staticmethod
    def _get_power_modifier(ship: ShipStats, mod: str):
        return "{:.1f}%".format(ship["Ship"][mod] * 100)
