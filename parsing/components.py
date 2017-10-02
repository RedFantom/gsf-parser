# A new parsing engine built by RedFantom based on principles from parse.py and realtime.py
# Is capable of parsing files as well as realtime parsing
"""
This file contains code to generate new ability data structures during runtime
"""
from parsing import abilities
from parsing.ships import ships as ships_full_dict

# Run-time generated dictionary of lists of abilities
ship_components = {
    # Imperial active ships
    "Rycer": abilities.rycerAbilities,
    "Quell": abilities.quellAbilities,
    "Imperium": abilities.imperiumAbilities,
    "Sting": abilities.stingAbilities,
    "Bloodmark": abilities.bloodmarkAbilities,
    "Blackbolt": abilities.blackboltAbilities,
    "Razorwire": abilities.razorwireAbilities,
    "Legion": abilities.legionAbilities,
    "Decimus": abilities.decimusAbilities,
    "Mangler": abilities.manglerAbilities,
    "Dustmaker": abilities.dustmakerAbilities,
    "Jurgoran": abilities.jurgoranAbilities,
}

# Update with keys of Republic ships
ship_components.update(
    {rep: ship_components[imp] for imp, rep in abilities.all_ships.items() if imp in ship_components}
)

# Update with keys of full names
ship_components.update(
    {full: ship_components[basic] for basic, full in ships_full_dict.items() if basic in ship_components}
)


