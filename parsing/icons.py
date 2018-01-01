# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

icons = {
    # Primary Weapons
    "Heavy Laser Cannon": "spvp_blaster_black_red",
    "Laser Cannon": "spvp_blaster_red",
    "Light Laser Cannon": "spvp_blaster_black_orange",
    "Quad Laser Cannon": "spvp_blaster_black_yellow",
    "Rapid-Fire Laser Cannon": "spvp_blaster_yellow",
    "Ion Cannon": "spvp_blaster_black_light_blue",
    "Burst Laser Cannon": "spvp_blaster_black_purple",
    # Secondary Weapons
    "Proton Torpedo": "spvp_protontorpedoes",
    "Concussion Missile": "spvp_concussionmissiles",
    "Thermite Torpedo": "spvp_plasmacruisemissile",
    "Cluster Missiles": "spvp_clustermissiles",
    "Seeker Mine": "spvp_gravitoncharges",
    "Rocket Pod": "spvp_rocketpods",
    "EMP Missile": "spvp_ioncruisemissile",
    "Ion Missile": "spvp_ionmissiles",
    "Sabotage Probe": "spvp_targettracker",
    "Seismic Mine": "spvp_interdictorsentrydome",
    "Slug Railgun": "spvp_railgun",
    "Ion Railgun": "spvp_ionrailgun",
    "Plasma Railgun": "spvp_plasmarailgun",
    "Interdiction Missile": "spvp_cruisemissile",
    # Engine components
    "Hyperspace Beacon": "spvp_sensorprobe",
    "Shield Power Converter": "spvp_powertransfertoshields",
    "Weapon Power Converter": "spvp_powertransfertoweapons",
    "Engine Power Converter": "spvp_powertransfertoengine",
    "Rotational Thrusters": "spvp_facetarget",
    "Koiogran Turn": "spvp_koiogranturn",
    "Power Dive": "spvp_powerdive",
    "Interdiction Drive": "spvp_servojammer",
    "Barrel Roll": "spvp_barrelroll",
    "Retro Thrusters": "spvp_retrothrusters",
    "Snap Turn": "spvp_facetarget",
    # Shield components
    "Distortion Field": "spvp_distortionfield",
    "Charged Plating": "spvp_damagereduction",
    "Overcharged Shield": "spvp_overchargedshield",
    "Shield Projector": "spvp_shieldprojector",
    "Repair Drone": "spvp_repairdrone",
    "Fortress Shield": "spvp_fortressshield",
    "Feedback Shield": "spvp_feedbackshield",
    "Directional Shield": "spvp_directionalshield",
    "Quick-Charge Shield": "spvp_quickrechargeshield",
    # System abilities
    "Railgun Sentry Drone": "spvp_reacallbeacon",
    "Interdiction Sentry Drone": "spvp_interdictorsentrydome",
    "Missile Sentry Drone": "spvp_missilesentrydome",
    "Targeting Telemetry": "spvp_sensorsweep",
    "Blaster Overcharge": "spvp_primaryweaponrof",
    "Booster Recharge": "spvp_enginepower",
    "Combat Command": "spvp_aoeoffensiveboost",
    "Repair Probes": "spvp_aoedefensiveboost",
    "Remote Slicing": "spvp_communicationjammed1",
    "Sensor Beacon": "spvp_sensorbeacon",
    "EMP Field": "spvp_jammingfield",
    "Interdiction Mine": "spvp_interdictionmines",
    "Ion Mine": "spvp_ionmines",
    "Concussion Mine": "spvp_hullcharges",
    "Tensor Field": "spvp_tensorfield",
    # Miscellaneous abilities
    "Secondary Weapon Swap": "spvp_secondaryweaponswap",
    "Primary Weapon Swap": "spvp_primaryweaponswap",
    # Overcharges
    "Damage Overcharge": "spvp_increasedduration_red",
    "Shield Overcharge": "spvp_increasedduration_green",
    "Weapon Overcharge": "spvp_increasedduration",
    "Engine Overcharge": "spvp_increasedduration_purple",
    # Crew abilities
    "Slicer's Loop": "spvp_infiniteloop",
    "Hydro Spanner": "spvp_hardreset",
    "Nullify": "spvp_hardreset",
    "Lockdown": "spvp_powerdrainengine",
    "In Your Sights": "spvp_targetpainter",
    "Servo Jammer": "improvedelectronicwarfarepod",
    "Bypass": "spvp_shieldpiercing",
    "Concentrated Fire": "spvp_increasedsystemsdamagechance",
    "Running Interference": "spvp_evasion",
    "Wingman": "spvp_wingman",
    "Suppression": "spvp_suppression",
    "Lingering Effect": "spvp_damageovertime",
    # Effects
    "Melting Hull": "spvp_protontorpedoes",  # Proton Torpedo DoT
    "Hyperspace Slingshot": "spvp_increaseenginepowerefficiency",  # Hyperspace Beacon speed upgrade
    "Railgun": "spvp_hyperspacebeacon",  # Railgun Sentry Drone damage
    "Selfdamage": "spvp_decoybeacon",  # Damage dealt to self
    "Space Exhaustion": "spvp_decoybeacon",  # Out of map bounds
    "Hull Resonance": "spvp_damageovertime",  # Seismic Mine DoT
    "Contamination": "spvp_targettracker",
    "Damage": "spvp_damagereduction",
    "Drone Disabled": "spvp_jammingfield",
    "System Ability Disabled": "spvp_reducedpowerdraw1",
    "Engine Ability Disabled": "spvp_reducedpowerdraw",
    "Shield Ability Disabled": "spvp_reducedpowerdraw2",
    "Missile Lock Immunity": "spvp_missiletargeting",
    "Accuracy Reduced": "spvp_communicationjammed",
    "Sensors Jammed": "spvp_sensorshadows",
    "Plasma Warheads": "spvp_damageovertime",  # Rocket Pods DoT
    "Plasma Burn": "spvp_plasmarailgun",  # Plasma Railgun DoT
    "Scope Mode": "spvp_cloakdisruption",  # Gunship Scope Mode
    "Invulnerable": "spvp_aoedefensiveboost",  # Tutorial Effect
    "Tutorial": "spvp_hardreset",  # Tutorial Effect
    # Default
    "default": "republic.png"
}
