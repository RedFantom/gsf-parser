# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

"""
Dictionary describing the duration of AoE effects
"""
durations = {
    # (ability: (allied, duration, DoT)
    "Combat Command": (True, 24, False),
    "EMP Field": (False, 13, False),
    "Tensor Field": (True, 24, False),
    "Repair Probes": (True, 24, False),
    "EMP Missile": (False, 10, False),
    "Interdiction Drive": (False, 9, False),
    "Targeting Telemetry": (False, 15, False),
    "Wingman": (True, 20, False),
    "Running Interference": (True, 15, False),
    "Melting Hull": (False, 4, True),
    "Plasma Burn": (False, 6, True),
    "Plasma Warheads": (False, 10, True),
    "Cluster Missiles": (False, 15, True),
    "Concussion Missile": (False, 15, False)
}

special_cases = ["EMP Missile", "EMP Field", "Plasma Warheads"]
