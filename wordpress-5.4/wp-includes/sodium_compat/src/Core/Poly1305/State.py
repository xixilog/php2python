#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import os
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
if php_class_exists("ParagonIE_Sodium_Core_Poly1305_State", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core_Poly1305_State
#//
class ParagonIE_Sodium_Core_Poly1305_State(ParagonIE_Sodium_Core_Util):
    #// 
    #// @var array<int, int>
    #//
    buffer = Array()
    #// 
    #// @var bool
    #//
    final = False
    #// 
    #// @var array<int, int>
    #//
    h = Array()
    #// 
    #// @var int
    #//
    leftover = 0
    #// 
    #// @var int[]
    #//
    r = Array()
    #// 
    #// @var int[]
    #//
    pad = Array()
    #// 
    #// ParagonIE_Sodium_Core_Poly1305_State constructor.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $key
    #// @throws InvalidArgumentException
    #// @throws TypeError
    #//
    def __init__(self, key_=""):
        
        
        if self.strlen(key_) < 32:
            raise php_new_class("InvalidArgumentException", lambda : InvalidArgumentException("Poly1305 requires a 32-byte key"))
        # end if
        #// r &= 0xffffffc0ffffffc0ffffffc0fffffff
        self.r = Array(php_int(self.load_4(self.substr(key_, 0, 4)) & 67108863), php_int(self.load_4(self.substr(key_, 3, 4)) >> 2 & 67108611), php_int(self.load_4(self.substr(key_, 6, 4)) >> 4 & 67092735), php_int(self.load_4(self.substr(key_, 9, 4)) >> 6 & 66076671), php_int(self.load_4(self.substr(key_, 12, 4)) >> 8 & 1048575))
        #// h = 0
        self.h = Array(0, 0, 0, 0, 0)
        #// save pad for later
        self.pad = Array(self.load_4(self.substr(key_, 16, 4)), self.load_4(self.substr(key_, 20, 4)), self.load_4(self.substr(key_, 24, 4)), self.load_4(self.substr(key_, 28, 4)))
        self.leftover = 0
        self.final = False
    # end def __init__
    #// 
    #// Zero internal buffer upon destruction
    #//
    def __del__(self):
        
        
        self.r[0] ^= self.r[0]
        self.r[1] ^= self.r[1]
        self.r[2] ^= self.r[2]
        self.r[3] ^= self.r[3]
        self.r[4] ^= self.r[4]
        self.h[0] ^= self.h[0]
        self.h[1] ^= self.h[1]
        self.h[2] ^= self.h[2]
        self.h[3] ^= self.h[3]
        self.h[4] ^= self.h[4]
        self.pad[0] ^= self.pad[0]
        self.pad[1] ^= self.pad[1]
        self.pad[2] ^= self.pad[2]
        self.pad[3] ^= self.pad[3]
        self.leftover = 0
        self.final = True
    # end def __del__
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $message
    #// @return self
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def update(self, message_=""):
        
        
        bytes_ = self.strlen(message_)
        if bytes_ < 1:
            return self
        # end if
        #// handle leftover
        if self.leftover:
            want_ = ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE - self.leftover
            if want_ > bytes_:
                want_ = bytes_
            # end if
            i_ = 0
            while i_ < want_:
                
                mi_ = self.chrtoint(message_[i_])
                self.buffer[self.leftover + i_] = mi_
                i_ += 1
            # end while
            #// We snip off the leftmost bytes.
            message_ = self.substr(message_, want_)
            bytes_ = self.strlen(message_)
            self.leftover += want_
            if self.leftover < ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE:
                #// We still don't have enough to run $this->blocks()
                return self
            # end if
            self.blocks(self.intarraytostring(self.buffer), ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE)
            self.leftover = 0
        # end if
        #// process full blocks
        if bytes_ >= ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE:
            #// @var int $want
            want_ = bytes_ & (1 << (ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE - 1).bit_length()) - 1 - ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE - 1
            if want_ >= ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE:
                block_ = self.substr(message_, 0, want_)
                if self.strlen(block_) >= ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE:
                    self.blocks(block_, want_)
                    message_ = self.substr(message_, want_)
                    bytes_ = self.strlen(message_)
                # end if
            # end if
        # end if
        #// store leftover
        if bytes_:
            i_ = 0
            while i_ < bytes_:
                
                mi_ = self.chrtoint(message_[i_])
                self.buffer[self.leftover + i_] = mi_
                i_ += 1
            # end while
            self.leftover = php_int(self.leftover) + bytes_
        # end if
        return self
    # end def update
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $message
    #// @param int $bytes
    #// @return self
    #// @throws TypeError
    #//
    def blocks(self, message_=None, bytes_=None):
        
        
        if self.strlen(message_) < 16:
            message_ = php_str_pad(message_, 16, " ", STR_PAD_RIGHT)
        # end if
        #// @var int $hibit
        hibit_ = 0 if self.final else 1 << 24
        #// 1 << 128
        r0_ = php_int(self.r[0])
        r1_ = php_int(self.r[1])
        r2_ = php_int(self.r[2])
        r3_ = php_int(self.r[3])
        r4_ = php_int(self.r[4])
        s1_ = self.mul(r1_, 5, 3)
        s2_ = self.mul(r2_, 5, 3)
        s3_ = self.mul(r3_, 5, 3)
        s4_ = self.mul(r4_, 5, 3)
        h0_ = self.h[0]
        h1_ = self.h[1]
        h2_ = self.h[2]
        h3_ = self.h[3]
        h4_ = self.h[4]
        while True:
            
            if not (bytes_ >= ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE):
                break
            # end if
            #// h += m[i]
            h0_ += self.load_4(self.substr(message_, 0, 4)) & 67108863
            h1_ += self.load_4(self.substr(message_, 3, 4)) >> 2 & 67108863
            h2_ += self.load_4(self.substr(message_, 6, 4)) >> 4 & 67108863
            h3_ += self.load_4(self.substr(message_, 9, 4)) >> 6 & 67108863
            h4_ += self.load_4(self.substr(message_, 12, 4)) >> 8 | hibit_
            #// h *= r
            d0_ = self.mul(h0_, r0_, 25) + self.mul(s4_, h1_, 26) + self.mul(s3_, h2_, 26) + self.mul(s2_, h3_, 26) + self.mul(s1_, h4_, 26)
            d1_ = self.mul(h0_, r1_, 25) + self.mul(h1_, r0_, 25) + self.mul(s4_, h2_, 26) + self.mul(s3_, h3_, 26) + self.mul(s2_, h4_, 26)
            d2_ = self.mul(h0_, r2_, 25) + self.mul(h1_, r1_, 25) + self.mul(h2_, r0_, 25) + self.mul(s4_, h3_, 26) + self.mul(s3_, h4_, 26)
            d3_ = self.mul(h0_, r3_, 25) + self.mul(h1_, r2_, 25) + self.mul(h2_, r1_, 25) + self.mul(h3_, r0_, 25) + self.mul(s4_, h4_, 26)
            d4_ = self.mul(h0_, r4_, 25) + self.mul(h1_, r3_, 25) + self.mul(h2_, r2_, 25) + self.mul(h3_, r1_, 25) + self.mul(h4_, r0_, 25)
            #// (partial) h %= p
            #// @var int $c
            c_ = d0_ >> 26
            #// @var int $h0
            h0_ = d0_ & 67108863
            d1_ += c_
            #// @var int $c
            c_ = d1_ >> 26
            #// @var int $h1
            h1_ = d1_ & 67108863
            d2_ += c_
            #// @var int $c
            c_ = d2_ >> 26
            #// @var int $h2
            h2_ = d2_ & 67108863
            d3_ += c_
            #// @var int $c
            c_ = d3_ >> 26
            #// @var int $h3
            h3_ = d3_ & 67108863
            d4_ += c_
            #// @var int $c
            c_ = d4_ >> 26
            #// @var int $h4
            h4_ = d4_ & 67108863
            h0_ += php_int(self.mul(c_, 5, 3))
            #// @var int $c
            c_ = h0_ >> 26
            #// @var int $h0
            h0_ &= 67108863
            h1_ += c_
            #// Chop off the left 32 bytes.
            message_ = self.substr(message_, ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE)
            bytes_ -= ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE
        # end while
        self.h = Array(php_int(h0_ & 4294967295), php_int(h1_ & 4294967295), php_int(h2_ & 4294967295), php_int(h3_ & 4294967295), php_int(h4_ & 4294967295))
        return self
    # end def blocks
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @return string
    #// @throws TypeError
    #//
    def finish(self):
        
        
        #// process the remaining block
        if self.leftover:
            i_ = self.leftover
            self.buffer[i_] = 1
            i_ += 1
            while i_ < ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE:
                
                self.buffer[i_] = 0
                i_ += 1
            # end while
            self.final = True
            self.blocks(self.substr(self.intarraytostring(self.buffer), 0, ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE), ParagonIE_Sodium_Core_Poly1305.BLOCK_SIZE)
        # end if
        h0_ = php_int(self.h[0])
        h1_ = php_int(self.h[1])
        h2_ = php_int(self.h[2])
        h3_ = php_int(self.h[3])
        h4_ = php_int(self.h[4])
        #// @var int $c
        c_ = h1_ >> 26
        #// @var int $h1
        h1_ &= 67108863
        #// @var int $h2
        h2_ += c_
        #// @var int $c
        c_ = h2_ >> 26
        #// @var int $h2
        h2_ &= 67108863
        h3_ += c_
        #// @var int $c
        c_ = h3_ >> 26
        h3_ &= 67108863
        h4_ += c_
        #// @var int $c
        c_ = h4_ >> 26
        h4_ &= 67108863
        #// @var int $h0
        h0_ += self.mul(c_, 5, 3)
        #// @var int $c
        c_ = h0_ >> 26
        #// @var int $h0
        h0_ &= 67108863
        #// @var int $h1
        h1_ += c_
        #// compute h + -p
        #// @var int $g0
        g0_ = h0_ + 5
        #// @var int $c
        c_ = g0_ >> 26
        #// @var int $g0
        g0_ &= 67108863
        #// @var int $g1
        g1_ = h1_ + c_
        #// @var int $c
        c_ = g1_ >> 26
        g1_ &= 67108863
        #// @var int $g2
        g2_ = h2_ + c_
        #// @var int $c
        c_ = g2_ >> 26
        #// @var int $g2
        g2_ &= 67108863
        #// @var int $g3
        g3_ = h3_ + c_
        #// @var int $c
        c_ = g3_ >> 26
        #// @var int $g3
        g3_ &= 67108863
        #// @var int $g4
        g4_ = h4_ + c_ - 1 << 26 & 4294967295
        #// select h if h < p, or h + -p if h >= p
        #// @var int $mask
        mask_ = g4_ >> 31 - 1
        g0_ &= mask_
        g1_ &= mask_
        g2_ &= mask_
        g3_ &= mask_
        g4_ &= mask_
        #// @var int $mask
        mask_ = (1 << (mask_).bit_length()) - 1 - mask_ & 4294967295
        #// @var int $h0
        h0_ = h0_ & mask_ | g0_
        #// @var int $h1
        h1_ = h1_ & mask_ | g1_
        #// @var int $h2
        h2_ = h2_ & mask_ | g2_
        #// @var int $h3
        h3_ = h3_ & mask_ | g3_
        #// @var int $h4
        h4_ = h4_ & mask_ | g4_
        #// h = h % (2^128)
        #// @var int $h0
        h0_ = h0_ | h1_ << 26 & 4294967295
        #// @var int $h1
        h1_ = h1_ >> 6 | h2_ << 20 & 4294967295
        #// @var int $h2
        h2_ = h2_ >> 12 | h3_ << 14 & 4294967295
        #// @var int $h3
        h3_ = h3_ >> 18 | h4_ << 8 & 4294967295
        #// mac = (h + pad) % (2^128)
        f_ = php_int(h0_ + self.pad[0])
        h0_ = php_int(f_)
        f_ = php_int(h1_ + self.pad[1] + f_ >> 32)
        h1_ = php_int(f_)
        f_ = php_int(h2_ + self.pad[2] + f_ >> 32)
        h2_ = php_int(f_)
        f_ = php_int(h3_ + self.pad[3] + f_ >> 32)
        h3_ = php_int(f_)
        return self.store32_le(h0_ & 4294967295) + self.store32_le(h1_ & 4294967295) + self.store32_le(h2_ & 4294967295) + self.store32_le(h3_ & 4294967295)
    # end def finish
    i_ += 1
# end class ParagonIE_Sodium_Core_Poly1305_State
