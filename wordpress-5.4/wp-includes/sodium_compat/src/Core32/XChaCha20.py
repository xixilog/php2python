#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import os
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
if php_class_exists("ParagonIE_Sodium_Core32_XChaCha20", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core32_XChaCha20
#//
class ParagonIE_Sodium_Core32_XChaCha20(ParagonIE_Sodium_Core32_HChaCha20):
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $len
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def stream(self, len_=64, nonce_="", key_=""):
        
        
        if self.strlen(nonce_) != 24:
            raise php_new_class("SodiumException", lambda : SodiumException("Nonce must be 24 bytes long"))
        # end if
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core32_ChaCha20_Ctx(self.hchacha20(self.substr(nonce_, 0, 16), key_), self.substr(nonce_, 16, 8))), php_str_repeat(" ", len_))
    # end def stream
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $message
    #// @param string $nonce
    #// @param string $key
    #// @param string $ic
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def streamxoric(self, message_=None, nonce_="", key_="", ic_=""):
        
        
        if self.strlen(nonce_) != 24:
            raise php_new_class("SodiumException", lambda : SodiumException("Nonce must be 24 bytes long"))
        # end if
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core32_ChaCha20_Ctx(self.hchacha20(self.substr(nonce_, 0, 16), key_), self.substr(nonce_, 16, 8), ic_)), message_)
    # end def streamxoric
# end class ParagonIE_Sodium_Core32_XChaCha20
