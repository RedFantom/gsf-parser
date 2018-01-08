"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
import os
import sys
import pip
from shutil import rmtree, move, copytree, copyfile, make_archive
import subprocess
# Own modules
from tools.settings import Settings
from tools import admin
from setup_script import script


def print_without_newline(*args):
    print(*args, end="", flush=True)


def get_inno_setup_path(executable="ISCC.exe", identifier="inno"):
    """
    Return an absolute path to the Inno Setup executable, if it exists on the system in a known folder. Otherwise,
    False is returned.
    """
    # Check PATH
    paths = os.environ["PATH"].split(os.pathsep)
    for path in paths:
        path = path.strip("\"").strip()
        path = os.path.join(path, executable)
        if os.path.exists(path):
            return path
    # Check Program Files and Program Files (x86) and C:\
    folders = ["C:\\", "C:\\Program Files (x86)", "C:\\Program Files"]
    for folder in folders:
        if os.path.exists(folder):
            for item in os.listdir(folder):
                iscc = os.path.join(folder, item, executable)
                if identifier in item.lower() and os.path.exists(iscc):
                    return iscc
    return False


def get_pyinstaller_path():
    """
    Return an absolute path to the pyinstaller executable
    """
    printw("Installing PyInstaller if required... ")
    pip.main(["install", "pyinstaller", "--quiet"])
    printw("Done.\n")
    path = os.path.join(os.path.dirname(sys.executable), "Scripts", "pyinstaller.exe")
    if not os.path.exists(path):
        raise ValueError("PyInstaller path does not exist while it is installed: {}".format(path))
    return path


if __name__ == '__main__':
    # Override the normal print
    printw = print_without_newline
    # Display welcome message
    printw("\n** Welcome to the GSF Parser Release Build Script **\n\n")
    # Check for Windows first
    if sys.platform != "win32":
        printw("This script is only supported on Windows.\n")
        exit(-1)
    # Check for admin permissions
    if not admin.is_user_admin():
        admin.run_as_admin()
    # Check the Python version
    major, minor = sys.version_info.major, sys.version_info.minor
    if major != 3 or minor != 5:
        printw("Only Python 3.5 is supported.\n")
        exit(-1)
    # List of arguments to pyinstaller:
    pyinstaller_args = ["../main.py", "--icon=../assets/logos/icon_green.ico", "--noconfirm"]
    # Ask the user if this is a debug or release build
    printw("Is this a debug or release build? (d/r) [d] ")
    answer = input()
    if "r" in answer:
        pyinstaller_args.append("--windowed")
    else:
        pyinstaller_args.append("--debug")
    # Ask for an output filename for the .exe
    printw("Enter a filename for the executable [parser.exe]: ")
    filename = input()
    if filename.strip() == "":
        filename = "parser.exe"
    if not filename.endswith(".exe"):
        filename += ".exe"
    filename = filename.replace(" ", "").replace("\n", "")
    pyinstaller_args.append("-n {}".format(filename))
    # Ask whether the executable should ask for admin rights by default
    printw("Should the executable ask for UAC by default? (y/n) [y] ")
    answer = input()
    if answer != "n":
        pyinstaller_args.append("--uac-admin")
        pyinstaller_args.append("--uac-uiaccess")
    # Ask whether a Setup, ZIP, or both should be created
    # For the Setup, Inno Setup is required in PATH, or in Program Files
    printw("Would you like to create a Setup, ZIP, both or neither? (s/z/b/n) [b] ")
    target = input()
    if target.strip() == "":
        target = "b"
    if target != "s" and target != "z" and target != "b" and target != "n":
        printw("Invalid input detected, defaulting to both.\n")
        target = "b"
    publisher = None
    if target == "s" or target == "b":
        printw("Please enter a Publisher name for the Setup: ")
        publisher = input()
    version = Settings.defaults["misc"]["version"]
    # Install all required packages using pip
    printw("Installing packages if required...")
    pip.main(["install", "-r", "../requirements.txt", "-q"])
    printw("  Done.\n")
    dist_dir = os.path.join(os.getcwd(), "dist")
    build_dir = os.path.join(dist_dir, os.path.splitext(filename)[0] + "\\")
    alt_build_dir = os.path.join(dist_dir, " " + filename + "\\")
    printw("Build directory determined as: {}\n".format(build_dir))
    for build_path in [build_dir, alt_build_dir]:
        if os.path.exists(build_path):
            printw("The build path exists. Would you like to delete it? (y/n) [y] ")
            answer = input()
            if "n" in answer:
                printw("Cancelled by user.\n")
                exit(-1)
            printw("Removing everything under \"{}\"... ".format(build_path))
            rmtree(build_path)
            printw("Done.\n")
    # Get the pyinstaller path
    pyinstaller_path = get_pyinstaller_path()
    # Use PyInstaller to build the base executable
    printw("Executing PyInstaller... ")
    pyinstaller_command = [pyinstaller_path] + pyinstaller_args
    p = subprocess.run(pyinstaller_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    printw("Done.\n")
    if os.path.exists(alt_build_dir) and alt_build_dir != build_dir:
        printw("Renaming output directory... ")
        move(alt_build_dir, build_dir)
        if not os.path.exists(build_dir):
            printw("Failed.\n")
            printw("Renaming command output: {}\n".format(p))
            exit(-1)
        alt_exe_path = os.path.join(build_dir, " " + filename)
        if os.path.exists(alt_exe_path):
            move(alt_exe_path, os.path.join(build_dir, filename))
        printw("Done.\n")
    if not os.path.exists(build_dir):
        from pprint import pprint
        printw("Failed.\n")
        pprint("PyInstaller Output: {}\n".format(p))
        exit(-1)
    # Copy files to the generated directory
    printw("Copying asset files to build directory... ")
    site_packages = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages")
    copytree(os.path.join(site_packages, "ttkthemes"), os.path.join(build_dir, "ttkthemes"))
    copytree(os.path.join(site_packages, "ttkwidgets"), os.path.join(build_dir, "ttkwidgets"))
    copytree("../tools", os.path.join(build_dir, "tools"))
    copytree("../archive", os.path.join(build_dir, "archive"))
    copytree("../assets", os.path.join(build_dir, "assets"))
    copyfile("../README.md", os.path.join(build_dir, "README.md"))
    copyfile("../LICENSE.md", os.path.join(build_dir, "LICENSE.md"))
    printw("Done.\n")
    # Build Setup File
    if target == "s" or target == "b":
        printw("Building Setup with version {}... ".format(version))
        setup_script = script.replace("{#AppName}", "GSF Parser").replace("{#AppVersion}", version).\
            replace("{#AppPublisher}", publisher).replace("{#AppURL}", "https://github.com/RedFantom/gsf-parser").\
            replace("{#AppExeName}", "parser.exe").replace("{#BuildDir}", build_dir).replace("{$BuildDir}", build_dir).\
            replace("\\\\", "\\")

        with open("setup.iss", "w") as fo:
            fo.write(setup_script)
        inno = get_inno_setup_path()
        if inno is False:
            printw("Inno Setup not found.\n")
        else:
            p = subprocess.run([inno, "setup.iss"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if not os.path.exists("Setups\\GSF_Parser_{}.exe".format(version)):
                printw("Failed.\n")
                printw("Inno Setup output: {}\n".format(p))
                exit(-1)
            printw("Done. \n")
    if target == "z" or target == "b":
        # Create a zip file
        printw("Creating ZIP archive... ")
        make_archive("Setups\\GSF_Parser_{}".format(version), "zip", build_dir)
        printw("Done.\n")
    printw("\n** Release creation complete **\n")
