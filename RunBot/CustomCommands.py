from Settings import *
from Initialize import *




commands_CustomCommands = {
    "!ccexample": ('customcmds.example', 'cmdArguments', 'user'),
    "!ccexamplemod": ('MOD', 'customcmds.modexample', 'cmdArguments', 'user'),
}

class resources:
    def __init__(self):
        pass


class CustomCommands:
    def __init__(self):
        pass

    def example(self, args, user):
        print("The user who did this command is: " + user)
        print("Everything after the command that the user typed is: " + args)

        # To send the message, return it as a string. Most messages start with 'user + " >> "'
        return "You just ran an example custom command. Your args were " + args

    def modexample(self, args, user):
        print("The user who did this command is: " + user)
        print("Everything after the command that the user typed is: " + args)

        # To send the message, return it as a string. Most messages start with 'user + " >> "'
        return "You just ran an example Mod-Only custom command. Your args were " + args


customcmds = CustomCommands()
resources = resources()