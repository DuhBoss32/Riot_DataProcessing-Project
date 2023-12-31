import cassiopeia as cass
import mysql.connector 
from mysql.connector import Error
import time
import json
import pandas as pd 

# Created by: Travis Huynh 11/15/2023

# Python Program that utlizes Panda Library, Cassiopeia Library, Riot API, MySQL 
# Program that takes in Riot Information regarding League of Legends Data. 
# ** IN PROGRESS ** 

def getAPI_key(): 
    f = open("private/apikey.txt", "r")
    return f.read()

cass.set_riot_api_key(getAPI_key())

def connect_to_database():
    connection = None
    try: 
        with open("private/config.json", "r") as file:
            config = json.load(file)
            mysql_config = config['mysql']
            connection = mysql.connector.connect(
                host=mysql_config['host'],
                user=mysql_config['user'],
                password=mysql_config['password'],
                database=mysql_config['database']
            )
            print("MySQL Database Connected!")
    except Error as err: 
        print(f"Error!: {err}")
    return connection

def fetch_data_from_database():
    try:
        try: 
            with open("private/config.json", "r") as file:
                config = json.load(file)
                mysql_config = config['mysql']
                connection = mysql.connector.connect(
                    host=mysql_config['host'],
                    user=mysql_config['user'],
                    password=mysql_config['password'],
                    database=mysql_config['database']
                )
                print("MySQL Database Connected!")
        except Error as err: 
            print(f"Error!: {err}")

        # Fetching data from the table
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Mastery7Champions")
        data = cursor.fetchall()

        columns = [i[0] for i in cursor.description]
        df = pd.DataFrame(data, columns=columns)

        cursor.close()
        connection.close()

        return df

    except mysql.connector.Error as error:
        print("Error connecting to MySQL:", error)
        return None

def create_champion_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Mastery7Champions (
            summoner_name VARCHAR(50),
            champion_name VARCHAR(50),
            champion_id INT,
            champion_points INT
        )
    ''')
     

def get_summoner_data(summoner_name, region):
    summoner = cass.get_summoner(name=summoner_name, region=region)
    print("{name} is a level {level} summoner on the {region} server.".format(name=summoner.name,
                                                                                  level=summoner.level,
                                                                                  region=summoner.region))
    champs = summoner.champion_masteries

    connection = connect_to_database()
    cursor = connection.cursor()
    create_champion_table(cursor)

    for champion_mastery in champs:
        champion = champion_mastery.champion
        cursor.execute('''
            INSERT INTO Mastery7Champions (summoner_name, champion_name, champion_id, champion_points)
            VALUES (%s, %s, %s, %s)
        ''', (summoner.name, champion.name, champion.id, champion_mastery.points))
        #print(f"Inserted: {summoner.name}, {champion.name}, {champion.id}, {champion_mastery.points}")

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__": 
    start_time = time.time()
    summoner_name = "DuhBoss32"  
    region = "NA"  

    get_summoner_data(summoner_name, region)
    df = fetch_data_from_database()
    if df is not None:
        print(df)

    print("\n--- %s seconds ---" % (time.time() - start_time))
    
