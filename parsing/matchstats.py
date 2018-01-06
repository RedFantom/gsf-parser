# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
from parsing.parser import Parser


def match_statistics(file_name, match, match_timing):
    """
    Return a formatted string with all the statistics for a match
    """
    lines = Parser.read_file(file_name)
    name = Parser.get_player_name(lines)
    id_list = Parser.get_player_id_list(lines)

    (abilities_dict, dmg_d, dmg_t, dmg_s, healing, hitcount, critcount,
     crit_luck, enemies, enemy_dmg_d, enemy_dmg_t, ships, uncounted) = \
        Parser.parse_match(match, id_list)
    # Calculate other statistics
    killsassists = sum(True if enemy_dmg_t[enemy] > 0 else False for enemy in enemies if enemy in enemy_dmg_t)

    start = match_timing
    finish = Parser.line_to_dictionary(match[-1][-1])["time"]
    delta = finish - start
    minutes, seconds = divmod(delta.total_seconds(), 60)

    stat_string = "{name}\n{enemies} enemies\n{dmg_d}\n{dmg_t}\n{dmg_r:.1f} : 1.0\n" \
                  "{dmg_s}\n{healing}\n{hitcount}\n{critcount}\n{crit_luck:.2f}\n" \
                  "{deaths}\n{minutes}:{seconds:.0f}\n{dps:.1f}"
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
        deaths=len(match) - 1,
        minutes=minutes,
        seconds=seconds,
        dps=dmg_d / delta.total_seconds() if delta.total_seconds() != 0 else 0
    )
    return abilities_dict, stat_string, ships, enemies, enemy_dmg_d, enemy_dmg_t, uncounted
