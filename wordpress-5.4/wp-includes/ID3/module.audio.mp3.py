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
#// module.audio.mp3.php
#// module for analyzing MP3 files
#// dependencies: NONE
#// 
#// 
#// number of frames to scan to determine if MPEG-audio sequence is valid
#// Lower this number to 5-20 for faster scanning
#// Increase this number to 50+ for most accurate detection of valid VBR/CBR
#// mpeg-audio streams
php_define("GETID3_MP3_VALID_CHECK_FRAMES", 35)
class getid3_mp3(getid3_handler):
    #// 
    #// Forces getID3() to scan the file byte-by-byte and log all the valid audio frame headers - extremely slow,
    #// unrecommended, but may provide data from otherwise-unusable files.
    #// 
    #// @var bool
    #//
    allow_bruteforce = False
    #// 
    #// @return bool
    #//
    def analyze(self):
        
        
        info_ = self.getid3.info
        initialOffset_ = info_["avdataoffset"]
        if (not self.getonlympegaudioinfo(info_["avdataoffset"])):
            if self.allow_bruteforce:
                self.error("Rescanning file in BruteForce mode")
                self.getonlympegaudioinfobruteforce()
            # end if
        # end if
        if (php_isset(lambda : info_["mpeg"]["audio"]["bitrate_mode"])):
            info_["audio"]["bitrate_mode"] = php_strtolower(info_["mpeg"]["audio"]["bitrate_mode"])
        # end if
        if (php_isset(lambda : info_["id3v2"]["headerlength"])) and info_["avdataoffset"] > info_["id3v2"]["headerlength"] or (not (php_isset(lambda : info_["id3v2"]))) and info_["avdataoffset"] > 0 and info_["avdataoffset"] != initialOffset_:
            synchoffsetwarning_ = "Unknown data before synch "
            if (php_isset(lambda : info_["id3v2"]["headerlength"])):
                synchoffsetwarning_ += "(ID3v2 header ends at " + info_["id3v2"]["headerlength"] + ", then " + info_["avdataoffset"] - info_["id3v2"]["headerlength"] + " bytes garbage, "
            elif initialOffset_ > 0:
                synchoffsetwarning_ += "(should be at " + initialOffset_ + ", "
            else:
                synchoffsetwarning_ += "(should be at beginning of file, "
            # end if
            synchoffsetwarning_ += "synch detected at " + info_["avdataoffset"] + ")"
            if (php_isset(lambda : info_["audio"]["bitrate_mode"])) and info_["audio"]["bitrate_mode"] == "cbr":
                if (not php_empty(lambda : info_["id3v2"]["headerlength"])) and info_["avdataoffset"] - info_["id3v2"]["headerlength"] == info_["mpeg"]["audio"]["framelength"]:
                    synchoffsetwarning_ += ". This is a known problem with some versions of LAME (3.90-3.92) DLL in CBR mode."
                    info_["audio"]["codec"] = "LAME"
                    CurrentDataLAMEversionString_ = "LAME3."
                elif php_empty(lambda : info_["id3v2"]["headerlength"]) and info_["avdataoffset"] == info_["mpeg"]["audio"]["framelength"]:
                    synchoffsetwarning_ += ". This is a known problem with some versions of LAME (3.90 - 3.92) DLL in CBR mode."
                    info_["audio"]["codec"] = "LAME"
                    CurrentDataLAMEversionString_ = "LAME3."
                # end if
            # end if
            self.warning(synchoffsetwarning_)
        # end if
        if (php_isset(lambda : info_["mpeg"]["audio"]["LAME"])):
            info_["audio"]["codec"] = "LAME"
            if (not php_empty(lambda : info_["mpeg"]["audio"]["LAME"]["long_version"])):
                info_["audio"]["encoder"] = php_rtrim(info_["mpeg"]["audio"]["LAME"]["long_version"], " ")
            elif (not php_empty(lambda : info_["mpeg"]["audio"]["LAME"]["short_version"])):
                info_["audio"]["encoder"] = php_rtrim(info_["mpeg"]["audio"]["LAME"]["short_version"], " ")
            # end if
        # end if
        CurrentDataLAMEversionString_ = CurrentDataLAMEversionString_ if (not php_empty(lambda : CurrentDataLAMEversionString_)) else info_["audio"]["encoder"] if (php_isset(lambda : info_["audio"]["encoder"])) else ""
        if (not php_empty(lambda : CurrentDataLAMEversionString_)) and php_substr(CurrentDataLAMEversionString_, 0, 6) == "LAME3." and (not php_preg_match("[0-9\\)]", php_substr(CurrentDataLAMEversionString_, -1))):
            #// a version number of LAME that does not end with a number like "LAME3.92"
            #// or with a closing parenthesis like "LAME3.88 (alpha)"
            #// or a version of LAME with the LAMEtag-not-filled-in-DLL-mode bug (3.90-3.92)
            #// not sure what the actual last frame length will be, but will be less than or equal to 1441
            PossiblyLongerLAMEversion_FrameLength_ = 1441
            #// Not sure what version of LAME this is - look in padding of last frame for longer version string
            PossibleLAMEversionStringOffset_ = info_["avdataend"] - PossiblyLongerLAMEversion_FrameLength_
            self.fseek(PossibleLAMEversionStringOffset_)
            PossiblyLongerLAMEversion_Data_ = self.fread(PossiblyLongerLAMEversion_FrameLength_)
            for case in Switch(php_substr(CurrentDataLAMEversionString_, -1)):
                if case("a"):
                    pass
                # end if
                if case("b"):
                    #// "LAME3.94a" will have a longer version string of "LAME3.94 (alpha)" for example
                    #// need to trim off "a" to match longer string
                    CurrentDataLAMEversionString_ = php_substr(CurrentDataLAMEversionString_, 0, -1)
                    break
                # end if
            # end for
            PossiblyLongerLAMEversion_String_ = php_strstr(PossiblyLongerLAMEversion_Data_, CurrentDataLAMEversionString_)
            if PossiblyLongerLAMEversion_String_ != False:
                if php_substr(PossiblyLongerLAMEversion_String_, 0, php_strlen(CurrentDataLAMEversionString_)) == CurrentDataLAMEversionString_:
                    PossiblyLongerLAMEversion_NewString_ = php_substr(PossiblyLongerLAMEversion_String_, 0, strspn(PossiblyLongerLAMEversion_String_, "LAME0123456789., (abcdefghijklmnopqrstuvwxyzJFSOND)"))
                    #// "LAME3.90.3"  "LAME3.87 (beta 1, Sep 27 2000)" "LAME3.88 (beta)"
                    if php_empty(lambda : info_["audio"]["encoder"]) or php_strlen(PossiblyLongerLAMEversion_NewString_) > php_strlen(info_["audio"]["encoder"]):
                        info_["audio"]["encoder"] = PossiblyLongerLAMEversion_NewString_
                    # end if
                # end if
            # end if
        # end if
        if (not php_empty(lambda : info_["audio"]["encoder"])):
            info_["audio"]["encoder"] = php_rtrim(info_["audio"]["encoder"], "  ")
        # end if
        for case in Switch(info_["mpeg"]["audio"]["layer"] if (php_isset(lambda : info_["mpeg"]["audio"]["layer"])) else ""):
            if case(1):
                pass
            # end if
            if case(2):
                info_["audio"]["dataformat"] = "mp" + info_["mpeg"]["audio"]["layer"]
                break
            # end if
        # end for
        if (php_isset(lambda : info_["fileformat"])) and info_["fileformat"] == "mp3":
            for case in Switch(info_["audio"]["dataformat"]):
                if case("mp1"):
                    pass
                # end if
                if case("mp2"):
                    pass
                # end if
                if case("mp3"):
                    info_["fileformat"] = info_["audio"]["dataformat"]
                    break
                # end if
                if case():
                    self.warning("Expecting [audio][dataformat] to be mp1/mp2/mp3 when fileformat == mp3, [audio][dataformat] actually \"" + info_["audio"]["dataformat"] + "\"")
                    break
                # end if
            # end for
        # end if
        if php_empty(lambda : info_["fileformat"]):
            info_["fileformat"] = None
            info_["audio"]["bitrate_mode"] = None
            info_["avdataoffset"] = None
            info_["avdataend"] = None
            return False
        # end if
        info_["mime_type"] = "audio/mpeg"
        info_["audio"]["lossless"] = False
        #// Calculate playtime
        if (not (php_isset(lambda : info_["playtime_seconds"]))) and (php_isset(lambda : info_["audio"]["bitrate"])) and info_["audio"]["bitrate"] > 0:
            #// https://github.com/JamesHeinrich/getID3/issues/161
            #// VBR header frame contains ~0.026s of silent audio data, but is not actually part of the original encoding and should be ignored
            xingVBRheaderFrameLength_ = info_["mpeg"]["audio"]["framelength"] if (php_isset(lambda : info_["mpeg"]["audio"]["VBR_frames"])) and (php_isset(lambda : info_["mpeg"]["audio"]["framelength"])) else 0
            info_["playtime_seconds"] = info_["avdataend"] - info_["avdataoffset"] - xingVBRheaderFrameLength_ * 8 / info_["audio"]["bitrate"]
        # end if
        info_["audio"]["encoder_options"] = self.guessencoderoptions()
        return True
    # end def analyze
    #// 
    #// @return string
    #//
    def guessencoderoptions(self):
        
        
        #// shortcuts
        info_ = self.getid3.info
        thisfile_mpeg_audio_ = Array()
        thisfile_mpeg_audio_lame_ = Array()
        if (not php_empty(lambda : info_["mpeg"]["audio"])):
            thisfile_mpeg_audio_ = info_["mpeg"]["audio"]
            if (not php_empty(lambda : thisfile_mpeg_audio_["LAME"])):
                thisfile_mpeg_audio_lame_ = thisfile_mpeg_audio_["LAME"]
            # end if
        # end if
        encoder_options_ = ""
        NamedPresetBitrates_ = Array(16, 24, 40, 56, 112, 128, 160, 192, 256)
        if (php_isset(lambda : thisfile_mpeg_audio_["VBR_method"])) and thisfile_mpeg_audio_["VBR_method"] == "Fraunhofer" and (not php_empty(lambda : thisfile_mpeg_audio_["VBR_quality"])):
            encoder_options_ = "VBR q" + thisfile_mpeg_audio_["VBR_quality"]
        elif (not php_empty(lambda : thisfile_mpeg_audio_lame_["preset_used"])) and (php_isset(lambda : thisfile_mpeg_audio_lame_["preset_used_id"])) and (not php_in_array(thisfile_mpeg_audio_lame_["preset_used_id"], NamedPresetBitrates_)):
            encoder_options_ = thisfile_mpeg_audio_lame_["preset_used"]
        elif (not php_empty(lambda : thisfile_mpeg_audio_lame_["vbr_quality"])):
            KnownEncoderValues_ = Array()
            if php_empty(lambda : KnownEncoderValues_):
                #// $KnownEncoderValues[abrbitrate_minbitrate][vbr_quality][raw_vbr_method][raw_noise_shaping][raw_stereo_mode][ath_type][lowpass_frequency] = 'preset name';
                KnownEncoderValues_[255][58][1][1][3][2][20500] = "--alt-preset insane"
                #// 3.90,   3.90.1, 3.92
                KnownEncoderValues_[255][58][1][1][3][2][20600] = "--alt-preset insane"
                #// 3.90.2, 3.90.3, 3.91
                KnownEncoderValues_[255][57][1][1][3][4][20500] = "--alt-preset insane"
                #// 3.94,   3.95
                KnownEncoderValues_["**"][78][3][2][3][2][19500] = "--alt-preset extreme"
                #// 3.90,   3.90.1, 3.92
                KnownEncoderValues_["**"][78][3][2][3][2][19600] = "--alt-preset extreme"
                #// 3.90.2, 3.91
                KnownEncoderValues_["**"][78][3][1][3][2][19600] = "--alt-preset extreme"
                #// 3.90.3
                KnownEncoderValues_["**"][78][4][2][3][2][19500] = "--alt-preset fast extreme"
                #// 3.90,   3.90.1, 3.92
                KnownEncoderValues_["**"][78][4][2][3][2][19600] = "--alt-preset fast extreme"
                #// 3.90.2, 3.90.3, 3.91
                KnownEncoderValues_["**"][78][3][2][3][4][19000] = "--alt-preset standard"
                #// 3.90,   3.90.1, 3.90.2, 3.91, 3.92
                KnownEncoderValues_["**"][78][3][1][3][4][19000] = "--alt-preset standard"
                #// 3.90.3
                KnownEncoderValues_["**"][78][4][2][3][4][19000] = "--alt-preset fast standard"
                #// 3.90,   3.90.1, 3.90.2, 3.91, 3.92
                KnownEncoderValues_["**"][78][4][1][3][4][19000] = "--alt-preset fast standard"
                #// 3.90.3
                KnownEncoderValues_["**"][88][4][1][3][3][19500] = "--r3mix"
                #// 3.90,   3.90.1, 3.92
                KnownEncoderValues_["**"][88][4][1][3][3][19600] = "--r3mix"
                #// 3.90.2, 3.90.3, 3.91
                KnownEncoderValues_["**"][67][4][1][3][4][18000] = "--r3mix"
                #// 3.94,   3.95
                KnownEncoderValues_["**"][68][3][2][3][4][18000] = "--alt-preset medium"
                #// 3.90.3
                KnownEncoderValues_["**"][68][4][2][3][4][18000] = "--alt-preset fast medium"
                #// 3.90.3
                KnownEncoderValues_[255][99][1][1][1][2][0] = "--preset studio"
                #// 3.90,   3.90.1, 3.90.2, 3.91, 3.92
                KnownEncoderValues_[255][58][2][1][3][2][20600] = "--preset studio"
                #// 3.90.3, 3.93.1
                KnownEncoderValues_[255][58][2][1][3][2][20500] = "--preset studio"
                #// 3.93
                KnownEncoderValues_[255][57][2][1][3][4][20500] = "--preset studio"
                #// 3.94,   3.95
                KnownEncoderValues_[192][88][1][1][1][2][0] = "--preset cd"
                #// 3.90,   3.90.1, 3.90.2,   3.91, 3.92
                KnownEncoderValues_[192][58][2][2][3][2][19600] = "--preset cd"
                #// 3.90.3, 3.93.1
                KnownEncoderValues_[192][58][2][2][3][2][19500] = "--preset cd"
                #// 3.93
                KnownEncoderValues_[192][57][2][1][3][4][19500] = "--preset cd"
                #// 3.94,   3.95
                KnownEncoderValues_[160][78][1][1][3][2][18000] = "--preset hifi"
                #// 3.90,   3.90.1, 3.90.2,   3.91, 3.92
                KnownEncoderValues_[160][58][2][2][3][2][18000] = "--preset hifi"
                #// 3.90.3, 3.93,   3.93.1
                KnownEncoderValues_[160][57][2][1][3][4][18000] = "--preset hifi"
                #// 3.94,   3.95
                KnownEncoderValues_[128][67][1][1][3][2][18000] = "--preset tape"
                #// 3.90,   3.90.1, 3.90.2,   3.91, 3.92
                KnownEncoderValues_[128][67][1][1][3][2][15000] = "--preset radio"
                #// 3.90,   3.90.1, 3.90.2,   3.91, 3.92
                KnownEncoderValues_[112][67][1][1][3][2][15000] = "--preset fm"
                #// 3.90,   3.90.1, 3.90.2,   3.91, 3.92
                KnownEncoderValues_[112][58][2][2][3][2][16000] = "--preset tape/radio/fm"
                #// 3.90.3, 3.93,   3.93.1
                KnownEncoderValues_[112][57][2][1][3][4][16000] = "--preset tape/radio/fm"
                #// 3.94,   3.95
                KnownEncoderValues_[56][58][2][2][0][2][10000] = "--preset voice"
                #// 3.90.3, 3.93,   3.93.1
                KnownEncoderValues_[56][57][2][1][0][4][15000] = "--preset voice"
                #// 3.94,   3.95
                KnownEncoderValues_[56][57][2][1][0][4][16000] = "--preset voice"
                #// 3.94a14
                KnownEncoderValues_[40][65][1][1][0][2][7500] = "--preset mw-us"
                #// 3.90,   3.90.1, 3.92
                KnownEncoderValues_[40][65][1][1][0][2][7600] = "--preset mw-us"
                #// 3.90.2, 3.91
                KnownEncoderValues_[40][58][2][2][0][2][7000] = "--preset mw-us"
                #// 3.90.3, 3.93,   3.93.1
                KnownEncoderValues_[40][57][2][1][0][4][10500] = "--preset mw-us"
                #// 3.94,   3.95
                KnownEncoderValues_[40][57][2][1][0][4][11200] = "--preset mw-us"
                #// 3.94a14
                KnownEncoderValues_[40][57][2][1][0][4][8800] = "--preset mw-us"
                #// 3.94a15
                KnownEncoderValues_[24][58][2][2][0][2][4000] = "--preset phon+/lw/mw-eu/sw"
                #// 3.90.3, 3.93.1
                KnownEncoderValues_[24][58][2][2][0][2][3900] = "--preset phon+/lw/mw-eu/sw"
                #// 3.93
                KnownEncoderValues_[24][57][2][1][0][4][5900] = "--preset phon+/lw/mw-eu/sw"
                #// 3.94,   3.95
                KnownEncoderValues_[24][57][2][1][0][4][6200] = "--preset phon+/lw/mw-eu/sw"
                #// 3.94a14
                KnownEncoderValues_[24][57][2][1][0][4][3200] = "--preset phon+/lw/mw-eu/sw"
                #// 3.94a15
                KnownEncoderValues_[16][58][2][2][0][2][3800] = "--preset phone"
                #// 3.90.3, 3.93.1
                KnownEncoderValues_[16][58][2][2][0][2][3700] = "--preset phone"
                #// 3.93
                KnownEncoderValues_[16][57][2][1][0][4][5600] = "--preset phone"
                pass
            # end if
            if (php_isset(lambda : KnownEncoderValues_[thisfile_mpeg_audio_lame_["raw"]["abrbitrate_minbitrate"]][thisfile_mpeg_audio_lame_["vbr_quality"]][thisfile_mpeg_audio_lame_["raw"]["vbr_method"]][thisfile_mpeg_audio_lame_["raw"]["noise_shaping"]][thisfile_mpeg_audio_lame_["raw"]["stereo_mode"]][thisfile_mpeg_audio_lame_["ath_type"]][thisfile_mpeg_audio_lame_["lowpass_frequency"]])):
                encoder_options_ = KnownEncoderValues_[thisfile_mpeg_audio_lame_["raw"]["abrbitrate_minbitrate"]][thisfile_mpeg_audio_lame_["vbr_quality"]][thisfile_mpeg_audio_lame_["raw"]["vbr_method"]][thisfile_mpeg_audio_lame_["raw"]["noise_shaping"]][thisfile_mpeg_audio_lame_["raw"]["stereo_mode"]][thisfile_mpeg_audio_lame_["ath_type"]][thisfile_mpeg_audio_lame_["lowpass_frequency"]]
            elif (php_isset(lambda : KnownEncoderValues_["**"][thisfile_mpeg_audio_lame_["vbr_quality"]][thisfile_mpeg_audio_lame_["raw"]["vbr_method"]][thisfile_mpeg_audio_lame_["raw"]["noise_shaping"]][thisfile_mpeg_audio_lame_["raw"]["stereo_mode"]][thisfile_mpeg_audio_lame_["ath_type"]][thisfile_mpeg_audio_lame_["lowpass_frequency"]])):
                encoder_options_ = KnownEncoderValues_["**"][thisfile_mpeg_audio_lame_["vbr_quality"]][thisfile_mpeg_audio_lame_["raw"]["vbr_method"]][thisfile_mpeg_audio_lame_["raw"]["noise_shaping"]][thisfile_mpeg_audio_lame_["raw"]["stereo_mode"]][thisfile_mpeg_audio_lame_["ath_type"]][thisfile_mpeg_audio_lame_["lowpass_frequency"]]
            elif info_["audio"]["bitrate_mode"] == "vbr":
                #// http://gabriel.mp3-tech.org/mp3infotag.html
                #// int    Quality = (100 - 10 * gfp->VBR_q - gfp->quality)h
                LAME_V_value_ = 10 - ceil(thisfile_mpeg_audio_lame_["vbr_quality"] / 10)
                LAME_q_value_ = 100 - thisfile_mpeg_audio_lame_["vbr_quality"] - LAME_V_value_ * 10
                encoder_options_ = "-V" + LAME_V_value_ + " -q" + LAME_q_value_
            elif info_["audio"]["bitrate_mode"] == "cbr":
                encoder_options_ = php_strtoupper(info_["audio"]["bitrate_mode"]) + ceil(info_["audio"]["bitrate"] / 1000)
            else:
                encoder_options_ = php_strtoupper(info_["audio"]["bitrate_mode"])
            # end if
        elif (not php_empty(lambda : thisfile_mpeg_audio_lame_["bitrate_abr"])):
            encoder_options_ = "ABR" + thisfile_mpeg_audio_lame_["bitrate_abr"]
        elif (not php_empty(lambda : info_["audio"]["bitrate"])):
            if info_["audio"]["bitrate_mode"] == "cbr":
                encoder_options_ = php_strtoupper(info_["audio"]["bitrate_mode"]) + ceil(info_["audio"]["bitrate"] / 1000)
            else:
                encoder_options_ = php_strtoupper(info_["audio"]["bitrate_mode"])
            # end if
        # end if
        if (not php_empty(lambda : thisfile_mpeg_audio_lame_["bitrate_min"])):
            encoder_options_ += " -b" + thisfile_mpeg_audio_lame_["bitrate_min"]
        # end if
        if (not php_empty(lambda : thisfile_mpeg_audio_lame_["encoding_flags"]["nogap_prev"])) or (not php_empty(lambda : thisfile_mpeg_audio_lame_["encoding_flags"]["nogap_next"])):
            encoder_options_ += " --nogap"
        # end if
        if (not php_empty(lambda : thisfile_mpeg_audio_lame_["lowpass_frequency"])):
            ExplodedOptions_ = php_explode(" ", encoder_options_, 4)
            if ExplodedOptions_[0] == "--r3mix":
                ExplodedOptions_[1] = "r3mix"
            # end if
            for case in Switch(ExplodedOptions_[0]):
                if case("--preset"):
                    pass
                # end if
                if case("--alt-preset"):
                    pass
                # end if
                if case("--r3mix"):
                    if ExplodedOptions_[1] == "fast":
                        ExplodedOptions_[1] += " " + ExplodedOptions_[2]
                    # end if
                    for case in Switch(ExplodedOptions_[1]):
                        if case("portable"):
                            pass
                        # end if
                        if case("medium"):
                            pass
                        # end if
                        if case("standard"):
                            pass
                        # end if
                        if case("extreme"):
                            pass
                        # end if
                        if case("insane"):
                            pass
                        # end if
                        if case("fast portable"):
                            pass
                        # end if
                        if case("fast medium"):
                            pass
                        # end if
                        if case("fast standard"):
                            pass
                        # end if
                        if case("fast extreme"):
                            pass
                        # end if
                        if case("fast insane"):
                            pass
                        # end if
                        if case("r3mix"):
                            ExpectedLowpass_ = Array({"insane|20500": 20500, "insane|20600": 20600, "medium|18000": 18000, "fast medium|18000": 18000, "extreme|19500": 19500, "extreme|19600": 19600, "fast extreme|19500": 19500, "fast extreme|19600": 19600, "standard|19000": 19000, "fast standard|19000": 19000, "r3mix|19500": 19500, "r3mix|19600": 19600, "r3mix|18000": 18000})
                            if (not (php_isset(lambda : ExpectedLowpass_[ExplodedOptions_[1] + "|" + thisfile_mpeg_audio_lame_["lowpass_frequency"]]))) and thisfile_mpeg_audio_lame_["lowpass_frequency"] < 22050 and round(thisfile_mpeg_audio_lame_["lowpass_frequency"] / 1000) < round(thisfile_mpeg_audio_["sample_rate"] / 2000):
                                encoder_options_ += " --lowpass " + thisfile_mpeg_audio_lame_["lowpass_frequency"]
                            # end if
                            break
                        # end if
                        if case():
                            break
                        # end if
                    # end for
                    break
                # end if
            # end for
        # end if
        if (php_isset(lambda : thisfile_mpeg_audio_lame_["raw"]["source_sample_freq"])):
            if thisfile_mpeg_audio_["sample_rate"] == 44100 and thisfile_mpeg_audio_lame_["raw"]["source_sample_freq"] != 1:
                encoder_options_ += " --resample 44100"
            elif thisfile_mpeg_audio_["sample_rate"] == 48000 and thisfile_mpeg_audio_lame_["raw"]["source_sample_freq"] != 2:
                encoder_options_ += " --resample 48000"
            elif thisfile_mpeg_audio_["sample_rate"] < 44100:
                for case in Switch(thisfile_mpeg_audio_lame_["raw"]["source_sample_freq"]):
                    if case(0):
                        break
                    # end if
                    if case(1):
                        pass
                    # end if
                    if case(2):
                        pass
                    # end if
                    if case(3):
                        #// 48000+
                        ExplodedOptions_ = php_explode(" ", encoder_options_, 4)
                        for case in Switch(ExplodedOptions_[0]):
                            if case("--preset"):
                                pass
                            # end if
                            if case("--alt-preset"):
                                for case in Switch(ExplodedOptions_[1]):
                                    if case("fast"):
                                        pass
                                    # end if
                                    if case("portable"):
                                        pass
                                    # end if
                                    if case("medium"):
                                        pass
                                    # end if
                                    if case("standard"):
                                        pass
                                    # end if
                                    if case("extreme"):
                                        pass
                                    # end if
                                    if case("insane"):
                                        encoder_options_ += " --resample " + thisfile_mpeg_audio_["sample_rate"]
                                        break
                                    # end if
                                    if case():
                                        ExpectedResampledRate_ = Array({"phon+/lw/mw-eu/sw|16000": 16000, "mw-us|24000": 24000, "mw-us|32000": 32000, "mw-us|16000": 16000, "phone|16000": 16000, "phone|11025": 11025, "radio|32000": 32000, "fm/radio|32000": 32000, "fm|32000": 32000, "voice|32000": 32000})
                                        if (not (php_isset(lambda : ExpectedResampledRate_[ExplodedOptions_[1] + "|" + thisfile_mpeg_audio_["sample_rate"]]))):
                                            encoder_options_ += " --resample " + thisfile_mpeg_audio_["sample_rate"]
                                        # end if
                                        break
                                    # end if
                                # end for
                                break
                            # end if
                            if case("--r3mix"):
                                pass
                            # end if
                            if case():
                                encoder_options_ += " --resample " + thisfile_mpeg_audio_["sample_rate"]
                                break
                            # end if
                        # end for
                        break
                    # end if
                # end for
            # end if
        # end if
        if php_empty(lambda : encoder_options_) and (not php_empty(lambda : info_["audio"]["bitrate"])) and (not php_empty(lambda : info_["audio"]["bitrate_mode"])):
            #// $encoder_options = strtoupper($info['audio']['bitrate_mode']).ceil($info['audio']['bitrate'] / 1000);
            encoder_options_ = php_strtoupper(info_["audio"]["bitrate_mode"])
        # end if
        return encoder_options_
    # end def guessencoderoptions
    #// 
    #// @param int   $offset
    #// @param array $info
    #// @param bool  $recursivesearch
    #// @param bool  $ScanAsCBR
    #// @param bool  $FastMPEGheaderScan
    #// 
    #// @return bool
    #//
    def decodempegaudioheader(self, offset_=None, info_=None, recursivesearch_=None, ScanAsCBR_=None, FastMPEGheaderScan_=None):
        if recursivesearch_ is None:
            recursivesearch_ = True
        # end if
        if ScanAsCBR_ is None:
            ScanAsCBR_ = False
        # end if
        if FastMPEGheaderScan_ is None:
            FastMPEGheaderScan_ = False
        # end if
        
        MPEGaudioVersionLookup_ = None
        MPEGaudioLayerLookup_ = None
        MPEGaudioBitrateLookup_ = None
        MPEGaudioFrequencyLookup_ = None
        MPEGaudioChannelModeLookup_ = None
        MPEGaudioModeExtensionLookup_ = None
        MPEGaudioEmphasisLookup_ = None
        if php_empty(lambda : MPEGaudioVersionLookup_):
            MPEGaudioVersionLookup_ = self.mpegaudioversionarray()
            MPEGaudioLayerLookup_ = self.mpegaudiolayerarray()
            MPEGaudioBitrateLookup_ = self.mpegaudiobitratearray()
            MPEGaudioFrequencyLookup_ = self.mpegaudiofrequencyarray()
            MPEGaudioChannelModeLookup_ = self.mpegaudiochannelmodearray()
            MPEGaudioModeExtensionLookup_ = self.mpegaudiomodeextensionarray()
            MPEGaudioEmphasisLookup_ = self.mpegaudioemphasisarray()
        # end if
        if self.fseek(offset_) != 0:
            self.error("decodeMPEGaudioHeader() failed to seek to next offset at " + offset_)
            return False
        # end if
        #// $headerstring = $this->fread(1441); // worst-case max length = 32kHz @ 320kbps layer 3 = 1441 bytes/frame
        headerstring_ = self.fread(226)
        #// LAME header at offset 36 + 190 bytes of Xing/LAME data
        #// MP3 audio frame structure:
        #// $aa $aa $aa $aa [$bb $bb] $cc...
        #// where $aa..$aa is the four-byte mpeg-audio header (below)
        #// $bb $bb is the optional 2-byte CRC
        #// and $cc... is the audio data
        head4_ = php_substr(headerstring_, 0, 4)
        head4_key_ = getid3_lib.printhexbytes(head4_, True, False, False)
        MPEGaudioHeaderDecodeCache_ = Array()
        if (php_isset(lambda : MPEGaudioHeaderDecodeCache_[head4_key_])):
            MPEGheaderRawArray_ = MPEGaudioHeaderDecodeCache_[head4_key_]
        else:
            MPEGheaderRawArray_ = self.mpegaudioheaderdecode(head4_)
            MPEGaudioHeaderDecodeCache_[head4_key_] = MPEGheaderRawArray_
        # end if
        MPEGaudioHeaderValidCache_ = Array()
        if (not (php_isset(lambda : MPEGaudioHeaderValidCache_[head4_key_]))):
            #// Not in cache
            #// $MPEGaudioHeaderValidCache[$head4_key] = self::MPEGaudioHeaderValid($MPEGheaderRawArray, false, true);  // allow badly-formatted freeformat (from LAME 3.90 - 3.93.1)
            MPEGaudioHeaderValidCache_[head4_key_] = self.mpegaudioheadervalid(MPEGheaderRawArray_, False, False)
        # end if
        #// shortcut
        if (not (php_isset(lambda : info_["mpeg"]["audio"]))):
            info_["mpeg"]["audio"] = Array()
        # end if
        thisfile_mpeg_audio_ = info_["mpeg"]["audio"]
        if MPEGaudioHeaderValidCache_[head4_key_]:
            thisfile_mpeg_audio_["raw"] = MPEGheaderRawArray_
        else:
            self.error("Invalid MPEG audio header (" + getid3_lib.printhexbytes(head4_) + ") at offset " + offset_)
            return False
        # end if
        if (not FastMPEGheaderScan_):
            thisfile_mpeg_audio_["version"] = MPEGaudioVersionLookup_[thisfile_mpeg_audio_["raw"]["version"]]
            thisfile_mpeg_audio_["layer"] = MPEGaudioLayerLookup_[thisfile_mpeg_audio_["raw"]["layer"]]
            thisfile_mpeg_audio_["channelmode"] = MPEGaudioChannelModeLookup_[thisfile_mpeg_audio_["raw"]["channelmode"]]
            thisfile_mpeg_audio_["channels"] = 1 if thisfile_mpeg_audio_["channelmode"] == "mono" else 2
            thisfile_mpeg_audio_["sample_rate"] = MPEGaudioFrequencyLookup_[thisfile_mpeg_audio_["version"]][thisfile_mpeg_audio_["raw"]["sample_rate"]]
            thisfile_mpeg_audio_["protection"] = (not thisfile_mpeg_audio_["raw"]["protection"])
            thisfile_mpeg_audio_["private"] = php_bool(thisfile_mpeg_audio_["raw"]["private"])
            thisfile_mpeg_audio_["modeextension"] = MPEGaudioModeExtensionLookup_[thisfile_mpeg_audio_["layer"]][thisfile_mpeg_audio_["raw"]["modeextension"]]
            thisfile_mpeg_audio_["copyright"] = php_bool(thisfile_mpeg_audio_["raw"]["copyright"])
            thisfile_mpeg_audio_["original"] = php_bool(thisfile_mpeg_audio_["raw"]["original"])
            thisfile_mpeg_audio_["emphasis"] = MPEGaudioEmphasisLookup_[thisfile_mpeg_audio_["raw"]["emphasis"]]
            info_["audio"]["channels"] = thisfile_mpeg_audio_["channels"]
            info_["audio"]["sample_rate"] = thisfile_mpeg_audio_["sample_rate"]
            if thisfile_mpeg_audio_["protection"]:
                thisfile_mpeg_audio_["crc"] = getid3_lib.bigendian2int(php_substr(headerstring_, 4, 2))
            # end if
        # end if
        if thisfile_mpeg_audio_["raw"]["bitrate"] == 15:
            #// http://www.hydrogenaudio.org/?act=ST&f=16&t=9682&st=0
            self.warning("Invalid bitrate index (15), this is a known bug in free-format MP3s encoded by LAME v3.90 - 3.93.1")
            thisfile_mpeg_audio_["raw"]["bitrate"] = 0
        # end if
        thisfile_mpeg_audio_["padding"] = php_bool(thisfile_mpeg_audio_["raw"]["padding"])
        thisfile_mpeg_audio_["bitrate"] = MPEGaudioBitrateLookup_[thisfile_mpeg_audio_["version"]][thisfile_mpeg_audio_["layer"]][thisfile_mpeg_audio_["raw"]["bitrate"]]
        if thisfile_mpeg_audio_["bitrate"] == "free" and offset_ == info_["avdataoffset"]:
            #// only skip multiple frame check if free-format bitstream found at beginning of file
            #// otherwise is quite possibly simply corrupted data
            recursivesearch_ = False
        # end if
        #// For Layer 2 there are some combinations of bitrate and mode which are not allowed.
        if (not FastMPEGheaderScan_) and thisfile_mpeg_audio_["layer"] == "2":
            info_["audio"]["dataformat"] = "mp2"
            for case in Switch(thisfile_mpeg_audio_["channelmode"]):
                if case("mono"):
                    if thisfile_mpeg_audio_["bitrate"] == "free" or thisfile_mpeg_audio_["bitrate"] <= 192000:
                        pass
                    else:
                        self.error(thisfile_mpeg_audio_["bitrate"] + "kbps not allowed in Layer 2, " + thisfile_mpeg_audio_["channelmode"] + ".")
                        return False
                    # end if
                    break
                # end if
                if case("stereo"):
                    pass
                # end if
                if case("joint stereo"):
                    pass
                # end if
                if case("dual channel"):
                    if thisfile_mpeg_audio_["bitrate"] == "free" or thisfile_mpeg_audio_["bitrate"] == 64000 or thisfile_mpeg_audio_["bitrate"] >= 96000:
                        pass
                    else:
                        self.error(php_intval(round(thisfile_mpeg_audio_["bitrate"] / 1000)) + "kbps not allowed in Layer 2, " + thisfile_mpeg_audio_["channelmode"] + ".")
                        return False
                    # end if
                    break
                # end if
            # end for
        # end if
        if info_["audio"]["sample_rate"] > 0:
            thisfile_mpeg_audio_["framelength"] = self.mpegaudioframelength(thisfile_mpeg_audio_["bitrate"], thisfile_mpeg_audio_["version"], thisfile_mpeg_audio_["layer"], php_int(thisfile_mpeg_audio_["padding"]), info_["audio"]["sample_rate"])
        # end if
        nextframetestoffset_ = offset_ + 1
        if thisfile_mpeg_audio_["bitrate"] != "free":
            info_["audio"]["bitrate"] = thisfile_mpeg_audio_["bitrate"]
            if (php_isset(lambda : thisfile_mpeg_audio_["framelength"])):
                nextframetestoffset_ = offset_ + thisfile_mpeg_audio_["framelength"]
            else:
                self.error("Frame at offset(" + offset_ + ") is has an invalid frame length.")
                return False
            # end if
        # end if
        ExpectedNumberOfAudioBytes_ = 0
        #// 
        #// Variable-bitrate headers
        if php_substr(headerstring_, 4 + 32, 4) == "VBRI":
            #// Fraunhofer VBR header is hardcoded 'VBRI' at offset 0x24 (36)
            #// specs taken from http://minnie.tuhs.org/pipermail/mp3encoder/2001-January/001800.html
            thisfile_mpeg_audio_["bitrate_mode"] = "vbr"
            thisfile_mpeg_audio_["VBR_method"] = "Fraunhofer"
            info_["audio"]["codec"] = "Fraunhofer"
            SideInfoData_ = php_substr(headerstring_, 4 + 2, 32)
            FraunhoferVBROffset_ = 36
            thisfile_mpeg_audio_["VBR_encoder_version"] = getid3_lib.bigendian2int(php_substr(headerstring_, FraunhoferVBROffset_ + 4, 2))
            #// VbriVersion
            thisfile_mpeg_audio_["VBR_encoder_delay"] = getid3_lib.bigendian2int(php_substr(headerstring_, FraunhoferVBROffset_ + 6, 2))
            #// VbriDelay
            thisfile_mpeg_audio_["VBR_quality"] = getid3_lib.bigendian2int(php_substr(headerstring_, FraunhoferVBROffset_ + 8, 2))
            #// VbriQuality
            thisfile_mpeg_audio_["VBR_bytes"] = getid3_lib.bigendian2int(php_substr(headerstring_, FraunhoferVBROffset_ + 10, 4))
            #// VbriStreamBytes
            thisfile_mpeg_audio_["VBR_frames"] = getid3_lib.bigendian2int(php_substr(headerstring_, FraunhoferVBROffset_ + 14, 4))
            #// VbriStreamFrames
            thisfile_mpeg_audio_["VBR_seek_offsets"] = getid3_lib.bigendian2int(php_substr(headerstring_, FraunhoferVBROffset_ + 18, 2))
            #// VbriTableSize
            thisfile_mpeg_audio_["VBR_seek_scale"] = getid3_lib.bigendian2int(php_substr(headerstring_, FraunhoferVBROffset_ + 20, 2))
            #// VbriTableScale
            thisfile_mpeg_audio_["VBR_entry_bytes"] = getid3_lib.bigendian2int(php_substr(headerstring_, FraunhoferVBROffset_ + 22, 2))
            #// VbriEntryBytes
            thisfile_mpeg_audio_["VBR_entry_frames"] = getid3_lib.bigendian2int(php_substr(headerstring_, FraunhoferVBROffset_ + 24, 2))
            #// VbriEntryFrames
            ExpectedNumberOfAudioBytes_ = thisfile_mpeg_audio_["VBR_bytes"]
            previousbyteoffset_ = offset_
            i_ = 0
            while i_ < thisfile_mpeg_audio_["VBR_seek_offsets"]:
                
                Fraunhofer_OffsetN_ = getid3_lib.bigendian2int(php_substr(headerstring_, FraunhoferVBROffset_, thisfile_mpeg_audio_["VBR_entry_bytes"]))
                FraunhoferVBROffset_ += thisfile_mpeg_audio_["VBR_entry_bytes"]
                thisfile_mpeg_audio_["VBR_offsets_relative"][i_] = Fraunhofer_OffsetN_ * thisfile_mpeg_audio_["VBR_seek_scale"]
                thisfile_mpeg_audio_["VBR_offsets_absolute"][i_] = Fraunhofer_OffsetN_ * thisfile_mpeg_audio_["VBR_seek_scale"] + previousbyteoffset_
                previousbyteoffset_ += Fraunhofer_OffsetN_
                i_ += 1
            # end while
        else:
            #// Xing VBR header is hardcoded 'Xing' at a offset 0x0D (13), 0x15 (21) or 0x24 (36)
            #// depending on MPEG layer and number of channels
            VBRidOffset_ = self.xingvbridoffset(thisfile_mpeg_audio_["version"], thisfile_mpeg_audio_["channelmode"])
            SideInfoData_ = php_substr(headerstring_, 4 + 2, VBRidOffset_ - 4)
            if php_substr(headerstring_, VBRidOffset_, php_strlen("Xing")) == "Xing" or php_substr(headerstring_, VBRidOffset_, php_strlen("Info")) == "Info":
                #// 'Xing' is traditional Xing VBR frame
                #// 'Info' is LAME-encoded CBR (This was done to avoid CBR files to be recognized as traditional Xing VBR files by some decoders.)
                #// 'Info' *can* legally be used to specify a VBR file as well, however.
                #// http://www.multiweb.cz/twoinches/MP3inside.htm
                #// 00..03 = "Xing" or "Info"
                #// 04..07 = Flags:
                #// 0x01  Frames Flag     set if value for number of frames in file is stored
                #// 0x02  Bytes Flag      set if value for filesize in bytes is stored
                #// 0x04  TOC Flag        set if values for TOC are stored
                #// 0x08  VBR Scale Flag  set if values for VBR scale is stored
                #// 08..11  Frames: Number of frames in file (including the first Xing/Info one)
                #// 12..15  Bytes:  File length in Bytes
                #// 16..115  TOC (Table of Contents):
                #// Contains of 100 indexes (one Byte length) for easier lookup in file. Approximately solves problem with moving inside file.
                #// Each Byte has a value according this formula:
                #// (TOC[i] / 256) * fileLenInBytes
                #// So if song lasts eg. 240 sec. and you want to jump to 60. sec. (and file is 5 000 000 Bytes length) you can use:
                #// TOC[(60/240)*100] = TOC[25]
                #// and corresponding Byte in file is then approximately at:
                #// (TOC[25]/256) * 5000000
                #// 116..119  VBR Scale
                #// should be safe to leave this at 'vbr' and let it be overriden to 'cbr' if a CBR preset/mode is used by LAME
                #// if (substr($headerstring, $VBRidOffset, strlen('Info')) == 'Xing') {
                thisfile_mpeg_audio_["bitrate_mode"] = "vbr"
                thisfile_mpeg_audio_["VBR_method"] = "Xing"
                #// } else {
                #// $ScanAsCBR = true;
                #// $thisfile_mpeg_audio['bitrate_mode'] = 'cbr';
                #// }
                thisfile_mpeg_audio_["xing_flags_raw"] = getid3_lib.bigendian2int(php_substr(headerstring_, VBRidOffset_ + 4, 4))
                thisfile_mpeg_audio_["xing_flags"]["frames"] = php_bool(thisfile_mpeg_audio_["xing_flags_raw"] & 1)
                thisfile_mpeg_audio_["xing_flags"]["bytes"] = php_bool(thisfile_mpeg_audio_["xing_flags_raw"] & 2)
                thisfile_mpeg_audio_["xing_flags"]["toc"] = php_bool(thisfile_mpeg_audio_["xing_flags_raw"] & 4)
                thisfile_mpeg_audio_["xing_flags"]["vbr_scale"] = php_bool(thisfile_mpeg_audio_["xing_flags_raw"] & 8)
                if thisfile_mpeg_audio_["xing_flags"]["frames"]:
                    thisfile_mpeg_audio_["VBR_frames"] = getid3_lib.bigendian2int(php_substr(headerstring_, VBRidOffset_ + 8, 4))
                    pass
                # end if
                if thisfile_mpeg_audio_["xing_flags"]["bytes"]:
                    thisfile_mpeg_audio_["VBR_bytes"] = getid3_lib.bigendian2int(php_substr(headerstring_, VBRidOffset_ + 12, 4))
                # end if
                #// if (($thisfile_mpeg_audio['bitrate'] == 'free') && !empty($thisfile_mpeg_audio['VBR_frames']) && !empty($thisfile_mpeg_audio['VBR_bytes'])) {
                #// if (!empty($thisfile_mpeg_audio['VBR_frames']) && !empty($thisfile_mpeg_audio['VBR_bytes'])) {
                if (not php_empty(lambda : thisfile_mpeg_audio_["VBR_frames"])):
                    used_filesize_ = 0
                    if (not php_empty(lambda : thisfile_mpeg_audio_["VBR_bytes"])):
                        used_filesize_ = thisfile_mpeg_audio_["VBR_bytes"]
                    elif (not php_empty(lambda : info_["filesize"])):
                        used_filesize_ = info_["filesize"]
                        used_filesize_ -= php_intval(info_["id3v2"]["headerlength"]) if (php_isset(lambda : info_["id3v2"]["headerlength"])) else 0
                        used_filesize_ -= 128 if (php_isset(lambda : info_["id3v1"])) else 0
                        used_filesize_ -= info_["tag_offset_end"] - info_["tag_offset_start"] if (php_isset(lambda : info_["tag_offset_end"])) else 0
                        self.warning("MP3.Xing header missing VBR_bytes, assuming MPEG audio portion of file is " + number_format(used_filesize_) + " bytes")
                    # end if
                    framelengthfloat_ = used_filesize_ / thisfile_mpeg_audio_["VBR_frames"]
                    if thisfile_mpeg_audio_["layer"] == "1":
                        #// BitRate = (((FrameLengthInBytes / 4) - Padding) * SampleRate) / 12
                        #// $info['audio']['bitrate'] = ((($framelengthfloat / 4) - intval($thisfile_mpeg_audio['padding'])) * $thisfile_mpeg_audio['sample_rate']) / 12;
                        info_["audio"]["bitrate"] = framelengthfloat_ / 4 * thisfile_mpeg_audio_["sample_rate"] * 2 / info_["audio"]["channels"] / 12
                    else:
                        #// Bitrate = ((FrameLengthInBytes - Padding) * SampleRate) / 144
                        #// $info['audio']['bitrate'] = (($framelengthfloat - intval($thisfile_mpeg_audio['padding'])) * $thisfile_mpeg_audio['sample_rate']) / 144;
                        info_["audio"]["bitrate"] = framelengthfloat_ * thisfile_mpeg_audio_["sample_rate"] * 2 / info_["audio"]["channels"] / 144
                    # end if
                    thisfile_mpeg_audio_["framelength"] = floor(framelengthfloat_)
                # end if
                if thisfile_mpeg_audio_["xing_flags"]["toc"]:
                    LAMEtocData_ = php_substr(headerstring_, VBRidOffset_ + 16, 100)
                    i_ = 0
                    while i_ < 100:
                        
                        thisfile_mpeg_audio_["toc"][i_] = php_ord(LAMEtocData_[i_])
                        i_ += 1
                    # end while
                # end if
                if thisfile_mpeg_audio_["xing_flags"]["vbr_scale"]:
                    thisfile_mpeg_audio_["VBR_scale"] = getid3_lib.bigendian2int(php_substr(headerstring_, VBRidOffset_ + 116, 4))
                # end if
                #// http://gabriel.mp3-tech.org/mp3infotag.html
                if php_substr(headerstring_, VBRidOffset_ + 120, 4) == "LAME":
                    #// shortcut
                    thisfile_mpeg_audio_["LAME"] = Array()
                    thisfile_mpeg_audio_lame_ = thisfile_mpeg_audio_["LAME"]
                    thisfile_mpeg_audio_lame_["long_version"] = php_substr(headerstring_, VBRidOffset_ + 120, 20)
                    thisfile_mpeg_audio_lame_["short_version"] = php_substr(thisfile_mpeg_audio_lame_["long_version"], 0, 9)
                    if thisfile_mpeg_audio_lame_["short_version"] >= "LAME3.90":
                        thisfile_mpeg_audio_lame_["long_version"] = None
                        #// It the LAME tag was only introduced in LAME v3.90
                        #// http://www.hydrogenaudio.org/?act=ST&f=15&t=9933
                        #// Offsets of various bytes in http://gabriel.mp3-tech.org/mp3infotag.html
                        #// are assuming a 'Xing' identifier offset of 0x24, which is the case for
                        #// MPEG-1 non-mono, but not for other combinations
                        LAMEtagOffsetContant_ = VBRidOffset_ - 36
                        #// shortcuts
                        thisfile_mpeg_audio_lame_["RGAD"] = Array({"track": Array(), "album": Array()})
                        thisfile_mpeg_audio_lame_RGAD_ = thisfile_mpeg_audio_lame_["RGAD"]
                        thisfile_mpeg_audio_lame_RGAD_track_ = thisfile_mpeg_audio_lame_RGAD_["track"]
                        thisfile_mpeg_audio_lame_RGAD_album_ = thisfile_mpeg_audio_lame_RGAD_["album"]
                        thisfile_mpeg_audio_lame_["raw"] = Array()
                        thisfile_mpeg_audio_lame_raw_ = thisfile_mpeg_audio_lame_["raw"]
                        thisfile_mpeg_audio_["VBR_scale"] = None
                        thisfile_mpeg_audio_lame_["vbr_quality"] = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 155, 1))
                        #// bytes $9C-$A4  Encoder short VersionString
                        thisfile_mpeg_audio_lame_["short_version"] = php_substr(headerstring_, LAMEtagOffsetContant_ + 156, 9)
                        #// byte $A5  Info Tag revision + VBR method
                        LAMEtagRevisionVBRmethod_ = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 165, 1))
                        thisfile_mpeg_audio_lame_["tag_revision"] = LAMEtagRevisionVBRmethod_ & 240 >> 4
                        thisfile_mpeg_audio_lame_raw_["vbr_method"] = LAMEtagRevisionVBRmethod_ & 15
                        thisfile_mpeg_audio_lame_["vbr_method"] = self.lamevbrmethodlookup(thisfile_mpeg_audio_lame_raw_["vbr_method"])
                        thisfile_mpeg_audio_["bitrate_mode"] = php_substr(thisfile_mpeg_audio_lame_["vbr_method"], 0, 3)
                        #// usually either 'cbr' or 'vbr', but truncates 'vbr-old / vbr-rh' to 'vbr'
                        #// byte $A6  Lowpass filter value
                        thisfile_mpeg_audio_lame_["lowpass_frequency"] = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 166, 1)) * 100
                        #// bytes $A7-$AE  Replay Gain
                        #// http://privatewww.essex.ac.uk/~djmrob/replaygain/rg_data_format.html
                        #// bytes $A7-$AA : 32 bit floating point "Peak signal amplitude"
                        if thisfile_mpeg_audio_lame_["short_version"] >= "LAME3.94b":
                            #// LAME 3.94a16 and later - 9.23 fixed point
                            #// ie 0x0059E2EE / (2^23) = 5890798 / 8388608 = 0.7022378444671630859375
                            thisfile_mpeg_audio_lame_RGAD_["peak_amplitude"] = php_float(getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 167, 4)) / 8388608)
                        else:
                            #// LAME 3.94a15 and earlier - 32-bit floating point
                            #// Actually 3.94a16 will fall in here too and be WRONG, but is hard to detect 3.94a16 vs 3.94a15
                            thisfile_mpeg_audio_lame_RGAD_["peak_amplitude"] = getid3_lib.littleendian2float(php_substr(headerstring_, LAMEtagOffsetContant_ + 167, 4))
                        # end if
                        if thisfile_mpeg_audio_lame_RGAD_["peak_amplitude"] == 0:
                            thisfile_mpeg_audio_lame_RGAD_["peak_amplitude"] = None
                        else:
                            thisfile_mpeg_audio_lame_RGAD_["peak_db"] = getid3_lib.rgadamplitude2db(thisfile_mpeg_audio_lame_RGAD_["peak_amplitude"])
                        # end if
                        thisfile_mpeg_audio_lame_raw_["RGAD_track"] = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 171, 2))
                        thisfile_mpeg_audio_lame_raw_["RGAD_album"] = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 173, 2))
                        if thisfile_mpeg_audio_lame_raw_["RGAD_track"] != 0:
                            thisfile_mpeg_audio_lame_RGAD_track_["raw"]["name"] = thisfile_mpeg_audio_lame_raw_["RGAD_track"] & 57344 >> 13
                            thisfile_mpeg_audio_lame_RGAD_track_["raw"]["originator"] = thisfile_mpeg_audio_lame_raw_["RGAD_track"] & 7168 >> 10
                            thisfile_mpeg_audio_lame_RGAD_track_["raw"]["sign_bit"] = thisfile_mpeg_audio_lame_raw_["RGAD_track"] & 512 >> 9
                            thisfile_mpeg_audio_lame_RGAD_track_["raw"]["gain_adjust"] = thisfile_mpeg_audio_lame_raw_["RGAD_track"] & 511
                            thisfile_mpeg_audio_lame_RGAD_track_["name"] = getid3_lib.rgadnamelookup(thisfile_mpeg_audio_lame_RGAD_track_["raw"]["name"])
                            thisfile_mpeg_audio_lame_RGAD_track_["originator"] = getid3_lib.rgadoriginatorlookup(thisfile_mpeg_audio_lame_RGAD_track_["raw"]["originator"])
                            thisfile_mpeg_audio_lame_RGAD_track_["gain_db"] = getid3_lib.rgadadjustmentlookup(thisfile_mpeg_audio_lame_RGAD_track_["raw"]["gain_adjust"], thisfile_mpeg_audio_lame_RGAD_track_["raw"]["sign_bit"])
                            if (not php_empty(lambda : thisfile_mpeg_audio_lame_RGAD_["peak_amplitude"])):
                                info_["replay_gain"]["track"]["peak"] = thisfile_mpeg_audio_lame_RGAD_["peak_amplitude"]
                            # end if
                            info_["replay_gain"]["track"]["originator"] = thisfile_mpeg_audio_lame_RGAD_track_["originator"]
                            info_["replay_gain"]["track"]["adjustment"] = thisfile_mpeg_audio_lame_RGAD_track_["gain_db"]
                        else:
                            thisfile_mpeg_audio_lame_RGAD_["track"] = None
                        # end if
                        if thisfile_mpeg_audio_lame_raw_["RGAD_album"] != 0:
                            thisfile_mpeg_audio_lame_RGAD_album_["raw"]["name"] = thisfile_mpeg_audio_lame_raw_["RGAD_album"] & 57344 >> 13
                            thisfile_mpeg_audio_lame_RGAD_album_["raw"]["originator"] = thisfile_mpeg_audio_lame_raw_["RGAD_album"] & 7168 >> 10
                            thisfile_mpeg_audio_lame_RGAD_album_["raw"]["sign_bit"] = thisfile_mpeg_audio_lame_raw_["RGAD_album"] & 512 >> 9
                            thisfile_mpeg_audio_lame_RGAD_album_["raw"]["gain_adjust"] = thisfile_mpeg_audio_lame_raw_["RGAD_album"] & 511
                            thisfile_mpeg_audio_lame_RGAD_album_["name"] = getid3_lib.rgadnamelookup(thisfile_mpeg_audio_lame_RGAD_album_["raw"]["name"])
                            thisfile_mpeg_audio_lame_RGAD_album_["originator"] = getid3_lib.rgadoriginatorlookup(thisfile_mpeg_audio_lame_RGAD_album_["raw"]["originator"])
                            thisfile_mpeg_audio_lame_RGAD_album_["gain_db"] = getid3_lib.rgadadjustmentlookup(thisfile_mpeg_audio_lame_RGAD_album_["raw"]["gain_adjust"], thisfile_mpeg_audio_lame_RGAD_album_["raw"]["sign_bit"])
                            if (not php_empty(lambda : thisfile_mpeg_audio_lame_RGAD_["peak_amplitude"])):
                                info_["replay_gain"]["album"]["peak"] = thisfile_mpeg_audio_lame_RGAD_["peak_amplitude"]
                            # end if
                            info_["replay_gain"]["album"]["originator"] = thisfile_mpeg_audio_lame_RGAD_album_["originator"]
                            info_["replay_gain"]["album"]["adjustment"] = thisfile_mpeg_audio_lame_RGAD_album_["gain_db"]
                        else:
                            thisfile_mpeg_audio_lame_RGAD_["album"] = None
                        # end if
                        if php_empty(lambda : thisfile_mpeg_audio_lame_RGAD_):
                            thisfile_mpeg_audio_lame_["RGAD"] = None
                        # end if
                        #// byte $AF  Encoding flags + ATH Type
                        EncodingFlagsATHtype_ = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 175, 1))
                        thisfile_mpeg_audio_lame_["encoding_flags"]["nspsytune"] = php_bool(EncodingFlagsATHtype_ & 16)
                        thisfile_mpeg_audio_lame_["encoding_flags"]["nssafejoint"] = php_bool(EncodingFlagsATHtype_ & 32)
                        thisfile_mpeg_audio_lame_["encoding_flags"]["nogap_next"] = php_bool(EncodingFlagsATHtype_ & 64)
                        thisfile_mpeg_audio_lame_["encoding_flags"]["nogap_prev"] = php_bool(EncodingFlagsATHtype_ & 128)
                        thisfile_mpeg_audio_lame_["ath_type"] = EncodingFlagsATHtype_ & 15
                        #// byte $B0  if ABR {specified bitrate} else {minimal bitrate}
                        thisfile_mpeg_audio_lame_["raw"]["abrbitrate_minbitrate"] = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 176, 1))
                        if thisfile_mpeg_audio_lame_raw_["vbr_method"] == 2:
                            #// Average BitRate (ABR)
                            thisfile_mpeg_audio_lame_["bitrate_abr"] = thisfile_mpeg_audio_lame_["raw"]["abrbitrate_minbitrate"]
                        elif thisfile_mpeg_audio_lame_raw_["vbr_method"] == 1:
                            pass
                        elif thisfile_mpeg_audio_lame_["raw"]["abrbitrate_minbitrate"] > 0:
                            #// Variable BitRate (VBR) - minimum bitrate
                            thisfile_mpeg_audio_lame_["bitrate_min"] = thisfile_mpeg_audio_lame_["raw"]["abrbitrate_minbitrate"]
                        # end if
                        #// bytes $B1-$B3  Encoder delays
                        EncoderDelays_ = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 177, 3))
                        thisfile_mpeg_audio_lame_["encoder_delay"] = EncoderDelays_ & 16773120 >> 12
                        thisfile_mpeg_audio_lame_["end_padding"] = EncoderDelays_ & 4095
                        #// byte $B4  Misc
                        MiscByte_ = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 180, 1))
                        thisfile_mpeg_audio_lame_raw_["noise_shaping"] = MiscByte_ & 3
                        thisfile_mpeg_audio_lame_raw_["stereo_mode"] = MiscByte_ & 28 >> 2
                        thisfile_mpeg_audio_lame_raw_["not_optimal_quality"] = MiscByte_ & 32 >> 5
                        thisfile_mpeg_audio_lame_raw_["source_sample_freq"] = MiscByte_ & 192 >> 6
                        thisfile_mpeg_audio_lame_["noise_shaping"] = thisfile_mpeg_audio_lame_raw_["noise_shaping"]
                        thisfile_mpeg_audio_lame_["stereo_mode"] = self.lamemiscstereomodelookup(thisfile_mpeg_audio_lame_raw_["stereo_mode"])
                        thisfile_mpeg_audio_lame_["not_optimal_quality"] = php_bool(thisfile_mpeg_audio_lame_raw_["not_optimal_quality"])
                        thisfile_mpeg_audio_lame_["source_sample_freq"] = self.lamemiscsourcesamplefrequencylookup(thisfile_mpeg_audio_lame_raw_["source_sample_freq"])
                        #// byte $B5  MP3 Gain
                        thisfile_mpeg_audio_lame_raw_["mp3_gain"] = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 181, 1), False, True)
                        thisfile_mpeg_audio_lame_["mp3_gain_db"] = getid3_lib.rgadamplitude2db(2) / 4 * thisfile_mpeg_audio_lame_raw_["mp3_gain"]
                        thisfile_mpeg_audio_lame_["mp3_gain_factor"] = pow(2, thisfile_mpeg_audio_lame_["mp3_gain_db"] / 6)
                        #// bytes $B6-$B7  Preset and surround info
                        PresetSurroundBytes_ = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 182, 2))
                        #// Reserved                                                    = ($PresetSurroundBytes & 0xC000);
                        thisfile_mpeg_audio_lame_raw_["surround_info"] = PresetSurroundBytes_ & 14336
                        thisfile_mpeg_audio_lame_["surround_info"] = self.lamesurroundinfolookup(thisfile_mpeg_audio_lame_raw_["surround_info"])
                        thisfile_mpeg_audio_lame_["preset_used_id"] = PresetSurroundBytes_ & 2047
                        thisfile_mpeg_audio_lame_["preset_used"] = self.lamepresetusedlookup(thisfile_mpeg_audio_lame_)
                        if (not php_empty(lambda : thisfile_mpeg_audio_lame_["preset_used_id"])) and php_empty(lambda : thisfile_mpeg_audio_lame_["preset_used"]):
                            self.warning("Unknown LAME preset used (" + thisfile_mpeg_audio_lame_["preset_used_id"] + ") - please report to info@getid3.org")
                        # end if
                        if thisfile_mpeg_audio_lame_["short_version"] == "LAME3.90." and (not php_empty(lambda : thisfile_mpeg_audio_lame_["preset_used_id"])):
                            #// this may change if 3.90.4 ever comes out
                            thisfile_mpeg_audio_lame_["short_version"] = "LAME3.90.3"
                        # end if
                        #// bytes $B8-$BB  MusicLength
                        thisfile_mpeg_audio_lame_["audio_bytes"] = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 184, 4))
                        ExpectedNumberOfAudioBytes_ = thisfile_mpeg_audio_lame_["audio_bytes"] if thisfile_mpeg_audio_lame_["audio_bytes"] > 0 else thisfile_mpeg_audio_["VBR_bytes"]
                        #// bytes $BC-$BD  MusicCRC
                        thisfile_mpeg_audio_lame_["music_crc"] = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 188, 2))
                        #// bytes $BE-$BF  CRC-16 of Info Tag
                        thisfile_mpeg_audio_lame_["lame_tag_crc"] = getid3_lib.bigendian2int(php_substr(headerstring_, LAMEtagOffsetContant_ + 190, 2))
                        #// LAME CBR
                        if thisfile_mpeg_audio_lame_raw_["vbr_method"] == 1:
                            thisfile_mpeg_audio_["bitrate_mode"] = "cbr"
                            thisfile_mpeg_audio_["bitrate"] = self.closeststandardmp3bitrate(thisfile_mpeg_audio_["bitrate"])
                            info_["audio"]["bitrate"] = thisfile_mpeg_audio_["bitrate"]
                            pass
                        # end if
                    # end if
                # end if
            else:
                #// not Fraunhofer or Xing VBR methods, most likely CBR (but could be VBR with no header)
                thisfile_mpeg_audio_["bitrate_mode"] = "cbr"
                if recursivesearch_:
                    thisfile_mpeg_audio_["bitrate_mode"] = "vbr"
                    if self.recursiveframescanning(offset_, nextframetestoffset_, True):
                        recursivesearch_ = False
                        thisfile_mpeg_audio_["bitrate_mode"] = "cbr"
                    # end if
                    if thisfile_mpeg_audio_["bitrate_mode"] == "vbr":
                        self.warning("VBR file with no VBR header. Bitrate values calculated from actual frame bitrates.")
                    # end if
                # end if
            # end if
        # end if
        if ExpectedNumberOfAudioBytes_ > 0 and ExpectedNumberOfAudioBytes_ != info_["avdataend"] - info_["avdataoffset"]:
            if ExpectedNumberOfAudioBytes_ > info_["avdataend"] - info_["avdataoffset"]:
                if self.isdependencyfor("matroska") or self.isdependencyfor("riff"):
                    pass
                elif ExpectedNumberOfAudioBytes_ - info_["avdataend"] - info_["avdataoffset"] == 1:
                    self.warning("Last byte of data truncated (this is a known bug in Meracl ID3 Tag Writer before v1.3.5)")
                else:
                    self.warning("Probable truncated file: expecting " + ExpectedNumberOfAudioBytes_ + " bytes of audio data, only found " + info_["avdataend"] - info_["avdataoffset"] + " (short by " + ExpectedNumberOfAudioBytes_ - info_["avdataend"] - info_["avdataoffset"] + " bytes)")
                # end if
            else:
                if info_["avdataend"] - info_["avdataoffset"] - ExpectedNumberOfAudioBytes_ == 1:
                    #// $prenullbytefileoffset = $this->ftell();
                    #// $this->fseek($info['avdataend']);
                    #// $PossibleNullByte = $this->fread(1);
                    #// $this->fseek($prenullbytefileoffset);
                    #// if ($PossibleNullByte === "\x00") {
                    info_["avdataend"] -= 1
                    pass
                else:
                    self.warning("Too much data in file: expecting " + ExpectedNumberOfAudioBytes_ + " bytes of audio data, found " + info_["avdataend"] - info_["avdataoffset"] + " (" + info_["avdataend"] - info_["avdataoffset"] - ExpectedNumberOfAudioBytes_ + " bytes too many)")
                # end if
            # end if
        # end if
        if thisfile_mpeg_audio_["bitrate"] == "free" and php_empty(lambda : info_["audio"]["bitrate"]):
            if offset_ == info_["avdataoffset"] and php_empty(lambda : thisfile_mpeg_audio_["VBR_frames"]):
                framebytelength_ = self.freeformatframelength(offset_, True)
                if framebytelength_ > 0:
                    thisfile_mpeg_audio_["framelength"] = framebytelength_
                    if thisfile_mpeg_audio_["layer"] == "1":
                        #// BitRate = (((FrameLengthInBytes / 4) - Padding) * SampleRate) / 12
                        info_["audio"]["bitrate"] = framebytelength_ / 4 - php_intval(thisfile_mpeg_audio_["padding"]) * thisfile_mpeg_audio_["sample_rate"] / 12
                    else:
                        #// Bitrate = ((FrameLengthInBytes - Padding) * SampleRate) / 144
                        info_["audio"]["bitrate"] = framebytelength_ - php_intval(thisfile_mpeg_audio_["padding"]) * thisfile_mpeg_audio_["sample_rate"] / 144
                    # end if
                else:
                    self.error("Error calculating frame length of free-format MP3 without Xing/LAME header")
                # end if
            # end if
        # end if
        if thisfile_mpeg_audio_["VBR_frames"] if (php_isset(lambda : thisfile_mpeg_audio_["VBR_frames"])) else "":
            for case in Switch(thisfile_mpeg_audio_["bitrate_mode"]):
                if case("vbr"):
                    pass
                # end if
                if case("abr"):
                    bytes_per_frame_ = 1152
                    if thisfile_mpeg_audio_["version"] == "1" and thisfile_mpeg_audio_["layer"] == 1:
                        bytes_per_frame_ = 384
                    elif thisfile_mpeg_audio_["version"] == "2" or thisfile_mpeg_audio_["version"] == "2.5" and thisfile_mpeg_audio_["layer"] == 3:
                        bytes_per_frame_ = 576
                    # end if
                    thisfile_mpeg_audio_["VBR_bitrate"] = thisfile_mpeg_audio_["VBR_bytes"] / thisfile_mpeg_audio_["VBR_frames"] * 8 * info_["audio"]["sample_rate"] / bytes_per_frame_ if (php_isset(lambda : thisfile_mpeg_audio_["VBR_bytes"])) else 0
                    if thisfile_mpeg_audio_["VBR_bitrate"] > 0:
                        info_["audio"]["bitrate"] = thisfile_mpeg_audio_["VBR_bitrate"]
                        thisfile_mpeg_audio_["bitrate"] = thisfile_mpeg_audio_["VBR_bitrate"]
                        pass
                    # end if
                    break
                # end if
            # end for
        # end if
        #// End variable-bitrate headers
        #//
        if recursivesearch_:
            if (not self.recursiveframescanning(offset_, nextframetestoffset_, ScanAsCBR_)):
                return False
            # end if
        # end if
        #// if (false) {
        #// experimental side info parsing section - not returning anything useful yet
        #// 
        #// $SideInfoBitstream = getid3_lib::BigEndian2Bin($SideInfoData);
        #// $SideInfoOffset = 0;
        #// 
        #// if ($thisfile_mpeg_audio['version'] == '1') {
        #// if ($thisfile_mpeg_audio['channelmode'] == 'mono') {
        #// MPEG-1 (mono)
        #// $thisfile_mpeg_audio['side_info']['main_data_begin'] = substr($SideInfoBitstream, $SideInfoOffset, 9);
        #// $SideInfoOffset += 9;
        #// $SideInfoOffset += 5;
        #// } else {
        #// MPEG-1 (stereo, joint-stereo, dual-channel)
        #// $thisfile_mpeg_audio['side_info']['main_data_begin'] = substr($SideInfoBitstream, $SideInfoOffset, 9);
        #// $SideInfoOffset += 9;
        #// $SideInfoOffset += 3;
        #// }
        #// } else { // 2 or 2.5
        #// if ($thisfile_mpeg_audio['channelmode'] == 'mono') {
        #// MPEG-2, MPEG-2.5 (mono)
        #// $thisfile_mpeg_audio['side_info']['main_data_begin'] = substr($SideInfoBitstream, $SideInfoOffset, 8);
        #// $SideInfoOffset += 8;
        #// $SideInfoOffset += 1;
        #// } else {
        #// MPEG-2, MPEG-2.5 (stereo, joint-stereo, dual-channel)
        #// $thisfile_mpeg_audio['side_info']['main_data_begin'] = substr($SideInfoBitstream, $SideInfoOffset, 8);
        #// $SideInfoOffset += 8;
        #// $SideInfoOffset += 2;
        #// }
        #// }
        #// 
        #// if ($thisfile_mpeg_audio['version'] == '1') {
        #// for ($channel = 0; $channel < $info['audio']['channels']; $channel++) {
        #// for ($scfsi_band = 0; $scfsi_band < 4; $scfsi_band++) {
        #// $thisfile_mpeg_audio['scfsi'][$channel][$scfsi_band] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 2;
        #// }
        #// }
        #// }
        #// for ($granule = 0; $granule < (($thisfile_mpeg_audio['version'] == '1') ? 2 : 1); $granule++) {
        #// for ($channel = 0; $channel < $info['audio']['channels']; $channel++) {
        #// $thisfile_mpeg_audio['part2_3_length'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 12);
        #// $SideInfoOffset += 12;
        #// $thisfile_mpeg_audio['big_values'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 9);
        #// $SideInfoOffset += 9;
        #// $thisfile_mpeg_audio['global_gain'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 8);
        #// $SideInfoOffset += 8;
        #// if ($thisfile_mpeg_audio['version'] == '1') {
        #// $thisfile_mpeg_audio['scalefac_compress'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 4);
        #// $SideInfoOffset += 4;
        #// } else {
        #// $thisfile_mpeg_audio['scalefac_compress'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 9);
        #// $SideInfoOffset += 9;
        #// }
        #// $thisfile_mpeg_audio['window_switching_flag'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 1;
        #// 
        #// if ($thisfile_mpeg_audio['window_switching_flag'][$granule][$channel] == '1') {
        #// 
        #// $thisfile_mpeg_audio['block_type'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 2);
        #// $SideInfoOffset += 2;
        #// $thisfile_mpeg_audio['mixed_block_flag'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 1;
        #// 
        #// for ($region = 0; $region < 2; $region++) {
        #// $thisfile_mpeg_audio['table_select'][$granule][$channel][$region] = substr($SideInfoBitstream, $SideInfoOffset, 5);
        #// $SideInfoOffset += 5;
        #// }
        #// $thisfile_mpeg_audio['table_select'][$granule][$channel][2] = 0;
        #// 
        #// for ($window = 0; $window < 3; $window++) {
        #// $thisfile_mpeg_audio['subblock_gain'][$granule][$channel][$window] = substr($SideInfoBitstream, $SideInfoOffset, 3);
        #// $SideInfoOffset += 3;
        #// }
        #// 
        #// } else {
        #// 
        #// for ($region = 0; $region < 3; $region++) {
        #// $thisfile_mpeg_audio['table_select'][$granule][$channel][$region] = substr($SideInfoBitstream, $SideInfoOffset, 5);
        #// $SideInfoOffset += 5;
        #// }
        #// 
        #// $thisfile_mpeg_audio['region0_count'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 4);
        #// $SideInfoOffset += 4;
        #// $thisfile_mpeg_audio['region1_count'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 3);
        #// $SideInfoOffset += 3;
        #// $thisfile_mpeg_audio['block_type'][$granule][$channel] = 0;
        #// }
        #// 
        #// if ($thisfile_mpeg_audio['version'] == '1') {
        #// $thisfile_mpeg_audio['preflag'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 1;
        #// }
        #// $thisfile_mpeg_audio['scalefac_scale'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 1;
        #// $thisfile_mpeg_audio['count1table_select'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 1;
        #// }
        #// }
        #// }
        return True
    # end def decodempegaudioheader
    #// 
    #// @param int $offset
    #// @param int $nextframetestoffset
    #// @param bool $ScanAsCBR
    #// 
    #// @return bool
    #//
    def recursiveframescanning(self, offset_=None, nextframetestoffset_=None, ScanAsCBR_=None):
        
        
        info_ = self.getid3.info
        firstframetestarray_ = Array({"error": Array(), "warning": Array(), "avdataend": info_["avdataend"], "avdataoffset": info_["avdataoffset"]})
        self.decodempegaudioheader(offset_, firstframetestarray_, False)
        i_ = 0
        while i_ < GETID3_MP3_VALID_CHECK_FRAMES:
            
            #// check next GETID3_MP3_VALID_CHECK_FRAMES frames for validity, to make sure we haven't run across a false synch
            if nextframetestoffset_ + 4 >= info_["avdataend"]:
                #// end of file
                return True
            # end if
            nextframetestarray_ = Array({"error": Array(), "warning": Array(), "avdataend": info_["avdataend"], "avdataoffset": info_["avdataoffset"]})
            if self.decodempegaudioheader(nextframetestoffset_, nextframetestarray_, False):
                if ScanAsCBR_:
                    #// force CBR mode, used for trying to pick out invalid audio streams with valid(?) VBR headers, or VBR streams with no VBR header
                    if (not (php_isset(lambda : nextframetestarray_["mpeg"]["audio"]["bitrate"]))) or (not (php_isset(lambda : firstframetestarray_["mpeg"]["audio"]["bitrate"]))) or nextframetestarray_["mpeg"]["audio"]["bitrate"] != firstframetestarray_["mpeg"]["audio"]["bitrate"]:
                        return False
                    # end if
                # end if
                #// next frame is OK, get ready to check the one after that
                if (php_isset(lambda : nextframetestarray_["mpeg"]["audio"]["framelength"])) and nextframetestarray_["mpeg"]["audio"]["framelength"] > 0:
                    nextframetestoffset_ += nextframetestarray_["mpeg"]["audio"]["framelength"]
                else:
                    self.error("Frame at offset (" + offset_ + ") is has an invalid frame length.")
                    return False
                # end if
            elif (not php_empty(lambda : firstframetestarray_["mpeg"]["audio"]["framelength"])) and nextframetestoffset_ + firstframetestarray_["mpeg"]["audio"]["framelength"] > info_["avdataend"]:
                #// it's not the end of the file, but there's not enough data left for another frame, so assume it's garbage/padding and return OK
                return True
            else:
                #// next frame is not valid, note the error and fail, so scanning can contiue for a valid frame sequence
                self.warning("Frame at offset (" + offset_ + ") is valid, but the next one at (" + nextframetestoffset_ + ") is not.")
                return False
            # end if
            i_ += 1
        # end while
        return True
    # end def recursiveframescanning
    #// 
    #// @param int  $offset
    #// @param bool $deepscan
    #// 
    #// @return int|false
    #//
    def freeformatframelength(self, offset_=None, deepscan_=None):
        if deepscan_ is None:
            deepscan_ = False
        # end if
        
        info_ = self.getid3.info
        self.fseek(offset_)
        MPEGaudioData_ = self.fread(32768)
        SyncPattern1_ = php_substr(MPEGaudioData_, 0, 4)
        #// may be different pattern due to padding
        SyncPattern2_ = SyncPattern1_[0] + SyncPattern1_[1] + chr(php_ord(SyncPattern1_[2]) | 2) + SyncPattern1_[3]
        if SyncPattern2_ == SyncPattern1_:
            SyncPattern2_ = SyncPattern1_[0] + SyncPattern1_[1] + chr(php_ord(SyncPattern1_[2]) & 253) + SyncPattern1_[3]
        # end if
        framelength_ = False
        framelength1_ = php_strpos(MPEGaudioData_, SyncPattern1_, 4)
        framelength2_ = php_strpos(MPEGaudioData_, SyncPattern2_, 4)
        if framelength1_ > 4:
            framelength_ = framelength1_
        # end if
        if framelength2_ > 4 and framelength2_ < framelength1_:
            framelength_ = framelength2_
        # end if
        if (not framelength_):
            #// LAME 3.88 has a different value for modeextension on the first frame vs the rest
            framelength1_ = php_strpos(MPEGaudioData_, php_substr(SyncPattern1_, 0, 3), 4)
            framelength2_ = php_strpos(MPEGaudioData_, php_substr(SyncPattern2_, 0, 3), 4)
            if framelength1_ > 4:
                framelength_ = framelength1_
            # end if
            if framelength2_ > 4 and framelength2_ < framelength1_:
                framelength_ = framelength2_
            # end if
            if (not framelength_):
                self.error("Cannot find next free-format synch pattern (" + getid3_lib.printhexbytes(SyncPattern1_) + " or " + getid3_lib.printhexbytes(SyncPattern2_) + ") after offset " + offset_)
                return False
            else:
                self.warning("ModeExtension varies between first frame and other frames (known free-format issue in LAME 3.88)")
                info_["audio"]["codec"] = "LAME"
                info_["audio"]["encoder"] = "LAME3.88"
                SyncPattern1_ = php_substr(SyncPattern1_, 0, 3)
                SyncPattern2_ = php_substr(SyncPattern2_, 0, 3)
            # end if
        # end if
        if deepscan_:
            ActualFrameLengthValues_ = Array()
            nextoffset_ = offset_ + framelength_
            while True:
                
                if not (nextoffset_ < info_["avdataend"] - 6):
                    break
                # end if
                self.fseek(nextoffset_ - 1)
                NextSyncPattern_ = self.fread(6)
                if php_substr(NextSyncPattern_, 1, php_strlen(SyncPattern1_)) == SyncPattern1_ or php_substr(NextSyncPattern_, 1, php_strlen(SyncPattern2_)) == SyncPattern2_:
                    #// good - found where expected
                    ActualFrameLengthValues_[-1] = framelength_
                elif php_substr(NextSyncPattern_, 0, php_strlen(SyncPattern1_)) == SyncPattern1_ or php_substr(NextSyncPattern_, 0, php_strlen(SyncPattern2_)) == SyncPattern2_:
                    #// ok - found one byte earlier than expected (last frame wasn't padded, first frame was)
                    ActualFrameLengthValues_[-1] = framelength_ - 1
                    nextoffset_ -= 1
                elif php_substr(NextSyncPattern_, 2, php_strlen(SyncPattern1_)) == SyncPattern1_ or php_substr(NextSyncPattern_, 2, php_strlen(SyncPattern2_)) == SyncPattern2_:
                    #// ok - found one byte later than expected (last frame was padded, first frame wasn't)
                    ActualFrameLengthValues_[-1] = framelength_ + 1
                    nextoffset_ += 1
                else:
                    self.error("Did not find expected free-format sync pattern at offset " + nextoffset_)
                    return False
                # end if
                nextoffset_ += framelength_
            # end while
            if php_count(ActualFrameLengthValues_) > 0:
                framelength_ = php_intval(round(array_sum(ActualFrameLengthValues_) / php_count(ActualFrameLengthValues_)))
            # end if
        # end if
        return framelength_
    # end def freeformatframelength
    #// 
    #// @return bool
    #//
    def getonlympegaudioinfobruteforce(self):
        
        
        MPEGaudioHeaderDecodeCache_ = Array()
        MPEGaudioHeaderValidCache_ = Array()
        MPEGaudioHeaderLengthCache_ = Array()
        MPEGaudioVersionLookup_ = self.mpegaudioversionarray()
        MPEGaudioLayerLookup_ = self.mpegaudiolayerarray()
        MPEGaudioBitrateLookup_ = self.mpegaudiobitratearray()
        MPEGaudioFrequencyLookup_ = self.mpegaudiofrequencyarray()
        MPEGaudioChannelModeLookup_ = self.mpegaudiochannelmodearray()
        MPEGaudioModeExtensionLookup_ = self.mpegaudiomodeextensionarray()
        MPEGaudioEmphasisLookup_ = self.mpegaudioemphasisarray()
        LongMPEGversionLookup_ = Array()
        LongMPEGlayerLookup_ = Array()
        LongMPEGbitrateLookup_ = Array()
        LongMPEGpaddingLookup_ = Array()
        LongMPEGfrequencyLookup_ = Array()
        Distribution_["bitrate"] = Array()
        Distribution_["frequency"] = Array()
        Distribution_["layer"] = Array()
        Distribution_["version"] = Array()
        Distribution_["padding"] = Array()
        info_ = self.getid3.info
        self.fseek(info_["avdataoffset"])
        max_frames_scan_ = 5000
        frames_scanned_ = 0
        previousvalidframe_ = info_["avdataoffset"]
        while True:
            
            if not (self.ftell() < info_["avdataend"]):
                break
            # end if
            set_time_limit(30)
            head4_ = self.fread(4)
            if php_strlen(head4_) < 4:
                break
            # end if
            if head4_[0] != "ÿ":
                i_ = 1
                while i_ < 4:
                    
                    if head4_[i_] == "ÿ":
                        self.fseek(i_ - 4, SEEK_CUR)
                        continue
                    # end if
                    i_ += 1
                # end while
                continue
            # end if
            if (not (php_isset(lambda : MPEGaudioHeaderDecodeCache_[head4_]))):
                MPEGaudioHeaderDecodeCache_[head4_] = self.mpegaudioheaderdecode(head4_)
            # end if
            if (not (php_isset(lambda : MPEGaudioHeaderValidCache_[head4_]))):
                MPEGaudioHeaderValidCache_[head4_] = self.mpegaudioheadervalid(MPEGaudioHeaderDecodeCache_[head4_], False, False)
            # end if
            if MPEGaudioHeaderValidCache_[head4_]:
                if (not (php_isset(lambda : MPEGaudioHeaderLengthCache_[head4_]))):
                    LongMPEGversionLookup_[head4_] = MPEGaudioVersionLookup_[MPEGaudioHeaderDecodeCache_[head4_]["version"]]
                    LongMPEGlayerLookup_[head4_] = MPEGaudioLayerLookup_[MPEGaudioHeaderDecodeCache_[head4_]["layer"]]
                    LongMPEGbitrateLookup_[head4_] = MPEGaudioBitrateLookup_[LongMPEGversionLookup_[head4_]][LongMPEGlayerLookup_[head4_]][MPEGaudioHeaderDecodeCache_[head4_]["bitrate"]]
                    LongMPEGpaddingLookup_[head4_] = php_bool(MPEGaudioHeaderDecodeCache_[head4_]["padding"])
                    LongMPEGfrequencyLookup_[head4_] = MPEGaudioFrequencyLookup_[LongMPEGversionLookup_[head4_]][MPEGaudioHeaderDecodeCache_[head4_]["sample_rate"]]
                    MPEGaudioHeaderLengthCache_[head4_] = self.mpegaudioframelength(LongMPEGbitrateLookup_[head4_], LongMPEGversionLookup_[head4_], LongMPEGlayerLookup_[head4_], LongMPEGpaddingLookup_[head4_], LongMPEGfrequencyLookup_[head4_])
                # end if
                if MPEGaudioHeaderLengthCache_[head4_] > 4:
                    WhereWeWere_ = self.ftell()
                    self.fseek(MPEGaudioHeaderLengthCache_[head4_] - 4, SEEK_CUR)
                    next4_ = self.fread(4)
                    if next4_[0] == "ÿ":
                        if (not (php_isset(lambda : MPEGaudioHeaderDecodeCache_[next4_]))):
                            MPEGaudioHeaderDecodeCache_[next4_] = self.mpegaudioheaderdecode(next4_)
                        # end if
                        if (not (php_isset(lambda : MPEGaudioHeaderValidCache_[next4_]))):
                            MPEGaudioHeaderValidCache_[next4_] = self.mpegaudioheadervalid(MPEGaudioHeaderDecodeCache_[next4_], False, False)
                        # end if
                        if MPEGaudioHeaderValidCache_[next4_]:
                            self.fseek(-4, SEEK_CUR)
                            getid3_lib.safe_inc(Distribution_["bitrate"][LongMPEGbitrateLookup_[head4_]])
                            getid3_lib.safe_inc(Distribution_["layer"][LongMPEGlayerLookup_[head4_]])
                            getid3_lib.safe_inc(Distribution_["version"][LongMPEGversionLookup_[head4_]])
                            getid3_lib.safe_inc(Distribution_["padding"][php_intval(LongMPEGpaddingLookup_[head4_])])
                            getid3_lib.safe_inc(Distribution_["frequency"][LongMPEGfrequencyLookup_[head4_]])
                            frames_scanned_ += 1
                            frames_scanned_ += 1
                            if max_frames_scan_ and frames_scanned_ >= max_frames_scan_:
                                pct_data_scanned_ = self.ftell() - info_["avdataoffset"] / info_["avdataend"] - info_["avdataoffset"]
                                self.warning("too many MPEG audio frames to scan, only scanned first " + max_frames_scan_ + " frames (" + number_format(pct_data_scanned_ * 100, 1) + "% of file) and extrapolated distribution, playtime and bitrate may be incorrect.")
                                for key1_,value1_ in Distribution_:
                                    for key2_,value2_ in value1_:
                                        Distribution_[key1_][key2_] = round(value2_ / pct_data_scanned_)
                                    # end for
                                # end for
                                break
                            # end if
                            continue
                        # end if
                    # end if
                    next4_ = None
                    self.fseek(WhereWeWere_ - 3)
                # end if
            # end if
        # end while
        for key_,value_ in Distribution_:
            ksort(Distribution_[key_], SORT_NUMERIC)
        # end for
        ksort(Distribution_["version"], SORT_STRING)
        info_["mpeg"]["audio"]["bitrate_distribution"] = Distribution_["bitrate"]
        info_["mpeg"]["audio"]["frequency_distribution"] = Distribution_["frequency"]
        info_["mpeg"]["audio"]["layer_distribution"] = Distribution_["layer"]
        info_["mpeg"]["audio"]["version_distribution"] = Distribution_["version"]
        info_["mpeg"]["audio"]["padding_distribution"] = Distribution_["padding"]
        if php_count(Distribution_["version"]) > 1:
            self.error("Corrupt file - more than one MPEG version detected")
        # end if
        if php_count(Distribution_["layer"]) > 1:
            self.error("Corrupt file - more than one MPEG layer detected")
        # end if
        if php_count(Distribution_["frequency"]) > 1:
            self.error("Corrupt file - more than one MPEG sample rate detected")
        # end if
        bittotal_ = 0
        for bitratevalue_,bitratecount_ in Distribution_["bitrate"]:
            if bitratevalue_ != "free":
                bittotal_ += bitratevalue_ * bitratecount_
            # end if
        # end for
        info_["mpeg"]["audio"]["frame_count"] = array_sum(Distribution_["bitrate"])
        if info_["mpeg"]["audio"]["frame_count"] == 0:
            self.error("no MPEG audio frames found")
            return False
        # end if
        info_["mpeg"]["audio"]["bitrate"] = bittotal_ / info_["mpeg"]["audio"]["frame_count"]
        info_["mpeg"]["audio"]["bitrate_mode"] = "vbr" if php_count(Distribution_["bitrate"]) > 0 else "cbr"
        info_["mpeg"]["audio"]["sample_rate"] = getid3_lib.array_max(Distribution_["frequency"], True)
        info_["audio"]["bitrate"] = info_["mpeg"]["audio"]["bitrate"]
        info_["audio"]["bitrate_mode"] = info_["mpeg"]["audio"]["bitrate_mode"]
        info_["audio"]["sample_rate"] = info_["mpeg"]["audio"]["sample_rate"]
        info_["audio"]["dataformat"] = "mp" + getid3_lib.array_max(Distribution_["layer"], True)
        info_["fileformat"] = info_["audio"]["dataformat"]
        return True
    # end def getonlympegaudioinfobruteforce
    #// 
    #// @param int  $avdataoffset
    #// @param bool $BitrateHistogram
    #// 
    #// @return bool
    #//
    def getonlympegaudioinfo(self, avdataoffset_=None, BitrateHistogram_=None):
        if BitrateHistogram_ is None:
            BitrateHistogram_ = False
        # end if
        
        #// looks for synch, decodes MPEG audio header
        info_ = self.getid3.info
        MPEGaudioVersionLookup_ = None
        MPEGaudioLayerLookup_ = None
        MPEGaudioBitrateLookup_ = None
        if php_empty(lambda : MPEGaudioVersionLookup_):
            MPEGaudioVersionLookup_ = self.mpegaudioversionarray()
            MPEGaudioLayerLookup_ = self.mpegaudiolayerarray()
            MPEGaudioBitrateLookup_ = self.mpegaudiobitratearray()
        # end if
        self.fseek(avdataoffset_)
        sync_seek_buffer_size_ = php_min(128 * 1024, info_["avdataend"] - avdataoffset_)
        if sync_seek_buffer_size_ <= 0:
            self.error("Invalid $sync_seek_buffer_size at offset " + avdataoffset_)
            return False
        # end if
        header_ = self.fread(sync_seek_buffer_size_)
        sync_seek_buffer_size_ = php_strlen(header_)
        SynchSeekOffset_ = 0
        while True:
            
            if not (SynchSeekOffset_ < sync_seek_buffer_size_):
                break
            # end if
            if avdataoffset_ + SynchSeekOffset_ < info_["avdataend"] and (not php_feof(self.getid3.fp)):
                if SynchSeekOffset_ > sync_seek_buffer_size_:
                    #// if a synch's not found within the first 128k bytes, then give up
                    self.error("Could not find valid MPEG audio synch within the first " + round(sync_seek_buffer_size_ / 1024) + "kB")
                    if (php_isset(lambda : info_["audio"]["bitrate"])):
                        info_["audio"]["bitrate"] = None
                    # end if
                    if (php_isset(lambda : info_["mpeg"]["audio"])):
                        info_["mpeg"]["audio"] = None
                    # end if
                    if php_empty(lambda : info_["mpeg"]):
                        info_["mpeg"] = None
                    # end if
                    return False
                elif php_feof(self.getid3.fp):
                    self.error("Could not find valid MPEG audio synch before end of file")
                    if (php_isset(lambda : info_["audio"]["bitrate"])):
                        info_["audio"]["bitrate"] = None
                    # end if
                    if (php_isset(lambda : info_["mpeg"]["audio"])):
                        info_["mpeg"]["audio"] = None
                    # end if
                    if (php_isset(lambda : info_["mpeg"])) and (not php_is_array(info_["mpeg"])) or php_count(info_["mpeg"]) == 0:
                        info_["mpeg"] = None
                    # end if
                    return False
                # end if
            # end if
            if SynchSeekOffset_ + 1 >= php_strlen(header_):
                self.error("Could not find valid MPEG synch before end of file")
                return False
            # end if
            if header_[SynchSeekOffset_] == "ÿ" and header_[SynchSeekOffset_ + 1] > "à":
                #// synch detected
                FirstFrameAVDataOffset_ = None
                if (not (php_isset(lambda : FirstFrameThisfileInfo_))) and (not (php_isset(lambda : info_["mpeg"]["audio"]))):
                    FirstFrameThisfileInfo_ = info_
                    FirstFrameAVDataOffset_ = avdataoffset_ + SynchSeekOffset_
                    if (not self.decodempegaudioheader(FirstFrameAVDataOffset_, FirstFrameThisfileInfo_, False)):
                        FirstFrameThisfileInfo_ = None
                    # end if
                # end if
                dummy_ = info_
                #// only overwrite real data if valid header found
                if self.decodempegaudioheader(avdataoffset_ + SynchSeekOffset_, dummy_, True):
                    info_ = dummy_
                    info_["avdataoffset"] = avdataoffset_ + SynchSeekOffset_
                    for case in Switch(info_["fileformat"] if (php_isset(lambda : info_["fileformat"])) else ""):
                        if case(""):
                            pass
                        # end if
                        if case("id3"):
                            pass
                        # end if
                        if case("ape"):
                            pass
                        # end if
                        if case("mp3"):
                            info_["fileformat"] = "mp3"
                            info_["audio"]["dataformat"] = "mp3"
                            break
                        # end if
                    # end for
                    if (php_isset(lambda : FirstFrameThisfileInfo_)) and (php_isset(lambda : FirstFrameThisfileInfo_["mpeg"]["audio"]["bitrate_mode"])) and FirstFrameThisfileInfo_["mpeg"]["audio"]["bitrate_mode"] == "vbr":
                        if (not abs(info_["audio"]["bitrate"] - FirstFrameThisfileInfo_["audio"]["bitrate"]) <= 1):
                            #// If there is garbage data between a valid VBR header frame and a sequence
                            #// of valid MPEG-audio frames the VBR data is no longer discarded.
                            info_ = FirstFrameThisfileInfo_
                            info_["avdataoffset"] = FirstFrameAVDataOffset_
                            info_["fileformat"] = "mp3"
                            info_["audio"]["dataformat"] = "mp3"
                            dummy_ = info_
                            dummy_["mpeg"]["audio"] = None
                            GarbageOffsetStart_ = FirstFrameAVDataOffset_ + FirstFrameThisfileInfo_["mpeg"]["audio"]["framelength"]
                            GarbageOffsetEnd_ = avdataoffset_ + SynchSeekOffset_
                            if self.decodempegaudioheader(GarbageOffsetEnd_, dummy_, True, True):
                                info_ = dummy_
                                info_["avdataoffset"] = GarbageOffsetEnd_
                                self.warning("apparently-valid VBR header not used because could not find " + GETID3_MP3_VALID_CHECK_FRAMES + " consecutive MPEG-audio frames immediately after VBR header (garbage data for " + GarbageOffsetEnd_ - GarbageOffsetStart_ + " bytes between " + GarbageOffsetStart_ + " and " + GarbageOffsetEnd_ + "), but did find valid CBR stream starting at " + GarbageOffsetEnd_)
                            else:
                                self.warning("using data from VBR header even though could not find " + GETID3_MP3_VALID_CHECK_FRAMES + " consecutive MPEG-audio frames immediately after VBR header (garbage data for " + GarbageOffsetEnd_ - GarbageOffsetStart_ + " bytes between " + GarbageOffsetStart_ + " and " + GarbageOffsetEnd_ + ")")
                            # end if
                        # end if
                    # end if
                    if (php_isset(lambda : info_["mpeg"]["audio"]["bitrate_mode"])) and info_["mpeg"]["audio"]["bitrate_mode"] == "vbr" and (not (php_isset(lambda : info_["mpeg"]["audio"]["VBR_method"]))):
                        #// VBR file with no VBR header
                        BitrateHistogram_ = True
                    # end if
                    if BitrateHistogram_:
                        info_["mpeg"]["audio"]["stereo_distribution"] = Array({"stereo": 0, "joint stereo": 0, "dual channel": 0, "mono": 0})
                        info_["mpeg"]["audio"]["version_distribution"] = Array({"1": 0, "2": 0, "2.5": 0})
                        if info_["mpeg"]["audio"]["version"] == "1":
                            if info_["mpeg"]["audio"]["layer"] == 3:
                                info_["mpeg"]["audio"]["bitrate_distribution"] = Array({"free": 0, 32000: 0, 40000: 0, 48000: 0, 56000: 0, 64000: 0, 80000: 0, 96000: 0, 112000: 0, 128000: 0, 160000: 0, 192000: 0, 224000: 0, 256000: 0, 320000: 0})
                            elif info_["mpeg"]["audio"]["layer"] == 2:
                                info_["mpeg"]["audio"]["bitrate_distribution"] = Array({"free": 0, 32000: 0, 48000: 0, 56000: 0, 64000: 0, 80000: 0, 96000: 0, 112000: 0, 128000: 0, 160000: 0, 192000: 0, 224000: 0, 256000: 0, 320000: 0, 384000: 0})
                            elif info_["mpeg"]["audio"]["layer"] == 1:
                                info_["mpeg"]["audio"]["bitrate_distribution"] = Array({"free": 0, 32000: 0, 64000: 0, 96000: 0, 128000: 0, 160000: 0, 192000: 0, 224000: 0, 256000: 0, 288000: 0, 320000: 0, 352000: 0, 384000: 0, 416000: 0, 448000: 0})
                            # end if
                        elif info_["mpeg"]["audio"]["layer"] == 1:
                            info_["mpeg"]["audio"]["bitrate_distribution"] = Array({"free": 0, 32000: 0, 48000: 0, 56000: 0, 64000: 0, 80000: 0, 96000: 0, 112000: 0, 128000: 0, 144000: 0, 160000: 0, 176000: 0, 192000: 0, 224000: 0, 256000: 0})
                        else:
                            info_["mpeg"]["audio"]["bitrate_distribution"] = Array({"free": 0, 8000: 0, 16000: 0, 24000: 0, 32000: 0, 40000: 0, 48000: 0, 56000: 0, 64000: 0, 80000: 0, 96000: 0, 112000: 0, 128000: 0, 144000: 0, 160000: 0})
                        # end if
                        dummy_ = Array({"error": info_["error"], "warning": info_["warning"], "avdataend": info_["avdataend"], "avdataoffset": info_["avdataoffset"]})
                        synchstartoffset_ = info_["avdataoffset"]
                        self.fseek(info_["avdataoffset"])
                        #// you can play with these numbers:
                        max_frames_scan_ = 50000
                        max_scan_segments_ = 10
                        #// don't play with these numbers:
                        FastMode_ = False
                        SynchErrorsFound_ = 0
                        frames_scanned_ = 0
                        this_scan_segment_ = 0
                        frames_scan_per_segment_ = ceil(max_frames_scan_ / max_scan_segments_)
                        pct_data_scanned_ = 0
                        current_segment_ = 0
                        while current_segment_ < max_scan_segments_:
                            
                            frames_scanned_this_segment_ = 0
                            if self.ftell() >= info_["avdataend"]:
                                break
                            # end if
                            scan_start_offset_[current_segment_] = php_max(self.ftell(), info_["avdataoffset"] + round(current_segment_ * info_["avdataend"] - info_["avdataoffset"] / max_scan_segments_))
                            if current_segment_ > 0:
                                self.fseek(scan_start_offset_[current_segment_])
                                buffer_4k_ = self.fread(4096)
                                j_ = 0
                                while j_ < php_strlen(buffer_4k_) - 4:
                                    
                                    if buffer_4k_[j_] == "ÿ" and buffer_4k_[j_ + 1] > "à":
                                        #// synch detected
                                        if self.decodempegaudioheader(scan_start_offset_[current_segment_] + j_, dummy_, False, False, FastMode_):
                                            calculated_next_offset_ = scan_start_offset_[current_segment_] + j_ + dummy_["mpeg"]["audio"]["framelength"]
                                            if self.decodempegaudioheader(calculated_next_offset_, dummy_, False, False, FastMode_):
                                                scan_start_offset_[current_segment_] += j_
                                                break
                                            # end if
                                        # end if
                                    # end if
                                    j_ += 1
                                # end while
                            # end if
                            synchstartoffset_ = scan_start_offset_[current_segment_]
                            while True:
                                
                                if not (synchstartoffset_ < info_["avdataend"] and self.decodempegaudioheader(synchstartoffset_, dummy_, False, False, FastMode_)):
                                    break
                                # end if
                                FastMode_ = True
                                thisframebitrate_ = MPEGaudioBitrateLookup_[MPEGaudioVersionLookup_[dummy_["mpeg"]["audio"]["raw"]["version"]]][MPEGaudioLayerLookup_[dummy_["mpeg"]["audio"]["raw"]["layer"]]][dummy_["mpeg"]["audio"]["raw"]["bitrate"]]
                                if php_empty(lambda : dummy_["mpeg"]["audio"]["framelength"]):
                                    SynchErrorsFound_ += 1
                                    synchstartoffset_ += 1
                                else:
                                    getid3_lib.safe_inc(info_["mpeg"]["audio"]["bitrate_distribution"][thisframebitrate_])
                                    getid3_lib.safe_inc(info_["mpeg"]["audio"]["stereo_distribution"][dummy_["mpeg"]["audio"]["channelmode"]])
                                    getid3_lib.safe_inc(info_["mpeg"]["audio"]["version_distribution"][dummy_["mpeg"]["audio"]["version"]])
                                    synchstartoffset_ += dummy_["mpeg"]["audio"]["framelength"]
                                # end if
                                frames_scanned_ += 1
                                frames_scanned_this_segment_ += 1
                                frames_scanned_this_segment_ += 1
                                if frames_scan_per_segment_ and frames_scanned_this_segment_ >= frames_scan_per_segment_:
                                    this_pct_scanned_ = self.ftell() - scan_start_offset_[current_segment_] / info_["avdataend"] - info_["avdataoffset"]
                                    if current_segment_ == 0 and this_pct_scanned_ * max_scan_segments_ >= 1:
                                        #// file likely contains < $max_frames_scan, just scan as one segment
                                        max_scan_segments_ = 1
                                        frames_scan_per_segment_ = max_frames_scan_
                                    else:
                                        pct_data_scanned_ += this_pct_scanned_
                                        break
                                    # end if
                                # end if
                            # end while
                            current_segment_ += 1
                        # end while
                        if pct_data_scanned_ > 0:
                            self.warning("too many MPEG audio frames to scan, only scanned " + frames_scanned_ + " frames in " + max_scan_segments_ + " segments (" + number_format(pct_data_scanned_ * 100, 1) + "% of file) and extrapolated distribution, playtime and bitrate may be incorrect.")
                            for key1_,value1_ in info_["mpeg"]["audio"]:
                                if (not php_preg_match("#_distribution$#i", key1_)):
                                    continue
                                # end if
                                for key2_,value2_ in value1_:
                                    info_["mpeg"]["audio"][key1_][key2_] = round(value2_ / pct_data_scanned_)
                                # end for
                            # end for
                        # end if
                        if SynchErrorsFound_ > 0:
                            self.warning("Found " + SynchErrorsFound_ + " synch errors in histogram analysis")
                            pass
                        # end if
                        bittotal_ = 0
                        framecounter_ = 0
                        for bitratevalue_,bitratecount_ in info_["mpeg"]["audio"]["bitrate_distribution"]:
                            framecounter_ += bitratecount_
                            if bitratevalue_ != "free":
                                bittotal_ += bitratevalue_ * bitratecount_
                            # end if
                        # end for
                        if framecounter_ == 0:
                            self.error("Corrupt MP3 file: framecounter == zero")
                            return False
                        # end if
                        info_["mpeg"]["audio"]["frame_count"] = getid3_lib.castasint(framecounter_)
                        info_["mpeg"]["audio"]["bitrate"] = bittotal_ / framecounter_
                        info_["audio"]["bitrate"] = info_["mpeg"]["audio"]["bitrate"]
                        #// Definitively set VBR vs CBR, even if the Xing/LAME/VBRI header says differently
                        distinct_bitrates_ = 0
                        for bitrate_value_,bitrate_count_ in info_["mpeg"]["audio"]["bitrate_distribution"]:
                            if bitrate_count_ > 0:
                                distinct_bitrates_ += 1
                            # end if
                        # end for
                        if distinct_bitrates_ > 1:
                            info_["mpeg"]["audio"]["bitrate_mode"] = "vbr"
                        else:
                            info_["mpeg"]["audio"]["bitrate_mode"] = "cbr"
                        # end if
                        info_["audio"]["bitrate_mode"] = info_["mpeg"]["audio"]["bitrate_mode"]
                    # end if
                    break
                    pass
                # end if
            # end if
            SynchSeekOffset_ += 1
            if avdataoffset_ + SynchSeekOffset_ >= info_["avdataend"]:
                #// end of file/data
                if php_empty(lambda : info_["mpeg"]["audio"]):
                    self.error("could not find valid MPEG synch before end of file")
                    if (php_isset(lambda : info_["audio"]["bitrate"])):
                        info_["audio"]["bitrate"] = None
                    # end if
                    if (php_isset(lambda : info_["mpeg"]["audio"])):
                        info_["mpeg"]["audio"] = None
                    # end if
                    if (php_isset(lambda : info_["mpeg"])) and (not php_is_array(info_["mpeg"])) or php_empty(lambda : info_["mpeg"]):
                        info_["mpeg"] = None
                    # end if
                    return False
                # end if
                break
            # end if
        # end while
        info_["audio"]["channels"] = info_["mpeg"]["audio"]["channels"]
        info_["audio"]["channelmode"] = info_["mpeg"]["audio"]["channelmode"]
        info_["audio"]["sample_rate"] = info_["mpeg"]["audio"]["sample_rate"]
        return True
    # end def getonlympegaudioinfo
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudioversionarray(self):
        
        
        MPEGaudioVersion_ = Array("2.5", False, "2", "1")
        return MPEGaudioVersion_
    # end def mpegaudioversionarray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudiolayerarray(self):
        
        
        MPEGaudioLayer_ = Array(False, 3, 2, 1)
        return MPEGaudioLayer_
    # end def mpegaudiolayerarray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudiobitratearray(self):
        
        
        MPEGaudioBitrate_ = None
        if php_empty(lambda : MPEGaudioBitrate_):
            MPEGaudioBitrate_ = Array({"1": Array({1: Array("free", 32000, 64000, 96000, 128000, 160000, 192000, 224000, 256000, 288000, 320000, 352000, 384000, 416000, 448000), 2: Array("free", 32000, 48000, 56000, 64000, 80000, 96000, 112000, 128000, 160000, 192000, 224000, 256000, 320000, 384000), 3: Array("free", 32000, 40000, 48000, 56000, 64000, 80000, 96000, 112000, 128000, 160000, 192000, 224000, 256000, 320000)})}, {"2": Array({1: Array("free", 32000, 48000, 56000, 64000, 80000, 96000, 112000, 128000, 144000, 160000, 176000, 192000, 224000, 256000), 2: Array("free", 8000, 16000, 24000, 32000, 40000, 48000, 56000, 64000, 80000, 96000, 112000, 128000, 144000, 160000)})})
            MPEGaudioBitrate_["2"][3] = MPEGaudioBitrate_["2"][2]
            MPEGaudioBitrate_["2.5"] = MPEGaudioBitrate_["2"]
        # end if
        return MPEGaudioBitrate_
    # end def mpegaudiobitratearray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudiofrequencyarray(self):
        
        
        MPEGaudioFrequency_ = None
        if php_empty(lambda : MPEGaudioFrequency_):
            MPEGaudioFrequency_ = Array({"1": Array(44100, 48000, 32000), "2": Array(22050, 24000, 16000), "2.5": Array(11025, 12000, 8000)})
        # end if
        return MPEGaudioFrequency_
    # end def mpegaudiofrequencyarray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudiochannelmodearray(self):
        
        
        MPEGaudioChannelMode_ = Array("stereo", "joint stereo", "dual channel", "mono")
        return MPEGaudioChannelMode_
    # end def mpegaudiochannelmodearray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudiomodeextensionarray(self):
        
        
        MPEGaudioModeExtension_ = None
        if php_empty(lambda : MPEGaudioModeExtension_):
            MPEGaudioModeExtension_ = Array({1: Array("4-31", "8-31", "12-31", "16-31"), 2: Array("4-31", "8-31", "12-31", "16-31"), 3: Array("", "IS", "MS", "IS+MS")})
        # end if
        return MPEGaudioModeExtension_
    # end def mpegaudiomodeextensionarray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudioemphasisarray(self):
        
        
        MPEGaudioEmphasis_ = Array("none", "50/15ms", False, "CCIT J.17")
        return MPEGaudioEmphasis_
    # end def mpegaudioemphasisarray
    #// 
    #// @param string $head4
    #// @param bool   $allowBitrate15
    #// 
    #// @return bool
    #//
    @classmethod
    def mpegaudioheaderbytesvalid(self, head4_=None, allowBitrate15_=None):
        if allowBitrate15_ is None:
            allowBitrate15_ = False
        # end if
        
        return self.mpegaudioheadervalid(self.mpegaudioheaderdecode(head4_), False, allowBitrate15_)
    # end def mpegaudioheaderbytesvalid
    #// 
    #// @param array $rawarray
    #// @param bool  $echoerrors
    #// @param bool  $allowBitrate15
    #// 
    #// @return bool
    #//
    @classmethod
    def mpegaudioheadervalid(self, rawarray_=None, echoerrors_=None, allowBitrate15_=None):
        if echoerrors_ is None:
            echoerrors_ = False
        # end if
        if allowBitrate15_ is None:
            allowBitrate15_ = False
        # end if
        
        if rawarray_["synch"] & 4094 != 4094:
            return False
        # end if
        MPEGaudioVersionLookup_ = None
        MPEGaudioLayerLookup_ = None
        MPEGaudioBitrateLookup_ = None
        MPEGaudioFrequencyLookup_ = None
        MPEGaudioChannelModeLookup_ = None
        MPEGaudioModeExtensionLookup_ = None
        MPEGaudioEmphasisLookup_ = None
        if php_empty(lambda : MPEGaudioVersionLookup_):
            MPEGaudioVersionLookup_ = self.mpegaudioversionarray()
            MPEGaudioLayerLookup_ = self.mpegaudiolayerarray()
            MPEGaudioBitrateLookup_ = self.mpegaudiobitratearray()
            MPEGaudioFrequencyLookup_ = self.mpegaudiofrequencyarray()
            MPEGaudioChannelModeLookup_ = self.mpegaudiochannelmodearray()
            MPEGaudioModeExtensionLookup_ = self.mpegaudiomodeextensionarray()
            MPEGaudioEmphasisLookup_ = self.mpegaudioemphasisarray()
        # end if
        if (php_isset(lambda : MPEGaudioVersionLookup_[rawarray_["version"]])):
            decodedVersion_ = MPEGaudioVersionLookup_[rawarray_["version"]]
        else:
            php_print("\n" + "invalid Version (" + rawarray_["version"] + ")" if echoerrors_ else "")
            return False
        # end if
        if (php_isset(lambda : MPEGaudioLayerLookup_[rawarray_["layer"]])):
            decodedLayer_ = MPEGaudioLayerLookup_[rawarray_["layer"]]
        else:
            php_print("\n" + "invalid Layer (" + rawarray_["layer"] + ")" if echoerrors_ else "")
            return False
        # end if
        if (not (php_isset(lambda : MPEGaudioBitrateLookup_[decodedVersion_][decodedLayer_][rawarray_["bitrate"]]))):
            php_print("\n" + "invalid Bitrate (" + rawarray_["bitrate"] + ")" if echoerrors_ else "")
            if rawarray_["bitrate"] == 15:
                #// known issue in LAME 3.90 - 3.93.1 where free-format has bitrate ID of 15 instead of 0
                #// let it go through here otherwise file will not be identified
                if (not allowBitrate15_):
                    return False
                # end if
            else:
                return False
            # end if
        # end if
        if (not (php_isset(lambda : MPEGaudioFrequencyLookup_[decodedVersion_][rawarray_["sample_rate"]]))):
            php_print("\n" + "invalid Frequency (" + rawarray_["sample_rate"] + ")" if echoerrors_ else "")
            return False
        # end if
        if (not (php_isset(lambda : MPEGaudioChannelModeLookup_[rawarray_["channelmode"]]))):
            php_print("\n" + "invalid ChannelMode (" + rawarray_["channelmode"] + ")" if echoerrors_ else "")
            return False
        # end if
        if (not (php_isset(lambda : MPEGaudioModeExtensionLookup_[decodedLayer_][rawarray_["modeextension"]]))):
            php_print("\n" + "invalid Mode Extension (" + rawarray_["modeextension"] + ")" if echoerrors_ else "")
            return False
        # end if
        if (not (php_isset(lambda : MPEGaudioEmphasisLookup_[rawarray_["emphasis"]]))):
            php_print("\n" + "invalid Emphasis (" + rawarray_["emphasis"] + ")" if echoerrors_ else "")
            return False
        # end if
        #// These are just either set or not set, you can't mess that up :)
        #// $rawarray['protection'];
        #// $rawarray['padding'];
        #// $rawarray['private'];
        #// $rawarray['copyright'];
        #// $rawarray['original'];
        return True
    # end def mpegaudioheadervalid
    #// 
    #// @param string $Header4Bytes
    #// 
    #// @return array|false
    #//
    @classmethod
    def mpegaudioheaderdecode(self, Header4Bytes_=None):
        
        
        #// AAAA AAAA  AAAB BCCD  EEEE FFGH  IIJJ KLMM
        #// A - Frame sync (all bits set)
        #// B - MPEG Audio version ID
        #// C - Layer description
        #// D - Protection bit
        #// E - Bitrate index
        #// F - Sampling rate frequency index
        #// G - Padding bit
        #// H - Private bit
        #// I - Channel Mode
        #// J - Mode extension (Only if Joint stereo)
        #// K - Copyright
        #// L - Original
        #// M - Emphasis
        if php_strlen(Header4Bytes_) != 4:
            return False
        # end if
        MPEGrawHeader_["synch"] = getid3_lib.bigendian2int(php_substr(Header4Bytes_, 0, 2)) & 65504 >> 4
        MPEGrawHeader_["version"] = php_ord(Header4Bytes_[1]) & 24 >> 3
        #// BB
        MPEGrawHeader_["layer"] = php_ord(Header4Bytes_[1]) & 6 >> 1
        #// CC
        MPEGrawHeader_["protection"] = php_ord(Header4Bytes_[1]) & 1
        #// D
        MPEGrawHeader_["bitrate"] = php_ord(Header4Bytes_[2]) & 240 >> 4
        #// EEEE
        MPEGrawHeader_["sample_rate"] = php_ord(Header4Bytes_[2]) & 12 >> 2
        #// FF
        MPEGrawHeader_["padding"] = php_ord(Header4Bytes_[2]) & 2 >> 1
        #// G
        MPEGrawHeader_["private"] = php_ord(Header4Bytes_[2]) & 1
        #// H
        MPEGrawHeader_["channelmode"] = php_ord(Header4Bytes_[3]) & 192 >> 6
        #// II
        MPEGrawHeader_["modeextension"] = php_ord(Header4Bytes_[3]) & 48 >> 4
        #// JJ
        MPEGrawHeader_["copyright"] = php_ord(Header4Bytes_[3]) & 8 >> 3
        #// K
        MPEGrawHeader_["original"] = php_ord(Header4Bytes_[3]) & 4 >> 2
        #// L
        MPEGrawHeader_["emphasis"] = php_ord(Header4Bytes_[3]) & 3
        #// MM
        return MPEGrawHeader_
    # end def mpegaudioheaderdecode
    #// 
    #// @param int|string $bitrate
    #// @param string     $version
    #// @param string     $layer
    #// @param bool       $padding
    #// @param int        $samplerate
    #// 
    #// @return int|false
    #//
    @classmethod
    def mpegaudioframelength(self, bitrate_=None, version_=None, layer_=None, padding_=None, samplerate_=None):
        
        
        AudioFrameLengthCache_ = Array()
        if (not (php_isset(lambda : AudioFrameLengthCache_[bitrate_][version_][layer_][padding_][samplerate_]))):
            AudioFrameLengthCache_[bitrate_][version_][layer_][padding_][samplerate_] = False
            if bitrate_ != "free":
                if version_ == "1":
                    if layer_ == "1":
                        #// For Layer I slot is 32 bits long
                        FrameLengthCoefficient_ = 48
                        SlotLength_ = 4
                    else:
                        #// Layer 2 / 3
                        #// for Layer 2 and Layer 3 slot is 8 bits long.
                        FrameLengthCoefficient_ = 144
                        SlotLength_ = 1
                    # end if
                else:
                    #// MPEG-2 / MPEG-2.5
                    if layer_ == "1":
                        #// For Layer I slot is 32 bits long
                        FrameLengthCoefficient_ = 24
                        SlotLength_ = 4
                    elif layer_ == "2":
                        #// for Layer 2 and Layer 3 slot is 8 bits long.
                        FrameLengthCoefficient_ = 144
                        SlotLength_ = 1
                    else:
                        #// layer 3
                        #// for Layer 2 and Layer 3 slot is 8 bits long.
                        FrameLengthCoefficient_ = 72
                        SlotLength_ = 1
                    # end if
                # end if
                #// FrameLengthInBytes = ((Coefficient * BitRate) / SampleRate) + Padding
                if samplerate_ > 0:
                    NewFramelength_ = FrameLengthCoefficient_ * bitrate_ / samplerate_
                    NewFramelength_ = floor(NewFramelength_ / SlotLength_) * SlotLength_
                    #// round to next-lower multiple of SlotLength (1 byte for Layer 2/3, 4 bytes for Layer I)
                    if padding_:
                        NewFramelength_ += SlotLength_
                    # end if
                    AudioFrameLengthCache_[bitrate_][version_][layer_][padding_][samplerate_] = php_int(NewFramelength_)
                # end if
            # end if
        # end if
        return AudioFrameLengthCache_[bitrate_][version_][layer_][padding_][samplerate_]
    # end def mpegaudioframelength
    #// 
    #// @param float|int $bit_rate
    #// 
    #// @return int|float|string
    #//
    @classmethod
    def closeststandardmp3bitrate(self, bit_rate_=None):
        
        
        standard_bit_rates_ = Array(320000, 256000, 224000, 192000, 160000, 128000, 112000, 96000, 80000, 64000, 56000, 48000, 40000, 32000, 24000, 16000, 8000)
        bit_rate_table_ = Array({0: "-"})
        round_bit_rate_ = php_intval(round(bit_rate_, -3))
        if (not (php_isset(lambda : bit_rate_table_[round_bit_rate_]))):
            if round_bit_rate_ > php_max(standard_bit_rates_):
                bit_rate_table_[round_bit_rate_] = round(bit_rate_, 2 - php_strlen(bit_rate_))
            else:
                bit_rate_table_[round_bit_rate_] = php_max(standard_bit_rates_)
                for standard_bit_rate_ in standard_bit_rates_:
                    if round_bit_rate_ >= standard_bit_rate_ + bit_rate_table_[round_bit_rate_] - standard_bit_rate_ / 2:
                        break
                    # end if
                    bit_rate_table_[round_bit_rate_] = standard_bit_rate_
                # end for
            # end if
        # end if
        return bit_rate_table_[round_bit_rate_]
    # end def closeststandardmp3bitrate
    #// 
    #// @param string $version
    #// @param string $channelmode
    #// 
    #// @return int
    #//
    @classmethod
    def xingvbridoffset(self, version_=None, channelmode_=None):
        
        
        XingVBRidOffsetCache_ = Array()
        if php_empty(lambda : XingVBRidOffsetCache_):
            XingVBRidOffsetCache_ = Array({"1": Array({"mono": 21, "stereo": 36, "joint stereo": 36, "dual channel": 36})}, {"2": Array({"mono": 13, "stereo": 21, "joint stereo": 21, "dual channel": 21})}, {"2.5": Array({"mono": 21, "stereo": 21, "joint stereo": 21, "dual channel": 21})})
        # end if
        return XingVBRidOffsetCache_[version_][channelmode_]
    # end def xingvbridoffset
    #// 
    #// @param int $VBRmethodID
    #// 
    #// @return string
    #//
    @classmethod
    def lamevbrmethodlookup(self, VBRmethodID_=None):
        
        
        LAMEvbrMethodLookup_ = Array({0: "unknown", 1: "cbr", 2: "abr", 3: "vbr-old / vbr-rh", 4: "vbr-new / vbr-mtrh", 5: "vbr-mt", 6: "vbr (full vbr method 4)", 8: "cbr (constant bitrate 2 pass)", 9: "abr (2 pass)", 15: "reserved"})
        return LAMEvbrMethodLookup_[VBRmethodID_] if (php_isset(lambda : LAMEvbrMethodLookup_[VBRmethodID_])) else ""
    # end def lamevbrmethodlookup
    #// 
    #// @param int $StereoModeID
    #// 
    #// @return string
    #//
    @classmethod
    def lamemiscstereomodelookup(self, StereoModeID_=None):
        
        
        LAMEmiscStereoModeLookup_ = Array({0: "mono", 1: "stereo", 2: "dual mono", 3: "joint stereo", 4: "forced stereo", 5: "auto", 6: "intensity stereo", 7: "other"})
        return LAMEmiscStereoModeLookup_[StereoModeID_] if (php_isset(lambda : LAMEmiscStereoModeLookup_[StereoModeID_])) else ""
    # end def lamemiscstereomodelookup
    #// 
    #// @param int $SourceSampleFrequencyID
    #// 
    #// @return string
    #//
    @classmethod
    def lamemiscsourcesamplefrequencylookup(self, SourceSampleFrequencyID_=None):
        
        
        LAMEmiscSourceSampleFrequencyLookup_ = Array({0: "<= 32 kHz", 1: "44.1 kHz", 2: "48 kHz", 3: "> 48kHz"})
        return LAMEmiscSourceSampleFrequencyLookup_[SourceSampleFrequencyID_] if (php_isset(lambda : LAMEmiscSourceSampleFrequencyLookup_[SourceSampleFrequencyID_])) else ""
    # end def lamemiscsourcesamplefrequencylookup
    #// 
    #// @param int $SurroundInfoID
    #// 
    #// @return string
    #//
    @classmethod
    def lamesurroundinfolookup(self, SurroundInfoID_=None):
        
        
        LAMEsurroundInfoLookup_ = Array({0: "no surround info", 1: "DPL encoding", 2: "DPL2 encoding", 3: "Ambisonic encoding"})
        return LAMEsurroundInfoLookup_[SurroundInfoID_] if (php_isset(lambda : LAMEsurroundInfoLookup_[SurroundInfoID_])) else "reserved"
    # end def lamesurroundinfolookup
    #// 
    #// @param array $LAMEtag
    #// 
    #// @return string
    #//
    @classmethod
    def lamepresetusedlookup(self, LAMEtag_=None):
        
        
        if LAMEtag_["preset_used_id"] == 0:
            #// no preset used (LAME >=3.93)
            #// no preset recorded (LAME <3.93)
            return ""
        # end if
        LAMEpresetUsedLookup_ = Array()
        #// THIS PART CANNOT BE STATIC .
        i_ = 8
        while i_ <= 320:
            
            for case in Switch(LAMEtag_["vbr_method"]):
                if case("cbr"):
                    LAMEpresetUsedLookup_[i_] = "--alt-preset " + LAMEtag_["vbr_method"] + " " + i_
                    break
                # end if
                if case("abr"):
                    pass
                # end if
                if case():
                    #// other VBR modes shouldn't be here(?)
                    LAMEpresetUsedLookup_[i_] = "--alt-preset " + i_
                    break
                # end if
            # end for
            i_ += 1
        # end while
        #// named old-style presets (studio, phone, voice, etc) are handled in GuessEncoderOptions()
        #// named alt-presets
        LAMEpresetUsedLookup_[1000] = "--r3mix"
        LAMEpresetUsedLookup_[1001] = "--alt-preset standard"
        LAMEpresetUsedLookup_[1002] = "--alt-preset extreme"
        LAMEpresetUsedLookup_[1003] = "--alt-preset insane"
        LAMEpresetUsedLookup_[1004] = "--alt-preset fast standard"
        LAMEpresetUsedLookup_[1005] = "--alt-preset fast extreme"
        LAMEpresetUsedLookup_[1006] = "--alt-preset medium"
        LAMEpresetUsedLookup_[1007] = "--alt-preset fast medium"
        #// LAME 3.94 additions/changes
        LAMEpresetUsedLookup_[1010] = "--preset portable"
        #// 3.94a15 Oct 21 2003
        LAMEpresetUsedLookup_[1015] = "--preset radio"
        #// 3.94a15 Oct 21 2003
        LAMEpresetUsedLookup_[320] = "--preset insane"
        #// 3.94a15 Nov 12 2003
        LAMEpresetUsedLookup_[410] = "-V9"
        LAMEpresetUsedLookup_[420] = "-V8"
        LAMEpresetUsedLookup_[440] = "-V6"
        LAMEpresetUsedLookup_[430] = "--preset radio"
        #// 3.94a15 Nov 12 2003
        LAMEpresetUsedLookup_[450] = "--preset " + "fast " if LAMEtag_["raw"]["vbr_method"] == 4 else "" + "portable"
        #// 3.94a15 Nov 12 2003
        LAMEpresetUsedLookup_[460] = "--preset " + "fast " if LAMEtag_["raw"]["vbr_method"] == 4 else "" + "medium"
        #// 3.94a15 Nov 12 2003
        LAMEpresetUsedLookup_[470] = "--r3mix"
        #// 3.94b1  Dec 18 2003
        LAMEpresetUsedLookup_[480] = "--preset " + "fast " if LAMEtag_["raw"]["vbr_method"] == 4 else "" + "standard"
        #// 3.94a15 Nov 12 2003
        LAMEpresetUsedLookup_[490] = "-V1"
        LAMEpresetUsedLookup_[500] = "--preset " + "fast " if LAMEtag_["raw"]["vbr_method"] == 4 else "" + "extreme"
        #// 3.94a15 Nov 12 2003
        return LAMEpresetUsedLookup_[LAMEtag_["preset_used_id"]] if (php_isset(lambda : LAMEpresetUsedLookup_[LAMEtag_["preset_used_id"]])) else "new/unknown preset: " + LAMEtag_["preset_used_id"] + " - report to info@getid3.org"
    # end def lamepresetusedlookup
# end class getid3_mp3
