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

components_english = {'3330936116609024': 'Hyperspace Beacon', 
                      '3300630827368448': 'Shield Power Converter', 
                      '3294609283219456': 'Distortion Field', 
                      '3295356607528960': 'Retro Thrusters', 
                      '3294897046028288': 'Laser Cannon', 
                      '3320048374513664': 'Snap Turn', 
                      '3362078924472320': 'EMP Field', 
                      '3295768924389637': 'Booster Recharge', 
                      '3302232850169856': 'Repair Drone', 
                      '3290932791214080': 'Light Laser Cannon', 
                      '3290958561017856': 'Burst Laser Cannon', 
                      '3298831236071424': 'Cluster Missiles', 
                      '3301777583636480': 'Slug Railgun', 
                      '3323312549658624': 'Concussion Mine', 
                      '3397954786295808': 'Interdiction Missile', 
                      '3292272821010432': 'Quad Laser Cannon', 
                      '3295305067921408': 'Rocket Pod', 
                      '3298985854894080': 'Proton Torpedo', 
                      '3301949382328320': 'Feedback Shield', 
                      '3298981559926784': 'Ion Missile', 
                      '3296133996609536': 'Sabotage Probe', 
                      '3321744886595584': 'Remote Slicing', 
                      '3300639417303040': 'Overcharged Shield', 
                      '3295313657856000': 'Barrel Roll', 
                      '3292320065650688': 'Targeting Telemetry', 
                      '811980747177984': 'Charged Plating', 
                      '3321878030581760': 'Interdiction Drive', 
                      '3325030536577024': 'Seismic Mine', 
                      '3328019833815040': 'Railgun Sentry Drone', 
                      '3300759676387328': 'Combat Command', 
                      '3357483309465600': 'EMP Missile', 
                      '3302542087815168': 'Interdiction Sentry Drone', 
                      '3295193398771712': 'Directional Shield', 
                      '3324609629782016': 'Seeker Mine', 
                      '3300751086452736': 'Repair Probes', 
                      '3301786173571072': 'Ion Railgun', 
                      '3295317952823296': 'Power Dive', 
                      '3295309362888704': 'Koiogran Turn', 
                      '3295425327005696': 'Tensor Field', 
                      '3290962855985152': 'Heavy Laser Cannon', 
                      '3298960085090304': 'Concussion Missile', 
                      '3325073486249984': 'Thermite Torpedo', 
                      '3301794763505664': 'Plasma Railgun', 
                      '3311600173842432': 'Fortress Shield', 
                      '3300703841812480': 'Shield Projector', 
                      '3327289689374720': 'Interdiction Mine', 
                      '3326061328728064': 'Ion Mine'}

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
                   "Railgun", "Railgun Sentry Drone", "Interdiction Sentry Drone", "Missile Sentry Drone", # Railgun = Railgun Sentry Drone
                   "Shield Projector", "Repair Drone", "Overcharged Shield"]
razorwireAbilities = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon",
                      "Seismic Mine", "Proton Torpedo", "Seeker Mine",
                      "Shield Power Converter", "Interdiction Drive", "Hyperspace Beacon",
                      "Interdiction Mine", "Concussion Mine", "Ion Mine",
                      "Charged Plating", "Overcharged Shield", "Shield Projector"]
decimusAbilities = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon", "Quad Laser Cannon",
                    "Cluster Missiles", "Concussion Missile", "Proton Torpedo",
                    "Shield Power Converter", "Power Dive", "Interdiction Drive",
                    "Ion Mine", "Concussion Mine", "Interdiction Sentry Drone",
                    "Overcharged Shield", "Directional Shield", "Charged Plating"]
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
                     "Selfdamage", "Secondary Weapon Swap", "Primary Weapon Swap", "Sabotage Probe",
                     "Plasma Burn", "Plasma Warheads"]

ships = ["Legion", "Decimus", "Razorwire", "Jurgoran", "Dustmaker", "Mangler", "Bloodmark", "Blackbolt", "Sting", "Imperium", "Rycer", "Quell"]
rep_ships = {"Legion":"Warcarrier",
             "Razorwire":"Rampart Mark Four",
             "Decimus":"Sledgehammer",
             "Mangler": "Quarrel",
             "Jurgoran":"Condor",
             "Dustmaker":"Comet Breaker",
             "Rycer":"Star Guard",
             "Imperium":"Clarion",
             "Quell":"Pike",
             "Sting":"Flashfire",
             "Bloodmark":"Spearpoint",
             "Blackbolt":"Novadive"}
ships_rep = {"Legion" : "Warcarrier", "Decimus" : "Sledgehammer", "Razorwire" : "Rampart Mark Four",
             "Jurgoran" : "Condor", "Dustmaker" : "Comet Breaker", "Mangler" : "Quarrel",
             "Bloodmark" : "Spearpoint", "Blackbolt" : "Novadive", "Sting" : "Flashfire",
             "Imperium" : "Clarion", "Rycer" : "Star Guard", "Quell" : "Pike"}
ships_strings = ["Legion\t", "Decimus\t", "Razorwire\t", "Jurgoran\t", "Dustmaker", "Mangler\t", "Bloodmark", "Blackbolt\t", "Sting\t", "Imperium\t", "Rycer\t", "Quell\t"]