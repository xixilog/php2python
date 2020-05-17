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
#// SimplePie
#// 
#// A PHP-Based RSS and Atom Feed Framework.
#// Takes the hard work out of managing a complete RSS/Atom solution.
#// 
#// Copyright (c) 2004-2012, Ryan Parman, Geoffrey Sneddon, Ryan McCue, and contributors
#// All rights reserved.
#// 
#// Redistribution and use in source and binary forms, with or without modification, are
#// permitted provided that the following conditions are met:
#// 
#// Redistributions of source code must retain the above copyright notice, this list of
#// conditions and the following disclaimer.
#// 
#// Redistributions in binary form must reproduce the above copyright notice, this list
#// of conditions and the following disclaimer in the documentation and/or other materials
#// provided with the distribution.
#// 
#// Neither the name of the SimplePie Team nor the names of its contributors may be used
#// to endorse or promote products derived from this software without specific prior
#// written permission.
#// 
#// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
#// OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
#// AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS
#// AND CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#// OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#// POSSIBILITY OF SUCH DAMAGE.
#// 
#// @package SimplePie
#// @version 1.3.1
#// @copyright 2004-2012 Ryan Parman, Geoffrey Sneddon, Ryan McCue
#// @author Ryan Parman
#// @author Geoffrey Sneddon
#// @author Ryan McCue
#// @link http://simplepie.org/ SimplePie
#// @license http://www.opensource.org/licenses/bsd-license.php BSD License
#// 
#// 
#// Decode 'gzip' encoded HTTP data
#// 
#// @package SimplePie
#// @subpackage HTTP
#// @link http://www.gzip.org/format.txt
#//
class SimplePie_gzdecode():
    #// 
    #// Compressed data
    #// 
    #// @access private
    #// @var string
    #// @see gzdecode::$data
    #//
    compressed_data = Array()
    #// 
    #// Size of compressed data
    #// 
    #// @access private
    #// @var int
    #//
    compressed_size = Array()
    #// 
    #// Minimum size of a valid gzip string
    #// 
    #// @access private
    #// @var int
    #//
    min_compressed_size = 18
    #// 
    #// Current position of pointer
    #// 
    #// @access private
    #// @var int
    #//
    position = 0
    #// 
    #// Flags (FLG)
    #// 
    #// @access private
    #// @var int
    #//
    flags = Array()
    #// 
    #// Uncompressed data
    #// 
    #// @access public
    #// @see gzdecode::$compressed_data
    #// @var string
    #//
    data = Array()
    #// 
    #// Modified time
    #// 
    #// @access public
    #// @var int
    #//
    MTIME = Array()
    #// 
    #// Extra Flags
    #// 
    #// @access public
    #// @var int
    #//
    XFL = Array()
    #// 
    #// Operating System
    #// 
    #// @access public
    #// @var int
    #//
    OS = Array()
    #// 
    #// Subfield ID 1
    #// 
    #// @access public
    #// @see gzdecode::$extra_field
    #// @see gzdecode::$SI2
    #// @var string
    #//
    SI1 = Array()
    #// 
    #// Subfield ID 2
    #// 
    #// @access public
    #// @see gzdecode::$extra_field
    #// @see gzdecode::$SI1
    #// @var string
    #//
    SI2 = Array()
    #// 
    #// Extra field content
    #// 
    #// @access public
    #// @see gzdecode::$SI1
    #// @see gzdecode::$SI2
    #// @var string
    #//
    extra_field = Array()
    #// 
    #// Original filename
    #// 
    #// @access public
    #// @var string
    #//
    filename = Array()
    #// 
    #// Human readable comment
    #// 
    #// @access public
    #// @var string
    #//
    comment = Array()
    #// 
    #// Don't allow anything to be set
    #// 
    #// @param string $name
    #// @param mixed $value
    #//
    def __set(self, name_=None, value_=None):
        
        
        trigger_error(str("Cannot write property ") + str(name_), E_USER_ERROR)
    # end def __set
    #// 
    #// Set the compressed string and related properties
    #// 
    #// @param string $data
    #//
    def __init__(self, data_=None):
        
        
        self.compressed_data = data_
        self.compressed_size = php_strlen(data_)
    # end def __init__
    #// 
    #// Decode the GZIP stream
    #// 
    #// @return bool Successfulness
    #//
    def parse(self):
        
        
        if self.compressed_size >= self.min_compressed_size:
            #// Check ID1, ID2, and CM
            if php_substr(self.compressed_data, 0, 3) != "":
                return False
            # end if
            #// Get the FLG (FLaGs)
            self.flags = php_ord(self.compressed_data[3])
            #// FLG bits above (1 << 4) are reserved
            if self.flags > 31:
                return False
            # end if
            #// Advance the pointer after the above
            self.position += 4
            #// MTIME
            mtime_ = php_substr(self.compressed_data, self.position, 4)
            #// Reverse the string if we're on a big-endian arch because l is the only signed long and is machine endianness
            if current(unpack("S", " ")) == 1:
                mtime_ = php_strrev(mtime_)
            # end if
            self.MTIME = current(unpack("l", mtime_))
            self.position += 4
            #// Get the XFL (eXtra FLags)
            self.XFL = php_ord(self.compressed_data[self.position])
            self.position += 1
            self.position += 1
            #// Get the OS (Operating System)
            self.OS = php_ord(self.compressed_data[self.position])
            self.position += 1
            self.position += 1
            #// Parse the FEXTRA
            if self.flags & 4:
                #// Read subfield IDs
                self.SI1 = self.compressed_data[self.position]
                self.position += 1
                self.position += 1
                self.SI2 = self.compressed_data[self.position]
                self.position += 1
                self.position += 1
                #// SI2 set to zero is reserved for future use
                if self.SI2 == " ":
                    return False
                # end if
                #// Get the length of the extra field
                len_ = current(unpack("v", php_substr(self.compressed_data, self.position, 2)))
                self.position += 2
                #// Check the length of the string is still valid
                self.min_compressed_size += len_ + 4
                if self.compressed_size >= self.min_compressed_size:
                    #// Set the extra field to the given data
                    self.extra_field = php_substr(self.compressed_data, self.position, len_)
                    self.position += len_
                else:
                    return False
                # end if
            # end if
            #// Parse the FNAME
            if self.flags & 8:
                #// Get the length of the filename
                len_ = strcspn(self.compressed_data, " ", self.position)
                #// Check the length of the string is still valid
                self.min_compressed_size += len_ + 1
                if self.compressed_size >= self.min_compressed_size:
                    #// Set the original filename to the given string
                    self.filename = php_substr(self.compressed_data, self.position, len_)
                    self.position += len_ + 1
                else:
                    return False
                # end if
            # end if
            #// Parse the FCOMMENT
            if self.flags & 16:
                #// Get the length of the comment
                len_ = strcspn(self.compressed_data, " ", self.position)
                #// Check the length of the string is still valid
                self.min_compressed_size += len_ + 1
                if self.compressed_size >= self.min_compressed_size:
                    #// Set the original comment to the given string
                    self.comment = php_substr(self.compressed_data, self.position, len_)
                    self.position += len_ + 1
                else:
                    return False
                # end if
            # end if
            #// Parse the FHCRC
            if self.flags & 2:
                #// Check the length of the string is still valid
                self.min_compressed_size += len_ + 2
                if self.compressed_size >= self.min_compressed_size:
                    #// Read the CRC
                    crc_ = current(unpack("v", php_substr(self.compressed_data, self.position, 2)))
                    #// Check the CRC matches
                    if crc32(php_substr(self.compressed_data, 0, self.position)) & 65535 == crc_:
                        self.position += 2
                    else:
                        return False
                    # end if
                else:
                    return False
                # end if
            # end if
            #// Decompress the actual data
            self.data = gzinflate(php_substr(self.compressed_data, self.position, -8))
            if self.data == False:
                return False
            else:
                self.position = self.compressed_size - 8
            # end if
            #// Check CRC of data
            crc_ = current(unpack("V", php_substr(self.compressed_data, self.position, 4)))
            self.position += 4
            #// if (extension_loaded('hash') && sprintf('%u', current(unpack('V', hash('crc32b', $this->data)))) !== sprintf('%u', $crc))
            #// {
            #// return false;
            #// }
            #// Check ISIZE of data
            isize_ = current(unpack("V", php_substr(self.compressed_data, self.position, 4)))
            self.position += 4
            if php_sprintf("%u", php_strlen(self.data) & 4294967295) != php_sprintf("%u", isize_):
                return False
            # end if
            #// Wow, against all odds, we've actually got a valid gzip string
            return True
        else:
            return False
        # end if
    # end def parse
# end class SimplePie_gzdecode
