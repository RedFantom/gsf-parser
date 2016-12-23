# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# abilities is a matrix of dictionaries
# damagetaken is a matrix of numbers
# damagedealt is a matrix of numbers
# selfdamage is a matrix of numbers
# healingreceived is a matrix of numbers
# enemies is a cube of strings
# criticalcount is matrix of numbers
# criticalluck is a matrix of numbers
# hitcount is matrix of numbers
# enemydamaged is a dictionary
# enemydamaget is a dictionary
# match_timings is a list of datetimes
# spawn_timings is a matrix of datetimes
import settings
import os
import Queue

FLAG = False

files_done              = 0
abilities               = None
damagetaken             = None
damagedealt             = None
selfdamage              = None
healingreceived         = None
enemies                 = None
criticalcount           = None
criticalluck            = None
hitcount                = None
enemydamaged            = None
enemydamaget            = None
match_timings           = None
spawn_timings           = None
enemies_names           = None

deaths                  = None

file_cube              = None
player_numbers         = {}
player_name            = None

file_name = None
match_timing = None
user_name = None

statisticsfile = False

abilities_string = None
events_string = None
statistics_string = None
allies_string = None
enemies_string = None
ships_list = None
ships_comps = None

user_path = None
privacy = None
server_address = None
server_port = None
auto_upload = None
parse = []
path = ""

set_obj = settings.settings()
client_obj = None
main_window = None
cl_path = None

spawn_timing = None
spawn_index = None
spawn = None
rt_timing = None

needs_closing = []

insert_queue = Queue.Queue()