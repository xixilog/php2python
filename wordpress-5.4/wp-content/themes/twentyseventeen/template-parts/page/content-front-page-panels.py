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
#// Template part for displaying pages on front page
#// 
#// @package WordPress
#// @subpackage Twenty_Seventeen
#// @since Twenty Seventeen 1.0
#// @version 1.0
#//
global twentyseventeencounter_
php_check_if_defined("twentyseventeencounter_")
php_print("\n<article id=\"panel")
php_print(twentyseventeencounter_)
php_print("\" ")
post_class("twentyseventeen-panel ")
php_print(" >\n\n   ")
if has_post_thumbnail():
    thumbnail_ = wp_get_attachment_image_src(get_post_thumbnail_id(post_.ID), "twentyseventeen-featured-image")
    #// Calculate aspect ratio: h / w * 100%.
    ratio_ = thumbnail_[2] / thumbnail_[1] * 100
    php_print("\n       <div class=\"panel-image\" style=\"background-image: url(")
    php_print(esc_url(thumbnail_[0]))
    php_print(");\">\n          <div class=\"panel-image-prop\" style=\"padding-top: ")
    php_print(esc_attr(ratio_))
    php_print("""%\"></div>
    </div><!-- .panel-image -->
    """)
# end if
php_print("""
<div class=\"panel-content\">
<div class=\"wrap\">
<header class=\"entry-header\">
""")
the_title("<h2 class=\"entry-title\">", "</h2>")
php_print("\n               ")
twentyseventeen_edit_link(get_the_ID())
php_print("""
</header><!-- .entry-header -->
<div class=\"entry-content\">
""")
the_content(php_sprintf(__("Continue reading<span class=\"screen-reader-text\"> \"%s\"</span>", "twentyseventeen"), get_the_title()))
php_print("         </div><!-- .entry-content -->\n\n           ")
#// Show recent blog posts if is blog posts page (Note that get_option returns a string, so we're casting the result as an int).
if get_the_ID() == php_int(get_option("page_for_posts")):
    php_print("\n               ")
    #// Show three most recent posts.
    recent_posts_ = php_new_class("WP_Query", lambda : WP_Query(Array({"posts_per_page": 3, "post_status": "publish", "ignore_sticky_posts": True, "no_found_rows": True})))
    php_print("\n               ")
    if recent_posts_.have_posts():
        php_print("""
        <div class=\"recent-posts\">
        """)
        while True:
            
            if not (recent_posts_.have_posts()):
                break
            # end if
            recent_posts_.the_post()
            get_template_part("template-parts/post/content", "excerpt")
        # end while
        wp_reset_postdata()
        php_print("                 </div><!-- .recent-posts -->\n              ")
    # end if
    php_print("         ")
# end if
php_print("""
</div><!-- .wrap -->
</div><!-- .panel-content -->
</article><!-- #post-""")
the_ID()
php_print(" -->\n")
