import logging
from http.cookies import SimpleCookie

import cherrypy
from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_SOAP
from ventcat.response import BadRequest
from ventcat.response import Redirect
from ventcat.response import Response
from ventcat.response import Unauthorized

__author__ = 'Roland Hedberg'
__version__ = '0.4.0'

logger = logging.getLogger("")

class UnSupported(Exception):
    pass


def as_bytes(s):
    """
    Convert an unicode string to bytes.
    :param s: Unicode / bytes string
    :return: bytes string
    """
    try:
        s = s.encode()
    except (AttributeError, UnicodeDecodeError):
        pass
    return s


def as_unicode(b):
    """
    Convert a byte string to a unicode string
    :param b: byte string
    :return: unicode string
    """
    try:
        b = b.decode()
    except (AttributeError, UnicodeDecodeError):
        pass
    return b


def conv_response(resp, **kwargs):
    if not isinstance(resp, Response):
        return as_bytes(resp)

    if kwargs:
        resp(**kwargs)
    cookie = cherrypy.response.cookie
    for header, value in resp.headers:
        if header == 'Set-Cookie':
            cookie_obj = SimpleCookie(value)
            for name in cookie_obj:
                morsel = cookie_obj[name]
                cookie[name] = morsel.value
                for key in ['expires', 'path', 'comment', 'domain', 'max-age',
                            'secure', 'version']:
                    if morsel[key]:
                        cookie[name][key] = morsel[key]

    _stat = int(resp._status.split(' ')[0])
    if _stat < 300:
        cherrypy.response.status = _stat
        for key, val in resp.headers:
            cherrypy.response.headers[key] = val
        return as_bytes(resp.message)
    elif 300 <= _stat < 400:
        raise cherrypy.HTTPRedirect(resp.message, status=_stat)
    else:
        raise cherrypy.HTTPError(_stat, message=resp.message)


class Service(object):
    def __init__(self, user=None):
        self.user = user
        self.sp = None

    def unpack_post(self):
        if cherrypy.request.process_request_body is True:
            _request = as_unicode(cherrypy.request.body.read())
            logger.debug("unpack_post:: %s" % _request)
            return _request
        else:
            raise ValueError('No body')

    def unpack_soap(self):
        if cherrypy.request.process_request_body is True:
            _request = as_unicode(cherrypy.request.body.read())
        else:
            raise ValueError('No body')

        return {"SAMLResponse": _request, "RelayState": ""}

    def unpack_either(self, **kwargs):
        if cherrypy.request.method == "GET":
            pass
        elif cherrypy.request.method == "POST":
            kwargs = self.unpack_post()
        else:
            kwargs = {}
        logger.debug("_kwargs: {}".format(kwargs))
        return kwargs

    def operation(self, binding, **kwargs):
        logger.debug("_operation: %s" % kwargs)
        if not kwargs:
            resp = BadRequest('Error parsing request or no request')
            return conv_response(resp)
        else:
            try:
                _relay_state = kwargs["RelayState"]
            except KeyError:
                _relay_state = ""
            if "SAMLResponse" in kwargs:
                return self.do(kwargs["SAMLResponse"], binding,
                               _relay_state, mtype="response")
            elif "SAMLRequest" in kwargs:
                return self.do(kwargs["SAMLRequest"], binding,
                               _relay_state, mtype="request")

    def artifact_operation(self, **kwargs):
        if not kwargs:
            resp = BadRequest("Missing query")
            return conv_response(resp)
        else:
            # exchange artifact for response
            request = self.sp.artifact2message(kwargs["SAMLart"], "spsso")
            return self.do(request, BINDING_HTTP_ARTIFACT, kwargs["RelayState"])

    def response(self, binding, http_args):
        if binding == BINDING_HTTP_ARTIFACT:
            resp = Redirect()
        else:
            resp = Response(http_args["data"], headers=http_args["headers"])
        return conv_response(resp)

    def do(self, query, binding, relay_state="", mtype="response"):
        pass

    def redirect(self, **kwargs):
        """ Expects a HTTP-redirect response """

        return self.operation(BINDING_HTTP_REDIRECT, **kwargs)

    def post(self):
        """ Expects a HTTP-POST response """

        kwargs = self.unpack_post()
        return self.operation(BINDING_HTTP_POST, **kwargs)

    def artifact(self):
        # Can be either by HTTP_Redirect or HTTP_POST
        _dict = self.unpack_either()
        return self.artifact_operation(**_dict)

    def soap(self):
        """
        Single log out using HTTP_SOAP binding
        """
        logger.debug("- SOAP -")
        kwargs = self.unpack_soap()
        logger.debug("_kwargs: {}".format(kwargs))
        return self.operation(BINDING_SOAP, **kwargs)

    def uri(self):
        kwargs = self.unpack_either()
        logger.debug("_kwargs: {}".format(kwargs))
        return self.operation(BINDING_SOAP, **kwargs)

    def not_authn(self):
        resp = Unauthorized('Unknown user')

        return conv_response(resp)

