#!/usr/bin/python3

# Tracks crashes for linux by following kern.log. I'm not sure if all versions of Linux log crashes
# but at least 1 version of Ubuntu does.

import crashtracker

import datetime
import os
import re
import time

CRASH_DUMP_PATH = "/var/log/kern.log"

def matchCrashDump(line):
    m = re.match(r"([A-Za-z]*\s*\d+\s*\d{2}:\d{2}:\d{2})\s*(\S*)\s.*Civ6Sub.*segfault.*",
                 line)
    if m:
        groups = m.groups(0)
        currentYear = datetime.datetime.now().year
        crashTime = datetime.datetime.strptime(str(currentYear) + " " + groups[0], "%Y %b %d %H:%M:%S")

        return crashTime, groups[1]
    else:
        return None, None

def track(conf):
    if "debug_crash_path" in conf:
        path = conf["debug_crash_path"]
    else:
        path = CRASH_DUMP_PATH

    try:
        with open(path) as kernLog:
            kernLog.seek(0, os.SEEK_END)
            while True:
                line = kernLog.readline()

                if line:
                    line = line.strip()
                    crashTime, machine = matchCrashDump(line)
                    if crashTime:
                        crashtracker.notifyCrashDetected(crashTime, conf)
                else:
                    time.sleep(1)
    except KeyboardInterrupt:
        pass
