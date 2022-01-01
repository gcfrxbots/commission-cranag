from websocket import create_connection
import json
import time
import datetime
import string
import random
import webbrowser


def formatted_time():
    return datetime.datetime.today().now().strftime("%I:%M")

def ran16characterstring():
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(16))

rndString = ran16characterstring()

authLine = "auth_redirect%3A{rndstring}%3Acaffeinated_twitch%3Arxbots".format(rndstring=rndString)

url = "wss://api.casterlabs.co/v1/kinoko?type=parent&channel=" + authLine


class chat:
    def __init__(self):
        self.ws = create_connection(url)

    def sendRequest(self, request):
        self.ws.send(request)

    def main(self, account):
        webbrowser.open("https://casterlabs.co/auth/redirect/twitch?state=" + authLine)
        if account == "main":
            print("Please open the browser window and sign in to your CHANNEL's twitch account.")
        else:
            print("Please open the browser window and sign in to your BOT's twitch account.")
        while True:
            time.sleep(0.2)
            result = self.ws.recv()

            if ":ping" in result:
                self.sendRequest(":ping")


            if "token:" in result and account == "main":
                token = json.loads(result)
                token = token.split(":")[1]
                with open("../Config/token.txt", "w") as file:
                    file.write(token)
                    file.close()


                    print("Login to your channel's Twitch account successful!\n\n")
                    print("Do you wish to have the bot chat through a different Twitch user? If you choose No, your bot will send messages to chat from your own account, not its own bot account.")
                    inp = input("Please type Y or N\n >> ").lower()

                    if inp == "n":
                        exit()
                    else:
                        self.main("puppet")

            if "token:" in result and account == "puppet":
                token = json.loads(result)
                token = token.split(":")[1]
                with open("../Config/puppet.txt", "w") as file:
                    file.write(token)
                    file.close()
                    print("Login to your bot's Twitch account successful! All set, you can close this now.")
                    exit()


chatConnection = chat()
chatConnection.main("main")







