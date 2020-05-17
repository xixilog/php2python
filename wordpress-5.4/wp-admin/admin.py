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
#// WordPress Administration Bootstrap
#// 
#// @package WordPress
#// @subpackage Administration
#// 
#// 
#// In WordPress Administration Screens
#// 
#// @since 2.3.2
#//
if (not php_defined("WP_ADMIN")):
    php_define("WP_ADMIN", True)
# end if
if (not php_defined("WP_NETWORK_ADMIN")):
    php_define("WP_NETWORK_ADMIN", False)
# end if
if (not php_defined("WP_USER_ADMIN")):
    php_define("WP_USER_ADMIN", False)
# end if
if (not WP_NETWORK_ADMIN) and (not WP_USER_ADMIN):
    php_define("WP_BLOG_ADMIN", True)
# end if
if (php_isset(lambda : PHP_REQUEST["import"])) and (not php_defined("WP_LOAD_IMPORTERS")):
    php_define("WP_LOAD_IMPORTERS", True)
# end if
php_include_file(php_dirname(__DIR__) + "/wp-load.php", once=True)
nocache_headers()
if get_option("db_upgraded"):
    flush_rewrite_rules()
    update_option("db_upgraded", False)
    #// 
    #// Fires on the next page load after a successful DB upgrade.
    #// 
    #// @since 2.8.0
    #//
    do_action("after_db_upgrade")
elif get_option("db_version") != wp_db_version_ and php_empty(lambda : PHP_POST):
    if (not is_multisite()):
        wp_redirect(admin_url("upgrade.php?_wp_http_referer=" + urlencode(wp_unslash(PHP_SERVER["REQUEST_URI"]))))
        php_exit(0)
    # end if
    #// 
    #// Filters whether to attempt to perform the multisite DB upgrade routine.
    #// 
    #// In single site, the user would be redirected to wp-admin/upgrade.php.
    #// In multisite, the DB upgrade routine is automatically fired, but only
    #// when this filter returns true.
    #// 
    #// If the network is 50 sites or less, it will run every time. Otherwise,
    #// it will throttle itself to reduce load.
    #// 
    #// @since MU (3.0.0)
    #// 
    #// @param bool $do_mu_upgrade Whether to perform the Multisite upgrade routine. Default true.
    #//
    if apply_filters("do_mu_upgrade", True):
        c_ = get_blog_count()
        #// 
        #// If there are 50 or fewer sites, run every time. Otherwise, throttle to reduce load:
        #// attempt to do no more than threshold value, with some +/- allowed.
        #//
        if c_ <= 50 or c_ > 50 and mt_rand(0, php_int(c_ / 50)) == 1:
            php_include_file(ABSPATH + WPINC + "/http.php", once=True)
            response_ = wp_remote_get(admin_url("upgrade.php?step=1"), Array({"timeout": 120, "httpversion": "1.1"}))
            #// This action is documented in wp-admin/network/upgrade.php
            do_action("after_mu_upgrade", response_)
            response_ = None
        # end if
        c_ = None
    # end if
# end if
php_include_file(ABSPATH + "wp-admin/includes/admin.php", once=True)
auth_redirect()
#// Schedule Trash collection.
if (not wp_next_scheduled("wp_scheduled_delete")) and (not wp_installing()):
    wp_schedule_event(time(), "daily", "wp_scheduled_delete")
# end if
#// Schedule transient cleanup.
if (not wp_next_scheduled("delete_expired_transients")) and (not wp_installing()):
    wp_schedule_event(time(), "daily", "delete_expired_transients")
# end if
set_screen_options()
date_format_ = __("F j, Y")
time_format_ = __("g:i a")
wp_enqueue_script("common")
#// 
#// $pagenow is set in vars.php
#// $wp_importers is sometimes set in wp-admin/includes/import.php
#// The remaining variables are imported as globals elsewhere, declared as globals here
#// 
#// @global string $pagenow
#// @global array  $wp_importers
#// @global string $hook_suffix
#// @global string $plugin_page
#// @global string $typenow
#// @global string $taxnow
#//
global pagenow_
global wp_importers_
global hook_suffix_
global plugin_page_
global typenow_
global taxnow_
php_check_if_defined("pagenow_","wp_importers_","hook_suffix_","plugin_page_","typenow_","taxnow_")
page_hook_ = None
editing_ = False
if (php_isset(lambda : PHP_REQUEST["page"])):
    plugin_page_ = wp_unslash(PHP_REQUEST["page"])
    plugin_page_ = plugin_basename(plugin_page_)
# end if
if (php_isset(lambda : PHP_REQUEST["post_type"])) and post_type_exists(PHP_REQUEST["post_type"]):
    typenow_ = PHP_REQUEST["post_type"]
else:
    typenow_ = ""
# end if
if (php_isset(lambda : PHP_REQUEST["taxonomy"])) and taxonomy_exists(PHP_REQUEST["taxonomy"]):
    taxnow_ = PHP_REQUEST["taxonomy"]
else:
    taxnow_ = ""
# end if
if WP_NETWORK_ADMIN:
    php_include_file(ABSPATH + "wp-admin/network/menu.php", once=False)
elif WP_USER_ADMIN:
    php_include_file(ABSPATH + "wp-admin/user/menu.php", once=False)
else:
    php_include_file(ABSPATH + "wp-admin/menu.php", once=False)
# end if
if current_user_can("manage_options"):
    wp_raise_memory_limit("admin")
# end if
#// 
#// Fires as an admin screen or script is being initialized.
#// 
#// Note, this does not just run on user-facing admin screens.
#// It runs on admin-ajax.php and admin-post.php as well.
#// 
#// This is roughly analogous to the more general {@see 'init'} hook, which fires earlier.
#// 
#// @since 2.5.0
#//
do_action("admin_init")
if (php_isset(lambda : plugin_page_)):
    if (not php_empty(lambda : typenow_)):
        the_parent_ = pagenow_ + "?post_type=" + typenow_
    else:
        the_parent_ = pagenow_
    # end if
    page_hook_ = get_plugin_page_hook(plugin_page_, the_parent_)
    if (not page_hook_):
        page_hook_ = get_plugin_page_hook(plugin_page_, plugin_page_)
        #// Back-compat for plugins using add_management_page().
        if php_empty(lambda : page_hook_) and "edit.php" == pagenow_ and get_plugin_page_hook(plugin_page_, "tools.php"):
            #// There could be plugin specific params on the URL, so we need the whole query string.
            if (not php_empty(lambda : PHP_SERVER["QUERY_STRING"])):
                query_string_ = PHP_SERVER["QUERY_STRING"]
            else:
                query_string_ = "page=" + plugin_page_
            # end if
            wp_redirect(admin_url("tools.php?" + query_string_))
            php_exit(0)
        # end if
    # end if
    the_parent_ = None
# end if
hook_suffix_ = ""
if (php_isset(lambda : page_hook_)):
    hook_suffix_ = page_hook_
elif (php_isset(lambda : plugin_page_)):
    hook_suffix_ = plugin_page_
elif (php_isset(lambda : pagenow_)):
    hook_suffix_ = pagenow_
# end if
set_current_screen()
#// Handle plugin admin pages.
if (php_isset(lambda : plugin_page_)):
    if page_hook_:
        #// 
        #// Fires before a particular screen is loaded.
        #// 
        #// The load-* hook fires in a number of contexts. This hook is for plugin screens
        #// where a callback is provided when the screen is registered.
        #// 
        #// The dynamic portion of the hook name, `$page_hook`, refers to a mixture of plugin
        #// page information including:
        #// 1. The page type. If the plugin page is registered as a submenu page, such as for
        #// Settings, the page type would be 'settings'. Otherwise the type is 'toplevel'.
        #// 2. A separator of '_page_'.
        #// 3. The plugin basename minus the file extension.
        #// 
        #// Together, the three parts form the `$page_hook`. Citing the example above,
        #// the hook name used would be 'load-settings_page_pluginbasename'.
        #// 
        #// @see get_plugin_page_hook()
        #// 
        #// @since 2.1.0
        #//
        do_action(str("load-") + str(page_hook_))
        #// phpcs:ignore WordPress.NamingConventions.ValidHookName.UseUnderscores
        if (not (php_isset(lambda : PHP_REQUEST["noheader"]))):
            php_include_file(ABSPATH + "wp-admin/admin-header.php", once=True)
        # end if
        #// 
        #// Used to call the registered callback for a plugin screen.
        #// 
        #// This hook uses a dynamic hook name, `$page_hook`, which refers to a mixture of plugin
        #// page information including:
        #// 1. The page type. If the plugin page is registered as a submenu page, such as for
        #// Settings, the page type would be 'settings'. Otherwise the type is 'toplevel'.
        #// 2. A separator of '_page_'.
        #// 3. The plugin basename minus the file extension.
        #// 
        #// Together, the three parts form the `$page_hook`. Citing the example above,
        #// the hook name used would be 'settings_page_pluginbasename'.
        #// 
        #// @see get_plugin_page_hook()
        #// 
        #// @since 1.5.0
        #//
        do_action(page_hook_)
    else:
        if validate_file(plugin_page_):
            wp_die(__("Invalid plugin page."))
        # end if
        if (not php_file_exists(WP_PLUGIN_DIR + str("/") + str(plugin_page_)) and php_is_file(WP_PLUGIN_DIR + str("/") + str(plugin_page_))) and (not php_file_exists(WPMU_PLUGIN_DIR + str("/") + str(plugin_page_)) and php_is_file(WPMU_PLUGIN_DIR + str("/") + str(plugin_page_))):
            #// translators: %s: Admin page generated by a plugin.
            wp_die(php_sprintf(__("Cannot load %s."), htmlentities(plugin_page_)))
        # end if
        #// 
        #// Fires before a particular screen is loaded.
        #// 
        #// The load-* hook fires in a number of contexts. This hook is for plugin screens
        #// where the file to load is directly included, rather than the use of a function.
        #// 
        #// The dynamic portion of the hook name, `$plugin_page`, refers to the plugin basename.
        #// 
        #// @see plugin_basename()
        #// 
        #// @since 1.5.0
        #//
        do_action(str("load-") + str(plugin_page_))
        #// phpcs:ignore WordPress.NamingConventions.ValidHookName.UseUnderscores
        if (not (php_isset(lambda : PHP_REQUEST["noheader"]))):
            php_include_file(ABSPATH + "wp-admin/admin-header.php", once=True)
        # end if
        if php_file_exists(WPMU_PLUGIN_DIR + str("/") + str(plugin_page_)):
            php_include_file(WPMU_PLUGIN_DIR + str("/") + str(plugin_page_), once=False)
        else:
            php_include_file(WP_PLUGIN_DIR + str("/") + str(plugin_page_), once=False)
        # end if
    # end if
    php_include_file(ABSPATH + "wp-admin/admin-footer.php", once=True)
    php_exit(0)
elif (php_isset(lambda : PHP_REQUEST["import"])):
    importer_ = PHP_REQUEST["import"]
    if (not current_user_can("import")):
        wp_die(__("Sorry, you are not allowed to import content into this site."))
    # end if
    if validate_file(importer_):
        wp_redirect(admin_url("import.php?invalid=" + importer_))
        php_exit(0)
    # end if
    if (not (php_isset(lambda : wp_importers_[importer_]))) or (not php_is_callable(wp_importers_[importer_][2])):
        wp_redirect(admin_url("import.php?invalid=" + importer_))
        php_exit(0)
    # end if
    #// 
    #// Fires before an importer screen is loaded.
    #// 
    #// The dynamic portion of the hook name, `$importer`, refers to the importer slug.
    #// 
    #// @since 3.5.0
    #//
    do_action(str("load-importer-") + str(importer_))
    #// phpcs:ignore WordPress.NamingConventions.ValidHookName.UseUnderscores
    parent_file_ = "tools.php"
    submenu_file_ = "import.php"
    title_ = __("Import")
    if (not (php_isset(lambda : PHP_REQUEST["noheader"]))):
        php_include_file(ABSPATH + "wp-admin/admin-header.php", once=True)
    # end if
    php_include_file(ABSPATH + "wp-admin/includes/upgrade.php", once=True)
    php_define("WP_IMPORTING", True)
    #// 
    #// Whether to filter imported data through kses on import.
    #// 
    #// Multisite uses this hook to filter all data through kses by default,
    #// as a super administrator may be assisting an untrusted user.
    #// 
    #// @since 3.1.0
    #// 
    #// @param bool $force Whether to force data to be filtered through kses. Default false.
    #//
    if apply_filters("force_filtered_html_on_import", False):
        kses_init_filters()
        pass
    # end if
    php_call_user_func(wp_importers_[importer_][2])
    php_include_file(ABSPATH + "wp-admin/admin-footer.php", once=True)
    #// Make sure rules are flushed.
    flush_rewrite_rules(False)
    php_exit(0)
else:
    #// 
    #// Fires before a particular screen is loaded.
    #// 
    #// The load-* hook fires in a number of contexts. This hook is for core screens.
    #// 
    #// The dynamic portion of the hook name, `$pagenow`, is a global variable
    #// referring to the filename of the current page, such as 'admin.php',
    #// 'post-new.php' etc. A complete hook for the latter would be
    #// 'load-post-new.php'.
    #// 
    #// @since 2.1.0
    #//
    do_action(str("load-") + str(pagenow_))
    #// phpcs:ignore WordPress.NamingConventions.ValidHookName.UseUnderscores
    #// 
    #// The following hooks are fired to ensure backward compatibility.
    #// In all other cases, 'load-' . $pagenow should be used instead.
    #//
    if "page" == typenow_:
        if "post-new.php" == pagenow_:
            do_action("load-page-new.php")
            pass
        elif "post.php" == pagenow_:
            do_action("load-page.php")
            pass
        # end if
    elif "edit-tags.php" == pagenow_:
        if "category" == taxnow_:
            do_action("load-categories.php")
            pass
        elif "link_category" == taxnow_:
            do_action("load-edit-link-categories.php")
            pass
        # end if
    elif "term.php" == pagenow_:
        do_action("load-edit-tags.php")
        pass
    # end if
# end if
if (not php_empty(lambda : PHP_REQUEST["action"])):
    action_ = PHP_REQUEST["action"]
    #// 
    #// Fires when an 'action' request variable is sent.
    #// 
    #// The dynamic portion of the hook name, `$action`, refers to
    #// the action derived from the `GET` or `POST` request.
    #// 
    #// @since 2.6.0
    #//
    do_action(str("admin_action_") + str(action_))
# end if
