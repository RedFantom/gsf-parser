"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from parsing.parser import Parser
from data import abilities


def spawn_statistics(file_name, spawn, spawn_timing, sharing_db=None):
    """Build strings to show in the StatsFrame"""
    # Retrieve required data
    lines = Parser.read_file(file_name, sharing_db)
    player_numbers = Parser.get_player_id_list(lines)
    (abilities_dict, dmg_t, dmg_d, healing, dmg_s, enemies, critcount,
     crit_luck, hitcount, ships_list, enemy_dmg_d, enemy_dmg_t) = \
        Parser.parse_spawn(spawn, player_numbers)
    name = Parser.get_player_name(lines)
    # Build the statistics string
    stat_string = "{name}\n{enemies} enemies\n{dmg_d}\n{dmg_t}\n{dmg_r:.1f} : 1.0\n" \
                  "{dmg_s}\n{healing}\n{hitcount}\n{critcount}\n{crit_luck:.2f}\n" \
                  "{deaths}\n{minutes}:{seconds:.0f}\n{dps:.1f}"
    start = spawn_timing
    finish = Parser.line_to_dictionary(spawn[-1])["time"]
    delta = finish - start
    minutes, seconds = divmod(delta.total_seconds(), 60)
    killsassists = sum(True if enemy_dmg_t[enemy] > 0 else False for enemy in enemies if enemy in enemy_dmg_t)
    stat_string = stat_string.format(
        name=name,
        enemies=killsassists,
        dmg_d=dmg_d,
        dmg_t=dmg_t,
        dmg_r=dmg_d / dmg_t if dmg_t != 0 else 0,
        dmg_s=dmg_s,
        healing=healing,
        hitcount=hitcount,
        critcount=critcount,
        crit_luck=critcount / hitcount if hitcount != 0 else 0,
        deaths="-",
        minutes=minutes,
        seconds=seconds,
        dps=dmg_d / delta.total_seconds() if delta.total_seconds() != 0 else 0
    )
    # Build the components list
    components = {key: "" for key in abilities.component_types}
    for component in [ability for ability in abilities_dict.keys() if ability in abilities.components]:
        for type in components.keys():
            if component not in getattr(abilities, type):
                continue
            # Dual primary/secondary weapons
            if components[type] != "":
                components[type] += " / {}".format(component)
                break
            components[type] = component
            break
    components = [components[category] for category in abilities.component_types]
    # Return
    return name, spawn, abilities_dict, stat_string, ships_list, components, enemies, enemy_dmg_d, enemy_dmg_t
