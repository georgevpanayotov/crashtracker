#!/usr/bin/python3

# Tracks crashes of Civ6 on macos/linux and notifies a discord webhook.
# Expects a "conf.json" file with the following keys:
# "local_user" : The discord user id of the local user (i.e. who's running the tracker?)
# "next_user" : The discord user id of the next user (i.e. who's turn is it after the current user?)
# "bot_path" : the path portion of the web hook URL.
#
# NOTE: You may have noticed tha this is not aware of which game is in play so it can only select
# one "next_user".

import linuxtracker
import mactracker

import datetime
import http.client
import json
import platform
import ssl
import sys

DISCORD_BOT_HOST = "discordapp.com"

def isRecent(crashTime):
    return abs(datetime.datetime.now() - crashTime).total_seconds() < 60

def createMessage(localUser, nextUser):
    formatString = "Civ6 just crashed on <@{0}>'s machine. <@{1}> You know what that means!"
    return formatString.format(localUser, nextUser)

def notifyBots(botPath, localUser, nextUser):
    connection = http.client.HTTPSConnection(DISCORD_BOT_HOST,
        context = ssl.SSLContext(protocol = ssl.PROTOCOL_TLSv1_2))
    connection.request("POST", botPath,
                       "content={0}".format(createMessage(localUser, nextUser)),
                       {"Content-Type" : "application/x-www-form-urlencoded"})
    print("Response: {0}".format(connection.getresponse().read().decode("utf-8")))

def notifyCrashDetected(crashTime, conf):
    print ("Matching crash log found.")
    if isRecent(crashTime):
        print ("Crash log is recent -- reporting.")
        notifyBots(conf["bot_path"], conf["local_user"], conf["next_user"])

def getConfFile():
    if (len(sys.argv) > 1):
        return sys.argv[1]
    else:
        return "conf.json"

if __name__ == "__main__":
    with open(getConfFile()) as confFile:
        conf = json.load(confFile)

    platformSystemName = platform.system()
    if platformSystemName == "Darwin":
        mactracker.track(conf)
    elif platformSystemName == "Linux":
        linuxtracker.track(conf)
