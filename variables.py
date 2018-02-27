"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import os
from settings import Settings, ColorScheme

settings = Settings()
colors = ColorScheme()

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
