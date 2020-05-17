#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import os
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
if php_class_exists("ParagonIE_Sodium_Core32_Poly1305_State", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core32_Poly1305_State
#//
class ParagonIE_Sodium_Core32_Poly1305_State(ParagonIE_Sodium_Core32_Util):
    #// 
    #// @var array<int, int>
    #//
    buffer = Array()
    #// 
    #// @var bool
    #//
    final = False
    #// 
    #// @var array<int, ParagonIE_Sodium_Core32_Int32>
    #//
    h = Array()
    #// 
    #// @var int
    #//
    leftover = 0
    #// 
    #// @var array<int, ParagonIE_Sodium_Core32_Int32>
    #//
    r = Array()
    #// 
    #// @var array<int, ParagonIE_Sodium_Core32_Int64>
    #//
    pad = Array()
    #// 
    #// ParagonIE_Sodium_Core32_Poly1305_State constructor.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $key
    #// @throws InvalidArgumentException
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def __init__(self, key_=""):
        
        
        if self.strlen(key_) < 32:
            raise php_new_class("InvalidArgumentException", lambda : InvalidArgumentException("Poly1305 requires a 32-byte key"))
        # end if
        #// r &= 0xffffffc0ffffffc0ffffffc0fffffff
        self.r = Array(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key_, 0, 4)).setunsignedint(True).mask(67108863), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key_, 3, 4)).setunsignedint(True).shiftright(2).mask(67108611), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key_, 6, 4)).setunsignedint(True).shiftright(4).mask(67092735), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key_, 9, 4)).setunsignedint(True).shiftright(6).mask(66076671), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key_, 12, 4)).setunsignedint(True).shiftright(8).mask(1048575))
        #// h = 0
        self.h = Array(php_new_class("ParagonIE_Sodium_Core32_Int32", lambda : ParagonIE_Sodium_Core32_Int32(Array(0, 0), True)), php_new_class("ParagonIE_Sodium_Core32_Int32", lambda : ParagonIE_Sodium_Core32_Int32(Array(0, 0), True)), php_new_class("ParagonIE_Sodium_Core32_Int32", lambda : ParagonIE_Sodium_Core32_Int32(Array(0, 0), True)), php_new_class("ParagonIE_Sodium_Core32_Int32", lambda : ParagonIE_Sodium_Core32_Int32(Array(0, 0), True)), php_new_class("ParagonIE_Sodium_Core32_Int32", lambda : ParagonIE_Sodium_Core32_Int32(Array(0, 0), True)))
        #// save pad for later
        self.pad = Array(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key_, 16, 4)).setunsignedint(True).toint64(), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key_, 20, 4)).setunsignedint(True).toint64(), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key_, 24, 4)).setunsignedint(True).toint64(), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key_, 28, 4)).setunsignedint(True).toint64())
        self.leftover = 0
        self.final = False
    # end def __init__
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
        #// handle leftover
        if self.leftover:
            #// @var int $want
            want_ = ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE - self.leftover
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
            if self.leftover < ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE:
                #// We still don't have enough to run $this->blocks()
                return self
            # end if
            self.blocks(self.intarraytostring(self.buffer), ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE)
            self.leftover = 0
        # end if
        #// process full blocks
        if bytes_ >= ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE:
            #// @var int $want
            want_ = bytes_ & (1 << (ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE - 1).bit_length()) - 1 - ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE - 1
            if want_ >= ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE:
                #// @var string $block
                block_ = self.substr(message_, 0, want_)
                if self.strlen(block_) >= ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE:
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
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def blocks(self, message_=None, bytes_=None):
        
        
        if self.strlen(message_) < 16:
            message_ = php_str_pad(message_, 16, " ", STR_PAD_RIGHT)
        # end if
        hibit_ = ParagonIE_Sodium_Core32_Int32.fromint(php_int(0 if self.final else 1 << 24))
        #// 1 << 128
        hibit_.setunsignedint(True)
        zero_ = php_new_class("ParagonIE_Sodium_Core32_Int64", lambda : ParagonIE_Sodium_Core32_Int64(Array(0, 0, 0, 0), True))
        #// 
        #// @var ParagonIE_Sodium_Core32_Int64 $d0
        #// @var ParagonIE_Sodium_Core32_Int64 $d1
        #// @var ParagonIE_Sodium_Core32_Int64 $d2
        #// @var ParagonIE_Sodium_Core32_Int64 $d3
        #// @var ParagonIE_Sodium_Core32_Int64 $d4
        #// @var ParagonIE_Sodium_Core32_Int64 $r0
        #// @var ParagonIE_Sodium_Core32_Int64 $r1
        #// @var ParagonIE_Sodium_Core32_Int64 $r2
        #// @var ParagonIE_Sodium_Core32_Int64 $r3
        #// @var ParagonIE_Sodium_Core32_Int64 $r4
        #// 
        #// @var ParagonIE_Sodium_Core32_Int32 $h0
        #// @var ParagonIE_Sodium_Core32_Int32 $h1
        #// @var ParagonIE_Sodium_Core32_Int32 $h2
        #// @var ParagonIE_Sodium_Core32_Int32 $h3
        #// @var ParagonIE_Sodium_Core32_Int32 $h4
        #//
        r0_ = self.r[0].toint64()
        r1_ = self.r[1].toint64()
        r2_ = self.r[2].toint64()
        r3_ = self.r[3].toint64()
        r4_ = self.r[4].toint64()
        s1_ = r1_.toint64().mulint(5, 3)
        s2_ = r2_.toint64().mulint(5, 3)
        s3_ = r3_.toint64().mulint(5, 3)
        s4_ = r4_.toint64().mulint(5, 3)
        h0_ = self.h[0]
        h1_ = self.h[1]
        h2_ = self.h[2]
        h3_ = self.h[3]
        h4_ = self.h[4]
        while True:
            
            if not (bytes_ >= ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE):
                break
            # end if
            #// h += m[i]
            h0_ = h0_.addint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 0, 4)).mask(67108863)).toint64()
            h1_ = h1_.addint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 3, 4)).shiftright(2).mask(67108863)).toint64()
            h2_ = h2_.addint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 6, 4)).shiftright(4).mask(67108863)).toint64()
            h3_ = h3_.addint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 9, 4)).shiftright(6).mask(67108863)).toint64()
            h4_ = h4_.addint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 12, 4)).shiftright(8).orint32(hibit_)).toint64()
            #// h *= r
            d0_ = zero_.addint64(h0_.mulint64(r0_, 25)).addint64(s4_.mulint64(h1_, 26)).addint64(s3_.mulint64(h2_, 26)).addint64(s2_.mulint64(h3_, 26)).addint64(s1_.mulint64(h4_, 26))
            d1_ = zero_.addint64(h0_.mulint64(r1_, 25)).addint64(h1_.mulint64(r0_, 25)).addint64(s4_.mulint64(h2_, 26)).addint64(s3_.mulint64(h3_, 26)).addint64(s2_.mulint64(h4_, 26))
            d2_ = zero_.addint64(h0_.mulint64(r2_, 25)).addint64(h1_.mulint64(r1_, 25)).addint64(h2_.mulint64(r0_, 25)).addint64(s4_.mulint64(h3_, 26)).addint64(s3_.mulint64(h4_, 26))
            d3_ = zero_.addint64(h0_.mulint64(r3_, 25)).addint64(h1_.mulint64(r2_, 25)).addint64(h2_.mulint64(r1_, 25)).addint64(h3_.mulint64(r0_, 25)).addint64(s4_.mulint64(h4_, 26))
            d4_ = zero_.addint64(h0_.mulint64(r4_, 25)).addint64(h1_.mulint64(r3_, 25)).addint64(h2_.mulint64(r2_, 25)).addint64(h3_.mulint64(r1_, 25)).addint64(h4_.mulint64(r0_, 25))
            #// (partial) h %= p
            c_ = d0_.shiftright(26)
            h0_ = d0_.toint32().mask(67108863)
            d1_ = d1_.addint64(c_)
            c_ = d1_.shiftright(26)
            h1_ = d1_.toint32().mask(67108863)
            d2_ = d2_.addint64(c_)
            c_ = d2_.shiftright(26)
            h2_ = d2_.toint32().mask(67108863)
            d3_ = d3_.addint64(c_)
            c_ = d3_.shiftright(26)
            h3_ = d3_.toint32().mask(67108863)
            d4_ = d4_.addint64(c_)
            c_ = d4_.shiftright(26)
            h4_ = d4_.toint32().mask(67108863)
            h0_ = h0_.addint32(c_.toint32().mulint(5, 3))
            c_ = h0_.shiftright(26)
            h0_ = h0_.mask(67108863)
            h1_ = h1_.addint32(c_)
            #// Chop off the left 32 bytes.
            message_ = self.substr(message_, ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE)
            bytes_ -= ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE
        # end while
        #// @var array<int, ParagonIE_Sodium_Core32_Int32> $h
        self.h = Array(h0_, h1_, h2_, h3_, h4_)
        return self
    # end def blocks
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def finish(self):
        
        
        #// process the remaining block
        if self.leftover:
            i_ = self.leftover
            self.buffer[i_] = 1
            i_ += 1
            while i_ < ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE:
                
                self.buffer[i_] = 0
                i_ += 1
            # end while
            self.final = True
            self.blocks(self.substr(self.intarraytostring(self.buffer), 0, ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE), b_ = ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE)
        # end if
        #// 
        #// @var ParagonIE_Sodium_Core32_Int32 $f
        #// @var ParagonIE_Sodium_Core32_Int32 $g0
        #// @var ParagonIE_Sodium_Core32_Int32 $g1
        #// @var ParagonIE_Sodium_Core32_Int32 $g2
        #// @var ParagonIE_Sodium_Core32_Int32 $g3
        #// @var ParagonIE_Sodium_Core32_Int32 $g4
        #// @var ParagonIE_Sodium_Core32_Int32 $h0
        #// @var ParagonIE_Sodium_Core32_Int32 $h1
        #// @var ParagonIE_Sodium_Core32_Int32 $h2
        #// @var ParagonIE_Sodium_Core32_Int32 $h3
        #// @var ParagonIE_Sodium_Core32_Int32 $h4
        #//
        h0_ = self.h[0]
        h1_ = self.h[1]
        h2_ = self.h[2]
        h3_ = self.h[3]
        h4_ = self.h[4]
        c_ = h1_.shiftright(26)
        #// # $c = $h1 >> 26;
        h1_ = h1_.mask(67108863)
        #// # $h1 &= 0x3ffffff;
        h2_ = h2_.addint32(c_)
        #// # $h2 += $c;
        c_ = h2_.shiftright(26)
        #// # $c = $h2 >> 26;
        h2_ = h2_.mask(67108863)
        #// # $h2 &= 0x3ffffff;
        h3_ = h3_.addint32(c_)
        #// # $h3 += $c;
        c_ = h3_.shiftright(26)
        #// # $c = $h3 >> 26;
        h3_ = h3_.mask(67108863)
        #// # $h3 &= 0x3ffffff;
        h4_ = h4_.addint32(c_)
        #// # $h4 += $c;
        c_ = h4_.shiftright(26)
        #// # $c = $h4 >> 26;
        h4_ = h4_.mask(67108863)
        #// # $h4 &= 0x3ffffff;
        h0_ = h0_.addint32(c_.mulint(5, 3))
        #// # $h0 += self::mul($c, 5);
        c_ = h0_.shiftright(26)
        #// # $c = $h0 >> 26;
        h0_ = h0_.mask(67108863)
        #// # $h0 &= 0x3ffffff;
        h1_ = h1_.addint32(c_)
        #// # $h1 += $c;
        #// compute h + -p
        g0_ = h0_.addint(5)
        c_ = g0_.shiftright(26)
        g0_ = g0_.mask(67108863)
        g1_ = h1_.addint32(c_)
        c_ = g1_.shiftright(26)
        g1_ = g1_.mask(67108863)
        g2_ = h2_.addint32(c_)
        c_ = g2_.shiftright(26)
        g2_ = g2_.mask(67108863)
        g3_ = h3_.addint32(c_)
        c_ = g3_.shiftright(26)
        g3_ = g3_.mask(67108863)
        g4_ = h4_.addint32(c_).subint(1 << 26)
        #// # $mask = ($g4 >> 31) - 1;
        #// select h if h < p, or h + -p if h >= p
        mask_ = php_int(g4_.toint() >> 31 + 1)
        g0_ = g0_.mask(mask_)
        g1_ = g1_.mask(mask_)
        g2_ = g2_.mask(mask_)
        g3_ = g3_.mask(mask_)
        g4_ = g4_.mask(mask_)
        #// @var int $mask
        mask_ = (1 << (mask_).bit_length()) - 1 - mask_ & 4294967295
        h0_ = h0_.mask(mask_).orint32(g0_)
        h1_ = h1_.mask(mask_).orint32(g1_)
        h2_ = h2_.mask(mask_).orint32(g2_)
        h3_ = h3_.mask(mask_).orint32(g3_)
        h4_ = h4_.mask(mask_).orint32(g4_)
        #// h = h % (2^128)
        h0_ = h0_.orint32(h1_.shiftleft(26))
        h1_ = h1_.shiftright(6).orint32(h2_.shiftleft(20))
        h2_ = h2_.shiftright(12).orint32(h3_.shiftleft(14))
        h3_ = h3_.shiftright(18).orint32(h4_.shiftleft(8))
        #// mac = (h + pad) % (2^128)
        f_ = h0_.toint64().addint64(self.pad[0])
        h0_ = f_.toint32()
        f_ = h1_.toint64().addint64(self.pad[1]).addint(h0_.overflow)
        h1_ = f_.toint32()
        f_ = h2_.toint64().addint64(self.pad[2]).addint(h1_.overflow)
        h2_ = f_.toint32()
        f_ = h3_.toint64().addint64(self.pad[3]).addint(h2_.overflow)
        h3_ = f_.toint32()
        return h0_.toreversestring() + h1_.toreversestring() + h2_.toreversestring() + h3_.toreversestring()
    # end def finish
    i_ += 1
# end class ParagonIE_Sodium_Core32_Poly1305_State
