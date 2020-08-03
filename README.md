# CrashTracker

A crash tracker for Civ6 on MacOS and Linux. Reports to a discord webhook when civ6 crashes.

Requires a conf.json in the following form:

```
{
    "local_user" : "...",
    "next_user" : "...",
    "bot_path" : "..."
}
```

Where, the users are discord user ids and the path is the path part of the webhook URL
(after discordapp.com).

pre-reqs: [watchdog](https://pypi.org/project/watchdog/)
