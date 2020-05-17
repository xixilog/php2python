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
#// Case-insensitive dictionary, suitable for HTTP headers
#// 
#// @package Requests
#// 
#// 
#// Case-insensitive dictionary, suitable for HTTP headers
#// 
#// @package Requests
#//
class Requests_Response_Headers(Requests_Utility_CaseInsensitiveDictionary):
    #// 
    #// Get the given header
    #// 
    #// Unlike {@see self::getValues()}, this returns a string. If there are
    #// multiple values, it concatenates them with a comma as per RFC2616.
    #// 
    #// Avoid using this where commas may be used unquoted in values, such as
    #// Set-Cookie headers.
    #// 
    #// @param string $key
    #// @return string Header value
    #//
    def offsetget(self, key_=None):
        
        
        key_ = php_strtolower(key_)
        if (not (php_isset(lambda : self.data[key_]))):
            return None
        # end if
        return self.flatten(self.data[key_])
    # end def offsetget
    #// 
    #// Set the given item
    #// 
    #// @throws Requests_Exception On attempting to use dictionary as list (`invalidset`)
    #// 
    #// @param string $key Item name
    #// @param string $value Item value
    #//
    def offsetset(self, key_=None, value_=None):
        
        
        if key_ == None:
            raise php_new_class("Requests_Exception", lambda : Requests_Exception("Object is a dictionary, not a list", "invalidset"))
        # end if
        key_ = php_strtolower(key_)
        if (not (php_isset(lambda : self.data[key_]))):
            self.data[key_] = Array()
        # end if
        self.data[key_][-1] = value_
    # end def offsetset
    #// 
    #// Get all values for a given header
    #// 
    #// @param string $key
    #// @return array Header values
    #//
    def getvalues(self, key_=None):
        
        
        key_ = php_strtolower(key_)
        if (not (php_isset(lambda : self.data[key_]))):
            return None
        # end if
        return self.data[key_]
    # end def getvalues
    #// 
    #// Flattens a value into a string
    #// 
    #// Converts an array into a string by imploding values with a comma, as per
    #// RFC2616's rules for folding headers.
    #// 
    #// @param string|array $value Value to flatten
    #// @return string Flattened value
    #//
    def flatten(self, value_=None):
        
        
        if php_is_array(value_):
            value_ = php_implode(",", value_)
        # end if
        return value_
    # end def flatten
    #// 
    #// Get an iterator for the data
    #// 
    #// Converts the internal
    #// @return ArrayIterator
    #//
    def getiterator(self):
        
        
        return php_new_class("Requests_Utility_FilteredIterator", lambda : Requests_Utility_FilteredIterator(self.data, Array(self, "flatten")))
    # end def getiterator
# end class Requests_Response_Headers
