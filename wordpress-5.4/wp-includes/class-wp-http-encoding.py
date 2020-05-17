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
#// HTTP API: WP_Http_Encoding class
#// 
#// @package WordPress
#// @subpackage HTTP
#// @since 4.4.0
#// 
#// 
#// Core class used to implement deflate and gzip transfer encoding support for HTTP requests.
#// 
#// Includes RFC 1950, RFC 1951, and RFC 1952.
#// 
#// @since 2.8.0
#//
class WP_Http_Encoding():
    #// 
    #// Compress raw string using the deflate format.
    #// 
    #// Supports the RFC 1951 standard.
    #// 
    #// @since 2.8.0
    #// 
    #// @param string $raw String to compress.
    #// @param int $level Optional, default is 9. Compression level, 9 is highest.
    #// @param string $supports Optional, not used. When implemented it will choose the right compression based on what the server supports.
    #// @return string|false False on failure.
    #//
    @classmethod
    def compress(self, raw_=None, level_=9, supports_=None):
        
        
        return gzdeflate(raw_, level_)
    # end def compress
    #// 
    #// Decompression of deflated string.
    #// 
    #// Will attempt to decompress using the RFC 1950 standard, and if that fails
    #// then the RFC 1951 standard deflate will be attempted. Finally, the RFC
    #// 1952 standard gzip decode will be attempted. If all fail, then the
    #// original compressed string will be returned.
    #// 
    #// @since 2.8.0
    #// 
    #// @param string $compressed String to decompress.
    #// @param int $length The optional length of the compressed data.
    #// @return string|bool False on failure.
    #//
    @classmethod
    def decompress(self, compressed_=None, length_=None):
        
        
        if php_empty(lambda : compressed_):
            return compressed_
        # end if
        decompressed_ = php_no_error(lambda: gzinflate(compressed_))
        if False != decompressed_:
            return decompressed_
        # end if
        decompressed_ = self.compatible_gzinflate(compressed_)
        if False != decompressed_:
            return decompressed_
        # end if
        decompressed_ = php_no_error(lambda: gzuncompress(compressed_))
        if False != decompressed_:
            return decompressed_
        # end if
        if php_function_exists("gzdecode"):
            decompressed_ = php_no_error(lambda: gzdecode(compressed_))
            if False != decompressed_:
                return decompressed_
            # end if
        # end if
        return compressed_
    # end def decompress
    #// 
    #// Decompression of deflated string while staying compatible with the majority of servers.
    #// 
    #// Certain Servers will return deflated data with headers which PHP's gzinflate()
    #// function cannot handle out of the box. The following function has been created from
    #// various snippets on the gzinflate() PHP documentation.
    #// 
    #// Warning: Magic numbers within. Due to the potential different formats that the compressed
    #// data may be returned in, some "magic offsets" are needed to ensure proper decompression
    #// takes place. For a simple progmatic way to determine the magic offset in use, see:
    #// https://core.trac.wordpress.org/ticket/18273
    #// 
    #// @since 2.8.1
    #// @link https://core.trac.wordpress.org/ticket/18273
    #// @link https://www.php.net/manual/en/function.gzinflate.php#70875
    #// @link https://www.php.net/manual/en/function.gzinflate.php#77336
    #// 
    #// @param string $gzData String to decompress.
    #// @return string|bool False on failure.
    #//
    @classmethod
    def compatible_gzinflate(self, gzData_=None):
        
        
        #// Compressed data might contain a full header, if so strip it for gzinflate().
        if php_substr(gzData_, 0, 3) == "":
            i_ = 10
            flg_ = php_ord(php_substr(gzData_, 3, 1))
            if flg_ > 0:
                if flg_ & 4:
                    xlen_ = unpack("v", php_substr(gzData_, i_, 2))
                    i_ = i_ + 2 + xlen_
                # end if
                if flg_ & 8:
                    i_ = php_strpos(gzData_, " ", i_) + 1
                # end if
                if flg_ & 16:
                    i_ = php_strpos(gzData_, " ", i_) + 1
                # end if
                if flg_ & 2:
                    i_ = i_ + 2
                # end if
            # end if
            decompressed_ = php_no_error(lambda: gzinflate(php_substr(gzData_, i_, -8)))
            if False != decompressed_:
                return decompressed_
            # end if
        # end if
        #// Compressed data from java.util.zip.Deflater amongst others.
        decompressed_ = php_no_error(lambda: gzinflate(php_substr(gzData_, 2)))
        if False != decompressed_:
            return decompressed_
        # end if
        return False
    # end def compatible_gzinflate
    #// 
    #// What encoding types to accept and their priority values.
    #// 
    #// @since 2.8.0
    #// 
    #// @param string $url
    #// @param array  $args
    #// @return string Types of encoding to accept.
    #//
    @classmethod
    def accept_encoding(self, url_=None, args_=None):
        
        
        type_ = Array()
        compression_enabled_ = self.is_available()
        if (not args_["decompress"]):
            #// Decompression specifically disabled.
            compression_enabled_ = False
        elif args_["stream"]:
            #// Disable when streaming to file.
            compression_enabled_ = False
        elif (php_isset(lambda : args_["limit_response_size"])):
            #// If only partial content is being requested, we won't be able to decompress it.
            compression_enabled_ = False
        # end if
        if compression_enabled_:
            if php_function_exists("gzinflate"):
                type_[-1] = "deflate;q=1.0"
            # end if
            if php_function_exists("gzuncompress"):
                type_[-1] = "compress;q=0.5"
            # end if
            if php_function_exists("gzdecode"):
                type_[-1] = "gzip;q=0.5"
            # end if
        # end if
        #// 
        #// Filters the allowed encoding types.
        #// 
        #// @since 3.6.0
        #// 
        #// @param string[] $type Array of what encoding types to accept and their priority values.
        #// @param string   $url  URL of the HTTP request.
        #// @param array    $args HTTP request arguments.
        #//
        type_ = apply_filters("wp_http_accept_encoding", type_, url_, args_)
        return php_implode(", ", type_)
    # end def accept_encoding
    #// 
    #// What encoding the content used when it was compressed to send in the headers.
    #// 
    #// @since 2.8.0
    #// 
    #// @return string Content-Encoding string to send in the header.
    #//
    @classmethod
    def content_encoding(self):
        
        
        return "deflate"
    # end def content_encoding
    #// 
    #// Whether the content be decoded based on the headers.
    #// 
    #// @since 2.8.0
    #// 
    #// @param array|string $headers All of the available headers.
    #// @return bool
    #//
    @classmethod
    def should_decode(self, headers_=None):
        
        
        if php_is_array(headers_):
            if php_array_key_exists("content-encoding", headers_) and (not php_empty(lambda : headers_["content-encoding"])):
                return True
            # end if
        elif php_is_string(headers_):
            return php_stripos(headers_, "content-encoding:") != False
        # end if
        return False
    # end def should_decode
    #// 
    #// Whether decompression and compression are supported by the PHP version.
    #// 
    #// Each function is tested instead of checking for the zlib extension, to
    #// ensure that the functions all exist in the PHP version and aren't
    #// disabled.
    #// 
    #// @since 2.8.0
    #// 
    #// @return bool
    #//
    @classmethod
    def is_available(self):
        
        
        return php_function_exists("gzuncompress") or php_function_exists("gzdeflate") or php_function_exists("gzinflate")
    # end def is_available
# end class WP_Http_Encoding
