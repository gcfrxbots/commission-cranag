from Settings import *
from subprocess import call
import urllib, urllib.request
import json
import socket
import os
import datetime
import sqlite3
from sqlite3 import Error
try:
    import xlsxwriter
    import xlrd
    import validators
except ImportError as e:
    print(e)
    raise ImportError(">>> One or more required packages are not properly installed! Run INSTALL_REQUIREMENTS.bat to fix!")
global settings, commandsFromFile

class coreFunctions:
    def __init__(self):
        pass


    def getmoderators(self):
        moderators = []
        json_url = urllib.request.urlopen('http://tmi.twitch.tv/group/user/' + settings['CHANNEL'].lower() + '/chatters')
        data = json.loads(json_url.read())['chatters']
        mods = data['moderators'] + data['broadcaster']

        for item in mods:
            moderators.append(item)

        return moderators

class dbControl:
    def __init__(self):
        self.db = None

    def createDb(self):
        try:
            self.db = sqlite3.connect('botData.db', check_same_thread=False)
            sql_creation_commands = (
                # Create chat log
                """ CREATE TABLE IF NOT EXISTS players (
                                id integer PRIMARY KEY,
                                username text,
                                currentArea text,
                                currentRoom text
                            ); """,

            )
            c = self.db.cursor()
            for item in sql_creation_commands:
                c.execute(item)
            self.db.commit()
        except Error as e:
            print(e)

    def sqlError(self, src, command, e):
        print("DATABASE ERROR INSIDE %s FUNCTION:" % src.upper())
        print(e)
        print(command)
        return False

    def read(self, command):
        self.db = sqlite3.connect('botData.db', check_same_thread=False)
        try:
            cursor = self.db.cursor()
            cursor.execute(command)
            data = cursor.fetchone()
            self.db.close()
            return data
        except Error as e:
            self.db.rollback()
            self.sqlError("READ", command, e)

    def fetchAll(self, command):
        self.db = sqlite3.connect('botData.db', check_same_thread=False)
        try:
            cursor = self.db.cursor()
            cursor.execute(command)
            data = cursor.fetchall()
            self.db.close()
            return data
        except Error as e:
            self.db.rollback()
            self.sqlError("FETCHALL", command, e)

    def write(self, command):
        self.db = sqlite3.connect('botData.db', check_same_thread=False)
        try:
            cursor = self.db.cursor()
            cursor.execute(command)
            self.db.commit()
            self.db.close()
            return True
        except Error as e:
            self.db.rollback()
            self.sqlError("WRITE", command, e)

core = coreFunctions()
db = dbControl()

def initSetup():
    global settings, commandsFromFile

    # Create Folders
    if not os.path.exists('../Config'):
        buildConfig()
    if not os.path.exists('../Config/Commands.xlsx'):
        buildConfig()
    if not os.path.exists('Resources'):
        os.makedirs('Resources')
        print("Creating necessary folders...")

    db.createDb()

    # Create Settings.xlsx
    settings = settingsConfig.settingsSetup(settingsConfig())
    commandsFromFile = settingsConfig.readCommands(settingsConfig())

    return


