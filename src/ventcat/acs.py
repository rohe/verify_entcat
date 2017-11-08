import json
import logging

import cherrypy
from saml2.response import StatusError
from saml2.response import VerificationError
from saml2.s_utils import UnknownPrincipal
from saml2.s_utils import UnsupportedBinding
from saml2.sigver import SignatureError

from ventcat import conv_response
from ventcat import Service
from ventcat.response import Response
from ventcat.response import ServiceError
from ventcat.response import Unauthorized

logger = logging.getLogger(__name__)


class ACS(Service):
    """
    Attribute Consuming Service
    """

    def __init__(self, sp, ec_test, cache=None,
                 lookup=None, res_db=None, policy=None, **kwargs):
        Service.__init__(self)
        self.sp = sp
        self.outstanding_queries = cache.outstanding_queries
        self.cache = cache
        self.response = None
        self.kwargs = kwargs
        self.ec_test = ec_test
        self.lookup = lookup
        self.res_db = res_db
        self.policy = policy

    @cherrypy.expose
    def index(self, binding, **kwargs):
        """
        :param binding: Which binding the query came in over
        """
        # tmp_outstanding_queries = dict(self.outstanding_queries)
        try:
            response = kwargs['SAMLResponse']
        except KeyError:
            logger.info("Missing Response")
            resp = Unauthorized('Unknown user')
            return conv_response(resp)

        try:
            self.response = self.sp.parse_authn_request_response(
                response, binding, self.outstanding_queries)
        except UnknownPrincipal as excp:
            logger.error("UnknownPrincipal: %s" % (excp,))
            resp = ServiceError("UnknownPrincipal: %s" % (excp,))
            return conv_response(resp)
        except UnsupportedBinding as excp:
            logger.error("UnsupportedBinding: %s" % (excp,))
            resp = ServiceError("UnsupportedBinding: %s" % (excp,))
            return conv_response(resp)
        except VerificationError as err:
            resp = ServiceError("Verification error: %s" % (err,))
            return conv_response(resp)
        except StatusError as err:
            resp = ServiceError("IdP Status error: %s" % (err,))
            return conv_response(resp)
        except SignatureError as err:
            resp = ServiceError("Signature error on response: %s" % (err,))
            return conv_response(resp)
        except Exception as err:
            resp = ServiceError("Other error: %s" % (err,))
            return conv_response(resp)

        # logger.info("parsed OK")
        _resp = self.response.response
        try:
            logger.info("SAML Response: %s" % str(self.response))
        except Exception:
            pass
        logger.info("AVA: %s" % self.response.ava)

        _cmp = self.verify_attributes(self.response.ava)
        # Log result to DB
        self.res_db.update_test_result(_resp.issuer.text, self.ec_test, _cmp)

        logger.info(
            ">{}>{}> {}".format(_resp.issuer.text, self.sp.config.entityid,
                                _cmp))

        resp = Response(mako_template="check_result.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "cmp": json.dumps({"data": _cmp})
        }
        return conv_response(resp, **argv)

    def verify_attributes(self, ava):
        logger.info("SP: %s" % self.sp.config.entityid)
        rest = self.policy.get_entity_categories(
            self.sp.config.entityid, self.sp.metadata, True)
        logger.info("policy: %s" % rest)

        akeys = [k.lower() for k in ava.keys()]

        res = {"less": [], "more": []}
        for key, attr in rest.items():
            if key not in ava:
                if key not in akeys:
                    res["less"].append(key)

        for key, attr in ava.items():
            _key = key.lower()
            if _key not in rest:
                res["more"].append(key)

        return res
