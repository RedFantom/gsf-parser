"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
"""
File with all basic data structures for easy access by the SharingFrame, SharingClient and other classes
"""

servers_list = [
    "Darth Malgus",
    "Tulak Hord",
    "The Leviathan",
    "Star Forge",
    "Satele Shan"
]

factions_list = [
    "The Empire",
    "The Republic"
]

servers = {
    # US servers
    "SF": "Star Forge",
    "SA": "Satele Shan",
    # European servers
    "TH": "Tulak Hord",
    "DM": "Darth Malgus",
    "TL": "The Leviathan"
}

servers_dict = {value: key for key, value in servers.items()}

servers_code_list = ["SF", "SA", "TH", "DM", "TL"]

factions_dict = {
    "The Empire": "IMP",
    "Imperial": "IMP",
    "Empire": "IMP",
    "The Republic": "REP",
    "Republic": "REP"
}
