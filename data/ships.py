"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from collections import OrderedDict

ship_names = {
    "Decimus": "Imperial_B-5_Decimus",
    "Quell": "Imperial_F-T2_Quell",
    "Imperium": "Imperial_FT-3C_Imperium",
    "Rycer": "Imperial_F-T6_Rycer",
    "Mangler": "Imperial_GSS-3_Mangler",
    "Jurgoran": "Imperial_GSS-4Y_Jurgoran",
    "Dustmaker": "Imperial_GSS-5C_Dustmaker",
    "Onslaught": "Imperial_G-X1_Onslaught",
    "Frostburn": "Imperial_ICA-2B_Frostburn",
    "Sable Claw": "Imperial_ICA-3A_-_Sable_Claw",
    "Tormentor": "Imperial_ICA-X_Tormentor",
    "Ocula": "Imperial_IL-5_Ocula",
    "Demolisher": "Imperial_K-52_Demolisher",
    "Razorwire": "Imperial_M-7_Razorwire",
    "Blackbolt": "Imperial_S-12_Blackbolt",
    "Sting": "Imperial_S-13_Sting",
    "Bloodmark": "Imperial_S-SC4_Bloodmark",
    "Gladiator": "Imperial_TZ-24_Gladiator",
    "Mailoc": "Imperial_VX-9_Mailoc",
    "Banshee": "Republic_Banshee",
    "Flashfire": "Republic_Flashfire",
    "Pike": "Republic_FT-6_Pike",
    "Clarion": "Republic_FT-7B_Clarion",
    "Star Guard": "Republic_FT-8_Star_Guard",
    "Firehauler": "Republic_G-X1_Firehauler",
    "Skybolt": "Republic_IL-5_Skybolt",
    "Strongarm": "Republic_K-52_Strongarm",
    "Novadive": "Republic_NovaDive",
    "Rampart Mark Four": "Republic_Rampart_Mark_Four",
    "Comet Breaker": "Republic_SGS-41B_Comet_Breaker",
    "Quarrel": "Republic_SGS-45_Quarrel",
    "Condor": "Republic_SGS-S1_Condor",
    "Sledgehammer": "Republic_Sledgehammer",
    "Spearpoint": "Republic_Spearpoint",
    "Enforcer": "Republic_TZ-24_Enforcer",
    "Redeemer": "Republic_VX-9_Redeemer",
    "Warcarrier": "Republic_Warcarrier",
    "Whisper": 'Republic_X5-Whisper',
    "Mirage": "Republic_X7-Mirage",
    "Legion": "Imperial_B-4D_Legion"
}

ships_names_reverse = {value: key for key, value in ship_names.items()}

ships_reverse = {
    value.replace("Republic_", "").replace("Imperial_", "").replace("_", " "): key
    for key, value in ship_names.items()
}

ships_other = {
    value.replace("Imperial_", "").replace("Republic_", "").replace("_", " "): key
    for key, value in ship_names.items()
}

companion_indices = {
    "Engineering": 0,
    "Offensive": 1,
    "Tactical": 2,
    "Defensive": 3,
    "CoPilot": 4
}

ship_indices = {
    "Bomber": 0,
    "Gunship": 1,
    "Infiltrator": 2,
    "Scout": 3,
    "Strike Fighter": 4
}
sorted_ships = OrderedDict()
sorted_ships["Legion"] = "Warcarrier"
sorted_ships["Razorwire"] = "Rampart Mark Four"
sorted_ships["Decimus"] = "Sledgehammer"
sorted_ships["Mangler"] = "Quarrel"
sorted_ships["Jurgoran"] = "Condor"
sorted_ships["Dustmaker"] = "Comet Breaker"
sorted_ships["Rycer"] = "Star Guard"
sorted_ships["Imperium"] = "Clarion"
sorted_ships["Quell"] = "Pike"
sorted_ships["Sting"] = "Flashfire"
sorted_ships["Bloodmark"] = "Spearpoint"
sorted_ships["Blackbolt"] = "Novadive"
sorted_ships["Onslaught"] = "Firehauler"
sorted_ships["Mailoc"] = "Redeemer"
sorted_ships["Demolisher"] = "Strongarm"
sorted_ships["Ocula"] = "Skybolt"
sorted_ships["Gladiator"] = "Enforcer"
