from datetime import datetime
import time
import random
import os


"""
Small tool to simulate the creation of a log file
"""


def flusher():
    """
    Tester function

    flushes to file after every write

    :return:
    """
    count = 0
    with open("OnGoing2.log", "a") as fo:
        while count < 10:
            fo.write("[" + datetime.now().time().isoformat() + "] [This is line " + str(count) + "]" +
                     " [dest] [abi] [eff] ()\n")
            print("[" + datetime.now().time().isoformat() + "] [This is line " + str(count) + "]" +
                  " [dest] [abi] [eff] ()")
            fo.flush()
            sleep_time = random.randrange(0, 10)
            time.sleep(sleep_time)
            count += 1


def unbuffered():
    """
    Tester function

    uses an unbuffered file stream to update the file while created

    :return:
    """
    count = 0
    with open("OnGoing2.log", "a", 0) as fo:
        while count < 10:
            fo.write("[" + datetime.now().time().isoformat() + "] [This is line " + str(
                count) + "]" + " [dest] [abi] [eff] ()\n")
            print("[" + datetime.now().time().isoformat() + "] [This is line " + str(
                count) + "]" + " [dest] [abi] [eff] ()")
            fo.flush()
            sleep_time = random.randrange(0, 10)
            time.sleep(sleep_time)
            count += 1


def open_close():
    """
    Tester function

    file is opened and closed for every write

    :return:
    """
    count = 0
    while count < 10:
        f = open("OnGoing2.log", "a")
        f.write("[" + datetime.now().time().isoformat() + "] [This is line " + str(count) + "]" +
                " [dest] [abi] [eff] ()\n")
        print("[" + datetime.now().time().isoformat() + "] [This is line " + str(count) + "]" +
              " [dest] [abi] [eff] ()")
        sleep_time = random.randrange(0, 10)
        time.sleep(sleep_time)
        count += 1
        f.close()


def simulate(input_file):
    """
    Takes an existent log file and copies it into a newly created file, simulating the time-delta.

    :param: input_file: input file to be copied
    :return: None
    """

    # Create new log file name with the form: "combat_2012-04-17_20_08_37_242569.txt"
    timestamp = str(datetime.now()).replace(" ", "_").replace(":", "_").replace(".", "_")
    file_name = "combat_" + timestamp + ".txt"

    last, current = "", ""
    FMT = "%H:%M:%S.%f"

    with open(input_file, "r") as fi, open(file_name, "a") as fo:
        for line in fi:

            if last is "":
                last = line.split(None, 1)[0].replace('[', '').replace(']', '')
            else:
                last = current

            current = line.split(None, 1)[0].replace('[', '').replace(']', '')

            delta = datetime.strptime(current, FMT) - datetime.strptime(last, FMT)
            delta_sec = delta.total_seconds()

            fo.write(line)
            fo.flush()

            print line

            time.sleep(delta_sec)

"""
--------------  Execute -----------------
"""

# flusher()
# unbuffered()
# open_close()
simulate("CombatLog.txt")
