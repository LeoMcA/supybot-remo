###
# Copyright (c) 2012, Leo McArdle
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import pycurl
import StringIO
try:
    import json
except ImportError:
    import simplejson as json


class ReMo(callbacks.Plugin):
    """Add the help for "@plugin help ReMo" here
    This should describe *how* to use this plugin."""
    threaded = True

    def _curl(self, display_name, name):
        c = pycurl.Curl()
        b = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        if display_name:
            c.setopt(pycurl.URL, "https://reps.mozilla.org/api/v1/rep/?profile__display_name=" + name)
        else:
            c.setopt(pycurl.URL, "https://reps.mozilla.org/api/v1/rep/?profile__irc_name=" + name)
        c.perform()
        return b.getvalue()

    def _lookup(self, name):
        res = json.loads(self._curl(1, name))
        if res["meta"]["total_count"] == 0:
            res = json.loads(self._curl(0, name))
        if res["meta"]["total_count"] == 0:
            return 0
        else:
            return res["objects"][0]


    def whois(self, irc, msg, args, name):
        """<name>

        Displays a Rep's full name and a link to their profile. <name> can either be a ReMo portal username or an IRC nick."""

        rep = self._lookup(name)
        if rep:
            profile = rep["profile"]
            irc.reply(name + " is '" + rep["fullname"] + "'' " + profile["profile_url"])
        else:
            irc.reply("That Rep doesn't exist.")
    whois = wrap(whois, ["text"])

    def mentor(self, irc, msg, args, name):
        """<name>

        Displays a Rep's mentor and a link to their mentor's profile. <name> can either be a ReMo portal username or an IRC nick."""

        rep = self._lookup(name)
        if rep:
            profile = rep["profile"]
            irc.reply(rep["first_name"] + "'s mentor is '")
        else:
            irc.reply("That Rep doesn't exist.")
    #mentor = wrap(mentor, ["text"])

Class = ReMo


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
