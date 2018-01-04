# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
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
