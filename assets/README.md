# Ships database

The ships database contains a Python `pickle`, that can best be read using `cPickle`, with a dictionary of data. This
dictionary contains the following keys:
```
Republic_X7-Mirage
Imperial_TZ-24_Gladiator
Republic_Sledgehammer
Republic_Spearpoint
Imperial_ICA-X_Tormentor
Republic_SGS-45_Quarrel
Imperial_S-13_Sting
Imperial_VX-9_Mailoc
Imperial_K-52_Demolisher
Imperial_M-7_Razorwire
Republic_TZ-24_Enforcer
Imperial_GSS-4Y_Jurgoran
Imperial_S-SC4_Bloodmark
Republic_IL-5_Skybolt
Imperial_GSS-3_Mangler
Republic_X5-Whisper
Republic_K-52_Strongarm
Republic_FT-6_Pike
Republic_Rampart_Mark_Four
Republic_FT-7B_Clarion
Imperial_F-T6_Rycer
Republic_SGS-41B_Comet_Breaker
Republic_NovaDive
Imperial_IL-5_Ocula
Imperial_B-5_Decimus
Republic_Flashfire
Imperial_ICA-2B_Frostburn
Imperial_FT-3C_Imperium
Imperial_ICA-3A_-_Sable_Claw
Imperial_S-12_Blackbolt
Republic_SGS-S1_Condor
Republic_Banshee
Republic_VX-9_Redeemer
Imperial_G-X1_Onslaught
Imperial_F-T2_Quell
Republic_FT-8_Star_Guard
Republic_G-X1_Firehauler
Republic_Warcarrier
Imperial_GSS-5C_Dustmaker
Imperial_B-4D_Legion

CompanionsByCrewPosition
```

Each key points to yet another dictionary. For the ships, the keys are:
```
Engine
Stats
Reactor
PrimaryWeapon
Armor
SecondaryWeapon
ShieldProjector
Thruster
AuxSystemContainer
Systems
MinorEquipType
Sensor
```
With the possible addition of an extra key with a `2` appended to the name for ships with two components of the same
category, such as the Rycer with the `PrimaryWeapon2`. This contains the same data. Each of these keys points to a
`list` containing a dictionary with the following keys:
```
Available
Base
Stats
Name
Default
ShipRequisitionCost
HasControllerStats
TalentTree
TalentRowCosts
Icon
Description
```
`TalentTree` points to yet another dictionary, but the structure of this is dependent on the component type (Major,
Middle or Minor). 
