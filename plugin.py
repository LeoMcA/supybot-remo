# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import pycurl
import StringIO
import urllib
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
    attribute = urllib.quote_plus(attribute, '=')
    res = json.loads(curl(attribute))
    if res["meta"]["total_count"] == 0:
        return 0
    else:
        return res["objects"]

def whois_reply(rep, query, irc):
    irc.reply(query + " is " + rep["fullname"] + ": " + rep["profile"]["profile_url"])

class ReMo(callbacks.Plugin):
    """Add the help for "@plugin help ReMo" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(ReMo, self)
        self.__parent.__init__(irc)

    def whois(self, irc, msg, args, query):
        """<query>

        Displays a Rep's full name and a link to their profile. <query> can be an IRC nick or ReMo Portal username."""

        reps = rep_lookup("profile__irc_name=" + query)
        if reps:
            rep = reps[0]
            whois_reply(rep, query, irc)
        else:
            reps = rep_lookup("profile__display_name=" + query)
            if reps:
                rep = reps[0]
                whois_reply(rep, query, irc)
            else:
                irc.reply("Sorry, I can't find that Rep. :(")
    whois = wrap(whois, ["text"])

Class = ReMo
