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
    "misc": {
        "version": "v4.0.2",
        "autoupdate": True,
        "patch_level": "5.5",
        "temp_dir": ""
    },
    "gui": {
        "event_colors": True,
        "event_scheme": "pastel",
        "faction": "empire",
        "debug": False
    },
    "parsing": {
        "path": get_combatlogs_folder(),
        "address": "parser.thrantasquadron.tk",
        "port": 83
    },
    "realtime": {
        "overlay": True,
        "overlay_text": "Yellow",
        "overlay_position": "x0y0",
        "overlay_when_gsf": True,
        "screenparsing": True,
        "screen_overlay": True,
        "screen_features": ["Tracking penalty", "Ship health", "Power management"],
        "overlay_experimental": False
    },
}
