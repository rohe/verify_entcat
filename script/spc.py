#!/usr/bin/env python
import json
import logging
import argparse
import os

import cherrypy

import server_conf
import category_desc_conf

from mako.lookup import TemplateLookup
from saml2.client import Saml2Client
from saml2.config import SPConfig

from ventcat.app import Application
from ventcat.cache import Cache
from ventcat.resdb import ResultDB

logger = logging.getLogger("")
hdlr = logging.FileHandler('spx.log')
base_formatter = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

hdlr.setFormatter(base_formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

COMBOS = json.loads(open("build.json").read())
EC_SEQUENCE = [""]
EC_SEQUENCE.extend(COMBOS.keys())

SP = {}
SEED = ""
POLICY = None

LOOKUP = TemplateLookup(directories=['templates', 'htdocs'],
                        module_directory='modules',
                        input_encoding='utf-8',
                        output_encoding='utf-8')

PORT = server_conf.PORT
# ------- HTTPS -------
# These should point to relevant files
SERVER_CERT = server_conf.SERVER_CERT
SERVER_KEY = server_conf.SERVER_KEY
# This is of course the certificate chain for the CA that signed
# you cert and all the way up to the top
CERT_CHAIN = server_conf.CERT_CHAIN

if __name__ == '__main__':
    _parser = argparse.ArgumentParser()
    _parser.add_argument('-d', dest='debug', action='store_true',
                         help="Print debug information")
    _parser.add_argument(
        '-E', dest='entity_id',
        help="If you only want to test one IdP you can manually set the "
             "entity id.")
    _parser.add_argument('-D', dest='discosrv',
                         help="Which disco server to use")
    _parser.add_argument('-s', dest='seed',
                         help="Cookie seed")
    _parser.add_argument('-W', dest='wayf', action='store_true',
                         help="Which WAYF url to use")
    _parser.add_argument("config", help="SAML client config")

    ARGS = {}
    _args = _parser.parse_args()

    if _args.entity_id:
        ARGS["entity_id"] = _args.entity_id
    if _args.discosrv:
        ARGS["discosrv"] = _args.discosrv
    if _args.wayf:
        ARGS["wayf"] = _args.wayf

    CNFBASE = _args.config
    if _args.seed:
        SEED = _args.seed
    else:
        SEED = "SnabbtInspel"

    cherrypy.config.update(
        {'environment': 'production',
         'log.error_file': 'site.log',
         'tools.trailing_slash.on': False,
         'server.socket_host': '0.0.0.0',
         'log.screen': True,
         'tools.sessions.on': True,
         'tools.encode.on': True,
         'tools.encode.encoding': 'utf-8',
         'server.socket_port': PORT
         })

    folder = os.path.abspath(os.curdir)

    provider_config = {
        '/': {
            'root_path': 'localhost',
            'log.screen': True
        },
        '/static': {
            'tools.staticdir.dir': os.path.join(folder, 'static'),
            'tools.staticdir.debug': True,
            'tools.staticdir.on': True,
            'log.screen': True,
            'cors.expose_public.on': True
        },
        '/bootstrap': {
            'tools.staticdir.dir': os.path.join(folder, 'static', 'bootstrap'),
            'tools.staticdir.debug': True,
            'tools.staticdir.on': True,
            'log.screen': True,
            'cors.expose_public.on': True
        },
        '/modules': {
            'tools.staticdir.dir': os.path.join(folder, 'modules'),
            'tools.staticdir.debug': True,
            'tools.staticdir.on': True,
            'log.screen': True,
            'cors.expose_public.on': True
        },
        '/htdocs': {
            'tools.staticdir.dir': os.path.join(folder, 'htdocs'),
            'tools.staticdir.debug': True,
            'tools.staticdir.on': True,
            'log.screen': True,
            'cors.expose_public.on': True
        }
    }

    sp_base_conf = SPConfig().load_file("%s" % CNFBASE,
                                        metadata_construction=False)

    SP[""] = Saml2Client(config=sp_base_conf)
    for variant in EC_SEQUENCE[1:]:
        sp_conf = SPConfig().load_file(config_file="%s_%s" % (CNFBASE, variant),
                                       metadata_construction=True)
        sp_conf.metadata = sp_base_conf.metadata
        SP[variant] = Saml2Client(config=sp_conf)

    POLICY = server_conf.POLICY
    for entcat in SP:
        sp = SP[entcat]
        attr_list = POLICY.get_entity_categories(sp.config.entityid,
                                                 sp.metadata,
                                                 True)
        attr_html_list = ""
        if attr_list is not None and len(attr_list) > 0:
            attr_html_list += "<ul>"
            for attr in attr_list:
                attr_html_list += "<li>%s</li>" % attr
            attr_html_list += "</ul>"
            category_desc_conf.EC_INFORMATION[entcat][
                "Description"] += category_desc_conf.RETURN_CATEGORY + \
                                  attr_html_list
        pass

    # sso_args = wayf=None, discosrv=None, bindings=None
    application = Application(SP, cache=Cache(), lookup=LOOKUP,
                              ec_sequence=EC_SEQUENCE,
                              res_db=ResultDB(server_conf.DB_PATH),
                              ec_information=category_desc_conf.EC_INFORMATION,
                              sso_args=ARGS, policy=POLICY)
    cherrypy.tree.mount(application, "/", provider_config)

    # Unsubscribe the default server
    cherrypy.server.unsubscribe()

    server = cherrypy._cpserver.Server()
    server.socket_host = "0.0.0.0"
    server.socket_port = PORT

    server.subscribe()

    if server_conf.HTTPS:
        cherrypy.server.ssl_module = 'builtin'
        cherrypy.server.ssl_certificate = SERVER_CERT
        cherrypy.server.ssl_private_key = SERVER_KEY
        if CERT_CHAIN:
            cherrypy.server.ssl_certificate_chain = CERT_CHAIN

    logger.info("Server starting")
    print("SP listening on port: %s" % PORT)

    cherrypy.engine.start()
    cherrypy.engine.block()
