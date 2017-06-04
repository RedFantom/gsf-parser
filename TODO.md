# TODO List
This is the TODO list for the targeted release of GSF Parser v3.0.0. 

## Features planned
- Implement the build calculator 
  * Connection to `CharacterFrame` with `Character` objects
  * `Ship` objects with the right statistics in the right places with the possibility add a 
    time-to-kill calculator for `Ship` objects
  * Save `Character` objects with `Ship` objects in a `pickle` database for loading after exit
  
- Finish screen parsing
  * Make `vision.py` work for GUI Parsing
  * Finish the implementation of `ScreenParser`
  * Create a parser to parse the data and calculate statistics from it for file parsing
  * Screen parsing overlay with real-time tracking penalty and time-to-kill
  * Add a spawn-timer to show when the new spawn is
  
- Implement all planned filters
  * Damage filters
  * Ship filters
  * Component filters
  * Date filters

- Implement the name functions of the GSF Server
  * The GSF-Server has working capabilities to save name-ID combinations
  * Allow the GSF Parser to create a local database of these name-ID combinations

- Finish the settings importer tool
  * Add all the latest settings to the `importer.py` file
  * Add a working GUI for exporting and importing the settings
  
- Real-time events overlay
  * With support for coloured events
  * Only the last event with the source and target name with ability name is displayed
  * Multiple positioning options
  * Size and font options (font options shared with real-time overlay)

## Dropped features
These previously planned features have been dropped until further notice:

- The leaderboard functionality
  
  All other sharing/GSF-Server-communication functionality is still planned
  
- Support for CombatLogs generated in another language

  The priority for this feature is very low
  
- Galactic StarFighter themed interface
  
  Because of the new `Arc` theme that looks better than the previous `plastik` theme, the time required 
  to create such a theme is not worth it 
  
## Ideas

- More support for calculating contributions by allied team players
- Support for number of enemies damage taken from, not just damage dealt to
- Real-time kill count overlay
- Reading the position of the player on the map


