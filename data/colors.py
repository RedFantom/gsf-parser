"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

# Bright color scheme
default_colors = {
    'dmgd_pri': ['#ffd11a', '#000000'],
    'dmgt_pri': ['#ff0000', '#000000'],
    'dmgd_sec': ['#e6b800', '#000000'],
    'dmgt_sec': ['#cc0000', '#000000'],
    'selfdmg':  ['#990000', '#000000'],
    'healing':  ['#00b300', '#000000'],
    'selfheal': ['#008000', '#000000'],
    'engine':   ['#8533ff', '#ffffff'],
    'shield':   ['#004d00', '#ffffff'],
    'system':   ['#002db3', '#ffffff'],
    'other':    ['#33adff', '#000000'],
    'spawn':    ['#000000', '#ffffff'],
    'match':    ['#000000', '#ffffff'],
    'default':  ['#ffffff', '#000000'],
}
# Pastel color scheme
pastel_colors = {
    'dmgd_pri': ['#ffe066', '#000000'],
    'dmgt_pri': ['#ff6666', '#000000'],
    'dmgd_sec': ['#ffd633', '#000000'],
    'dmgt_sec': ['#ff3333', '#000000'],
    'selfdmg': ['#b30000', '#000000'],
    'healing': ['#80ff80', '#000000'],
    'selfheal': ['#66ff8c', '#000000'],
    'engine': ['#b380ff', '#000000'],
    'shield': ['#ccffcc', '#000000'],
    'system': ['#668cff', '#000000'],
    'other': ['#80ccff', '#000000'],
    'spawn': ['#b3b3b3', '#000000'],
    'match': ['#b3b3b3', '#000000'],
    'default': ['#ffffff', '#000000'],
}

# Color key list
color_keys = [
    "dmgd_pri", "dmgt_pri",
    "dmgd_sec", "dmgt_sec",
    "selfdmg", "healing", "selfheal",
    "engine", "shield", "system", "other",
    "spawn", "match", "default"
]

color_descriptions = {
    "dmgd_pri": "Damage dealt by Primary Weapons: ",
    "dmgt_pri": "Damage taken from Primary Weapons: ",
    "dmgd_sec": "Damage dealt by Secondary Weapons: ",
    "dmgt_sec": "Damage taken from Secondary Weapons: ",
    "selfdmg":  "Selfdamage: ",
    "healing":  "Healing received from others: ",
    "selfheal": "Healing received from yourself: ",
    "engine":   "Activation of engine abilities: ",
    "shield":   "Activation of shield abilities: ",
    "system":   "Activation of system abilities: ",
    "other":    "Activation of other abilities: ",
    "spawn":    "End of a spawn: ",
    "match":    "End of a match: ",
    "default":  "Unmatched categories: ",
}
