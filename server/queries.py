"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
"""
This file contains all queries needed for the server program to work
correctly with the database. All queries are triple-quoted strings with
passable values through %() operators. The databases are created using the
create_tb_* queries. To insert data, there are the insert_* queries and
to select data from the database get_* queries are used.

First the database Server is created, in which all servers must be put
with a three-letter shortcode and a serverlocation, also a three-letter
shortcode (NAE, NAW, EUR).
This database is referenced by the Alt table, containing data about the
characters in the database. These characters have a name, but also a name
of a character they belong to in case they are alts of a player and the
player prefers to have the name of his/her main character shown to other
users of the parser.
Then there's the table Combatlog in which the hash of a Combatlog, a string
of a list of Combatlog lines and an index number are stored. The hash is to
gain the ability to check whether a Combatlog has already been entered into
the database. This data is used so the server will be able to calculate
statistics on its own for reliability of the data of the Leaderboards.
The Id table stores the idhashes of players with a link to their respective
names and, optionally, the index number of the Combatlog in which this id
number can be found.

The standalone table Bombers contains the damage dealt by bombers to players,
as this damage is not logged in the Combatlog of the bomber itself, and this
makes the damage dealt calculation of a bomber very unreliable. In order to
work around this, the GSF Parser can ask for this data in the database and
recalculate damage dealt.
The standalone table Killedby contains idhashes of a killer and a victim so
the amount of kills can be calculated and victims can identify their killers.

IMPORTANT NOTE: Instead of idhashes, normal ID numbers might be used in the
future, because of the decrease in required processing power and increased
simplicity of the overall program structure.
"""

### SERVER TABLE ###
# Query to create the table Server
# servername is a three-letter shortcode for the servername
# serverlocation is a three-letter shortcode for the serverlocation
create_tb_server = """CREATE TABLE IF NOT EXISTS Server(
                      servername TEXT PRIMARY KEY,
                      serverlocation TEXT);
                      """
# Query to insert a server into the Servers table
# servername is a three-letter shortcode for the servername
# serverlocation is a three-letter schortcode for the server location
#   EUR = Europa
#   NAE = North America Eastcoast
#   NAW = North America Westcoast
insert_server = """INSERT OR IGNORE INTO Server(servername, serverlocation) VALUES ('%s', '%s');"""
# Query to select all servers of a certain region
get_servers_by_location = """SELECT FROM Server WHERE serverlocation == %s;"""
# Query to select all servers and their regions (return tuples with fetchall)
get_all_servers = """SELECT * FROM Server;"""

### ALT TABLE ###
# Query to create the table Alt
# WARNING: Alt REFERENCES Server, SO Server MUST EXIST
# altname is the name of the character
# belongsto is the name of the specified main character of the player
# server is a three-letter shortcode for the name of the server
# faction is a three-letter shortcode for the faction of the character
# primealt is an integer that is 1 when the alt is specified as a main character and
#   0 when this is not the case and the character is an alt of another main character
create_tb_alt = """
    CREATE TABLE IF NOT EXISTS Alt(
    altname TEXT,
    belongsto TEXT,
    server TEXT,
    faction TEXT,
    primealt INTEGER,
    PRIMARY KEY(altname, belongsto, server, faction),
    FOREIGN KEY(server) REFERENCES Server(servername));
"""
# This should be the first query to be executed to get the index number right
# RedFantom spelled with small letter F to match the name as written in the CombatLogs
alt_first_command = """INSERT OR IGNORE INTO Alt(altname, belongsto, server, faction, primealt) VALUES ('Redfantom', 'Redfantom', 'DM', 'IMP', 1);"""
# Query to insert a new main character into the database
# % (main_character_name, main_character_name, three-letter shortcode for server, three-letter shortcode for faction)
insert_main_character = """INSERT OR IGNORE INTO Alt(altname, belongsto, server, faction, primealt) VALUES ('%s', '%s', '%s', '%s', 1);"""
# Query to insert a new alt into the database
# % (alt_character_name, main_character_name, three-letter shortcode for server, three-letter shortcode for faction)
insert_alt_character = """INSERT OR IGNORE INTO Alt(altname, belongsto, server, faction, primealt) VALUES ('%s', '%s', '%s', '%s', 0);"""
insert_character = """INSERT OR IGNORE INTO Alt(altname, belongsto, server, faction, primealt) VALUES ('%s', '%s', '%s', '%s', %s);"""
# This is a list of test queries for the database
list_of_tests = [alt_first_command, insert_main_character % ("Yellowbird", "Yellowbird", "DM", "IMP"),
                 insert_main_character % ("Pyril", "Pyril", "DM", "IMP"),
                 insert_alt_character % ("Eighty-three", "Redfantom", "DM", "REP")]
# Query to get all alt names belonging to a certain character
# % (maincharacter_name)
get_all_alts = """SELECT altname FROM Alt WHERE belongsto == '%s';"""
# Query to get the main character for an alt
# % (alt_name)
get_main_char = """SELECT belongsto FROM Alt WHERE altname == '%s';"""
# Query to insert an alt name when not existing
# % (altname, mainname, server, faction, primealt)
insert_alt_ifnotexist = """INSERT OR IGNORE INTO Alt(altname, belongsto, server, faction, primealt) VALUES ('%s', '%s', '%s', '%s', %s)"""

### COMBATLOG TABLE ###
# Query to create the table Combatlog
# WARNING: Combatlog REFERENCES Alt AND Server SO THEY MUST EXIST
# loghash is the hash of the whole log file (SHA256)
# logdate is the unixtime of the datetime generated from the name of the combatlog
# log is a string made of a list of lines of the log ("['line', 'line', 'line', ...]")
# serv is a three-letter shortcode for the name of the server
# alt is the name of the character named in the combatlog
create_tb_combatlogs = """
    CREATE TABLE IF NOT EXISTS Combatlog(
    loghash TEXT PRIMARY KEY,
    logdate INTEGER,
    log TEXT,
    serv TEXT,
    FOREIGN KEY(serv) REFERENCES Server(servername));
"""
# This should be the first query to be executed to get the index number right
# % (hash_of_combatlog_txt, 0 {start of unixtime), list_of_lines_from_combatlog_txt)
combatlog_first_command = """INSERT OR IGNORE INTO Combatlog(loghash, logdate, log, serv) VALUES ('%s', 0, '%s', 'DM');"""
# Query to insert a new combatlog into the table
# % (hash_of_the_log_file, unixtime_of_the_log_file, string_of_list_of_lines_of_the_log_file, player_name_in_the_log_file)
insert_combatlog = """INSERT OR IGNORE INTO Combatlog(loghash, logdate, log, serv) VALUES ('%s', %s, '%s');"""
# Query to get all combatlogs for a certain character
# % (name_of_the_character)
get_combatlogs_by_alt = """SELECT log FROM Combatlog WHERE alt == '%s'"""
# Query to get all combatlogs for a certain server
# % (three-letter_shortcode_for_server)
get_combatlogs_by_server = """SELECT log FROM Combatlog WHERE serv == '%s'"""
# Query to get all combatlogs for a certain time period
# % (unixtime_one, unixtime_two)
get_combatlogs_by_period = """SELECT log FROM Combatlog WHERE logdate BETWEEN %s AND %s;"""
"""
DEPRECATED
# Query to get number of combatlog for a certain ID number
# % (server_shortcode, alt_name, logdate_unixtime)
get_logid = '''SELECT logID FROM Combatlog WHERE serv == '%s' AND alt == '%s' AND logdate == %s'''
"""
# Query to get all log hashes for a certain location
# % (serverlocation)
get_loghashes_by_location = """SELECT loghash FROM Combatlog WHERE serv IN (SELECT servername FROM Server WHERE serverlocation == '%s');"""
# Query to get all log hashes for a certain server
# % (servername)
get_loghashes_by_server = """SELECT loghash FROM Combatlog WHERE serv == '%s';"""

### ID TABLE ###
# Query to create the table Id
# WARNING: Id REFERENCES Server AND Combatlog AND Matches SO THEY MUST EXIST
# IDhash is a hash of an ID number
# server is a three-letter shortcode for a server
# combatlog is the combatlog in Combatlog that contains the ID
create_tb_id = """
    CREATE TABLE IF NOT EXISTS Id(
    IDhash TEXT,
    server TEXT,
    char TEXT NOT NULL,
    combatlog TEXT,
    PRIMARY KEY (IDhash, server),
    FOREIGN KEY(server) REFERENCES Server(servername),
    FOREIGN KEY(char) REFERENCES Alt(altname),
    FOREIGN KEY(combatlog) REFERENCES Combatlog(loghash));
"""
# Query to insert an ID with a server
# % (string_of_id_hash, three-letter_shortcode_for_server, name of the character)
insert_id_name = """INSERT OR IGNORE INTO Id(IDhash, server, char) VALUES ('%s', '%s', '%s');"""
# Query to insert an ID with a server and a combatlog
insert_id_name_combatlog = """INSERT OR IGNORE INTO Id(Idhash, server, char, combatlog) VALUES ('%s', '%s', '%s', %s);"""
# Query to add a combatlog a certain hash, server and char
update_combatlog = """UPDATE Id SET combatlog = %s WHERE Idhash == '%s' AND server == '%s' AND char == '%s';"""

### KILLEDBY TABLE ###
# Query to create table KilledBy
# killer is an ID hash
# victim is an ID hash
# server is a server shortcode
create_tb_killedby = """
    CREATE TABLE IF NOT EXISTS KilledBy(
    killer TEXT,
    victim TEXT,
    server TEXT,
    PRIMARY KEY(killer, victim, server),
    FOREIGN KEY(server) REFERENCES Server(servername));
"""
# Query to get the killer of a certain ID hash
# % (server_shortcode, victim_id_hash)
get_killer = """SELECT killer FROM KilledBy WHERE victim == '%s' AND server == '%s';"""
# Query to get the victims of a certain ID hash
# This query can return multiple results
# % (server_shortcode, killer_id_hash)
get_victim = """SELECT victim FROM KilledBy WHERE killer == '%s' AND server == '%s';"""
# Query to insert a killer-victim combination with a server
# % (killer, victim, server_shortcode)
insert_kill = """INSERT OR IGNORE INTO KilledBy(killer, victim, server) VALUES ('%s', '%s', '%s');"""
# Query to get all kills for a certain server
# % (server_shortcode)
get_kills_by_server = """SELECT killer, victim FROM KilledBy WHERE server == '%s';"""

### BOMBERS TABLE ###
# Query to create table Bombers
# bomber is an id hash of the bomber in question
# victim is an id hash of the victim of the bomb
# timing is a string of the time in the combatlog (three decimals)
# server is a server shortcode
# damage is the damage string (* for criticals)
create_tb_bombers = """
    CREATE TABLE IF NOT EXISTS Bombers(
    bomber TEXT,
    victim TEXT,
    datetime TEXT,
    server TEXT,
    damage TEXT,
    PRIMARY KEY(bomber, victim, server, datetime),
    FOREIGN KEY(server) REFERENCES Server(servername));
"""
# Query to insert a new bomb occurrence in the table
# % (bomber, victim, timing, server, damage)
insert_bomb = """INSERT OR IGNORE INTO Bombers(bomber, victim, timing, server, damage) VALUES ('%s', '%s', '%s', '%s', '%s');"""
# Query to get all bomb-damages of a bomber
# % (bomber_id_hash)
get_dmg_by_bomber = """SELECT damage FROM Bombers WHERE bomber == '%s';"""
# Query to get all bomb-damage of a victim
# % (victim_id_hash)
get_dmg_by_victim = """SELECT damage FROM Bombers WHERE victim == '%s';"""

### MULTIPLE DB QUERIES ###
# Query to get the name of the character belonging to a certain IDhash
# % (hash_of_id, server_shortcode)
get_altname_by_id = """SELECT altname FROM Alt WHERE altname IN (SELECT char FROM Id WHERE IDhash == '{}' AND server == '{}');"""
get_mainname_by_id = """SELECT belongsto FROM Combatlog WHERE loghash IN (SELECT combatlog FROM Id WHERE IDhash == '%s' AND server == '%s');"""
