from Settings import *
from subprocess import call
import urllib, urllib.request
import json
import socket
import os
import datetime
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

    # Create Settings.xlsx
    settings = settingsConfig.settingsSetup(settingsConfig())
    commandsFromFile = settingsConfig.readCommands(settingsConfig())

    return


