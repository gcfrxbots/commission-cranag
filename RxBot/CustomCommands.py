from Settings import *
from Initialize import *
from World import *




commands_rpg = {
    "!test": ('rpg.test', 'cmdArguments', 'user'),
    "!reset": ('rpg.reset', 'cmdArguments', 'user'),
    "!addarea": ('rpg.addArea', 'cmdArguments', 'user'),
}

class resources:
    def __init__(self):
        self.pollActive = False
        self.pollEntries = {}
        self.pollVoters = []
        # world["area"]["room"]["options"]

    def getCurrentLocation(self):
        result = db.read('''SELECT * FROM players''')
        area = result[1]
        room = result[2]
        return [area, room]

    def startPoll(self):
        timer.setTimer("poll", settings["POLL DURATION"])
        self.pollActive = True

    def pollAddEntry(self, entry, user):
        if not self.pollActive:
            self.startPoll()
        if user in self.pollVoters:
            return

        if not entry in self.pollEntries.keys():
            self.pollEntries[entry] = 1
        else:
            self.pollEntries[entry] += 1

        self.pollVoters.append(user)

    def pollDone(self):
        winnerPhrase = max(self.pollEntries, key=self.pollEntries.get)
        self.pollActive = False
        self.pollEntries = {}
        self.pollVoters = []
        print(winnerPhrase)

        roomOptions = world.world["areas"][rpg.area]["rooms"][rpg.room]["options"]
        for optionNum in roomOptions:
            option = roomOptions[optionNum]
            phrase = option["Phrase"]
            ID = option["ID"]
            if phrase.lower() in winnerPhrase:
                db.write('''UPDATE players SET currentRoom = "{ID}";'''.format(ID=ID))
                chatConnection.sendToChat("You " + winnerPhrase + ". " + world.world["areas"][rpg.area]["rooms"][ID]["description"])


class rpg():
    def __init__(self):
        self.addPlayer(None, None)
        self.area = None
        self.room = None

    def processChatMsg(self, message, user):
        location = resources.getCurrentLocation()
        self.area = location[0]
        self.room = location[1]

        # General Commands
        if "where am i" in message.lower():
            return self.whereAmI(None, user)
        if "what area am i in" in message.lower():
            return self.whereAmIArea(None, user)
        if "help" in message.lower():
            return self.help(None, user)

        roomOptions = world.world["areas"][self.area]["rooms"][self.room]["options"]
        for optionNum in roomOptions:
            option = roomOptions[optionNum]
            phrase = option["Phrase"]
            ID = option["ID"]
            if phrase.lower() in message:
                resources.pollAddEntry(phrase.lower(), user)




    def test(self, args, user):
        #print(resources.world["area1"]["room1"]["description"])
        print("What do you do?")
        #print(resources.world["area1"]["room1"]["options"])



    def addPlayer(self, args, user):
        # if args:
        #     user = args
        result = db.read('''SELECT * FROM players''')
        if result:
            return
        firstArea = list(world.world["areas"])[0]
        firstRoom = list(world.world["areas"][firstArea]["rooms"])[0]
        db.write(
            '''INSERT INTO players(currentArea, currentRoom) VALUES("{currentArea}", "{currentRoom}");'''.format(currentArea=firstArea, currentRoom=firstRoom))



    def whereAmI(self, args, user):
        location = resources.getCurrentLocation()
        self.area = location[0]
        self.room = location[1]

        return world.world["areas"][self.area]["rooms"][self.room]["description"]

    def whereAmIArea(self, args, user):
        location = resources.getCurrentLocation()
        self.area = location[0]
        self.room = location[1]

        return world.world["areas"][self.area]["description"]

    def help(self, args, user):
        location = resources.getCurrentLocation()
        self.area = location[0]
        self.room = location[1]

        options = world.world["areas"][self.area]["rooms"][self.room]["options"]
        optString = "You can do the following actions: "
        for opt in options:
            optString += (options[opt]["Phrase"]) + ", "

        return optString[:-2]

    def reset(self, args, user):
        if not args or args != "confirm":
            return "Are you sure? Type !reset confirm to reset your RPG progress."

        db.write('''DELETE FROM players;'''.format(user=user))
        self.addPlayer(None, user)
        return "Your progress in the RPG has been reset."

    def addArea(self, args, user):
        pass





class timer:
    def __init__(self):
        self.timerActive = False
        self.timers = {}


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

        if timer == "poll":
            resources.pollDone()


timer = timer()

resources = resources()

rpg = rpg()