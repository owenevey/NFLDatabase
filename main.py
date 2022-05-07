# Owen Evey
# CSE 480 Spring Semester 2022 Honors Option

import os
import csv
import sqlite3

def AddPlayers(db_filename):
    # Adds players table to database

    con = sqlite3.connect(db_filename)
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS players")

    # Create table with schema
    cur.execute('''CREATE TABLE players(name TEXT, team TEXT,
                age INTEGER, college TEXT, position TEXT, PRIMARY KEY (name))''')

    roster_directory = "Data/Rosters"

    # Iterate through each roster file
    for filename in os.listdir(roster_directory):

        # Creates accessible filename
        f = roster_directory + '/' + filename

        # Open file under read permissions
        with open(f, 'r') as csv_file:

            csv_reader = csv.reader(csv_file)

            next(csv_reader)

            for row in csv_reader:
                try:
                    # Names come in the format "name//ID"
                    # Retrieves just the name
                    name = row[1].split("\\")[0]

                    age = int(row[2])
                    position = row[3]
                    college = row[8]

                    # Gets team name from Data/Rosters/Name_roster.csv
                    # Retrieves just the name
                    team = filename.split("_")[0]

                    cur.execute('''INSERT INTO players(name, team, age, college, position)
                    VALUES (?, ?, ?, ?, ?)''', (name, team, age, college, position))

                # The bottom row of each csv file contains different categories,
                # and their types do not match
                # This makes it so only the actual data is added
                except:
                    pass

    con.commit()

    con.close()


def AddTeams(db_filename):
    # Adds teams table to database

    con = sqlite3.connect(db_filename)
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS teams")

    # Create table with schema
    cur.execute('''CREATE TABLE teams(name TEXT, wins INTEGER,
                losses INTEGER, wl_ratio FLOAT, offensive_rank INTEGER,
                defensive_rank INTEGER, PRIMARY KEY (name))''')

    standings_directory = "Data/Standings"

    # Will hold pairs of (rank, team)
    # because ranks are relative
    offensive_ranks = []
    defensive_ranks = []

    # Iterate through each standings file
    for filename in os.listdir(standings_directory):

        # Creates accessible filename
        f = standings_directory + '/' + filename

        # Open file under read permissions
        with open(f, 'r') as csv_file:

            csv_reader = csv.reader(csv_file)

            next(csv_reader)

            for row in csv_reader:
                name = row[0]

                # Removes playoff indicators on ends of names
                if not name[-1].isalpha():
                    name = name[:-1]

                wins = int(row[1])
                losses = int(row[2])
                wl_ratio = round(float(wins/(wins+losses)), 3)
                relative_offsenive_rank = float(row[-2])
                relative_defsenive_rank = float(row[-1])

                offensive_ranks.append((relative_offsenive_rank, name))
                defensive_ranks.append((relative_defsenive_rank, name))

                cur.execute('''INSERT INTO teams(name, wins, losses, wl_ratio)
                                    VALUES (?, ?, ?, ?)''', (name, wins, losses, wl_ratio))


    # Sorts each list based on the first element which is the relative rank
    # Pairs are (rank, name)
    offensive_ranks.sort(key=lambda x: x[0])
    defensive_ranks.sort(key=lambda x: x[0])

    # Updates the offensive ranks based on index in sorted list
    for i, pair in enumerate(offensive_ranks):
        rank = 32 - i
        cur.execute("UPDATE teams SET offensive_rank = ? WHERE name = ?", (rank, pair[1]))

    # Updates the defensive ranks based on index in sorted list
    for i, pair in enumerate(defensive_ranks):
        rank = 32 - i
        cur.execute("UPDATE teams SET defensive_rank = ? WHERE name = ?", (rank, pair[1]))

    con.commit()

    con.close()


def AddStadiums(db_filename):
    # Adds stadiums table to database

    con = sqlite3.connect(db_filename)
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS stadiums")

    # Create table with schema
    cur.execute('''CREATE TABLE stadiums(name TEXT, team TEXT, capacity INTEGER,
                opened_date DATETIME, field_type TEXT, PRIMARY KEY (name))''')

    f = "Data/stadiums.csv"

    # Open file under read permissions
    with open(f, 'r') as csv_file:

        csv_reader = csv.reader(csv_file)

        next(csv_reader)

        for row in csv_reader:
            name = row[0]
            team = row[1]

            # Removes commas before converting to integer
            capacity = int(row[2].replace(',', ''))

            opened_date = row[3]
            field_type = row[-2]

            cur.execute("INSERT INTO stadiums(name, team, capacity, opened_date, field_type)"
                        "VALUES(?, ?, ?, ?, ?)",
                        (name, team, capacity, opened_date, field_type))

    con.commit()

    con.close()


def AddGames(db_filename):
    # Adds games table to database

    con = sqlite3.connect(db_filename)
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS games")

    # Create table with schema
    cur.execute('''CREATE TABLE games(winner TEXT, loser TEXT, winner_score INTEGER,
                loser_score INTEGER, date DATETIME)''')

    f = "Data/schedule.csv"

    # Open file under read permissions
    with open(f, 'r') as csv_file:

        csv_reader = csv.reader(csv_file)

        next(csv_reader)

        for row in csv_reader:
            date = row[2]
            winner = row[4]
            loser = row[6]
            winner_score = int(row[8])
            loser_score = int(row[9])


            cur.execute("INSERT INTO games(winner, loser, winner_score, loser_score, date)"
                        "VALUES(?, ?, ?, ?, ?)",
                        (winner, loser, winner_score, loser_score, date))

    con.commit()

    con.close()


def AddViews(db_filename):
    #Adds a view for each skill position

    con = sqlite3.connect(db_filename)
    cur = con.cursor()

    # Add QB view

    cur.execute("DROP VIEW IF EXISTS only_qb")

    cur.execute('''
    CREATE VIEW only_qb AS
    SELECT * FROM players
    WHERE position = "QB"''')


    # Add RB view

    cur.execute("DROP VIEW IF EXISTS only_rb")

    cur.execute('''
    CREATE VIEW only_rb AS
    SELECT * FROM players
    WHERE position = "RB"''')


    # Add WR view

    cur.execute("DROP VIEW IF EXISTS only_wr")

    cur.execute('''
    CREATE VIEW only_wr AS
    SELECT * FROM players
    WHERE position = "WR"''')


    # Add TE view

    cur.execute("DROP VIEW IF EXISTS only_te")

    cur.execute('''
    CREATE VIEW only_te AS
    SELECT * FROM players
    WHERE position = "TE"''')


    con.commit()

    con.close()


def NewYearProcedure(db_filename):
    # Procedure to increase ages and reset standings

    con = sqlite3.connect(db_filename)
    cur = con.cursor()

    # Increase all players' ages by 1
    cur.execute("UPDATE players SET age = age + 1")

    # Reset team stats
    cur.execute("UPDATE teams SET wins = 0")
    cur.execute("UPDATE teams SET losses = 0")
    cur.execute("UPDATE teams SET offensive_rank = NULL")
    cur.execute("UPDATE teams SET defensive_rank = NULL")

    con.commit()

    con.close()


def RankOverallTeams(db_filename):
    # Procedure to rank all teams overall

    con = sqlite3.connect(db_filename)
    cur = con.cursor()


    cur.execute("SELECT name, offensive_rank, defensive_rank FROM teams")

    results = []

    # Ranks teams overall by averaging offensive and defensive ranks
    for line in cur.fetchall():
        name = line[0]
        offense = line[1]
        defense = line[2]

        average = (offense + defense)/2

        results.append((average, name))

    results.sort(key=lambda x: x[0])

    print("Overall Rankings:")

    for i in range(len(results)):
        pair = results[i]
        rank = pair[0]
        name = pair[1]

        print("{}. {}".format(i+1, name))



AddPlayers("example.db")

AddTeams("example.db")

AddStadiums("example.db")

AddGames("example.db")

AddViews("example.db")

RankOverallTeams("example.db")

NewYearProcedure("example.db")

