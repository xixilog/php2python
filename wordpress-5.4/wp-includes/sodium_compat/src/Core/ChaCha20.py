#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import os
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
if php_class_exists("ParagonIE_Sodium_Core_ChaCha20", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core_ChaCha20
#//
class ParagonIE_Sodium_Core_ChaCha20(ParagonIE_Sodium_Core_Util):
    #// 
    #// Bitwise left rotation
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $v
    #// @param int $n
    #// @return int
    #//
    @classmethod
    def rotate(self, v_=None, n_=None):
        
        
        v_ &= 4294967295
        n_ &= 31
        return php_int(4294967295 & v_ << n_ | v_ >> 32 - n_)
    # end def rotate
    #// 
    #// The ChaCha20 quarter round function. Works on four 32-bit integers.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $a
    #// @param int $b
    #// @param int $c
    #// @param int $d
    #// @return array<int, int>
    #//
    def quarterround(self, a_=None, b_=None, c_=None, d_=None):
        
        
        #// # a = PLUS(a,b); d = ROTATE(XOR(d,a),16);
        #// @var int $a
        a_ = a_ + b_ & 4294967295
        d_ = self.rotate(d_ ^ a_, 16)
        #// # c = PLUS(c,d); b = ROTATE(XOR(b,c),12);
        #// @var int $c
        c_ = c_ + d_ & 4294967295
        b_ = self.rotate(b_ ^ c_, 12)
        #// # a = PLUS(a,b); d = ROTATE(XOR(d,a), 8);
        #// @var int $a
        a_ = a_ + b_ & 4294967295
        d_ = self.rotate(d_ ^ a_, 8)
        #// # c = PLUS(c,d); b = ROTATE(XOR(b,c), 7);
        #// @var int $c
        c_ = c_ + d_ & 4294967295
        b_ = self.rotate(b_ ^ c_, 7)
        return Array(php_int(a_), php_int(b_), php_int(c_), php_int(d_))
    # end def quarterround
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param ParagonIE_Sodium_Core_ChaCha20_Ctx $ctx
    #// @param string $message
    #// 
    #// @return string
    #// @throws TypeError
    #// @throws SodiumException
    #//
    @classmethod
    def encryptbytes(self, ctx_=None, message_=""):
        
        
        bytes_ = self.strlen(message_)
        #// 
        #// j0 = ctx->input[0];
        #// j1 = ctx->input[1];
        #// j2 = ctx->input[2];
        #// j3 = ctx->input[3];
        #// j4 = ctx->input[4];
        #// j5 = ctx->input[5];
        #// j6 = ctx->input[6];
        #// j7 = ctx->input[7];
        #// j8 = ctx->input[8];
        #// j9 = ctx->input[9];
        #// j10 = ctx->input[10];
        #// j11 = ctx->input[11];
        #// j12 = ctx->input[12];
        #// j13 = ctx->input[13];
        #// j14 = ctx->input[14];
        #// j15 = ctx->input[15];
        #//
        j0_ = php_int(ctx_[0])
        j1_ = php_int(ctx_[1])
        j2_ = php_int(ctx_[2])
        j3_ = php_int(ctx_[3])
        j4_ = php_int(ctx_[4])
        j5_ = php_int(ctx_[5])
        j6_ = php_int(ctx_[6])
        j7_ = php_int(ctx_[7])
        j8_ = php_int(ctx_[8])
        j9_ = php_int(ctx_[9])
        j10_ = php_int(ctx_[10])
        j11_ = php_int(ctx_[11])
        j12_ = php_int(ctx_[12])
        j13_ = php_int(ctx_[13])
        j14_ = php_int(ctx_[14])
        j15_ = php_int(ctx_[15])
        c_ = ""
        while True:
            
            if bytes_ < 64:
                message_ += php_str_repeat(" ", 64 - bytes_)
            # end if
            x0_ = php_int(j0_)
            x1_ = php_int(j1_)
            x2_ = php_int(j2_)
            x3_ = php_int(j3_)
            x4_ = php_int(j4_)
            x5_ = php_int(j5_)
            x6_ = php_int(j6_)
            x7_ = php_int(j7_)
            x8_ = php_int(j8_)
            x9_ = php_int(j9_)
            x10_ = php_int(j10_)
            x11_ = php_int(j11_)
            x12_ = php_int(j12_)
            x13_ = php_int(j13_)
            x14_ = php_int(j14_)
            x15_ = php_int(j15_)
            #// # for (i = 20; i > 0; i -= 2) {
            i_ = 20
            while i_ > 0:
                
                #// # QUARTERROUND( x0,  x4,  x8,  x12)
                x0_, x4_, x8_, x12_ = self.quarterround(x0_, x4_, x8_, x12_)
                #// # QUARTERROUND( x1,  x5,  x9,  x13)
                x1_, x5_, x9_, x13_ = self.quarterround(x1_, x5_, x9_, x13_)
                #// # QUARTERROUND( x2,  x6,  x10,  x14)
                x2_, x6_, x10_, x14_ = self.quarterround(x2_, x6_, x10_, x14_)
                #// # QUARTERROUND( x3,  x7,  x11,  x15)
                x3_, x7_, x11_, x15_ = self.quarterround(x3_, x7_, x11_, x15_)
                #// # QUARTERROUND( x0,  x5,  x10,  x15)
                x0_, x5_, x10_, x15_ = self.quarterround(x0_, x5_, x10_, x15_)
                #// # QUARTERROUND( x1,  x6,  x11,  x12)
                x1_, x6_, x11_, x12_ = self.quarterround(x1_, x6_, x11_, x12_)
                #// # QUARTERROUND( x2,  x7,  x8,  x13)
                x2_, x7_, x8_, x13_ = self.quarterround(x2_, x7_, x8_, x13_)
                #// # QUARTERROUND( x3,  x4,  x9,  x14)
                x3_, x4_, x9_, x14_ = self.quarterround(x3_, x4_, x9_, x14_)
                i_ -= 2
            # end while
            #// 
            #// x0 = PLUS(x0, j0);
            #// x1 = PLUS(x1, j1);
            #// x2 = PLUS(x2, j2);
            #// x3 = PLUS(x3, j3);
            #// x4 = PLUS(x4, j4);
            #// x5 = PLUS(x5, j5);
            #// x6 = PLUS(x6, j6);
            #// x7 = PLUS(x7, j7);
            #// x8 = PLUS(x8, j8);
            #// x9 = PLUS(x9, j9);
            #// x10 = PLUS(x10, j10);
            #// x11 = PLUS(x11, j11);
            #// x12 = PLUS(x12, j12);
            #// x13 = PLUS(x13, j13);
            #// x14 = PLUS(x14, j14);
            #// x15 = PLUS(x15, j15);
            #// 
            #// @var int $x0
            x0_ = x0_ & 4294967295 + j0_
            #// @var int $x1
            x1_ = x1_ & 4294967295 + j1_
            #// @var int $x2
            x2_ = x2_ & 4294967295 + j2_
            #// @var int $x3
            x3_ = x3_ & 4294967295 + j3_
            #// @var int $x4
            x4_ = x4_ & 4294967295 + j4_
            #// @var int $x5
            x5_ = x5_ & 4294967295 + j5_
            #// @var int $x6
            x6_ = x6_ & 4294967295 + j6_
            #// @var int $x7
            x7_ = x7_ & 4294967295 + j7_
            #// @var int $x8
            x8_ = x8_ & 4294967295 + j8_
            #// @var int $x9
            x9_ = x9_ & 4294967295 + j9_
            #// @var int $x10
            x10_ = x10_ & 4294967295 + j10_
            #// @var int $x11
            x11_ = x11_ & 4294967295 + j11_
            #// @var int $x12
            x12_ = x12_ & 4294967295 + j12_
            #// @var int $x13
            x13_ = x13_ & 4294967295 + j13_
            #// @var int $x14
            x14_ = x14_ & 4294967295 + j14_
            #// @var int $x15
            x15_ = x15_ & 4294967295 + j15_
            #// 
            #// x0 = XOR(x0, LOAD32_LE(m + 0));
            #// x1 = XOR(x1, LOAD32_LE(m + 4));
            #// x2 = XOR(x2, LOAD32_LE(m + 8));
            #// x3 = XOR(x3, LOAD32_LE(m + 12));
            #// x4 = XOR(x4, LOAD32_LE(m + 16));
            #// x5 = XOR(x5, LOAD32_LE(m + 20));
            #// x6 = XOR(x6, LOAD32_LE(m + 24));
            #// x7 = XOR(x7, LOAD32_LE(m + 28));
            #// x8 = XOR(x8, LOAD32_LE(m + 32));
            #// x9 = XOR(x9, LOAD32_LE(m + 36));
            #// x10 = XOR(x10, LOAD32_LE(m + 40));
            #// x11 = XOR(x11, LOAD32_LE(m + 44));
            #// x12 = XOR(x12, LOAD32_LE(m + 48));
            #// x13 = XOR(x13, LOAD32_LE(m + 52));
            #// x14 = XOR(x14, LOAD32_LE(m + 56));
            #// x15 = XOR(x15, LOAD32_LE(m + 60));
            #//
            x0_ ^= self.load_4(self.substr(message_, 0, 4))
            x1_ ^= self.load_4(self.substr(message_, 4, 4))
            x2_ ^= self.load_4(self.substr(message_, 8, 4))
            x3_ ^= self.load_4(self.substr(message_, 12, 4))
            x4_ ^= self.load_4(self.substr(message_, 16, 4))
            x5_ ^= self.load_4(self.substr(message_, 20, 4))
            x6_ ^= self.load_4(self.substr(message_, 24, 4))
            x7_ ^= self.load_4(self.substr(message_, 28, 4))
            x8_ ^= self.load_4(self.substr(message_, 32, 4))
            x9_ ^= self.load_4(self.substr(message_, 36, 4))
            x10_ ^= self.load_4(self.substr(message_, 40, 4))
            x11_ ^= self.load_4(self.substr(message_, 44, 4))
            x12_ ^= self.load_4(self.substr(message_, 48, 4))
            x13_ ^= self.load_4(self.substr(message_, 52, 4))
            x14_ ^= self.load_4(self.substr(message_, 56, 4))
            x15_ ^= self.load_4(self.substr(message_, 60, 4))
            #// 
            #// j12 = PLUSONE(j12);
            #// if (!j12) {
            #// j13 = PLUSONE(j13);
            #// }
            #//
            j12_ += 1
            if j12_ & 4026531840:
                raise php_new_class("SodiumException", lambda : SodiumException("Overflow"))
            # end if
            #// 
            #// STORE32_LE(c + 0, x0);
            #// STORE32_LE(c + 4, x1);
            #// STORE32_LE(c + 8, x2);
            #// STORE32_LE(c + 12, x3);
            #// STORE32_LE(c + 16, x4);
            #// STORE32_LE(c + 20, x5);
            #// STORE32_LE(c + 24, x6);
            #// STORE32_LE(c + 28, x7);
            #// STORE32_LE(c + 32, x8);
            #// STORE32_LE(c + 36, x9);
            #// STORE32_LE(c + 40, x10);
            #// STORE32_LE(c + 44, x11);
            #// STORE32_LE(c + 48, x12);
            #// STORE32_LE(c + 52, x13);
            #// STORE32_LE(c + 56, x14);
            #// STORE32_LE(c + 60, x15);
            #//
            block_ = self.store32_le(php_int(x0_ & 4294967295)) + self.store32_le(php_int(x1_ & 4294967295)) + self.store32_le(php_int(x2_ & 4294967295)) + self.store32_le(php_int(x3_ & 4294967295)) + self.store32_le(php_int(x4_ & 4294967295)) + self.store32_le(php_int(x5_ & 4294967295)) + self.store32_le(php_int(x6_ & 4294967295)) + self.store32_le(php_int(x7_ & 4294967295)) + self.store32_le(php_int(x8_ & 4294967295)) + self.store32_le(php_int(x9_ & 4294967295)) + self.store32_le(php_int(x10_ & 4294967295)) + self.store32_le(php_int(x11_ & 4294967295)) + self.store32_le(php_int(x12_ & 4294967295)) + self.store32_le(php_int(x13_ & 4294967295)) + self.store32_le(php_int(x14_ & 4294967295)) + self.store32_le(php_int(x15_ & 4294967295))
            #// Partial block
            if bytes_ < 64:
                c_ += self.substr(block_, 0, bytes_)
                break
            # end if
            #// Full block
            c_ += block_
            bytes_ -= 64
            if bytes_ <= 0:
                break
            # end if
            message_ = self.substr(message_, 64)
            
        # end while
        #// end for(;;) loop
        ctx_[12] = j12_
        ctx_[13] = j13_
        return c_
    # end def encryptbytes
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
        
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core_ChaCha20_Ctx(key_, nonce_)), php_str_repeat(" ", len_))
    # end def stream
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
    def ietfstream(self, len_=None, nonce_="", key_=""):
        
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core_ChaCha20_IetfCtx", lambda : ParagonIE_Sodium_Core_ChaCha20_IetfCtx(key_, nonce_)), php_str_repeat(" ", len_))
    # end def ietfstream
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
    def ietfstreamxoric(self, message_=None, nonce_="", key_="", ic_=""):
        
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core_ChaCha20_IetfCtx", lambda : ParagonIE_Sodium_Core_ChaCha20_IetfCtx(key_, nonce_, ic_)), message_)
    # end def ietfstreamxoric
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
        
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core_ChaCha20_Ctx(key_, nonce_, ic_)), message_)
    # end def streamxoric
# end class ParagonIE_Sodium_Core_ChaCha20
