#!/usr/bin/env python
# -*- coding: utf-8; mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vim: fileencoding=utf-8 tabstop=4 expandtab shiftwidth=4

# (C) COPYRIGHT © Preston Landers 2010
# Released under the same license as Python 2.6.5


import sys, os, traceback, types


def is_user_admin():
    if os.name == 'nt':
        import ctypes
        # WARNING: requires Windows XP SP2 or higher!
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            traceback.print_exc()
            print("Admin check failed, assuming not an admin.")
            return False
    elif os.name == 'posix':
        # Check for root on Posix
        return os.getuid() == 0
    else:
        raise RuntimeError("Unsupported operating system for this module: %s" % (os.name,))


def run_as_admin(cmd_line=None, wait=True):
    if os.name != 'nt':
        raise RuntimeError("This function is only implemented on Windows.")

    import win32api, win32con, win32event, win32process
    from win32com.shell.shell import ShellExecuteEx
    from win32com.shell import shellcon

    python_exe = sys.executable

    if cmd_line is None:
        cmd_line = [python_exe] + sys.argv
    elif type(cmd_line) not in (tuple, list):
        raise ValueError("cmdLine is not a sequence.")
    cmd = '"%s"' % (cmd_line[0],)
    params = " ".join(['"%s"' % (x,) for x in cmd_line[1:]])
    show_cmd = win32con.SW_SHOWNORMAL
    # showCmd = win32con.SW_HIDE
    lp_verb = 'runas'  # causes UAC elevation prompt.

    # print "Running", cmd, params

    # ShellExecute() doesn't seem to allow us to fetch the PID or handle
    # of the process, so we can't get anything useful from it. Therefore
    # the more complex ShellExecuteEx() must be used.

    # procHandle = win32api.ShellExecute(0, lpVerb, cmd, params, cmdDir, showCmd)

    proc_info = ShellExecuteEx(nShow=show_cmd,
                               fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                               lpVerb=lp_verb,
                               lpFile=cmd,
                               lpParameters=params)

    if wait:
        proc_handle = proc_info['hProcess']
        obj = win32event.WaitForSingleObject(proc_handle, win32event.INFINITE)
        rc = win32process.GetExitCodeProcess(proc_handle)
        # print "Process handle %s returned code %s" % (procHandle, rc)
    else:
        rc = None

    return rc
