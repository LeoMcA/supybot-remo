###
# Copyright (c) 2012, Leo McArdle
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import pycurl
import StringIO
try:
    import simplejson as json
except ImportError:
    import json

def curl(query):
    c = pycurl.Curl()
    b = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(pycurl.URL, "https://reps.mozilla.org/api/v1/rep/?" + query)
    c.perform()
    return b.getvalue()

def rep_lookup(attribute):
    res = json.loads(curl(attribute))
    if res["meta"]["total_count"] == 0:
        return 0
    else:
        return res["objects"]

class ReMo(callbacks.Plugin):
    """Add the help for "@plugin help ReMo" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(ReMo, self)
        self.__parent.__init__(irc)

    def whois(self, irc, msg, args, nick):
        """<nick>

        Displays a Rep's full nick and a link to their profile. <nick> can either be a ReMo portal username or an IRC nick."""

        reps = rep_lookup("profile__irc_name=" + nick)
        if reps:
            rep = reps[0]
            profile = rep["profile"]
            irc.reply(profile["irc_name"] + " is " + rep["fullname"] + ": " + profile["profile_url"])
        else:
            irc.reply("Sorry, I don't recognise that Rep. :(")
    whois = wrap(whois, ["text"])

Class = ReMo
