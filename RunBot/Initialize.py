from Settings import *
from subprocess import call
import subprocess
import urllib, urllib.request
import json
import socket
import os
import datetime
from json import JSONDecodeError
from websocket import create_connection, WebSocketConnectionClosedException, WebSocketBadStatusException
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

core = coreFunctions()

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

    if not os.path.exists('../Config/badwords.txt'):
        open('../Config/badwords.txt', "w")

    # Create Settings.xlsx
    settings = settingsConfig.settingsSetup(settingsConfig())
    commandsFromFile = settingsConfig.readCommands(settingsConfig())

    return


class chat:
    global settings

    def __init__(self):
        self.ws = None
        self.koiBeta = False
        self.url = "wss://api.casterlabs.co/v2/koi?client_id=jJu2vQGnHf5U5trv"
        self.caffeineUrl = "wss://api.casterlabs.co/v2/koi?client_id=LmHG2ux992BxqQ7w9RJrfhkW"
        self.puppet = False
        self.active = False
        self.token = None
        self.puppetToken = None

        if self.koiBeta:
            self.url = "wss://api.casterlabs.co/beta/v2/koi?client_id=jJu2vQGnHf5U5trv"

        self.readTokens()

    def readTokens(self):
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
        self.readTokens()
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
        if message:
            request = {
                "type": "CHAT",
                "message": message,
                "chatter": "CLIENT",
                "isUserGesture": False,
                "reply_target": None}

            if self.puppet:
                request['chatter'] = "PUPPET"

            if settings["CHAT AS RXBOTS"]:
                request["chatter"] = "SYSTEM"

            self.sendRequest(request)

    def start(self, silent=False, reconnect=False):
        try:
            self.ws = create_connection(self.url)
            self.login()
            if not silent:
                print(">> Connecting to Twitch")
        except (WebSocketConnectionClosedException, WebSocketBadStatusException):
            if not reconnect:  # Only tries to reconnect if its not already being called from reconnect to prevent loops
                time.sleep(5)
                self.reconnect()
            pass


    def reconnect(self):
        print(">> Reconnecting, please wait...")
        for x in range(100):
            try:
                self.ws = None
                self.start(silent=True, reconnect=True)
                time.sleep(1)
                result = self.ws.recv()
                resultDict = json.loads(result)
                print(">> Reconnect to Koi successful.")
                return resultDict
            except:
                time.sleep(.8)
        raise ConnectionError("Unable to connect to Koi after multiple reconnect attempts. Please wait a few minutes then restart the bot.")

class runMiscControls:

    def __init__(self):
        self.timerActive = False
        self.timers = {}

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

    def setTimer(self, name, duration):
        self.timerActive = True
        curTime = datetime.datetime.now()
        targetTime = curTime + datetime.timedelta(seconds=duration)
        self.timers[name] = targetTime

    def timerDone(self, timer):
        self.timers.pop(timer)
        print(timer + " timer complete.")
        if not self.timers:
            self.timerActive = False


misc = runMiscControls()
chatConnection = chat()