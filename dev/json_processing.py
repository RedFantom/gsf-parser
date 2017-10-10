import json
import os
import pickle


ships_data = {}

for file in os.listdir(os.getcwd()):
    if not file.endswith(".json"):
        continue
    with open(file, "r") as fi:
        data = json.load(fi)
    if file == "CompanionsByCrewPosition.json":
        with open("companions.db", "wb") as fo:
            pickle.dump(data, fo)
    elif file == "ShipCategories.db":
        with open("categories.db", "wb") as fo:
            pickle.dump(data, fo)
    else:
        ships_data[file.replace(".json", "")] = data

with open("ships.db", "wb") as fo:
    pickle.dump(ships_data, fo)

