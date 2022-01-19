from threading import Thread
from Initialize import *
initSetup()
from CustomCommands import *
from Authenticate import *





def runcommand(command, cmdArguments, user, mute):
    commands = {**commands_rpg}
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



def main():
    chatConnection.ws = create_connection(chatConnection.url)
    chatConnection.login()
    while True:
        time.sleep(0.2)
        result = chatConnection.ws.recv()
        resultDict = json.loads(result)
        #print(resultDict)
        if "event" in resultDict.keys() and not chatConnection.active:
            if "is_live" in resultDict["event"]:
                print(">> Connection to chat successful!")
                channel = resultDict["event"]["streamer"]["username"]
                settings["CHANNEL"] = channel
                chatConnection.active = True
                if chatConnection.puppet:
                    chatConnection.puppetlogin()

        if "event" in resultDict.keys():  # Any actual event is under this
            eventKeys = resultDict["event"].keys()
            if "message" in eventKeys:  # Got chat message, display it then process commands
                try:
                    message = resultDict["event"]["message"]
                    user = resultDict["event"]["sender"]["displayname"]
                    command = ((message.split(' ', 1)[0]).lower()).replace("\r", "")
                    cmdarguments = message.replace(command or "\r" or "\n", "")[1:]
                    print("(" + misc.formatTime() + ")>> " + user + ": " + message)
                    if not (chatConnection.messageSent == message):
                        for cmdFromFile in commandsFromFile:
                            if command.lower() == cmdFromFile.lower():
                                chatConnection.sendToChat(commandsFromFile[cmdFromFile])

                        if command[0] == "!":  # Only run normal commands if COMMAND PHRASE is blank
                            runcommand(command, cmdarguments, user, False)
                        else:
                            chatConnection.sendToChat(rpg.processChatMsg(message, user))
                except PermissionError:
                    pass

            if "reward" in eventKeys:
                try:
                    rewardTitle = resultDict["event"]["reward"]["title"]
                    rewardPrompt = resultDict["event"]["reward"]["prompt"]
                    rewardCost = resultDict["event"]["reward"]["cost"]
                    user = resultDict["event"]["sender"]["displayname"]
                    print("(" + misc.formatTime() + ")>> " + user + " redeemed reward title %s, prompt %s, for %s points." % (rewardTitle, rewardPrompt, rewardCost))
                except:
                    pass

            if "subscriber" in eventKeys:
                try:
                    subUsername = resultDict["event"]["subscriber"]["username"]
                    subMonths = resultDict["event"]["months"]
                    subLevel = resultDict["event"]["sub_level"]
                    print("(" + misc.formatTime() + ")>> " + subUsername + " subscribed with level %s for %s months." % (subLevel, subMonths))
                except:
                    pass

            if "donations" in eventKeys:
                    bitsAmount = round(resultDict["event"]["donations"][0]["amount"])
                    user = resultDict["event"]["sender"]["displayname"]
                    message = resultDict["event"]["message"]
                    print("(" + misc.formatTime() + ")>> " + user + " cheered %s bits with the message %s" % (bitsAmount, message))

        if "disclaimer" in resultDict.keys():  # Should just be keepalives?
            if resultDict["type"] == "KEEP_ALIVE":
                response = {"type": "KEEP_ALIVE"}
                chatConnection.sendRequest(response)

        if "error" in resultDict.keys():
            print("CHAT CONNECTION ERROR : " + resultDict["error"])
            if resultDict['error'] == "USER_AUTH_INVALID":
                print("Channel Auth Token Expired or Invalid - Reauthenticating...")
                authChatConnection.main("main")
            elif resultDict['error'] == "PUPPET_AUTH_INVALID":
                print("Bot Account Auth Token Expired or Invalid -  Reauthenticating...")
                authChatConnection.main("main")
            else:
                print("Please report this error to rxbots so we can get it resolved.")
                print("Try running RXBOT_DEBUG.bat in the RxBot folder to get more info on this error to send to me.")

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

        if timer.timerActive:
            for t in timer.timers:
                if datetime.datetime.now() > timer.timers[t]:
                    timer.timerDone(t)
                    break

        # Timers that send stuff every X seconds

        # if datetime.datetime.now() > prevTime + datetime.timedelta(minutes=settings["TIMER DELAY"]):
        #     chatConnection.sendToChat(resources.askChatAQuestion())
        #     prevTime = datetime.datetime.now()


if __name__ == "__main__":
    t1 = Thread(target=main)
    t2 = Thread(target=console)
    t3 = Thread(target=tick)

    t1.start()
    t2.start()
    t3.start()