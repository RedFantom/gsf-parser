import os
import json
import pickle


with open("../assets/ships.db", "rb") as fi:
    data = pickle.load(fi)

with open("../assets/companions.db", "rb") as fi:
    companions = pickle.load(fi)

with open("../assets/categories.db", "rb") as fi:
    categories = pickle.load(fi)

if not os.path.exists("json"):
    os.mkdir("json")

for key, value in data.items():
    with open("json/" + key + ".json", "w") as fo:
        json.dump(value, fo)

with open("json/ShipCategories.json", "w") as fo:
    json.dump(categories, fo)

with open("json/CompanionsByCrewPosition.json", "w") as fo:
    json.dump(companions, fo)
