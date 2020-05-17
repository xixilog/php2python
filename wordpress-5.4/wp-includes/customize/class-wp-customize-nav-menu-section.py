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
#// Customize API: WP_Customize_Nav_Menu_Section class
#// 
#// @package WordPress
#// @subpackage Customize
#// @since 4.4.0
#// 
#// 
#// Customize Menu Section Class
#// 
#// Custom section only needed in JS.
#// 
#// @since 4.3.0
#// 
#// @see WP_Customize_Section
#//
class WP_Customize_Nav_Menu_Section(WP_Customize_Section):
    #// 
    #// Control type.
    #// 
    #// @since 4.3.0
    #// @var string
    #//
    type = "nav_menu"
    #// 
    #// Get section parameters for JS.
    #// 
    #// @since 4.3.0
    #// @return array Exported parameters.
    #//
    def json(self):
        
        
        exported_ = super().json()
        exported_["menu_id"] = php_intval(php_preg_replace("/^nav_menu\\[(-?\\d+)\\]/", "$1", self.id))
        return exported_
    # end def json
# end class WP_Customize_Nav_Menu_Section
