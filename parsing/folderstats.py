"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from parsing.parser import Parser


def folder_statistics():
    """
    Parses all files in the Current Working Directory by getting al .txt
    files in the folder and then returns the results in formats that can be
    used by the file_frame to set all the required strings to show the
    results to the user.
    """
    (abilities_dict, dmg_d, dmg_t, dmg_s, healing, hitcount, critcount,
     crit_luck, enemies, enemy_dmg_d, enemy_dmg_t, ships, uncounted,
     deaths, time) = \
        Parser.parse_folder()

    stat_string = "{name}\n{enemies} enemies\n{dmg_d}\n{dmg_t}\n{dmg_r:.1f} : 1.0\n" \
                  "{dmg_s}\n{healing}\n{hitcount}\n{critcount}\n{crit_luck:.2f}\n" \
                  "{deaths}\n{minutes}:{seconds:.0f}\n{dps:.1f}"

    minutes, seconds = divmod(time, 60)

    stat_string = stat_string.format(
        name="-",
        enemies=len([enemy for enemy in enemies if enemy in enemy_dmg_t and enemy_dmg_t[enemy] > 0]),
        dmg_d=dmg_d,
        dmg_t=dmg_t,
        dmg_r=dmg_d / dmg_t if dmg_t != 0 else 0,
        dmg_s=dmg_s,
        healing=healing,
        hitcount=hitcount,
        critcount=critcount,
        crit_luck=critcount / hitcount if hitcount != 0 else 0,
        deaths=deaths,
        minutes=minutes,
        seconds=seconds,
        dps=dmg_d / time,
    )

    return (abilities_dict, stat_string, ships, enemies, enemy_dmg_d,
            enemy_dmg_t, uncounted)
