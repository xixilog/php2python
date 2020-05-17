#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import os
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
#// 
#// Install theme network administration panel.
#// 
#// @package WordPress
#// @subpackage Multisite
#// @since 3.1.0
#//
if (php_isset(lambda : PHP_REQUEST["tab"])) and "theme-information" == PHP_REQUEST["tab"]:
    php_define("IFRAME_REQUEST", True)
# end if
#// Load WordPress Administration Bootstrap
php_include_file(__DIR__ + "/admin.php", once=True)
php_include_file(ABSPATH + "wp-admin/theme-install.php", once=False)
