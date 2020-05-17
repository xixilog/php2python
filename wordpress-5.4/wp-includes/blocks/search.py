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
#// Server-side rendering of the `core/search` block.
#// 
#// @package WordPress
#// 
#// 
#// Dynamically renders the `core/search` block.
#// 
#// @param array $attributes The block attributes.
#// 
#// @return string The search block markup.
#//
def render_block_core_search(attributes_=None, *_args_):
    
    
    instance_id_ = 0
    instance_id_ += 1
    input_id_ = "wp-block-search__input-" + instance_id_
    label_markup_ = ""
    button_markup_ = ""
    if (not php_empty(lambda : attributes_["label"])):
        label_markup_ = php_sprintf("<label for=\"%s\" class=\"wp-block-search__label\">%s</label>", input_id_, attributes_["label"])
    else:
        label_markup_ = php_sprintf("<label for=\"%s\" class=\"wp-block-search__label screen-reader-text\">%s</label>", input_id_, __("Search"))
    # end if
    input_markup_ = php_sprintf("<input type=\"search\" id=\"%s\" class=\"wp-block-search__input\" name=\"s\" value=\"%s\" placeholder=\"%s\" required />", input_id_, esc_attr(get_search_query()), esc_attr(attributes_["placeholder"]))
    if (not php_empty(lambda : attributes_["buttonText"])):
        button_markup_ = php_sprintf("<button type=\"submit\" class=\"wp-block-search__button\">%s</button>", attributes_["buttonText"])
    # end if
    class_ = "wp-block-search"
    if (php_isset(lambda : attributes_["className"])):
        class_ += " " + attributes_["className"]
    # end if
    if (php_isset(lambda : attributes_["align"])):
        class_ += " align" + attributes_["align"]
    # end if
    return php_sprintf("<form class=\"%s\" role=\"search\" method=\"get\" action=\"%s\">%s</form>", class_, esc_url(home_url("/")), label_markup_ + input_markup_ + button_markup_)
# end def render_block_core_search
#// 
#// Registers the `core/search` block on the server.
#//
def register_block_core_search(*_args_):
    
    
    register_block_type("core/search", Array({"attributes": Array({"align": Array({"type": "string", "enum": Array("left", "center", "right", "wide", "full")})}, {"className": Array({"type": "string"})}, {"label": Array({"type": "string", "default": __("Search")})}, {"placeholder": Array({"type": "string", "default": ""})}, {"buttonText": Array({"type": "string", "default": __("Search")})})}, {"render_callback": "render_block_core_search"}))
# end def register_block_core_search
add_action("init", "register_block_core_search")
