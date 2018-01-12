"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import sys
import os

"""
Based on various sources:

    admin.py module
    Copyright (C) 2010 Preston Landers
    Released under the GPL-compatible Python 2.6.5 license
    https://stackoverflow.com/questions/19672352
    
    Drop root privileges
    Tamas on StackOverflow
    https://stackoverflow.com/questions/2699907
        

Edited by RedFantom for platform support
"""


def check_privileges():
    """
    Return whether the current user running the program, not the one
    logged in, has administrator rights. Supports Linux and Windows.
    :return: True if admin, else False
    """
    if sys.platform == "win32":
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    elif sys.platform == "linux":
        return os.getuid() == 0
    else:
        raise NotImplementedError("Unsupported platform")


def escalate_privileges():
    """
    Rerun the currently active Python script as administrator. Only
    works on Windows with UAC activation. Does not return. The current
    program will exit. Behaviour:

    Windows: Rerun as administrator with a UAC prompt through PowerShell
             (PowerShell command).
    Linux:   Replaces the current process with a new one executed as
             administrator with a password prompt (sudo). Retains the
             same PID and other attributes.
    """
    print("[Admin] Escalating privileges.")
    if sys.platform == "win32":
        import win32con
        from win32com.shell import shellcon
        from win32com.shell.shell import ShellExecuteEx
        ShellExecuteEx(
            nShow=win32con.SW_SHOWNORMAL,
            fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
            lpVerb="runas",
            lpFile="\"{}\"".format(sys.executable),
            lpParameters=" ".join(["\"{}\"".format(arg) for arg in sys.argv])
        )
    elif sys.platform == "linux":
        os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
    else:
        raise NotImplementedError("Unsupported platform")


def drop_privileges():
    """
    Drop administrative privileges, if the program has any. Platform
    behaviour:
    - Windows: Rerunning the whole program as a non-administrative user
    - Linux:   Switching from an administrative user to a normal user.
               This assumes that the program was run with sudo.
    """
    print("[Admin] Dropping privileges.")
    # Check if the program is running with administrative privileges
    if check_privileges() is False:
        return False
    # Drop the privileges
    if sys.platform == "win32":
        import win32con
        from win32com.shell import shellcon
        from win32com.shell.shell import ShellExecuteEx
        ShellExecuteEx(
            nShow=win32con.SW_SHOWNORMAL,
            fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
            lpFile="\"{}\"".format(sys.executable),
            lpParameters=" ".join(["\"{}\"".format(arg) for arg in sys.argv])
        )
        return True
    elif sys.platform == "linux":
        import pwd
        import grp
        current_uid = pwd.getpwnam("nobody").pw_uid
        current_gid = grp.getgrnam("nogroup").gr_gid
        # Remove group privileges
        os.setgroups([])
        # Drop the privileges
        os.setgid(current_gid)
        os.setuid(current_uid)
        # Set a new umask for security
        os.umask(0o077)
        return True
    else:
        raise NotImplementedError("Unsupported platform")

