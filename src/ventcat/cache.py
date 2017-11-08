from http.cookies import SimpleCookie

import logging

from saml2 import time_util
from saml2.s_utils import rndstr

logger = logging.getLogger(__name__)

def _expiration(timeout, tformat=None):
    # Wed, 06-Jun-2012 01:34:34 GMT
    if not tformat:
        tformat = '%a, %d-%b-%Y %T GMT'

    if timeout == "now":
        return time_util.instant(tformat)
    else:
        # validity time should match lifetime of assertions
        return time_util.in_a_while(minutes=timeout, format=tformat)


class Cache(object):
    def __init__(self):
        self.uid2user = {}
        self.cookie_name = "spauthn"
        self.outstanding_queries = {}
        self.relay_state = {}
        self.user = {}
        self.result = {}

    def kaka2user(self, kaka):
        logger.debug("KAKA: %s" % kaka)
        if kaka:
            cookie_obj = SimpleCookie(kaka)
            morsel = cookie_obj.get(self.cookie_name, None)
            if morsel:
                try:
                    return self.uid2user[morsel.value]
                except KeyError:
                    return None
            else:
                logger.debug("No spauthn cookie")
        return None

    def delete_cookie(self, environ=None, kaka=None):
        if not kaka:
            kaka = environ.get("HTTP_COOKIE", '')
        logger.debug("delete KAKA: %s" % kaka)
        if kaka:
            _name = self.cookie_name
            cookie_obj = SimpleCookie(kaka)
            morsel = cookie_obj.get(_name, None)
            cookie = SimpleCookie()
            cookie[_name] = ""
            cookie[_name]['path'] = "/"
            logger.debug("Expire: %s" % morsel)
            cookie[_name]["expires"] = _expiration("dawn")
            return tuple(cookie.output().split(": ", 1))
        return None

    def user2kaka(self, user):
        uid = rndstr(32)
        self.uid2user[uid] = user
        cookie = SimpleCookie()
        cookie[self.cookie_name] = uid
        cookie[self.cookie_name]['path'] = "/"
        cookie[self.cookie_name]["expires"] = _expiration(480)
        logger.debug("Cookie expires: %s" % cookie[self.cookie_name]["expires"])
        return tuple(cookie.output().split(": ", 1))

