"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from utils.directories import get_combatlogs_folder


defaults = {
    # Miscellaneous settings
    "misc": {
        # GSF Parser version number (used for update checks)
        "version": "v5.2.0",
        # Whether checks for updates are enabled
        "autoupdate": True,
        # assets/ships.db SWTOR patch level
        "patch_level": "5.9.2",
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
        # RealTimeParser sleep
        "sleep": True,
        # RGB Keyboard Lighting Effects
        "rgb": False,
        # Discord Rich Presence
        "drp": True,
    },
    # Event Overlay Settings
    "event": {
        # Whether to enable EventOverlay
        "enabled": False,
        # Location of EventOverlay
        "position": "x0y0"
    },
    "screen": {
        # Whether screen parsing is enabled
        "enabled": True,
        # List of enabled screen parsing features
        "features": ["Tracking penalty", "Ship health", "Power management"],
        # Whether to use the experimental WindowsOverlay
        "experimental": False,
        # Whether to enable experimental Dynamic Window Location
        "window": False,
        # SWTOR Dynamic window support
        "dynamic": False,
        # Screen parsing performance monitoring
        "perf": True,
        "disable": True,
        # Multiprocessing support
        "multi": False,
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
