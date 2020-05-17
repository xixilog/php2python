#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import os
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
if php_class_exists("ParagonIE_Sodium_Core32_ChaCha20", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core32_ChaCha20
#//
class ParagonIE_Sodium_Core32_ChaCha20(ParagonIE_Sodium_Core32_Util):
    #// 
    #// The ChaCha20 quarter round function. Works on four 32-bit integers.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param ParagonIE_Sodium_Core32_Int32 $a
    #// @param ParagonIE_Sodium_Core32_Int32 $b
    #// @param ParagonIE_Sodium_Core32_Int32 $c
    #// @param ParagonIE_Sodium_Core32_Int32 $d
    #// @return array<int, ParagonIE_Sodium_Core32_Int32>
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def quarterround(self, a_=None, b_=None, c_=None, d_=None):
        
        
        #// @var ParagonIE_Sodium_Core32_Int32 $a
        #// @var ParagonIE_Sodium_Core32_Int32 $b
        #// @var ParagonIE_Sodium_Core32_Int32 $c
        #// @var ParagonIE_Sodium_Core32_Int32 $d
        #// # a = PLUS(a,b); d = ROTATE(XOR(d,a),16);
        a_ = a_.addint32(b_)
        d_ = d_.xorint32(a_).rotateleft(16)
        #// # c = PLUS(c,d); b = ROTATE(XOR(b,c),12);
        c_ = c_.addint32(d_)
        b_ = b_.xorint32(c_).rotateleft(12)
        #// # a = PLUS(a,b); d = ROTATE(XOR(d,a), 8);
        a_ = a_.addint32(b_)
        d_ = d_.xorint32(a_).rotateleft(8)
        #// # c = PLUS(c,d); b = ROTATE(XOR(b,c), 7);
        c_ = c_.addint32(d_)
        b_ = b_.xorint32(c_).rotateleft(7)
        return Array(a_, b_, c_, d_)
    # end def quarterround
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param ParagonIE_Sodium_Core32_ChaCha20_Ctx $ctx
    #// @param string $message
    #// 
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def encryptbytes(self, ctx_=None, message_=""):
        
        
        bytes_ = self.strlen(message_)
        #// @var ParagonIE_Sodium_Core32_Int32 $x0
        #// @var ParagonIE_Sodium_Core32_Int32 $x1
        #// @var ParagonIE_Sodium_Core32_Int32 $x2
        #// @var ParagonIE_Sodium_Core32_Int32 $x3
        #// @var ParagonIE_Sodium_Core32_Int32 $x4
        #// @var ParagonIE_Sodium_Core32_Int32 $x5
        #// @var ParagonIE_Sodium_Core32_Int32 $x6
        #// @var ParagonIE_Sodium_Core32_Int32 $x7
        #// @var ParagonIE_Sodium_Core32_Int32 $x8
        #// @var ParagonIE_Sodium_Core32_Int32 $x9
        #// @var ParagonIE_Sodium_Core32_Int32 $x10
        #// @var ParagonIE_Sodium_Core32_Int32 $x11
        #// @var ParagonIE_Sodium_Core32_Int32 $x12
        #// @var ParagonIE_Sodium_Core32_Int32 $x13
        #// @var ParagonIE_Sodium_Core32_Int32 $x14
        #// @var ParagonIE_Sodium_Core32_Int32 $x15
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
        #// @var ParagonIE_Sodium_Core32_Int32 $j0
        j0_ = ctx_[0]
        #// @var ParagonIE_Sodium_Core32_Int32 $j1
        j1_ = ctx_[1]
        #// @var ParagonIE_Sodium_Core32_Int32 $j2
        j2_ = ctx_[2]
        #// @var ParagonIE_Sodium_Core32_Int32 $j3
        j3_ = ctx_[3]
        #// @var ParagonIE_Sodium_Core32_Int32 $j4
        j4_ = ctx_[4]
        #// @var ParagonIE_Sodium_Core32_Int32 $j5
        j5_ = ctx_[5]
        #// @var ParagonIE_Sodium_Core32_Int32 $j6
        j6_ = ctx_[6]
        #// @var ParagonIE_Sodium_Core32_Int32 $j7
        j7_ = ctx_[7]
        #// @var ParagonIE_Sodium_Core32_Int32 $j8
        j8_ = ctx_[8]
        #// @var ParagonIE_Sodium_Core32_Int32 $j9
        j9_ = ctx_[9]
        #// @var ParagonIE_Sodium_Core32_Int32 $j10
        j10_ = ctx_[10]
        #// @var ParagonIE_Sodium_Core32_Int32 $j11
        j11_ = ctx_[11]
        #// @var ParagonIE_Sodium_Core32_Int32 $j12
        j12_ = ctx_[12]
        #// @var ParagonIE_Sodium_Core32_Int32 $j13
        j13_ = ctx_[13]
        #// @var ParagonIE_Sodium_Core32_Int32 $j14
        j14_ = ctx_[14]
        #// @var ParagonIE_Sodium_Core32_Int32 $j15
        j15_ = ctx_[15]
        c_ = ""
        while True:
            
            if bytes_ < 64:
                message_ += php_str_repeat(" ", 64 - bytes_)
            # end if
            x0_ = copy.deepcopy(j0_)
            x1_ = copy.deepcopy(j1_)
            x2_ = copy.deepcopy(j2_)
            x3_ = copy.deepcopy(j3_)
            x4_ = copy.deepcopy(j4_)
            x5_ = copy.deepcopy(j5_)
            x6_ = copy.deepcopy(j6_)
            x7_ = copy.deepcopy(j7_)
            x8_ = copy.deepcopy(j8_)
            x9_ = copy.deepcopy(j9_)
            x10_ = copy.deepcopy(j10_)
            x11_ = copy.deepcopy(j11_)
            x12_ = copy.deepcopy(j12_)
            x13_ = copy.deepcopy(j13_)
            x14_ = copy.deepcopy(j14_)
            x15_ = copy.deepcopy(j15_)
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
            x0_ = x0_.addint32(j0_)
            x1_ = x1_.addint32(j1_)
            x2_ = x2_.addint32(j2_)
            x3_ = x3_.addint32(j3_)
            x4_ = x4_.addint32(j4_)
            x5_ = x5_.addint32(j5_)
            x6_ = x6_.addint32(j6_)
            x7_ = x7_.addint32(j7_)
            x8_ = x8_.addint32(j8_)
            x9_ = x9_.addint32(j9_)
            x10_ = x10_.addint32(j10_)
            x11_ = x11_.addint32(j11_)
            x12_ = x12_.addint32(j12_)
            x13_ = x13_.addint32(j13_)
            x14_ = x14_.addint32(j14_)
            x15_ = x15_.addint32(j15_)
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
            x0_ = x0_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 0, 4)))
            x1_ = x1_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 4, 4)))
            x2_ = x2_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 8, 4)))
            x3_ = x3_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 12, 4)))
            x4_ = x4_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 16, 4)))
            x5_ = x5_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 20, 4)))
            x6_ = x6_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 24, 4)))
            x7_ = x7_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 28, 4)))
            x8_ = x8_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 32, 4)))
            x9_ = x9_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 36, 4)))
            x10_ = x10_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 40, 4)))
            x11_ = x11_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 44, 4)))
            x12_ = x12_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 48, 4)))
            x13_ = x13_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 52, 4)))
            x14_ = x14_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 56, 4)))
            x15_ = x15_.xorint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message_, 60, 4)))
            #// 
            #// j12 = PLUSONE(j12);
            #// if (!j12) {
            #// j13 = PLUSONE(j13);
            #// }
            #// 
            #// @var ParagonIE_Sodium_Core32_Int32 $j12
            j12_ = j12_.addint(1)
            if j12_.limbs[0] == 0 and j12_.limbs[1] == 0:
                j13_ = j13_.addint(1)
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
            block_ = x0_.toreversestring() + x1_.toreversestring() + x2_.toreversestring() + x3_.toreversestring() + x4_.toreversestring() + x5_.toreversestring() + x6_.toreversestring() + x7_.toreversestring() + x8_.toreversestring() + x9_.toreversestring() + x10_.toreversestring() + x11_.toreversestring() + x12_.toreversestring() + x13_.toreversestring() + x14_.toreversestring() + x15_.toreversestring()
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
        
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core32_ChaCha20_Ctx(key_, nonce_)), php_str_repeat(" ", len_))
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
        
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_IetfCtx", lambda : ParagonIE_Sodium_Core32_ChaCha20_IetfCtx(key_, nonce_)), php_str_repeat(" ", len_))
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
        
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_IetfCtx", lambda : ParagonIE_Sodium_Core32_ChaCha20_IetfCtx(key_, nonce_, ic_)), message_)
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
        
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core32_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core32_ChaCha20_Ctx(key_, nonce_, ic_)), message_)
    # end def streamxoric
# end class ParagonIE_Sodium_Core32_ChaCha20
