# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
from tools import utilities
import os
import xml.etree.ElementTree as xmlparser

"""
Example:
    <FreeFlightQuickBar>
        <anchorAlignment Type="3" Value="8.000000" />
        <anchorXOffset Type="3" Value="-78.000000" />
        <anchorYOffset Type="3" Value="-25.000000" />
        <scale Type="3" Value="1.000000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
        <NumVisible Type="3" Value="4.000000" />
        <NumPerRow Type="3" Value="12.000000" />
        <BGVisible Type="2" Value="1" />
    </FreeFlightQuickBar>
    <FreeFlightShipStatus>
        <anchorAlignment Type="3" Value="2.000000" />
        <anchorXOffset Type="3" Value="15.000000" />
        <anchorYOffset Type="3" Value="-20.000000" />
        <scale Type="3" Value="1.000000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightShipStatus>
    <FreeFlightPlayerStatusEffects>
        <anchorAlignment Type="3" Value="2.000000" />
        <anchorXOffset Type="3" Value="25.000000" />
        <anchorYOffset Type="3" Value="-200.000000" />
        <scale Type="3" Value="1.000000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightPlayerStatusEffects>
    <FreeFlightTargetStatusEffects>
        <anchorAlignment Type="3" Value="4.000000" />
        <anchorXOffset Type="3" Value="0.000000" />
        <anchorYOffset Type="3" Value="284.000000" />
        <scale Type="3" Value="1.000000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightTargetStatusEffects>
    <FreeFlightShipAmmo>
        <anchorAlignment Type="3" Value="8.000000" />
        <anchorXOffset Type="3" Value="128.000000" />
        <anchorYOffset Type="3" Value="-6.000000" />
        <scale Type="3" Value="1.000000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightShipAmmo>
    <FreeFlightTargetingComputer>
        <anchorAlignment Type="3" Value="4.000000" />
        <anchorXOffset Type="3" Value="5.000000" />
        <anchorYOffset Type="3" Value="5.000000" />
        <scale Type="3" Value="1.050000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightTargetingComputer>
    <FreeFlightPowerSettings>
        <anchorAlignment Type="3" Value="2.000000" />
        <anchorXOffset Type="3" Value="215.000000" />
        <anchorYOffset Type="3" Value="-15.000000" />
        <scale Type="3" Value="1.000000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightPowerSettings>
    <FreeFlightMissileLockIndicator>
        <anchorAlignment Type="3" Value="7.000000" />
        <anchorXOffset Type="3" Value="0.000000" />
        <anchorYOffset Type="3" Value="150.000000" />
        <scale Type="3" Value="1.000000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightMissileLockIndicator>
    <FreeFlightMiniMap>
        <anchorAlignment Type="3" Value="5.000000" />
        <anchorXOffset Type="3" Value="0.000000" />
        <anchorYOffset Type="3" Value="-10.000000" />
        <scale Type="3" Value="1.250000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightMiniMap>
    <FreeFlightScorecard>
        <anchorAlignment Type="3" Value="7.000000" />
        <anchorXOffset Type="3" Value="0.000000" />
        <anchorYOffset Type="3" Value="0.000000" />
        <scale Type="3" Value="1.000000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightScorecard>
    <FreeFlightCopilotBark>
        <anchorAlignment Type="3" Value="2.000000" />
        <anchorXOffset Type="3" Value="16.000000" />
        <anchorYOffset Type="3" Value="-305.000000" />
        <scale Type="3" Value="1.000000" />
        <enabled Type="2" Value="1" />
        <alpha Type="3" Value="100.000000" />
    </FreeFlightCopilotBark>
"""


class UIParser(object):
    def __init__(self, file_name):
        if not os.path.exists(file_name):
            file_name = os.path.join(utilities.get_swtor_directory(), "swtor", "settings", "GUIProfiles", file_name)
        if not os.path.exists(file_name):
            raise ValueError("Path received by UIParser not valid: %s" % file_name)
        self.parser = xmlparser.parse(file_name )


