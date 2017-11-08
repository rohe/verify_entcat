# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1510155020.292707
_enable_loop = True
_template_filename = 'htdocs/check_result.mako'
_template_uri = 'check_result.mako'
_source_encoding = 'utf-8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        cmp = context.get('cmp', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('<!DOCTYPE html>\n<html>\n<head>\n\n    <script src="/static/jquery.min.1.9.1.js"></script>\n    <title></title>\n</head>\n    <script language="JavaScript">\n        var $j = jQuery.noConflict();\n\n        function exists() {\n            return true;\n        }\n        $j(document).ready(function() {\n            window.parent.verifyData(\'')
        __M_writer(str(cmp))
        __M_writer("');\n         });\n    </script>\n<body>\n</body>\n</html>")
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "htdocs/check_result.mako", "source_encoding": "utf-8", "uri": "check_result.mako", "line_map": {"16": 0, "24": 15, "30": 24, "22": 1, "23": 15}}
__M_END_METADATA
"""
