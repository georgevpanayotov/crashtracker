#!/usr/bin/python3

# Track crashes on macos. This tracks new `.crash` files being added to
# `~/Library/Logs/DiagnosticReports`.

import crashtracker

import datetime
import os
import re
import time

from watchdog.events import EVENT_TYPE_CREATED
from watchdog.events import FileSystemEventHandler
from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import Observer

CRASH_DUMP_PATH = os.path.expanduser("~/Library/Logs/DiagnosticReports")

def matchCrashDump(path):
    m = re.match(r".*/Civ6_Metal_Exe_(\d{4})-(\d{2})-(\d{2})-(\d{1,2})(\d{2})(\d{2})_(.*)\.crash",
                 path)

    # TODO: use strptime
    if m:
        groups = m.groups(0)
        crashTime = datetime.datetime(int(groups[0]), int(groups[1]), int(groups[2]),
                                      int(groups[3]), int(groups[4]), int(groups[5]))

        return crashTime, groups[6]
    else:
        return None, None

class CrashFileEventHandler(FileSystemEventHandler):
    def __init__(self, conf):
        self.conf = conf

    def on_created(self, event):
        crashTime, machine = matchCrashDump(event.src_path)
        if crashTime:
            print(event.src_path)
            crashtracker.notifyCrashDetected(crashTime, self.conf)

def track(conf):
    if "debug_crash_path" in conf:
        path = conf["debug_crash_path"]
    else:
        path = CRASH_DUMP_PATH

    event_handler = CrashFileEventHandler(conf)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

