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
        "version": "v5.2.1",
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
        "color": "#2f77d0",
        # New FileFrame
        "fileframe": True,
    },
    # File results settings
    "results": {
        # CombatLogs path
        "path": get_combatlogs_folder(),
    },
    # Real-time results settings
    "realtime": {
        # RealTimeParser sleep
        "sleep": True,
        # RGB Keyboard Lighting Effects
        "rgb": False,
        # Discord Rich Presence
        "drp": True,
    },
    "overlay": {
        "position": "x0y0",
        "when_gsf": True,
        "enabled": True,
        "color": "Yellow"
    },
    # Event Overlay Settings
    "event": {
        # Whether to enable EventOverlay
        "enabled": False,
        # Location of EventOverlay
        "position": "x0y0"
    },
    "screen": {
        # Whether screen results is enabled
        "enabled": True,
        # List of enabled screen results features
        "features": ["Tracking penalty", "Ship health", "Power management"],
        # Whether to use the experimental WindowsOverlay
        "experimental": False,
        # Whether to enable experimental Dynamic Window Location
        "window": False,
        # SWTOR Dynamic window support
        "dynamic": False,
        # Screen results performance monitoring
        "perf": True,
        "disable": True,
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
