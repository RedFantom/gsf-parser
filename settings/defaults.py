"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from utils.directories import get_combatlogs_folder

"""
Default settings for the GSF Parser
"""
defaults = {
    # Miscellaneous settings
    "misc": {
        # GSF Parser version number (used for update checks)
        "version": "v5.0.0",
        # Whether checks for updates are enabled
        "autoupdate": True,
        # assets/ships.db SWTOR patch level
        "patch_level": "5.6.0",
        # SWTOR Temporary directory, for use on Linux
        "temp_dir": ""
    },
    # UI settings
    "gui": {
        # Whether the advanced color scheme is enabled
        "event_colors": True,
        # Color scheme to use (pastel, bright, custom)
        "event_scheme": "pastel",
        # Faction to use images and names of
        "faction": "empire",
        # Whether DebugWindow is enabled
        "debug": False,
        # Text color
        "color": "#2f77d0"
    },
    # File parsing settings
    "parsing": {
        # CombatLogs path
        "path": get_combatlogs_folder(),
        # Sharing Server address
        "address": "parser.thrantasquadron.tk",
        # Sharing Server port
        "port": 65088
    },
    # Real-time parsing settings
    "realtime": {
        # Whether the overlay is enabled
        "overlay": True,
        # Overlay text color
        "overlay_text": "Yellow",
        # Overlay position string
        "overlay_position": "x0y0",
        # Whether the Overlay hides outside of GSF
        "overlay_when_gsf": True,
        # Whether to enable EventOverlay
        "event_overlay": False,
        # Location of EventOverlay
        "event_location": "x0y0",
    },
    "screen": {
        # Whether screen parsing is enabled
        "enabled": True,
        # Whether screen parsing data is in the Overlay
        "overlay": True,
        # List of enabled screen parsing features
        "features": ["Tracking penalty", "Ship health", "Power management"],
        # Whether to use the experimental WindowsOverlay
        "experimental": False,
        # Whether to enable experimental Dynamic Window Location
        "window": False
    },
    "sharing": {
        "enabled": True,
        "discord": "",
        "auth": "",
        "host": "discord.gsfparser.tk",
        "port": 64731,
        "version": "0.0.2"
    }
}
