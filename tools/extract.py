"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import pickle
# Project Modules
from parsing import Parser

with open("realtime.db", "rb") as fi:
    data = pickle.load(fi)

fo = open("output.txt", "w")

for file, file_data in data.items():
    if file is None or len(file) == 0:
        continue
    fo.write("# {}\n".format(Parser.parse_filename(file).strftime("%Y-%m-%d - %H:%m")))
    for match, match_data in file_data.items():
        match_features = list()
        for spawn, spawn_data in match_data.items():
            for key, key_data in spawn_data.items():
                if isinstance(key_data, dict):
                    if len(key_data) > 0:
                        match_features.append(key)
                    continue
                if key_data is not None:
                    match_features.append(key)
        string = ", ".join(set(match_features)) if len(match_features) > 0 else "No data recorded"
        fo.write("{}: {}\n".format(match.strftime("%H:%M:%S"), string))

fo.close()
