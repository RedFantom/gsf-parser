"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from semantic_version import Version
from github import Github, GithubException
import socket
# Custom modules
from variables import settings
from toplevels.update import UpdateWindow


def check_update(window=None):
    """
    Function to check for GSF Parser updates by checking tags and
    opening a window if an update is available
    """
    if not settings["misc"]["autoupdate"]:
        return
    try:
        user = Github().get_user("RedFantom")
        repo = user.get_repo("gsf-parser")
        current = Version(settings["misc"]["version"].replace("v", ""))
        for item in repo.get_tags():
            try:
                if Version(item.name.replace("v", "")) > current:
                    UpdateWindow(window, item.name)
                    break
                elif Version(item.name.replace("v", "")) < current:
                    # The newest tags come first in the loop
                    # If the tag is older than the current version, an update isn't needed
                    # The loop is stopped to preserve the rate limit
                    break
            except ValueError as e:
                print(e)
                continue
    except (GithubException, socket.timeout, socket.error, socket.gaierror):
        pass

