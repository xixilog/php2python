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
#// getID3() by James Heinrich <info@getid3.org>
#// available at https://github.com/JamesHeinrich/getID3
#// or https://www.getid3.org
#// or http://getid3.sourceforge.net
#// see readme.txt for more details
#// 
#// 
#// module.audio.dts.php
#// module for analyzing DTS Audio files
#// dependencies: NONE
#// 
#// 
#// 
#// @tutorial http://wiki.multimedia.cx/index.php?title=DTS
#//
class getid3_dts(getid3_handler):
    syncword = "þ"
    #// 
    #// @var int
    #//
    readBinDataOffset = 0
    #// 
    #// Possible syncwords indicating bitstream encoding.
    #//
    syncwords = Array({0: "þ", 1: "þ", 2: "ÿè ", 3: "ÿ è"})
    #// 14-bit little-endian
    #// 
    #// @return bool
    #//
    def analyze(self):
        
        
        info_ = self.getid3.info
        info_["fileformat"] = "dts"
        self.fseek(info_["avdataoffset"])
        DTSheader_ = self.fread(20)
        #// we only need 2 words magic + 6 words frame header, but these words may be normal 16-bit words OR 14-bit words with 2 highest bits set to zero, so 8 words can be either 8*16/8 = 16 bytes OR 8*16*(16/14)/8 = 18.3 bytes
        #// check syncword
        sync_ = php_substr(DTSheader_, 0, 4)
        encoding_ = php_array_search(sync_, self.syncwords)
        if encoding_ != False:
            info_["dts"]["raw"]["magic"] = sync_
            self.readBinDataOffset = 32
        elif self.isdependencyfor("matroska"):
            #// Matroska contains DTS without syncword encoded as raw big-endian format
            encoding_ = 0
            self.readBinDataOffset = 0
        else:
            info_["fileformat"] = None
            return self.error("Expecting \"" + php_implode("| ", php_array_map("getid3_lib::PrintHexBytes", self.syncwords)) + "\" at offset " + info_["avdataoffset"] + ", found \"" + getid3_lib.printhexbytes(sync_) + "\"")
        # end if
        #// decode header
        fhBS_ = ""
        word_offset_ = 0
        while word_offset_ <= php_strlen(DTSheader_):
            
            for case in Switch(encoding_):
                if case(0):
                    #// raw big-endian
                    fhBS_ += getid3_lib.bigendian2bin(php_substr(DTSheader_, word_offset_, 2))
                    break
                # end if
                if case(1):
                    #// raw little-endian
                    fhBS_ += getid3_lib.bigendian2bin(php_strrev(php_substr(DTSheader_, word_offset_, 2)))
                    break
                # end if
                if case(2):
                    #// 14-bit big-endian
                    fhBS_ += php_substr(getid3_lib.bigendian2bin(php_substr(DTSheader_, word_offset_, 2)), 2, 14)
                    break
                # end if
                if case(3):
                    #// 14-bit little-endian
                    fhBS_ += php_substr(getid3_lib.bigendian2bin(php_strrev(php_substr(DTSheader_, word_offset_, 2))), 2, 14)
                    break
                # end if
            # end for
            word_offset_ += 2
        # end while
        info_["dts"]["raw"]["frame_type"] = self.readbindata(fhBS_, 1)
        info_["dts"]["raw"]["deficit_samples"] = self.readbindata(fhBS_, 5)
        info_["dts"]["flags"]["crc_present"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["raw"]["pcm_sample_blocks"] = self.readbindata(fhBS_, 7)
        info_["dts"]["raw"]["frame_byte_size"] = self.readbindata(fhBS_, 14)
        info_["dts"]["raw"]["channel_arrangement"] = self.readbindata(fhBS_, 6)
        info_["dts"]["raw"]["sample_frequency"] = self.readbindata(fhBS_, 4)
        info_["dts"]["raw"]["bitrate"] = self.readbindata(fhBS_, 5)
        info_["dts"]["flags"]["embedded_downmix"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["flags"]["dynamicrange"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["flags"]["timestamp"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["flags"]["auxdata"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["flags"]["hdcd"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["raw"]["extension_audio"] = self.readbindata(fhBS_, 3)
        info_["dts"]["flags"]["extended_coding"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["flags"]["audio_sync_insertion"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["raw"]["lfe_effects"] = self.readbindata(fhBS_, 2)
        info_["dts"]["flags"]["predictor_history"] = php_bool(self.readbindata(fhBS_, 1))
        if info_["dts"]["flags"]["crc_present"]:
            info_["dts"]["raw"]["crc16"] = self.readbindata(fhBS_, 16)
        # end if
        info_["dts"]["flags"]["mri_perfect_reconst"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["raw"]["encoder_soft_version"] = self.readbindata(fhBS_, 4)
        info_["dts"]["raw"]["copy_history"] = self.readbindata(fhBS_, 2)
        info_["dts"]["raw"]["bits_per_sample"] = self.readbindata(fhBS_, 2)
        info_["dts"]["flags"]["surround_es"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["flags"]["front_sum_diff"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["flags"]["surround_sum_diff"] = php_bool(self.readbindata(fhBS_, 1))
        info_["dts"]["raw"]["dialog_normalization"] = self.readbindata(fhBS_, 4)
        info_["dts"]["bitrate"] = self.bitratelookup(info_["dts"]["raw"]["bitrate"])
        info_["dts"]["bits_per_sample"] = self.bitpersamplelookup(info_["dts"]["raw"]["bits_per_sample"])
        info_["dts"]["sample_rate"] = self.sampleratelookup(info_["dts"]["raw"]["sample_frequency"])
        info_["dts"]["dialog_normalization"] = self.dialognormalization(info_["dts"]["raw"]["dialog_normalization"], info_["dts"]["raw"]["encoder_soft_version"])
        info_["dts"]["flags"]["lossless"] = True if info_["dts"]["raw"]["bitrate"] == 31 else False
        info_["dts"]["bitrate_mode"] = "vbr" if info_["dts"]["raw"]["bitrate"] == 30 else "cbr"
        info_["dts"]["channels"] = self.numchannelslookup(info_["dts"]["raw"]["channel_arrangement"])
        info_["dts"]["channel_arrangement"] = self.channelarrangementlookup(info_["dts"]["raw"]["channel_arrangement"])
        info_["audio"]["dataformat"] = "dts"
        info_["audio"]["lossless"] = info_["dts"]["flags"]["lossless"]
        info_["audio"]["bitrate_mode"] = info_["dts"]["bitrate_mode"]
        info_["audio"]["bits_per_sample"] = info_["dts"]["bits_per_sample"]
        info_["audio"]["sample_rate"] = info_["dts"]["sample_rate"]
        info_["audio"]["channels"] = info_["dts"]["channels"]
        info_["audio"]["bitrate"] = info_["dts"]["bitrate"]
        if (php_isset(lambda : info_["avdataend"])) and (not php_empty(lambda : info_["dts"]["bitrate"])) and php_is_numeric(info_["dts"]["bitrate"]):
            info_["playtime_seconds"] = info_["avdataend"] - info_["avdataoffset"] / info_["dts"]["bitrate"] / 8
            if encoding_ == 2 or encoding_ == 3:
                #// 14-bit data packed into 16-bit words, so the playtime is wrong because only (14/16) of the bytes in the data portion of the file are used at the specified bitrate
                info_["playtime_seconds"] *= 14 / 16
            # end if
        # end if
        return True
    # end def analyze
    #// 
    #// @param string $bin
    #// @param int $length
    #// 
    #// @return float|int
    #//
    def readbindata(self, bin_=None, length_=None):
        
        
        data_ = php_substr(bin_, self.readBinDataOffset, length_)
        self.readBinDataOffset += length_
        return bindec(data_)
    # end def readbindata
    #// 
    #// @param int $index
    #// 
    #// @return int|string|false
    #//
    @classmethod
    def bitratelookup(self, index_=None):
        
        
        lookup_ = Array({0: 32000, 1: 56000, 2: 64000, 3: 96000, 4: 112000, 5: 128000, 6: 192000, 7: 224000, 8: 256000, 9: 320000, 10: 384000, 11: 448000, 12: 512000, 13: 576000, 14: 640000, 15: 768000, 16: 960000, 17: 1024000, 18: 1152000, 19: 1280000, 20: 1344000, 21: 1408000, 22: 1411200, 23: 1472000, 24: 1536000, 25: 1920000, 26: 2048000, 27: 3072000, 28: 3840000, 29: "open", 30: "variable", 31: "lossless"})
        return lookup_[index_] if (php_isset(lambda : lookup_[index_])) else False
    # end def bitratelookup
    #// 
    #// @param int $index
    #// 
    #// @return int|string|false
    #//
    @classmethod
    def sampleratelookup(self, index_=None):
        
        
        lookup_ = Array({0: "invalid", 1: 8000, 2: 16000, 3: 32000, 4: "invalid", 5: "invalid", 6: 11025, 7: 22050, 8: 44100, 9: "invalid", 10: "invalid", 11: 12000, 12: 24000, 13: 48000, 14: "invalid", 15: "invalid"})
        return lookup_[index_] if (php_isset(lambda : lookup_[index_])) else False
    # end def sampleratelookup
    #// 
    #// @param int $index
    #// 
    #// @return int|false
    #//
    @classmethod
    def bitpersamplelookup(self, index_=None):
        
        
        lookup_ = Array({0: 16, 1: 20, 2: 24, 3: 24})
        return lookup_[index_] if (php_isset(lambda : lookup_[index_])) else False
    # end def bitpersamplelookup
    #// 
    #// @param int $index
    #// 
    #// @return int|false
    #//
    @classmethod
    def numchannelslookup(self, index_=None):
        
        
        for case in Switch(index_):
            if case(0):
                return 1
                break
            # end if
            if case(1):
                pass
            # end if
            if case(2):
                pass
            # end if
            if case(3):
                pass
            # end if
            if case(4):
                return 2
                break
            # end if
            if case(5):
                pass
            # end if
            if case(6):
                return 3
                break
            # end if
            if case(7):
                pass
            # end if
            if case(8):
                return 4
                break
            # end if
            if case(9):
                return 5
                break
            # end if
            if case(10):
                pass
            # end if
            if case(11):
                pass
            # end if
            if case(12):
                return 6
                break
            # end if
            if case(13):
                return 7
                break
            # end if
            if case(14):
                pass
            # end if
            if case(15):
                return 8
                break
            # end if
        # end for
        return False
    # end def numchannelslookup
    #// 
    #// @param int $index
    #// 
    #// @return string
    #//
    @classmethod
    def channelarrangementlookup(self, index_=None):
        
        
        lookup_ = Array({0: "A", 1: "A + B (dual mono)", 2: "L + R (stereo)", 3: "(L+R) + (L-R) (sum-difference)", 4: "LT + RT (left and right total)", 5: "C + L + R", 6: "L + R + S", 7: "C + L + R + S", 8: "L + R + SL + SR", 9: "C + L + R + SL + SR", 10: "CL + CR + L + R + SL + SR", 11: "C + L + R+ LR + RR + OV", 12: "CF + CR + LF + RF + LR + RR", 13: "CL + C + CR + L + R + SL + SR", 14: "CL + CR + L + R + SL1 + SL2 + SR1 + SR2", 15: "CL + C+ CR + L + R + SL + S + SR"})
        return lookup_[index_] if (php_isset(lambda : lookup_[index_])) else "user-defined"
    # end def channelarrangementlookup
    #// 
    #// @param int $index
    #// @param int $version
    #// 
    #// @return int|false
    #//
    @classmethod
    def dialognormalization(self, index_=None, version_=None):
        
        
        for case in Switch(version_):
            if case(7):
                return 0 - index_
                break
            # end if
            if case(6):
                return 0 - 16 - index_
                break
            # end if
        # end for
        return False
    # end def dialognormalization
# end class getid3_dts
