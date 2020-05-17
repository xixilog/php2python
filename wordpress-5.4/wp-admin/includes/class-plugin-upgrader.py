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
#// Upgrade API: Plugin_Upgrader class
#// 
#// @package WordPress
#// @subpackage Upgrader
#// @since 4.6.0
#// 
#// 
#// Core class used for upgrading/installing plugins.
#// 
#// It is designed to upgrade/install plugins from a local zip, remote zip URL,
#// or uploaded zip file.
#// 
#// @since 2.8.0
#// @since 4.6.0 Moved to its own file from wp-admin/includes/class-wp-upgrader.php.
#// 
#// @see WP_Upgrader
#//
class Plugin_Upgrader(WP_Upgrader):
    #// 
    #// Plugin upgrade result.
    #// 
    #// @since 2.8.0
    #// @var array|WP_Error $result
    #// 
    #// @see WP_Upgrader::$result
    #//
    result = Array()
    #// 
    #// Whether a bulk upgrade/installation is being performed.
    #// 
    #// @since 2.9.0
    #// @var bool $bulk
    #//
    bulk = False
    #// 
    #// Initialize the upgrade strings.
    #// 
    #// @since 2.8.0
    #//
    def upgrade_strings(self):
        
        
        self.strings["up_to_date"] = __("The plugin is at the latest version.")
        self.strings["no_package"] = __("Update package not available.")
        #// translators: %s: Package URL.
        self.strings["downloading_package"] = php_sprintf(__("Downloading update from %s&#8230;"), "<span class=\"code\">%s</span>")
        self.strings["unpack_package"] = __("Unpacking the update&#8230;")
        self.strings["remove_old"] = __("Removing the old version of the plugin&#8230;")
        self.strings["remove_old_failed"] = __("Could not remove the old plugin.")
        self.strings["process_failed"] = __("Plugin update failed.")
        self.strings["process_success"] = __("Plugin updated successfully.")
        self.strings["process_bulk_success"] = __("Plugins updated successfully.")
    # end def upgrade_strings
    #// 
    #// Initialize the installation strings.
    #// 
    #// @since 2.8.0
    #//
    def install_strings(self):
        
        
        self.strings["no_package"] = __("Installation package not available.")
        #// translators: %s: Package URL.
        self.strings["downloading_package"] = php_sprintf(__("Downloading installation package from %s&#8230;"), "<span class=\"code\">%s</span>")
        self.strings["unpack_package"] = __("Unpacking the package&#8230;")
        self.strings["installing_package"] = __("Installing the plugin&#8230;")
        self.strings["no_files"] = __("The plugin contains no files.")
        self.strings["process_failed"] = __("Plugin installation failed.")
        self.strings["process_success"] = __("Plugin installed successfully.")
    # end def install_strings
    #// 
    #// Install a plugin package.
    #// 
    #// @since 2.8.0
    #// @since 3.7.0 The `$args` parameter was added, making clearing the plugin update cache optional.
    #// 
    #// @param string $package The full local path or URI of the package.
    #// @param array  $args {
    #// Optional. Other arguments for installing a plugin package. Default empty array.
    #// 
    #// @type bool $clear_update_cache Whether to clear the plugin updates cache if successful.
    #// Default true.
    #// }
    #// @return bool|WP_Error True if the installation was successful, false or a WP_Error otherwise.
    #//
    def install(self, package_=None, args_=None):
        if args_ is None:
            args_ = Array()
        # end if
        
        defaults_ = Array({"clear_update_cache": True})
        parsed_args_ = wp_parse_args(args_, defaults_)
        self.init()
        self.install_strings()
        add_filter("upgrader_source_selection", Array(self, "check_package"))
        if parsed_args_["clear_update_cache"]:
            #// Clear cache so wp_update_plugins() knows about the new plugin.
            add_action("upgrader_process_complete", "wp_clean_plugins_cache", 9, 0)
        # end if
        self.run(Array({"package": package_, "destination": WP_PLUGIN_DIR, "clear_destination": False, "clear_working": True, "hook_extra": Array({"type": "plugin", "action": "install"})}))
        remove_action("upgrader_process_complete", "wp_clean_plugins_cache", 9)
        remove_filter("upgrader_source_selection", Array(self, "check_package"))
        if (not self.result) or is_wp_error(self.result):
            return self.result
        # end if
        #// Force refresh of plugin update information.
        wp_clean_plugins_cache(parsed_args_["clear_update_cache"])
        return True
    # end def install
    #// 
    #// Upgrade a plugin.
    #// 
    #// @since 2.8.0
    #// @since 3.7.0 The `$args` parameter was added, making clearing the plugin update cache optional.
    #// 
    #// @param string $plugin Path to the plugin file relative to the plugins directory.
    #// @param array  $args {
    #// Optional. Other arguments for upgrading a plugin package. Default empty array.
    #// 
    #// @type bool $clear_update_cache Whether to clear the plugin updates cache if successful.
    #// Default true.
    #// }
    #// @return bool|WP_Error True if the upgrade was successful, false or a WP_Error object otherwise.
    #//
    def upgrade(self, plugin_=None, args_=None):
        if args_ is None:
            args_ = Array()
        # end if
        
        defaults_ = Array({"clear_update_cache": True})
        parsed_args_ = wp_parse_args(args_, defaults_)
        self.init()
        self.upgrade_strings()
        current_ = get_site_transient("update_plugins")
        if (not (php_isset(lambda : current_.response[plugin_]))):
            self.skin.before()
            self.skin.set_result(False)
            self.skin.error("up_to_date")
            self.skin.after()
            return False
        # end if
        #// Get the URL to the zip file.
        r_ = current_.response[plugin_]
        add_filter("upgrader_pre_install", Array(self, "deactivate_plugin_before_upgrade"), 10, 2)
        add_filter("upgrader_pre_install", Array(self, "active_before"), 10, 2)
        add_filter("upgrader_clear_destination", Array(self, "delete_old_plugin"), 10, 4)
        add_filter("upgrader_post_install", Array(self, "active_after"), 10, 2)
        #// There's a Trac ticket to move up the directory for zips which are made a bit differently, useful for non-.org plugins.
        #// 'source_selection' => array( $this, 'source_selection' ),
        if parsed_args_["clear_update_cache"]:
            #// Clear cache so wp_update_plugins() knows about the new plugin.
            add_action("upgrader_process_complete", "wp_clean_plugins_cache", 9, 0)
        # end if
        self.run(Array({"package": r_.package, "destination": WP_PLUGIN_DIR, "clear_destination": True, "clear_working": True, "hook_extra": Array({"plugin": plugin_, "type": "plugin", "action": "update"})}))
        #// Cleanup our hooks, in case something else does a upgrade on this connection.
        remove_action("upgrader_process_complete", "wp_clean_plugins_cache", 9)
        remove_filter("upgrader_pre_install", Array(self, "deactivate_plugin_before_upgrade"))
        remove_filter("upgrader_pre_install", Array(self, "active_before"))
        remove_filter("upgrader_clear_destination", Array(self, "delete_old_plugin"))
        remove_filter("upgrader_post_install", Array(self, "active_after"))
        if (not self.result) or is_wp_error(self.result):
            return self.result
        # end if
        #// Force refresh of plugin update information.
        wp_clean_plugins_cache(parsed_args_["clear_update_cache"])
        return True
    # end def upgrade
    #// 
    #// Bulk upgrade several plugins at once.
    #// 
    #// @since 2.8.0
    #// @since 3.7.0 The `$args` parameter was added, making clearing the plugin update cache optional.
    #// 
    #// @param string[] $plugins Array of paths to plugin files relative to the plugins directory.
    #// @param array    $args {
    #// Optional. Other arguments for upgrading several plugins at once.
    #// 
    #// @type bool $clear_update_cache Whether to clear the plugin updates cache if successful. Default true.
    #// }
    #// @return array|false An array of results indexed by plugin file, or false if unable to connect to the filesystem.
    #//
    def bulk_upgrade(self, plugins_=None, args_=None):
        if args_ is None:
            args_ = Array()
        # end if
        
        defaults_ = Array({"clear_update_cache": True})
        parsed_args_ = wp_parse_args(args_, defaults_)
        self.init()
        self.bulk = True
        self.upgrade_strings()
        current_ = get_site_transient("update_plugins")
        add_filter("upgrader_clear_destination", Array(self, "delete_old_plugin"), 10, 4)
        self.skin.header()
        #// Connect to the filesystem first.
        res_ = self.fs_connect(Array(WP_CONTENT_DIR, WP_PLUGIN_DIR))
        if (not res_):
            self.skin.footer()
            return False
        # end if
        self.skin.bulk_header()
        #// 
        #// Only start maintenance mode if:
        #// - running Multisite and there are one or more plugins specified, OR
        #// - a plugin with an update available is currently active.
        #// @todo For multisite, maintenance mode should only kick in for individual sites if at all possible.
        #//
        maintenance_ = is_multisite() and (not php_empty(lambda : plugins_))
        for plugin_ in plugins_:
            maintenance_ = maintenance_ or is_plugin_active(plugin_) and (php_isset(lambda : current_.response[plugin_]))
        # end for
        if maintenance_:
            self.maintenance_mode(True)
        # end if
        results_ = Array()
        self.update_count = php_count(plugins_)
        self.update_current = 0
        for plugin_ in plugins_:
            self.update_current += 1
            self.skin.plugin_info = get_plugin_data(WP_PLUGIN_DIR + "/" + plugin_, False, True)
            if (not (php_isset(lambda : current_.response[plugin_]))):
                self.skin.set_result("up_to_date")
                self.skin.before()
                self.skin.feedback("up_to_date")
                self.skin.after()
                results_[plugin_] = True
                continue
            # end if
            #// Get the URL to the zip file.
            r_ = current_.response[plugin_]
            self.skin.plugin_active = is_plugin_active(plugin_)
            result_ = self.run(Array({"package": r_.package, "destination": WP_PLUGIN_DIR, "clear_destination": True, "clear_working": True, "is_multi": True, "hook_extra": Array({"plugin": plugin_})}))
            results_[plugin_] = self.result
            #// Prevent credentials auth screen from displaying multiple times.
            if False == result_:
                break
            # end if
        # end for
        #// End foreach $plugins.
        self.maintenance_mode(False)
        #// Force refresh of plugin update information.
        wp_clean_plugins_cache(parsed_args_["clear_update_cache"])
        #// This action is documented in wp-admin/includes/class-wp-upgrader.php
        do_action("upgrader_process_complete", self, Array({"action": "update", "type": "plugin", "bulk": True, "plugins": plugins_}))
        self.skin.bulk_footer()
        self.skin.footer()
        #// Cleanup our hooks, in case something else does a upgrade on this connection.
        remove_filter("upgrader_clear_destination", Array(self, "delete_old_plugin"))
        return results_
    # end def bulk_upgrade
    #// 
    #// Check a source package to be sure it contains a plugin.
    #// 
    #// This function is added to the {@see 'upgrader_source_selection'} filter by
    #// Plugin_Upgrader::install().
    #// 
    #// @since 3.3.0
    #// 
    #// @global WP_Filesystem_Base $wp_filesystem WordPress filesystem subclass.
    #// 
    #// @param string $source The path to the downloaded package source.
    #// @return string|WP_Error The source as passed, or a WP_Error object
    #// if no plugins were found.
    #//
    def check_package(self, source_=None):
        
        
        global wp_filesystem_
        php_check_if_defined("wp_filesystem_")
        if is_wp_error(source_):
            return source_
        # end if
        working_directory_ = php_str_replace(wp_filesystem_.wp_content_dir(), trailingslashit(WP_CONTENT_DIR), source_)
        if (not php_is_dir(working_directory_)):
            #// Sanity check, if the above fails, let's not prevent installation.
            return source_
        # end if
        #// Check that the folder contains at least 1 valid plugin.
        plugins_found_ = False
        files_ = glob(working_directory_ + "*.php")
        if files_:
            for file_ in files_:
                info_ = get_plugin_data(file_, False, False)
                if (not php_empty(lambda : info_["Name"])):
                    plugins_found_ = True
                    break
                # end if
            # end for
        # end if
        if (not plugins_found_):
            return php_new_class("WP_Error", lambda : WP_Error("incompatible_archive_no_plugins", self.strings["incompatible_archive"], __("No valid plugins were found.")))
        # end if
        return source_
    # end def check_package
    #// 
    #// Retrieve the path to the file that contains the plugin info.
    #// 
    #// This isn't used internally in the class, but is called by the skins.
    #// 
    #// @since 2.8.0
    #// 
    #// @return string|false The full path to the main plugin file, or false.
    #//
    def plugin_info(self):
        
        
        if (not php_is_array(self.result)):
            return False
        # end if
        if php_empty(lambda : self.result["destination_name"]):
            return False
        # end if
        #// Ensure to pass with leading slash.
        plugin_ = get_plugins("/" + self.result["destination_name"])
        if php_empty(lambda : plugin_):
            return False
        # end if
        #// Assume the requested plugin is the first in the list.
        pluginfiles_ = php_array_keys(plugin_)
        return self.result["destination_name"] + "/" + pluginfiles_[0]
    # end def plugin_info
    #// 
    #// Deactivates a plugin before it is upgraded.
    #// 
    #// Hooked to the {@see 'upgrader_pre_install'} filter by Plugin_Upgrader::upgrade().
    #// 
    #// @since 2.8.0
    #// @since 4.1.0 Added a return value.
    #// 
    #// @param bool|WP_Error $return Upgrade offer return.
    #// @param array         $plugin Plugin package arguments.
    #// @return bool|WP_Error The passed in $return param or WP_Error.
    #//
    def deactivate_plugin_before_upgrade(self, return_=None, plugin_=None):
        
        
        if is_wp_error(return_):
            #// Bypass.
            return return_
        # end if
        #// When in cron (background updates) don't deactivate the plugin, as we require a browser to reactivate it.
        if wp_doing_cron():
            return return_
        # end if
        plugin_ = plugin_["plugin"] if (php_isset(lambda : plugin_["plugin"])) else ""
        if php_empty(lambda : plugin_):
            return php_new_class("WP_Error", lambda : WP_Error("bad_request", self.strings["bad_request"]))
        # end if
        if is_plugin_active(plugin_):
            #// Deactivate the plugin silently, Prevent deactivation hooks from running.
            deactivate_plugins(plugin_, True)
        # end if
        return return_
    # end def deactivate_plugin_before_upgrade
    #// 
    #// Turns on maintenance mode before attempting to background update an active plugin.
    #// 
    #// Hooked to the {@see 'upgrader_pre_install'} filter by Plugin_Upgrader::upgrade().
    #// 
    #// @since 5.4.0
    #// 
    #// @param bool|WP_Error $return Upgrade offer return.
    #// @param array         $plugin Plugin package arguments.
    #// @return bool|WP_Error The passed in $return param or WP_Error.
    #//
    def active_before(self, return_=None, plugin_=None):
        
        
        if is_wp_error(return_):
            return return_
        # end if
        #// Only enable maintenance mode when in cron (background update).
        if (not wp_doing_cron()):
            return return_
        # end if
        plugin_ = plugin_["plugin"] if (php_isset(lambda : plugin_["plugin"])) else ""
        #// Only run if plugin is active.
        if (not is_plugin_active(plugin_)):
            return return_
        # end if
        #// Change to maintenance mode. Bulk edit handles this separately.
        if (not self.bulk):
            self.maintenance_mode(True)
        # end if
        return return_
    # end def active_before
    #// 
    #// Turns off maintenance mode after upgrading an active plugin.
    #// 
    #// Hooked to the {@see 'upgrader_post_install'} filter by Plugin_Upgrader::upgrade().
    #// 
    #// @since 5.4.0
    #// 
    #// @param bool|WP_Error $return Upgrade offer return.
    #// @param array         $plugin Plugin package arguments.
    #// @return bool|WP_Error The passed in $return param or WP_Error.
    #//
    def active_after(self, return_=None, plugin_=None):
        
        
        if is_wp_error(return_):
            return return_
        # end if
        #// Only disable maintenance mode when in cron (background update).
        if (not wp_doing_cron()):
            return return_
        # end if
        plugin_ = plugin_["plugin"] if (php_isset(lambda : plugin_["plugin"])) else ""
        #// Only run if plugin is active
        if (not is_plugin_active(plugin_)):
            return return_
        # end if
        #// Time to remove maintenance mode. Bulk edit handles this separately.
        if (not self.bulk):
            self.maintenance_mode(False)
        # end if
        return return_
    # end def active_after
    #// 
    #// Deletes the old plugin during an upgrade.
    #// 
    #// Hooked to the {@see 'upgrader_clear_destination'} filter by
    #// Plugin_Upgrader::upgrade() and Plugin_Upgrader::bulk_upgrade().
    #// 
    #// @since 2.8.0
    #// 
    #// @global WP_Filesystem_Base $wp_filesystem WordPress filesystem subclass.
    #// 
    #// @param bool|WP_Error $removed            Whether the destination was cleared.
    #// True on success, WP_Error on failure.
    #// @param string        $local_destination  The local package destination.
    #// @param string        $remote_destination The remote package destination.
    #// @param array         $plugin             Extra arguments passed to hooked filters.
    #// @return bool|WP_Error
    #//
    def delete_old_plugin(self, removed_=None, local_destination_=None, remote_destination_=None, plugin_=None):
        
        
        global wp_filesystem_
        php_check_if_defined("wp_filesystem_")
        if is_wp_error(removed_):
            return removed_
            pass
        # end if
        plugin_ = plugin_["plugin"] if (php_isset(lambda : plugin_["plugin"])) else ""
        if php_empty(lambda : plugin_):
            return php_new_class("WP_Error", lambda : WP_Error("bad_request", self.strings["bad_request"]))
        # end if
        plugins_dir_ = wp_filesystem_.wp_plugins_dir()
        this_plugin_dir_ = trailingslashit(php_dirname(plugins_dir_ + plugin_))
        if (not wp_filesystem_.exists(this_plugin_dir_)):
            #// If it's already vanished.
            return removed_
        # end if
        #// If plugin is in its own directory, recursively delete the directory.
        #// Base check on if plugin includes directory separator AND that it's not the root plugin folder.
        if php_strpos(plugin_, "/") and this_plugin_dir_ != plugins_dir_:
            deleted_ = wp_filesystem_.delete(this_plugin_dir_, True)
        else:
            deleted_ = wp_filesystem_.delete(plugins_dir_ + plugin_)
        # end if
        if (not deleted_):
            return php_new_class("WP_Error", lambda : WP_Error("remove_old_failed", self.strings["remove_old_failed"]))
        # end if
        return True
    # end def delete_old_plugin
# end class Plugin_Upgrader
