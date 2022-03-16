from Settings import *
from subprocess import call
import urllib, urllib.request
import json
import socket
import os
import datetime
import sqlite3
from sqlite3 import Error
from websocket import create_connection
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


class runMiscControls:

    def __init__(self):
        pass

    def getUser(self, line):
        seperate = line.split(":", 2)
        user = seperate[1].split("!", 1)[0]
        return user

    def getMessage(self, line):
        seperate = line.split(":", 2)
        message = seperate[2]
        return message

    def formatTime(self):
        return datetime.datetime.today().now().strftime("%I:%M")

class chat:
    global settings

    def __init__(self):
        self.ws = None
        self.url = "wss://api.casterlabs.co/v2/koi?client_id=LmHG2ux992BxqQ7w9RJrfhkW"
        self.puppet = False
        self.active = False
        self.messageSent = ""

        # Set the normal token
        if os.path.exists("../Config/token.txt"):
            with open("../Config/token.txt", "r") as f:
                self.token = f.read()
                f.close()

        # Set the puppet token, if it exists
        if os.path.exists("../Config/puppet.txt"):
            self.puppet = True
            with open("../Config/puppet.txt", "r") as f:
                self.puppetToken = f.read()
                f.close()

    def login(self):
        loginRequest = {
                "type": "LOGIN",
                "token": self.token
            }
        self.ws.send(json.dumps(loginRequest))
        time.sleep(1)

    def puppetlogin(self):
        time.sleep(1.5)
        loginRequest = {
            "type": "PUPPET_LOGIN",
            "token": self.puppetToken
        }
        self.ws.send(json.dumps(loginRequest))

    def sendRequest(self, request):
        self.ws.send(json.dumps(request))

    def sendToChat(self, message):
        self.messageSent = message
        if message:
            if not self.puppet:
                    request = {
                      "type": "CHAT",
                      "message": message,
                      "chatter": "CLIENT"}
            else:
                request = {
                    "type": "CHAT",
                    "message": message,
                    "chatter": "PUPPET"}
            self.sendRequest(request)


    def start(self):
        self.ws = create_connection(self.url)
        self.login()

chatConnection = chat()

misc = runMiscControls()



