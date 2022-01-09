from Settings import *
from Initialize import *
from World import *




commands_rpg = {
    "!test": ('rpg.test', 'cmdArguments', 'user'),
    "!addplayer": ('rpg.addPlayer', 'cmdArguments', 'user'),
    "!reset": ('rpg.reset', 'cmdArguments', 'user'),
}

class resources:
    def __init__(self):
        pass
        # world["area"]["room"]["options"]

    def getCurrentLocation(self, user):
        result = db.read('''SELECT * FROM players WHERE username="%s"''' % user)
        area = result[2]
        room = result[3]
        return [area, room]


class rpg():
    def __init__(self):
        pass

    def processChatMsg(self, message, user):
        location = resources.getCurrentLocation(user)
        area = location[0]
        room = location[1]

        # General Commands
        if "where am i" in message.lower():
            print("A")
            return self.whereAmI(None, user)
        if "what area am i in" in message.lower():
            return self.whereAmIArea(None, user)
        if "help" in message.lower():
            return self.help(None, user)

        roomOptions = world.world["areas"][area]["rooms"][room]["options"]
        for optionNum in roomOptions:
            option = roomOptions[optionNum]
            phrase = option["Phrase"]
            ID = option["ID"]
            if phrase.lower() in message:
                db.write(
                    '''UPDATE players SET currentRoom = "{ID}" WHERE username = "{user}";'''.format(ID=ID, user=user))
                return world.world["areas"][area]["rooms"][ID]["description"]




    def test(self, args, user):
        #print(resources.world["area1"]["room1"]["description"])
        print("What do you do?")
        #print(resources.world["area1"]["room1"]["options"])



    def addPlayer(self, args, user):
        if args:
            user = args
        result = db.read('''SELECT * FROM players WHERE username="%s"''' % user)
        if result:
            return "Can't add player, %s is already a player!" % user
        firstArea = list(world.world["areas"])[0]
        firstRoom = list(world.world["areas"][firstArea]["rooms"])[0]
        db.write(
            '''INSERT INTO players(username, currentArea, currentRoom) VALUES("{user}", "{currentArea}", "{currentRoom}");'''.format(user=user, currentArea=firstArea, currentRoom=firstRoom))
        return "Added %s as a player!" % user


    def whereAmI(self, args, user):
        location = resources.getCurrentLocation(user)
        area = location[0]
        room = location[1]

        return world.world["areas"][area]["rooms"][room]["description"]

    def whereAmIArea(self, args, user):
        location = resources.getCurrentLocation(user)
        area = location[0]
        room = location[1]

        return world.world["areas"][area]["description"]

    def help(self, args, user):
        location = resources.getCurrentLocation(user)
        area = location[0]
        room = location[1]

        options = world.world["areas"][area]["rooms"][room]["options"]
        optString = "You can do the following actions: "
        for opt in options:
            optString += (options[opt]["Phrase"]) + ", "

        return optString[:-2]

    def reset(self, args, user):
        if not args or args != "confirm":
            return "Are you sure? Type !reset confirm to reset your RPG progress."

        db.write('''DELETE FROM players WHERE username="{user}";'''.format(user=user))
        self.addPlayer(None, user)
        return "Your progress in the RPG has been reset."












resources = resources()