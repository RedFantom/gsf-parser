# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import os
from tools.settings import Settings, ColorSchemes

settings = Settings()
colors = ColorSchemes()

files_done = 0

user_path = None
privacy = None
server_address = None
server_port = None
auto_upload = None
parse = []

main_window = None
install_path = os.path.dirname(__file__)
path = settings["parsing"]["path"]

screen_w = 0
screen_h = 0
