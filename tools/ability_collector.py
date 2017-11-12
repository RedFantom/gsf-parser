from parsing.parse import splitter, check_gsf, determinePlayer
from tools.settings import Settings
import os
import re
from pprint import pformat


if __name__ == '__main__':
    settings = Settings()
    log_path = settings["parsing"]["cl_path"]
    files = os.listdir(log_path)
    current_dir = os.getcwd()
    os.chdir(log_path)
    effects = {}
    for combatlog in files:
        if not combatlog.endswith(".txt"):
            continue
        if not check_gsf(combatlog):
            continue
        print("Processing CombatLog {}".format(combatlog))
        fi = open(combatlog, "r")
        lines = fi.readlines()
        player = determinePlayer(lines)
        file_cube, match_timings, spawn_timings = splitter(lines, player)
        for match in file_cube:
            for spawn in match:
                for event in spawn:
                    elements = re.split(r"[\[\]]", event)
                    # print(elements)
                    _, timestamp, _, source, _, target, _, ability, _, effect, damage = elements
                    ability = ability.split("{")[0].strip()
                    effect = effect.split("{")[1].split(":")[1].strip()
                    if effect == "AbilityActivate":
                        continue
                    if ability not in effects:
                        effects[ability] = [effect]
                    elif effect not in effects[ability]:
                        effects[ability].append(effect)
    os.chdir(current_dir)
    with open("results.txt", "w") as fo:
        fo.write(pformat(effects))
