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
#// Diff API: WP_Text_Diff_Renderer_inline class
#// 
#// @package WordPress
#// @subpackage Diff
#// @since 4.7.0
#// 
#// 
#// Better word splitting than the PEAR package provides.
#// 
#// @since 2.6.0
#// @uses Text_Diff_Renderer_inline Extends
#//
class WP_Text_Diff_Renderer_inline(Text_Diff_Renderer_inline):
    #// 
    #// @ignore
    #// @since 2.6.0
    #// 
    #// @param string $string
    #// @param string $newlineEscape
    #// @return string
    #//
    def _splitonwords(self, string_=None, newlineEscape_="\n"):
        
        
        string_ = php_str_replace(" ", "", string_)
        words_ = php_preg_split("/([^\\w])/u", string_, -1, PREG_SPLIT_DELIM_CAPTURE)
        words_ = php_str_replace("\n", newlineEscape_, words_)
        return words_
    # end def _splitonwords
# end class WP_Text_Diff_Renderer_inline
