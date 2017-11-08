import cherrypy
import logging

from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2.s_utils import sid
from saml2.s_utils import rndstr
from ventcat import conv_response

from ventcat.response import parse_cookie
from ventcat.response import Redirect
from ventcat.response import Response
from ventcat.response import SeeOther
from ventcat.response import ServiceError

logger = logging.getLogger(__name__)


class SSO(object):
    def __init__(self, sp, cache=None, wayf=None, discosrv=None, bindings=None,
                 entity_id=None):
        self.sp = sp
        self.cache = cache
        self.idp_query_param = "IdpQuery"
        self.wayf = wayf
        self.discosrv = discosrv
        self.entity_id = entity_id
        if bindings:
            self.bindings = bindings
        else:
            self.bindings = [BINDING_HTTP_REDIRECT, BINDING_HTTP_POST,
                             BINDING_HTTP_ARTIFACT]
        logger.debug("--- SSO ---")

    def response(self, binding, http_args, ):
        if binding == BINDING_HTTP_ARTIFACT:
            resp = Redirect()
        elif binding == BINDING_HTTP_REDIRECT:
            for param, value in http_args["headers"]:
                if param == "Location":
                    resp = SeeOther(str(value))
                    break
            else:
                resp = ServiceError("Parameter error")
        else:
            resp = Response(http_args["data"], headers=http_args["headers"])

        return resp

    def _wayf_redirect(self, came_from):
        sid_ = sid()
        self.cache.outstanding_queries[sid_] = came_from
        logger.debug("Redirect to WAYF function: %s" % self.wayf)
        return -1, SeeOther(headers=[('Location', "%s?%s" % (self.wayf, sid_))])

    def _pick_idp(self, came_from, **kwargs):
        """
        If more than one idp and if none is selected, I have to do wayf or
        disco
        """

        # Find all IdPs
        idps = self.sp.metadata.with_descriptor("idpsso")

        try:
            kaka = cherrypy.request.headers["Cookie"]
        except KeyError:
            pass
        else:
            try:
                (idp_entity_id, _) = parse_cookie("ve_disco", "SEED_SAW", kaka)
            except ValueError:
                pass
            except TypeError:
                pass

        try:
            idp_entity_id = kwargs[self.idp_query_param]
        except KeyError:
            logger.debug("No IdP entity ID in query")

            if self.wayf:
                try:
                    wayf_selected = kwargs["wayf_selected"]
                except KeyError:
                    return self._wayf_redirect(came_from)
                idp_entity_id = wayf_selected
            elif self.discosrv:
                try:
                    idp_entity_id = self.sp.parse_discovery_service_response(
                        **kwargs)
                except Exception:
                    idp_entity_id = ''

                if not idp_entity_id:
                    sid_ = sid()
                    self.cache.outstanding_queries[sid_] = came_from
                    logger.debug("Redirect to Discovery Service function")
                    eid = self.sp.config.entityid
                    ret = self.sp.config.getattr(
                        "endpoints","sp")["discovery_response"][0][0]
                    ret += "?sid=%s" % sid_
                    loc = self.sp.create_discovery_service_request(
                        self.discosrv, eid, **{"return": ret})
                    return -1, SeeOther(loc)
            elif len(idps) == 1:
                # idps is a dictionary
                idp_entity_id = list(idps.keys())[0]
            elif not len(idps):
                return -1, ServiceError('Misconfiguration')
            else:
                return -1, NotImplemented("No WAYF or DS present!")

        logger.info("Chosen IdP: '%s'" % idp_entity_id)
        return 0, idp_entity_id

    def _redirect_to_auth(self, _cli, entity_id, came_from, vorg_name=""):
        try:
            _binding, destination = _cli.pick_binding(
                "single_sign_on_service", self.bindings, "idpsso",
                entity_id=entity_id)
            logger.debug("binding: %s, destination: %s" % (_binding,
                                                           destination))
            _id, req = _cli.create_authn_request(destination, vorg=vorg_name)
            _rstate = rndstr()
            self.cache.relay_state[_rstate] = came_from
            ht_args = _cli.apply_binding(_binding, "%s" % (req,), destination,
                                         relay_state=_rstate)
            _sid = req.id
            logger.debug("ht_args: %s" % ht_args)
        except Exception as exc:
            logger.exception(exc)
            resp = ServiceError(
                "Failed to construct the AuthnRequest: %s" % exc)
            return resp

        # remember the request
        self.cache.outstanding_queries[_sid] = came_from
        return self.response(_binding, ht_args)

    @cherrypy.expose
    def index(self, endp, **kwargs):
        _cli = self.sp

        # If more than one idp and if none is selected, I have to do wayf
        (done, response) = self._pick_idp(endp)
        # Two cases: -1 something went wrong or Discovery service used
        # 0 I've got an IdP to send a request to
        logger.debug("_idp_pick returned: %s" % done)
        if done == -1:
            return conv_response(response)
        else:
            entity_id = response
            # Do the AuthnRequest
            resp = self._redirect_to_auth(_cli, entity_id, endp)
            return conv_response(resp)
