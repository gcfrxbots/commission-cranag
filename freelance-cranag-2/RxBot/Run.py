from threading import Thread
from Initialize import *
initSetup()
from CustomCommands import *
from Authenticate import *
from gtts import gTTS
import os
import shutil
import playsound


def speak(text):
    # Check for bad words
    with open('../Config/badwords.txt', "r") as f:
        badwords = f.read().split("\n")
        while "" in badwords:
            badwords.remove("")

    for word in badwords:
        if word in text:
            text = text.replace(word, "BLEEP")

    shutil.copyfile("Resources/talk.gif", "source.gif")
    tts = gTTS(text=text, lang='en')
    filename = "text.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)
    shutil.copyfile("Resources/notalk.gif", "source.gif")


def runcommand(command, cmdArguments, user, mute):
    commands = {**commands_CustomCommands}
    cmd = None
    arg1 = None
    arg2 = None

    for item in commands:
        if item == command:
            if commands[item][0] == "MOD":  # MOD ONLY COMMANDS:
                if (user in core.getmoderators()):
                    cmd = commands[item][1]
                    arg1 = commands[item][2]
                    arg2 = commands[item][3]
                else:
                    chatConnection.sendToChat("You don't have permission to do this.")
                    return
            elif commands[item][0] == "STREAMER":  # STREAMER ONLY COMMANDS:
                if (user == settings['CHANNEL']):
                    cmd = commands[item][1]
                    arg1 = commands[item][2]
                    arg2 = commands[item][3]
                else:
                    chatConnection.sendToChat("You don't have permission to do this.")
                    return
            else:
                cmd = commands[item][0]
                arg1 = commands[item][1]
                arg2 = commands[item][2]
            break
    if not cmd:
        return

    output = eval(cmd + '(%s, %s)' % (arg1, arg2))
    if not output:
        return

    chatConnection.sendToChat(user + " >> " + output)


class mainChat:
    def __init__(self):
        global settings
        self.channel = None
        self.bitsAmount = 0
        self.rewardTitle = None
        self.rewardCost = None
        self.isSubscriber = False


    def main(self):
        chatConnection.start()
        while True:
            try:
                if not chatConnection.ws:  # Raise the exception to restart before getting an attritubuteerror below
                    raise WebSocketConnectionClosedException
                result = chatConnection.ws.recv()
                resultDict = json.loads(result)
            except (WebSocketConnectionClosedException, WebSocketBadStatusException, JSONDecodeError, ConnectionResetError):  # Reconnect silently if casterlabs dies

                chatConnection.reconnect()
                result = chatConnection.ws.recv()
                resultDict = json.loads(result)

            #print(resultDict)
            if debugMode:
                print(resultDict)

            if "event" in resultDict.keys() and not chatConnection.active:
                if "is_live" in resultDict["event"]:
                    print(">> Connection to chat successful!")
                    chatConnection.active = True
                    if chatConnection.puppet:
                        chatConnection.puppetlogin()

            if "event" in resultDict.keys():  # Any actual event is under this
                eventKeys = resultDict["event"].keys()
                eventType = resultDict["event"]["event_type"]

                if eventType == "USER_UPDATE":  # defines User Channel (and adds it to alt bot names)
                    self.channel = resultDict['event']['streamer']['username']

                elif eventType == "RICH_MESSAGE":  # Includes chat and donations (as they come from chat msgs)

                    if resultDict["event"]["donations"]:  # Check if message included a donation
                        self.bitsAmount = round(resultDict["event"]["donations"][0]["amount"])
                        user = resultDict["event"]["sender"]["displayname"]
                        message = resultDict["event"]["message"]
                        print("(" + misc.formatTime() + ")>> [EVENT] " + user + " cheered %s bits with the message %s" % (self.bitsAmount, message))

                    try:  # Process incoming messages
                        message = resultDict["event"]["raw"]
                        if message:
                            user = resultDict["event"]["sender"]["displayname"]
                            command = ((message.split(' ', 1)[0]).lower()).replace("\r", "")
                            cmdarguments = message.replace(command or "\r" or "\n", "")[1:]
                            self.isSubscriber = False
                            if "SUBSCRIBER" in resultDict["event"]["sender"]["roles"]:
                                self.isSubscriber = True


                            # START MESSAGE LOGIC
                            print("(" + misc.formatTime() + ")>> " + user + ": " + message)

                            self.bitsAmount = 0

                    except PermissionError:  # Catches permissionerrors when trying to open any files like settings/interactconfig
                        pass

                if eventType == "CHANNEL_POINTS":
                    message = resultDict["event"]["message"]
                    self.rewardTitle = resultDict["event"]["reward"]["title"]
                    rewardPrompt = resultDict["event"]["reward"]["prompt"]
                    self.rewardCost = resultDict["event"]["reward"]["cost"]
                    user = resultDict["event"]["sender"]["displayname"]
                    print(
                        "(" + misc.formatTime() + ")>> [EVENT] " + user + " redeemed reward title %s, prompt %s, for %s points." % (self.rewardTitle, rewardPrompt, self.rewardCost))

                    if self.rewardTitle == settings["EVENT NAME"]:

                        print("SAYING: " + message)

                        speak(message)



                if eventType == "SUBSCRIPTION":
                    try:
                        subUsername = resultDict["event"]["subscriber"]["username"]
                        subMonths = resultDict["event"]["months"]
                        subLevel = resultDict["event"]["sub_level"]
                        print(
                            "(" + misc.formatTime() + ")>> [EVENT] " + subUsername + " subscribed with level %s for %s months." % (subLevel, subMonths))
                        self.isSubscriber = True
                    except:
                        pass

            if "type" in resultDict.keys():
                if resultDict["type"] == "KEEP_ALIVE":
                    response = {"type": "KEEP_ALIVE"}
                    chatConnection.sendRequest(response)

            if "error" in resultDict.keys():
                print("CHAT CONNECTION ERROR : " + resultDict["error"])
                if resultDict['error'] == "USER_AUTH_INVALID":
                    print("Channel Auth Token Expired or Invalid - Reauthenticating...")
                    subprocess.call("py Authenticate.py")
                elif resultDict['error'] == "PUPPET_AUTH_INVALID":
                    print("Bot Account Auth Token Expired or Invalid -  Reauthenticating...")
                    subprocess.call("py Authenticate.py")
                else:
                    print("Please report this error to rxbots so we can get it resolved.")
                    print("Try running RXBOT_DEBUG.bat in the RxBot folder to get more info on this error to send to me.")


mainChatConnection = mainChat()


def console():  # Thread to handle console input
    while True:
        consoleIn = input("")

        command = ((consoleIn.split(' ', 1)[0]).lower()).replace("\r", "")
        cmdArguments = consoleIn.replace(command or "\r" or "\n", "").strip()
        # Run the commands function
        if command:
            if command[0] == "!":
                runcommand(command, cmdArguments, "CONSOLE", True)

            if command.lower() in ["quit", "exit", "leave", "stop", "close"]:
                print("Shutting down")
                os._exit(1)


def tick():
    prevTime = datetime.datetime.now()
    while True:
        time.sleep(0.4)

        if misc.timerActive:
            for timer in misc.timers:
                if datetime.datetime.now() > misc.timers[timer]:
                    misc.timerDone(timer)
                    break

        # Timers that send stuff every X seconds

        # if datetime.datetime.now() > prevTime + datetime.timedelta(minutes=settings["TIMER DELAY"]):
        #     chatConnection.sendToChat(resources.askChatAQuestion())
        #     prevTime = datetime.datetime.now()


if __name__ == "__main__":
    t1 = Thread(target=mainChatConnection.main)
    t2 = Thread(target=console)
    t3 = Thread(target=tick)

    t1.start()
    t2.start()
    t3.start()