"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom


This file contains lists and dictionaries of the abilities and ships
used in Galactic StarFighter, in order for the parser to be able to
identify ships by their components and abilities and print them neatly
onto the screen.
"""

component_types = ["primaries", "secondaries", "systems", "engines", "shields"]
"""
All components sorted into categories of their component type
"""
primaries = (  # PrimaryWeapon
    "Heavy Laser Cannon",
    "Laser Cannon",
    "Light Laser Cannon",
    "Quad Laser Cannon",
    "Rapid-fire Laser Cannon",
    "Ion Cannon",
    "Burst Laser Cannon",
)
secondaries = (  # SecondaryWeapon
    "Proton Torpedo",
    "Concussion Missile",
    "Thermite Torpedo",
    "Cluster Missiles",
    "Seeker Mine",
    "Rocket Pod",
    "EMP Missile",
    "Ion Missile",
    "Sabotage Probe",
    "Seismic Mine",
    "Slug Railgun",
    "Ion Railgun",
    "Plasma Railgun",
    "Interdiction Missile",
    # The ability name is Rocket Pod, the component name is Rocket Pods
    "Rocket Pods",
)
engines = (  # Engine
    "Shield Power Converter",
    "Weapon Power Converter",
    "Engine Power Converter",
    "Rotational Thrusters",
    "Koiogran Turn",
    "Snap Turn",
    "Retro Thrusters",
    "Power Dive",
    "Interdiction Drive",
    "Hyperspace Beacon",
    "Barrel Roll",
)
systems = (  # Systems
    "Railgun Sentry Drone",
    "Interdiction Sentry Drone",
    "Missile Sentry Drone",
    "Targeting Telemetry",
    "Blaster Overcharge",
    "Booster Recharge",
    "Combat Command",
    "Repair Probes",
    "Remote Slicing",
    "Sensor Beacon",
    "EMP Field",
    "Interdiction Mine",
    "Ion Mine",
    "Concussion Mine",
    "Tensor Field"
)
shields = (  # Shield
    "Charged Plating",
    "Overcharged Shield",
    "Shield Projector",
    "Repair Drone",
    "Fortress Shield",
    "Feedback Shield",
    "Directional Shield",
    "Distortion Field",
    "Quick-Charge Shield"
)
copilots = (  # CoPilot active abilities
    "Lockdown",
    "Slicer's Loop",
    "Servo Jammer",
    "Wingman",
    "Lingering Effect",
    "Hydro Spanner",
    "Nullify",
    "Concentrated Fire",
    "In Your Sights",
    "Running Interference",
    "Suppression",
    "Bypass",
)

# A tuple of all active components in Galactic StarFighter
components = primaries + secondaries + engines + shields + systems

"""
These lists were made with the help of Yellowbird

Lists of the components supported by each ship
"""
legionAbilities = [
    "Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon",
    "Proton Torpedo", "Concussion Missile", "Seeker Mine",
    "Shield Power Converter", "Interdiction Drive",
    "Railgun", "Railgun Sentry Drone",  # Railgun = Railgun Sentry Drone
        "Interdiction Sentry Drone", "Missile Sentry Drone",
    "Shield Projector", "Repair Drone", "Overcharged Shield"
]
razorwireAbilities = [
    "Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon",
    "Seismic Mine", "Proton Torpedo", "Seeker Mine",
    "Shield Power Converter", "Interdiction Drive", "Hyperspace Beacon",
    "Interdiction Mine", "Concussion Mine", "Ion Mine",
    "Charged Plating", "Overcharged Shield", "Shield Projector"
]
decimusAbilities = [
    "Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon", "Quad Laser Cannon",
    "Cluster Missiles", "Concussion Missile", "Proton Torpedo",
    "Shield Power Converter", "Power Dive", "Interdiction Drive",
    "Ion Mine", "Concussion Mine", "Interdiction Sentry Drone", "EMP Field",
    "Overcharged Shield", "Directional Shield", "Charged Plating"
]
jurgoranAbilities = [
    "Burst Laser Cannon", "Light Laser Cannon", "Laser Cannon",
    "Cluster Missiles", "Slug Railgun", "Interdiction Missile", "EMP Missile",
    "Koiogran Turn", "Retro Thrusters",
    "Power Dive", "Interdiction Drive",
    "Directional Shield", "Feedback Shield", "Distortion Field", "Fortress Shield"
]
dustmakerAbilities = [
    "Laser Cannon", "Heavy Laser Cannon",
    "Proton Torpedo", "Thermite Torpedo", "Plasma Railgun", "Slug Railgun",
    "Weapon Power Converter", "Rotational Thrusters", "Interdiction Drive", "Barrel Roll",
    "Fortress Shield", "Directional Shield", "Feedback Shield"
]
manglerAbilities = [
    "Light Laser Cannon", "Burst Laser Cannon",
    "Plasma Railgun", "Slug Railgun", "Ion Railgun",
    "Rotational Thrusters", "Barrel Roll", "Interdiction Drive", "Weapon Power Converter",
    "Feedback Shield", "Fortress Shield", "Distortion Field"
]
bloodmarkAbilities = [
    "Light Laser Cannon", "Laser Cannon", "Rapid-fire Laser Cannon",
    "Ion Missile", "EMP Missile", "Thermite Torpedo",
    "Snap Turn", "Power Dive", "Interdiction Drive", "Koiogran Turn",
    "Combat Command", "Tensor Field",
    "Sensor Beacon", "Targeting Telemetry",
    "Shield Projector", "Repair Drone", "Distortion Field"
]
blackboltAbilities = [
    "Rapid-fire Laser Cannon", "Light Laser Cannon", "Laser Cannon",
    "Rocket Pod", "Thermite Torpedo", "Sabotage Probe",
    "Power Dive", "Snap Turn", "Barrel Roll", "Koiogran Turn",
    "Targeting Telemetry", "EMP Field", "Booster Recharge", "Sensor Beacon",
    "Distortion Field", "Quick-Charge Shield", "Engine Power Converter"
]
stingAbilities = [
    "Burst Laser Cannon", "Light Laser Cannon", "Quad Laser Cannon", "Rapid-fire Laser Cannon",
    "Rocket Pod", "Cluster Missiles", "Sabotage Probe",
    "Koiogran Turn", "Retro Thrusters", "Power Dive", "Barrel Roll",
    "Targeting Telemetry", "Blaster Overcharge", "Booster Recharge",
    "Distortion Field", "Quick-Charge Shield", "Directional Shield"
]
imperiumAbilities = [
    "Quad Laser Cannon", "Rapid-fire Laser Cannon", "Light Laser Cannon",
    "Thermite Torpedo", "EMP Missile", "Proton Torpedo", "Ion Missile",
    "Koiogran Turn", "Shield Power Converter", "Power Dive", "Interdiction Drive",
    "Combat Command", "Remote Slicing", "Repair Probes",
    "Charged Plating", "Directional Shield", "Shield Projector"
]
rycerAbilities = [
    "Quad Laser Cannon", "Ion Cannon", "Rapid-fire Laser Cannon", "Heavy Laser Cannon", "Laser Cannon",
    "Concussion Missile", "Cluster Missiles", "Proton Torpedo",
    "Weapon Power Converter", "Retro Thrusters", "Barrel Roll", "Koiogran Turn",
    "Charged Plating", "Quick-Charge Shield", "Directional Shield"
]
quellAbilities = [
    "Heavy Laser Cannon", "Quad Laser Cannon", "Light Laser Cannon",
    "Cluster Missiles", "Ion Missile", "Proton Torpedo", "Concussion Missile", "EMP Missile",
    "Weapon Power Converter", "Shield Power Converter", "Koiogran Turn", "Barrel Roll",
    "Quick-Charge Shield", "Directional Shield", "Charged Plating"
]

# Abilities that are excluded from parsing
excluded_abilities = [
    "Wingman", "Hydro Spanner", "In Your Sights", "Slicer's Loop",
    "Servo Jammer", "Lockdown", "Concentrated Fire", "Lingering Effect",
    "Bypass", "Running Interference", "Suppression", "Nullify", "Hull Cutter",
    "Selfdamage", "Secondary Weapon Swap", "Primary Weapon Swap", "Sabotage Probe",
    "Plasma Burn", "Plasma Warheads", "Space Exhaustion", "Invulnerable", "Self Destruct",
    "Tutorial", "Melting Hull", "Contamination", "Scope Mode", "Launch Projectile"
]

# All ships with their Imperial Faction names available in GSF
ships = [
    "Legion", "Decimus", "Razorwire",
    "Jurgoran", "Dustmaker", "Mangler",
    "Bloodmark", "Blackbolt", "Sting",
    "Imperium", "Rycer", "Quell"
]
# Ships abilities
ships_abilities = {
    "Legion": legionAbilities,
    "Decimus": decimusAbilities,
    "Razorwire": razorwireAbilities,
    "Jurgoran": jurgoranAbilities,
    "Dustmaker": dustmakerAbilities,
    "Mangler": manglerAbilities,
    "Bloodmark": bloodmarkAbilities,
    "Blackbolt": blackboltAbilities,
    "Sting": stingAbilities,
    "Imperium": imperiumAbilities,
    "Rycer": rycerAbilities,
    "Quell": quellAbilities
}

# A dictionary for converting the names of the ships to the Republic Faction
# names, for future feature of allowing both faction names
rep_ships = {
    "Legion": "Warcarrier",
    "Razorwire": "Rampart Mark Four",
    "Decimus": "Sledgehammer",
    "Mangler": "Quarrel",
    "Jurgoran": "Condor",
    "Dustmaker": "Comet Breaker",
    "Rycer": "Star Guard",
    "Imperium": "Clarion",
    "Quell": "Pike",
    "Sting": "Flashfire",
    "Bloodmark": "Spearpoint",
    "Blackbolt": "Novadive"
}

# The ships with their Imperial Faction names to print on the screen, with \t padding
# to make the printing look the same for every ship.
ships_strings = [
    "Legion\t", "Decimus\t", "Razorwire\t",
    "Jurgoran\t", "Dustmaker", "Mangler\t",
    "Bloodmark", "Blackbolt\t", "Sting\t",
    "Imperium\t", "Rycer\t", "Quell\t"
]

rep_strings = {
    "Legion\t": "Warcarrier",
    "Razorwire\t": "Rampart Mark Four",
    "Decimus\t": "Sledgehammer",
    "Mangler\t": "Quarrel\t",
    "Jurgoran\t": "Condor\t",
    "Dustmaker": "Comet Breaker",
    "Rycer\t": "Star Guard",
    "Imperium\t": "Clarion\t",
    "Quell\t": "Pike\t",
    "Sting\t": "Flashfire\t",
    "Bloodmark": "Spearpoint",
    "Blackbolt\t": "Novadive\t"
}

all_ships = {
    "Legion": "Warcarrier",
    "Razorwire": "Rampart Mark Four",
    "Decimus": "Sledgehammer",
    "Mangler": "Quarrel",
    "Jurgoran": "Condor",
    "Dustmaker": "Comet Breaker",
    "Rycer": "Star Guard",
    "Imperium": "Clarion",
    "Quell": "Pike",
    "Sting": "Flashfire",
    "Bloodmark": "Spearpoint",
    "Blackbolt": "Novadive",
    "Frostburn": "Whisper",
    "Sable Claw": "Mirage",
    "Tormentor": "Banshee",
    "Ocula": "Skybolt",
    "Onslaught": "Firehauler",
    "Mailoc": "Redeemer",
    "Demolisher": "Strongarm",
    "Gladiator": "Enforcer"
}

ships_dual_secondaries = ["Mangler", "Jurgoran", "Dustmaker", "Quell"]
ships_dual_primaries = ["Rycer"]
