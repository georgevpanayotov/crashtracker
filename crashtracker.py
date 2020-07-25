#!/usr/bin/python3

# Tracks crashes of Civ6 on macos and notifies a discord webhook.
# Expects a "conf.json" file with the following keys:
# "local_user" : The discord user id of the local user (i.e. who's running the tracker?)
# "next_user" : The discord user id of the next user (i.e. who's turn is it after the current user?)
# "bot_path" : the path portion of the web hook URL.
#
# NOTE: You may have noticed tha this is not aware of which game is in play so it can only select
# one "next_user".

import datetime
import http.client
import json
import os
import re
import ssl
import sys
import time

from watchdog.events import EVENT_TYPE_CREATED
from watchdog.events import FileSystemEventHandler
from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import Observer

CRASH_DUMP_PATH = os.path.expanduser("~/Library/Logs/DiagnosticReports")
DISCORD_BOT_HOST = "discordapp.com"

def matchCrashDump(path):
    m = re.match(r".*/Civ6_Metal_Exe_(\d{4})-(\d{2})-(\d{2})-(\d{1,2})(\d{2})(\d{2})_(.*)\.crash",
                 path)
    if m:
        groups = m.groups(0)
        crashTime = datetime.datetime(int(groups[0]), int(groups[1]), int(groups[2]),
                                      int(groups[3]), int(groups[4]), int(groups[5]))

        return crashTime, groups[6]
    else:
        return None, None

def isRecent(crashTime):
    return abs(datetime.datetime.now() - crashTime).total_seconds() < 60

def createMessage(localUser, nextUser):
    formatString = "Civ6 just crashed on <@{0}>'s machine. <@{1}> You know what that means!"
    return formatString.format(localUser, nextUser)

def notifyBots(botPath, localUser, nextUser):
    connection = http.client.HTTPSConnection(DISCORD_BOT_HOST, context = ssl.SSLContext())
    connection.request("POST", botPath,
                       "content={0}".format(createMessage(localUser, nextUser)),
                       {"Content-Type" : "application/x-www-form-urlencoded"})
    print("Response: {0}".format(connection.getresponse().read().decode("utf-8")))

class CrashFileEventHandler(FileSystemEventHandler):
    def __init__(self, botPath, localUser, nextUser):
        self.botPath = botPath
        self.localUser = localUser
        self.nextUser = nextUser

    def on_created(self, event):
        print(event.src_path)
        crashTime, machine = matchCrashDump(event.src_path)
        if crashTime:
            print ("Matching crash log found.")
            if isRecent(crashTime):
                print ("Crash log is recent -- reporting.")
                notifyBots(self.botPath, self.localUser, self.nextUser)

def getConfFile():
    if (len(sys.argv) > 1):
        return sys.argv[1]
    else:
        return "conf.json"

if __name__ == "__main__":
    with open(getConfFile()) as confFile:
        conf = json.load(confFile)

    if "debug_crash_path" in conf:
        path = conf["debug_crash_path"]
    else:
        path = CRASH_DUMP_PATH

    event_handler = CrashFileEventHandler(conf["bot_path"], conf["local_user"], conf["next_user"])
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
