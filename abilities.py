# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

components = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon", "Quad Laser Cannon", "Rapid-fire Laser Cannon", "Ion Cannon", "Burst Laser Cannon",
              "Proton Torpedo", "Concussion Missile", "Thermite Torpedo", "Cluster Missiles", "Seeker Mine", "Rocket Pod", "EMP Missile", "Ion Missile",
                    "Sabotage Probe", "Seismic Mine", "Slug Railgun", "Ion Railgun", "Plasma Railgun", "Interdiction Missile",
              "Shield Power Converter", "Weapon Power Converter", "Engine Power Converter", "Rotational Thrusters", "Koiogran Turn", "Snap Turn", "Retro Thrusters",
                    "Power Dive", "Interdiction Drive", "Hyperspace Beacon", "Barrel Roll",
              "Railgun Sentry Drone", "Interdiction Sentry Drone", "Missile Sentry Drone", "Targeting Telemetry", "Blaster Overcharge", "Booster Recharge",
                    "Combat Command", "Repair Probes", "Remote Slicing", "Sensor Beacon", "EMP Field", "Interdiction Mine", "Ion Mine", "Concussion Mine", "Tensor Field", 
              "Charged Plating", "Overcharged Shield", "Shield Projector", "Repair Drone", "Overcharged Shield", "Fortress Shield", "Feedback Shield",
                    "Directional Shield", "Distortion Field", "Quick-charge Shield"]

primaries = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon", "Quad Laser Cannon", "Rapid-fire Laser Cannon", "Ion Cannon", "Burst Laser Cannon"]
secondaries = ["Proton Torpedo", "Concussion Missile", "Thermite Torpedo", "Cluster Missiles", "Seeker Mine", "Rocket Pod", "EMP Missile", "Ion Missile",
                    "Sabotage Probe", "Seismic Mine", "Slug Railgun", "Ion Railgun", "Plasma Railgun", "Interdiction Missile"]
engines = ["Shield Power Converter", "Weapon Power Converter", "Engine Power Converter", "Rotational Thrusters", "Koiogran Turn", "Snap Turn", "Retro Thrusters",
                    "Power Dive", "Interdiction Drive", "Hyperspace Beacon", "Barrel Roll"]
systems = ["Railgun Sentry Drone", "Interdiction Sentry Drone", "Missile Sentry Drone", "Targeting Telemetry", "Blaster Overcharge", "Booster Recharge",
                    "Combat Command", "Repair Probes", "Remote Slicing", "Sensor Beacon", "EMP Field", "Interdiction Mine", "Ion Mine", "Concussion Mine", "Tensor Field"]
shields = ["Charged Plating", "Overcharged Shield", "Shield Projector", "Repair Drone", "Overcharged Shield", "Fortress Shield", "Feedback Shield",
                    "Directional Shield", "Distortion Field", "Quick-charge Shield"]

# These lists were made with the help of Yellowbird
legionAbilities = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon",
                   "Proton Torpedo", "Concussion Missile", "Seeker Mine",
                   "Shield Power Converter", "Interdiction Drive",
                   "Railgun Sentry Drone", "Interdiction Sentry Drone", "Missile Sentry Drone",
                   "Shield Projector", "Repair Drone", "Overcharged Shield"]
razorwireAbilities = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon",
                      "Seismic Mine", "Proton Torpedo", "Seeker Mine",
                      "Shield Power Converter", "Interdiction Drive", "Hyperspace Beacon",
                      "Interdiction Mine", "Concussion Mine", "Ion Mine",
                      "Charged Plating", "Overcharged Shield", "Shield Projector"]
decimusAbilities = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon", "Quad Laser Cannon",
                    "Cluster Missiles", "Concussion Missile", "Proton Torpedo"
                    "Shield Power Converter", "Power Dive", "Interdiction Drive",
                    "Ion Mine", "Concussion Mine", "Interdiction Sentry Drone"]
jurgoranAbilities = ["Burst Laser Cannon", "Light Laser Cannon", "Laser Cannon",
                     "Cluster Missiles", "Slug Railgun", "Interdiction Missile", "EMP Missile"
                     "Koiogran Turn", "Retro Thrusters", "Power Dive", "Interdiction Drive",
                     "Directional Shield", "Feedback Shield", "Distortion Field", "Fortress Shield"]
dustmakerAbilities = ["Laser Cannon", "Heavy Laser Cannon",
                      "Proton Torpedo", "Thermite Torpedo", "Plasma Railgun", "Slug Railgun",
                      "Weapon Power Converter", "Rotational Thrusters", "Interdiction Drive", "Barrel Roll",
                      "Fortress Shield", "Directional Shield", "Feedback Shield"]
manglerAbilities = ["Light Laser Cannon", "Burst Laser Cannon",
                    "Plasma Railgun", "Slug Railgun", "Ion Railgun",
                    "Rotational Thrusters", "Barrel Roll", "Interdiction Drive", "Weapon Power Converter",
                    "Feedback Shield", "Fortress Shield", "Distortion Field"]
bloodmarkAbilities = ["Light Laser Cannon", "Laser Cannon", "Rapid-fire Laser Cannon",
                      "Ion Missile", "EMP Missile", "Thermite Torpedo",
                      "Snap Turn", "Power Dive", "Interdiction Drive", "Koiogran Turn"
                      "Combat Command", "Tensor Field", "Sensor Beacon", "Targeting Telemetry",
                      "Shield Projector", "Repair Drone", "Distortion Field"]
blackboltAbilities = ["Rapid-fire Laser Cannon", "Light Laser Cannon", "Laser Cannon",
                      "Rocket Pod", "Thermite Torpedo", "Sabotage Probe",
                      "Power Dive", "Snap Turn", "Barrel Roll", "Koiogran Turn",
                      "Targeting Telemetry", "EMP Field", "Booster Recharge", "Sensor Beacon",
                      "Distortion Field", "Quick-charge Shield", "Engine Power Converter"]
stingAbilities = ["Burst Laser Cannon", "Light Laser Cannon", "Quad Laser Cannon", "Rapid-fire Laser Cannon",
                  "Rocket Pod", "Cluster Missiles", "Sabotage Probe"
                  "Koiogran Turn", "Retro Thrusters", "Power Dive", "Barrel Roll",
                  "Targeting Telemetry", "Blaster Overcharge", "Booster Recharge",
                  "Distortion Field", "Quick-charge Shield", "Directional Shield"]
imperiumAbilities = ["Quad Laser Cannon", "Rapid-fire Laser Cannon", "Light Laser Cannon",
                     "Thermite Torpedo", "EMP Missile", "Proton Torpedo", "Ion Missile",
                     "Koiogran Turn", "Shield Power Converter", "Power Dive", "Interdiction Drive",
                     "Combat Command", "Remote Slicing", "Repair Probes",
                     "Charged Plating", "Directional Shield", "Shield Projector"]
rycerAbilities = ["Quad Laser Cannon", "Ion Cannon", "Rapid-fire Laser Cannon", "Heavy Laser Cannon", "Laser Cannon",
                  "Concussion Missile", "Cluster Missiles", "Proton Torpedo",
                  "Weapon Power Converter", "Retro Thrusters", "Barrel Roll", "Koiogran Turn",
                  "Charged Plating", "Quick-charge Shield", "Directional Shield"]
quellAbilities = ["Heavy Laser Cannon", "Quad Laser Cannon", "Light Laser Cannon",
                  "Cluster Missiles", "Ion Missile", "Proton Torpedo", "Concussion Missile", "EMP Missile",
                  "Weapon Power Converter", "Shield Power Converter", "Koiogran Turn", "Barrel Roll",
                  "Quick-charge Shield", "Directional Shield", "Charged Plating"]
excluded_abilities = ["Wingman", "Hydro Spanner", "In Your Sights", "Slicer's Loop",
                     "Servo Jammer", "Lockdown", "Concentrated Fire", "Lingering Effect",
                     "Bypass", "Running Interference", "Suppression", "Nullify", "Hull Cutter",
                     "Selfdamage", "Secondary Weapon Swap", "Primary Weapon Swap", "Sabotage Probe"]

# DEBUG
ships_components = [legionAbilities, razorwireAbilities, decimusAbilities, manglerAbilities, dustmakerAbilities, jurgoranAbilities,
                    bloodmarkAbilities, blackboltAbilities, stingAbilities, imperiumAbilities, quellAbilities, rycerAbilities]
# DEBUG END