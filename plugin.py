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
import urllib
try:
    import simplejson as json
except ImportError:
    import json

def curl(rep, query):
    c = pycurl.Curl()
    b = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    if rep:
        c.setopt(pycurl.URL, "https://reps.mozilla.org/api/v1/rep/?limit=0&" + query)
    else:
        c.setopt(pycurl.URL, "https://reps.mozilla.org/api/v1/event/??limit=0&" + query)
    c.perform()
    return b.getvalue()

def rep_lookup(attribute):
    res = json.loads(curl(1, "profile__" + attribute))
    if res["meta"]["total_count"] == 0:
        return 0
    else:
        return res["objects"]

def rep_lookup_by_name(name):
    name = urllib.quote_plus(name)
    reps = rep_lookup("display_name=" + name)
    if reps:
        return reps
    else:
        reps = rep_lookup("irc_name=" + name)
        if reps:
            return reps
        else:
            return 0


def rep_lookup_by_place(place):
    place = urllib.quote_plus(place)
    reps = rep_lookup("country=" + place)
    if reps:
        return reps
    else:
        reps = rep_lookup("region=" + place)
        if reps:
            return reps
        else:
            reps = rep_lookup("city=" + place)
            if reps:
                return reps
            else:
                return 0

class ReMo(callbacks.Plugin):
    """Add the help for "@plugin help ReMo" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(ReMo, self)
        self.__parent.__init__(irc)

    def whois(self, irc, msg, args, name):
        """<name>

        Displays a Rep's full name and a link to their profile. <name> can either be a ReMo portal username or an IRC nick."""

        reps = rep_lookup_by_name(name)
        if reps:
            rep = reps[0]
            profile = rep["profile"]
            irc.reply(name + " is '" + rep["fullname"] + "' " + profile["profile_url"])
        else:
            irc.reply("Sorry, I don't recognise that Rep. :(")
    whois = wrap(whois, ["text"])

    def council(self, irc, msg, args):
        """takes no arguments

        List the members of the ReMo Council."""

        reps = rep_lookup("council=true")
        for rep in reps:
            profile = rep["profile"]
            irc.reply(rep["fullname"] + " " + profile["profile_url"])
    #council = wrap(council)

    def mentors(self, irc, msg, args):
        """takes no arguments

        List the Reps who are Mentors."""

        reps = rep_lookup("mentor=true")
        for rep in reps:
            profile = rep["profile"]
            irc.reply(rep["fullname"] + " " + profile["profile_url"])
    #mentors = wrap(mentors)

    class reps(callbacks.Commands):

        def place(self, irc, msg, args, place):
            """<place>

            Displays all the Reps from a particular place. <place> can either be a country, region or city."""

            reps = rep_lookup_by_place(place)
            if reps:
                for rep in reps:
                    profile = rep["profile"]
                    irc.reply(rep["fullname"] + " " + profile["profile_url"])
            else:
                irc.reply("There are no Reps in that place.")
        place = wrap(place, ["text"])

        def interest(self, irc, msg, args, interest):
            """<interest>

            Displays Reps with a particular interest."""

            reps = rep_lookup("functional_areas__name="+interest)
            if reps:
                for rep in reps:
                    profile = rep["profile"]
                    irc.reply(rep["fullname"] + " " + profile["profile_url"])
            else:
                irc.reply("Sorry, I don't recognise that interest. :(")
        interest = wrap(interest, ["text"])

Class = ReMo


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
