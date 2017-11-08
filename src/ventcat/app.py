import json

import cherrypy
import logging

from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT

from ventcat import conv_response, as_unicode
from ventcat import UnSupported
from ventcat.acs import ACS
from ventcat.response import Response, make_cookie
from ventcat.sso import SSO

logger = logging.getLogger(__name__)

BINDING_MAP = {'post': BINDING_HTTP_POST, 'redirect': BINDING_HTTP_REDIRECT}


class Application():
    def __init__(self, sp, cache, lookup, ec_sequence, ec_information,
                 res_db, sso_args, policy):
        self.sp = sp
        self.cache = cache
        self.lookup = lookup
        self.ec_sequence = ec_sequence
        self.ec_information = ec_information
        self.res_db = res_db
        self.sso = dict(
            [(e, SSO(s, cache=cache, **sso_args)) for e, s in sp.items()])
        self.sso_args = sso_args
        self.policy = policy

        self.acs_handler = {}
        for key, _sso in self.sso.items():
            if key == '':
                self.acs_handler[key] = ACS(_sso.sp, cache=self.cache,
                                            lookup=self.lookup,
                                            res_db=self.res_db,
                                            policy=self.policy, ec_test='base')
            else:
                self.acs_handler[key] = ACS(_sso.sp, cache=self.cache,
                                            lookup=self.lookup,
                                            res_db=self.res_db,
                                            policy=self.policy, ec_test=key)

    def _cp_dispatch(self, vpath):
        # Only get here if vpath != None
        ent = cherrypy.request.remote.ip
        logger.info('ent:{}, vpath: {}'.format(ent, vpath))
        if vpath[0] == 'static':
            return self

        if len(vpath) >= 2:
            # acs/<ec>/post or acs/<ec>/redirect
            if vpath[0] == 'acs':
                # if cherrypy.request.method == 'POST':
                #     if cherrypy.request.process_request_body is True:
                #         try:
                #             _response = as_unicode(cherrypy.request.body.read())
                #         except ValueError:
                #             raise ValueError('No body')
                #         else:
                #             cherrypy.request.params['response'] = _response
                # else:
                #     cherrypy.request.params['response'] = ''

                vpath.pop(0)  # remove the 'acs'
                if vpath[0] in ['post', 'redirect']:
                    ec = ''
                    cherrypy.request.params['binding'] = BINDING_MAP[vpath[0]]
                    vpath.pop(0)
                else:
                    ec = vpath.pop(0)
                    if vpath[0] in ['post', 'redirect']:
                        cherrypy.request.params['binding'] = BINDING_MAP[
                            vpath[0]]
                        vpath.pop(0)
                    else:
                        raise UnSupported('binding: ')

                return self.acs_handler[ec]

        return self

    @cherrypy.expose
    def test(self, **kwargs):
        resp = Response(mako_template="test.mako",
                        template_lookup=self.lookup,
                        headers=[])

        str_ec_seq = []
        for ec in self.ec_sequence:
            str_ec_seq.append(str(ec))

        argv = {
            # "ec_seq_json": json.dumps(EC_SEQUENCE),
            "ec_seq": str_ec_seq,
            "ec_info": self.ec_information
        }
        return conv_response(resp, **argv)

    @cherrypy.expose
    def overview(self, **kwargs):
        resp = Response(mako_template="test_overview.mako",
                        template_lookup=self.lookup,
                        headers=[])
        str_ec_seq = []
        for ec in self.ec_sequence:
            str_ec_seq.append(str(ec))
        argv = {
            # "ec_seq_json": json.dumps(EC_SEQUENCE),
            "ec_seq": json.dumps(str_ec_seq),
            "ec_info": json.dumps(self.ec_information),
            "test_results": json.dumps(self.res_db.get_overview_data())
        }
        return conv_response(resp, **argv)

    @cherrypy.expose
    def disco(self, **kwargs):
        entity_id = kwargs["entityID"]
        sid = kwargs["sid"]
        came_from = self.cache.outstanding_queries[sid]
        _sso = SSO(self.sp[''], cache=self.cache, **self.sso_args)
        resp = _sso._redirect_to_auth(_sso.sp, entity_id, came_from)

        # Add cookie
        kaka = make_cookie("ve_disco", entity_id, "SEED_SAW")
        resp.headers.append(kaka)
        return conv_response(resp)

    @cherrypy.expose
    def login(self):
        _sso = SSO(self.sp[''], cache=self.cache, **self.sso_args)
        return _sso.index()

    @cherrypy.expose
    def ecat(self, **kwargs):
        if kwargs['c'] == 'base':
            _sso = SSO(self.sp[''], cache=self.cache, **self.sso_args)
        else:
            _sso = SSO(self.sp[kwargs['c']], cache=self.cache, **self.sso_args)
        return _sso.index('ecat')
