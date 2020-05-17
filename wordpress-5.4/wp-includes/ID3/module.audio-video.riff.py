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
#// module.audio-video.riff.php
#// module for analyzing RIFF files
#// multiple formats supported by this module:
#// Wave, AVI, AIFF/AIFC, (MP3,AC3)/RIFF, Wavpack v3, 8SVX
#// dependencies: module.audio.mp3.php
#// module.audio.ac3.php
#// module.audio.dts.php
#// 
#// 
#// 
#// @todo Parse AC-3/DTS audio inside WAVE correctly
#// @todo Rewrite RIFF parser totally
#//
getid3_lib.includedependency(GETID3_INCLUDEPATH + "module.audio.mp3.php", __FILE__, True)
getid3_lib.includedependency(GETID3_INCLUDEPATH + "module.audio.ac3.php", __FILE__, True)
getid3_lib.includedependency(GETID3_INCLUDEPATH + "module.audio.dts.php", __FILE__, True)
class getid3_riff(getid3_handler):
    container = "riff"
    #// default
    #// 
    #// @return bool
    #// 
    #// @throws getid3_exception
    #//
    def analyze(self):
        
        
        info_ = self.getid3.info
        #// initialize these values to an empty array, otherwise they default to NULL
        #// and you can't append array values to a NULL value
        info_["riff"] = Array({"raw": Array()})
        #// Shortcuts
        thisfile_riff_ = info_["riff"]
        thisfile_riff_raw_ = thisfile_riff_["raw"]
        thisfile_audio_ = info_["audio"]
        thisfile_video_ = info_["video"]
        thisfile_audio_dataformat_ = thisfile_audio_["dataformat"]
        thisfile_riff_audio_ = thisfile_riff_["audio"]
        thisfile_riff_video_ = thisfile_riff_["video"]
        thisfile_riff_WAVE_ = Array()
        Original_["avdataoffset"] = info_["avdataoffset"]
        Original_["avdataend"] = info_["avdataend"]
        self.fseek(info_["avdataoffset"])
        RIFFheader_ = self.fread(12)
        offset_ = self.ftell()
        RIFFtype_ = php_substr(RIFFheader_, 0, 4)
        RIFFsize_ = php_substr(RIFFheader_, 4, 4)
        RIFFsubtype_ = php_substr(RIFFheader_, 8, 4)
        for case in Switch(RIFFtype_):
            if case("FORM"):
                #// AIFF, AIFC
                #// $info['fileformat']   = 'aiff';
                self.container = "aiff"
                thisfile_riff_["header_size"] = self.eitherendian2int(RIFFsize_)
                thisfile_riff_[RIFFsubtype_] = self.parseriff(offset_, offset_ + thisfile_riff_["header_size"] - 4)
                break
            # end if
            if case("RIFF"):
                pass
            # end if
            if case("SDSS"):
                pass
            # end if
            if case("RMP3"):
                #// RMP3 is identical to RIFF, just renamed. Used by [unknown program] when creating RIFF-MP3s
                #// $info['fileformat']   = 'riff';
                self.container = "riff"
                thisfile_riff_["header_size"] = self.eitherendian2int(RIFFsize_)
                if RIFFsubtype_ == "RMP3":
                    #// RMP3 is identical to WAVE, just renamed. Used by [unknown program] when creating RIFF-MP3s
                    RIFFsubtype_ = "WAVE"
                # end if
                if RIFFsubtype_ != "AMV ":
                    #// AMV files are RIFF-AVI files with parts of the spec deliberately broken, such as chunk size fields hardcoded to zero (because players known in hardware that these fields are always a certain size
                    #// Handled separately in ParseRIFFAMV()
                    thisfile_riff_[RIFFsubtype_] = self.parseriff(offset_, offset_ + thisfile_riff_["header_size"] - 4)
                # end if
                if info_["avdataend"] - info_["filesize"] == 1:
                    #// LiteWave appears to incorrectly *not* pad actual output file
                    #// to nearest WORD boundary so may appear to be short by one
                    #// byte, in which case - skip warning
                    info_["avdataend"] = info_["filesize"]
                # end if
                nextRIFFoffset_ = Original_["avdataoffset"] + 8 + thisfile_riff_["header_size"]
                #// 8 = "RIFF" + 32-bit offset
                while True:
                    
                    if not (nextRIFFoffset_ < php_min(info_["filesize"], info_["avdataend"])):
                        break
                    # end if
                    try: 
                        self.fseek(nextRIFFoffset_)
                    except getid3_exception as e_:
                        if e_.getcode() == 10:
                            #// $this->warning('RIFF parser: '.$e->getMessage());
                            self.error("AVI extends beyond " + round(PHP_INT_MAX / 1073741824) + "GB and PHP filesystem functions cannot read that far, playtime may be wrong")
                            self.warning("[avdataend] value may be incorrect, multiple AVIX chunks may be present")
                            break
                        else:
                            raise e_
                        # end if
                    # end try
                    nextRIFFheader_ = self.fread(12)
                    if nextRIFFoffset_ == info_["avdataend"] - 1:
                        if php_substr(nextRIFFheader_, 0, 1) == " ":
                            break
                        # end if
                    # end if
                    nextRIFFheaderID_ = php_substr(nextRIFFheader_, 0, 4)
                    nextRIFFsize_ = self.eitherendian2int(php_substr(nextRIFFheader_, 4, 4))
                    nextRIFFtype_ = php_substr(nextRIFFheader_, 8, 4)
                    chunkdata_ = Array()
                    chunkdata_["offset"] = nextRIFFoffset_ + 8
                    chunkdata_["size"] = nextRIFFsize_
                    nextRIFFoffset_ = chunkdata_["offset"] + chunkdata_["size"]
                    for case in Switch(nextRIFFheaderID_):
                        if case("RIFF"):
                            chunkdata_["chunks"] = self.parseriff(chunkdata_["offset"] + 4, nextRIFFoffset_)
                            if (not (php_isset(lambda : thisfile_riff_[nextRIFFtype_]))):
                                thisfile_riff_[nextRIFFtype_] = Array()
                            # end if
                            thisfile_riff_[nextRIFFtype_][-1] = chunkdata_
                            break
                        # end if
                        if case("AMV "):
                            info_["riff"] = None
                            info_["amv"] = self.parseriffamv(chunkdata_["offset"] + 4, nextRIFFoffset_)
                            break
                        # end if
                        if case("JUNK"):
                            #// ignore
                            thisfile_riff_[nextRIFFheaderID_][-1] = chunkdata_
                            break
                        # end if
                        if case("IDVX"):
                            info_["divxtag"]["comments"] = self.parsedivxtag(self.fread(chunkdata_["size"]))
                            break
                        # end if
                        if case():
                            if info_["filesize"] == chunkdata_["offset"] - 8 + 128:
                                DIVXTAG_ = nextRIFFheader_ + self.fread(128 - 12)
                                if php_substr(DIVXTAG_, -7) == "DIVXTAG":
                                    #// DIVXTAG is supposed to be inside an IDVX chunk in a LIST chunk, but some bad encoders just slap it on the end of a file
                                    self.warning("Found wrongly-structured DIVXTAG at offset " + self.ftell() - 128 + ", parsing anyway")
                                    info_["divxtag"]["comments"] = self.parsedivxtag(DIVXTAG_)
                                    break
                                # end if
                            # end if
                            self.warning("Expecting \"RIFF|JUNK|IDVX\" at " + nextRIFFoffset_ + ", found \"" + nextRIFFheaderID_ + "\" (" + getid3_lib.printhexbytes(nextRIFFheaderID_) + ") - skipping rest of file")
                            break
                        # end if
                    # end for
                # end while
                if RIFFsubtype_ == "WAVE":
                    thisfile_riff_WAVE_ = thisfile_riff_["WAVE"]
                # end if
                break
            # end if
            if case():
                self.error("Cannot parse RIFF (this is maybe not a RIFF / WAV / AVI file?) - expecting \"FORM|RIFF|SDSS|RMP3\" found \"" + RIFFsubtype_ + "\" instead")
                #// unset($info['fileformat']);
                return False
            # end if
        # end for
        streamindex_ = 0
        for case in Switch(RIFFsubtype_):
            if case("WAVE"):
                info_["fileformat"] = "wav"
                if php_empty(lambda : thisfile_audio_["bitrate_mode"]):
                    thisfile_audio_["bitrate_mode"] = "cbr"
                # end if
                if php_empty(lambda : thisfile_audio_dataformat_):
                    thisfile_audio_dataformat_ = "wav"
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE_["data"][0]["offset"])):
                    info_["avdataoffset"] = thisfile_riff_WAVE_["data"][0]["offset"] + 8
                    info_["avdataend"] = info_["avdataoffset"] + thisfile_riff_WAVE_["data"][0]["size"]
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE_["fmt "][0]["data"])):
                    thisfile_riff_audio_[streamindex_] = self.parsewaveformatex(thisfile_riff_WAVE_["fmt "][0]["data"])
                    thisfile_audio_["wformattag"] = thisfile_riff_audio_[streamindex_]["raw"]["wFormatTag"]
                    if (not (php_isset(lambda : thisfile_riff_audio_[streamindex_]["bitrate"]))) or thisfile_riff_audio_[streamindex_]["bitrate"] == 0:
                        self.error("Corrupt RIFF file: bitrate_audio == zero")
                        return False
                    # end if
                    thisfile_riff_raw_["fmt "] = thisfile_riff_audio_[streamindex_]["raw"]
                    thisfile_riff_audio_[streamindex_]["raw"] = None
                    thisfile_audio_["streams"][streamindex_] = thisfile_riff_audio_[streamindex_]
                    thisfile_audio_ = getid3_lib.array_merge_noclobber(thisfile_audio_, thisfile_riff_audio_[streamindex_])
                    if php_substr(thisfile_audio_["codec"], 0, php_strlen("unknown: 0x")) == "unknown: 0x":
                        self.warning("Audio codec = " + thisfile_audio_["codec"])
                    # end if
                    thisfile_audio_["bitrate"] = thisfile_riff_audio_[streamindex_]["bitrate"]
                    if php_empty(lambda : info_["playtime_seconds"]):
                        #// may already be set (e.g. DTS-WAV)
                        info_["playtime_seconds"] = php_float(info_["avdataend"] - info_["avdataoffset"] * 8 / thisfile_audio_["bitrate"])
                    # end if
                    thisfile_audio_["lossless"] = False
                    if (php_isset(lambda : thisfile_riff_WAVE_["data"][0]["offset"])) and (php_isset(lambda : thisfile_riff_raw_["fmt "]["wFormatTag"])):
                        for case in Switch(thisfile_riff_raw_["fmt "]["wFormatTag"]):
                            if case(1):
                                #// PCM
                                thisfile_audio_["lossless"] = True
                                break
                            # end if
                            if case(8192):
                                #// AC-3
                                thisfile_audio_dataformat_ = "ac3"
                                break
                            # end if
                            if case():
                                break
                            # end if
                        # end for
                    # end if
                    thisfile_audio_["streams"][streamindex_]["wformattag"] = thisfile_audio_["wformattag"]
                    thisfile_audio_["streams"][streamindex_]["bitrate_mode"] = thisfile_audio_["bitrate_mode"]
                    thisfile_audio_["streams"][streamindex_]["lossless"] = thisfile_audio_["lossless"]
                    thisfile_audio_["streams"][streamindex_]["dataformat"] = thisfile_audio_dataformat_
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE_["rgad"][0]["data"])):
                    #// shortcuts
                    rgadData_ = thisfile_riff_WAVE_["rgad"][0]["data"]
                    thisfile_riff_raw_["rgad"] = Array({"track": Array(), "album": Array()})
                    thisfile_riff_raw_rgad_ = thisfile_riff_raw_["rgad"]
                    thisfile_riff_raw_rgad_track_ = thisfile_riff_raw_rgad_["track"]
                    thisfile_riff_raw_rgad_album_ = thisfile_riff_raw_rgad_["album"]
                    thisfile_riff_raw_rgad_["fPeakAmplitude"] = getid3_lib.littleendian2float(php_substr(rgadData_, 0, 4))
                    thisfile_riff_raw_rgad_["nRadioRgAdjust"] = self.eitherendian2int(php_substr(rgadData_, 4, 2))
                    thisfile_riff_raw_rgad_["nAudiophileRgAdjust"] = self.eitherendian2int(php_substr(rgadData_, 6, 2))
                    nRadioRgAdjustBitstring_ = php_str_pad(getid3_lib.dec2bin(thisfile_riff_raw_rgad_["nRadioRgAdjust"]), 16, "0", STR_PAD_LEFT)
                    nAudiophileRgAdjustBitstring_ = php_str_pad(getid3_lib.dec2bin(thisfile_riff_raw_rgad_["nAudiophileRgAdjust"]), 16, "0", STR_PAD_LEFT)
                    thisfile_riff_raw_rgad_track_["name"] = getid3_lib.bin2dec(php_substr(nRadioRgAdjustBitstring_, 0, 3))
                    thisfile_riff_raw_rgad_track_["originator"] = getid3_lib.bin2dec(php_substr(nRadioRgAdjustBitstring_, 3, 3))
                    thisfile_riff_raw_rgad_track_["signbit"] = getid3_lib.bin2dec(php_substr(nRadioRgAdjustBitstring_, 6, 1))
                    thisfile_riff_raw_rgad_track_["adjustment"] = getid3_lib.bin2dec(php_substr(nRadioRgAdjustBitstring_, 7, 9))
                    thisfile_riff_raw_rgad_album_["name"] = getid3_lib.bin2dec(php_substr(nAudiophileRgAdjustBitstring_, 0, 3))
                    thisfile_riff_raw_rgad_album_["originator"] = getid3_lib.bin2dec(php_substr(nAudiophileRgAdjustBitstring_, 3, 3))
                    thisfile_riff_raw_rgad_album_["signbit"] = getid3_lib.bin2dec(php_substr(nAudiophileRgAdjustBitstring_, 6, 1))
                    thisfile_riff_raw_rgad_album_["adjustment"] = getid3_lib.bin2dec(php_substr(nAudiophileRgAdjustBitstring_, 7, 9))
                    thisfile_riff_["rgad"]["peakamplitude"] = thisfile_riff_raw_rgad_["fPeakAmplitude"]
                    if thisfile_riff_raw_rgad_track_["name"] != 0 and thisfile_riff_raw_rgad_track_["originator"] != 0:
                        thisfile_riff_["rgad"]["track"]["name"] = getid3_lib.rgadnamelookup(thisfile_riff_raw_rgad_track_["name"])
                        thisfile_riff_["rgad"]["track"]["originator"] = getid3_lib.rgadoriginatorlookup(thisfile_riff_raw_rgad_track_["originator"])
                        thisfile_riff_["rgad"]["track"]["adjustment"] = getid3_lib.rgadadjustmentlookup(thisfile_riff_raw_rgad_track_["adjustment"], thisfile_riff_raw_rgad_track_["signbit"])
                    # end if
                    if thisfile_riff_raw_rgad_album_["name"] != 0 and thisfile_riff_raw_rgad_album_["originator"] != 0:
                        thisfile_riff_["rgad"]["album"]["name"] = getid3_lib.rgadnamelookup(thisfile_riff_raw_rgad_album_["name"])
                        thisfile_riff_["rgad"]["album"]["originator"] = getid3_lib.rgadoriginatorlookup(thisfile_riff_raw_rgad_album_["originator"])
                        thisfile_riff_["rgad"]["album"]["adjustment"] = getid3_lib.rgadadjustmentlookup(thisfile_riff_raw_rgad_album_["adjustment"], thisfile_riff_raw_rgad_album_["signbit"])
                    # end if
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE_["fact"][0]["data"])):
                    thisfile_riff_raw_["fact"]["NumberOfSamples"] = self.eitherendian2int(php_substr(thisfile_riff_WAVE_["fact"][0]["data"], 0, 4))
                    pass
                # end if
                if (not php_empty(lambda : thisfile_riff_raw_["fmt "]["nAvgBytesPerSec"])):
                    thisfile_audio_["bitrate"] = getid3_lib.castasint(thisfile_riff_raw_["fmt "]["nAvgBytesPerSec"] * 8)
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE_["bext"][0]["data"])):
                    #// shortcut
                    thisfile_riff_WAVE_bext_0_ = thisfile_riff_WAVE_["bext"][0]
                    thisfile_riff_WAVE_bext_0_["title"] = php_trim(php_substr(thisfile_riff_WAVE_bext_0_["data"], 0, 256))
                    thisfile_riff_WAVE_bext_0_["author"] = php_trim(php_substr(thisfile_riff_WAVE_bext_0_["data"], 256, 32))
                    thisfile_riff_WAVE_bext_0_["reference"] = php_trim(php_substr(thisfile_riff_WAVE_bext_0_["data"], 288, 32))
                    thisfile_riff_WAVE_bext_0_["origin_date"] = php_substr(thisfile_riff_WAVE_bext_0_["data"], 320, 10)
                    thisfile_riff_WAVE_bext_0_["origin_time"] = php_substr(thisfile_riff_WAVE_bext_0_["data"], 330, 8)
                    thisfile_riff_WAVE_bext_0_["time_reference"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_bext_0_["data"], 338, 8))
                    thisfile_riff_WAVE_bext_0_["bwf_version"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_bext_0_["data"], 346, 1))
                    thisfile_riff_WAVE_bext_0_["reserved"] = php_substr(thisfile_riff_WAVE_bext_0_["data"], 347, 254)
                    thisfile_riff_WAVE_bext_0_["coding_history"] = php_explode("\r\n", php_trim(php_substr(thisfile_riff_WAVE_bext_0_["data"], 601)))
                    if php_preg_match("#^([0-9]{4}).([0-9]{2}).([0-9]{2})$#", thisfile_riff_WAVE_bext_0_["origin_date"], matches_bext_date_):
                        if php_preg_match("#^([0-9]{2}).([0-9]{2}).([0-9]{2})$#", thisfile_riff_WAVE_bext_0_["origin_time"], matches_bext_time_):
                            dummy_, bext_timestamp_["year"], bext_timestamp_["month"], bext_timestamp_["day"] = matches_bext_date_
                            dummy_, bext_timestamp_["hour"], bext_timestamp_["minute"], bext_timestamp_["second"] = matches_bext_time_
                            thisfile_riff_WAVE_bext_0_["origin_date_unix"] = gmmktime(bext_timestamp_["hour"], bext_timestamp_["minute"], bext_timestamp_["second"], bext_timestamp_["month"], bext_timestamp_["day"], bext_timestamp_["year"])
                        else:
                            self.warning("RIFF.WAVE.BEXT.origin_time is invalid")
                        # end if
                    else:
                        self.warning("RIFF.WAVE.BEXT.origin_date is invalid")
                    # end if
                    thisfile_riff_["comments"]["author"][-1] = thisfile_riff_WAVE_bext_0_["author"]
                    thisfile_riff_["comments"]["title"][-1] = thisfile_riff_WAVE_bext_0_["title"]
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE_["MEXT"][0]["data"])):
                    #// shortcut
                    thisfile_riff_WAVE_MEXT_0_ = thisfile_riff_WAVE_["MEXT"][0]
                    thisfile_riff_WAVE_MEXT_0_["raw"]["sound_information"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_MEXT_0_["data"], 0, 2))
                    thisfile_riff_WAVE_MEXT_0_["flags"]["homogenous"] = php_bool(thisfile_riff_WAVE_MEXT_0_["raw"]["sound_information"] & 1)
                    if thisfile_riff_WAVE_MEXT_0_["flags"]["homogenous"]:
                        thisfile_riff_WAVE_MEXT_0_["flags"]["padding"] = False if thisfile_riff_WAVE_MEXT_0_["raw"]["sound_information"] & 2 else True
                        thisfile_riff_WAVE_MEXT_0_["flags"]["22_or_44"] = php_bool(thisfile_riff_WAVE_MEXT_0_["raw"]["sound_information"] & 4)
                        thisfile_riff_WAVE_MEXT_0_["flags"]["free_format"] = php_bool(thisfile_riff_WAVE_MEXT_0_["raw"]["sound_information"] & 8)
                        thisfile_riff_WAVE_MEXT_0_["nominal_frame_size"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_MEXT_0_["data"], 2, 2))
                    # end if
                    thisfile_riff_WAVE_MEXT_0_["anciliary_data_length"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_MEXT_0_["data"], 6, 2))
                    thisfile_riff_WAVE_MEXT_0_["raw"]["anciliary_data_def"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_MEXT_0_["data"], 8, 2))
                    thisfile_riff_WAVE_MEXT_0_["flags"]["anciliary_data_left"] = php_bool(thisfile_riff_WAVE_MEXT_0_["raw"]["anciliary_data_def"] & 1)
                    thisfile_riff_WAVE_MEXT_0_["flags"]["anciliary_data_free"] = php_bool(thisfile_riff_WAVE_MEXT_0_["raw"]["anciliary_data_def"] & 2)
                    thisfile_riff_WAVE_MEXT_0_["flags"]["anciliary_data_right"] = php_bool(thisfile_riff_WAVE_MEXT_0_["raw"]["anciliary_data_def"] & 4)
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE_["cart"][0]["data"])):
                    #// shortcut
                    thisfile_riff_WAVE_cart_0_ = thisfile_riff_WAVE_["cart"][0]
                    thisfile_riff_WAVE_cart_0_["version"] = php_substr(thisfile_riff_WAVE_cart_0_["data"], 0, 4)
                    thisfile_riff_WAVE_cart_0_["title"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 4, 64))
                    thisfile_riff_WAVE_cart_0_["artist"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 68, 64))
                    thisfile_riff_WAVE_cart_0_["cut_id"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 132, 64))
                    thisfile_riff_WAVE_cart_0_["client_id"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 196, 64))
                    thisfile_riff_WAVE_cart_0_["category"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 260, 64))
                    thisfile_riff_WAVE_cart_0_["classification"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 324, 64))
                    thisfile_riff_WAVE_cart_0_["out_cue"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 388, 64))
                    thisfile_riff_WAVE_cart_0_["start_date"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 452, 10))
                    thisfile_riff_WAVE_cart_0_["start_time"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 462, 8))
                    thisfile_riff_WAVE_cart_0_["end_date"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 470, 10))
                    thisfile_riff_WAVE_cart_0_["end_time"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 480, 8))
                    thisfile_riff_WAVE_cart_0_["producer_app_id"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 488, 64))
                    thisfile_riff_WAVE_cart_0_["producer_app_version"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 552, 64))
                    thisfile_riff_WAVE_cart_0_["user_defined_text"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 616, 64))
                    thisfile_riff_WAVE_cart_0_["zero_db_reference"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_cart_0_["data"], 680, 4), True)
                    i_ = 0
                    while i_ < 8:
                        
                        thisfile_riff_WAVE_cart_0_["post_time"][i_]["usage_fourcc"] = php_substr(thisfile_riff_WAVE_cart_0_["data"], 684 + i_ * 8, 4)
                        thisfile_riff_WAVE_cart_0_["post_time"][i_]["timer_value"] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_cart_0_["data"], 684 + i_ * 8 + 4, 4))
                        i_ += 1
                    # end while
                    thisfile_riff_WAVE_cart_0_["url"] = php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 748, 1024))
                    thisfile_riff_WAVE_cart_0_["tag_text"] = php_explode("\r\n", php_trim(php_substr(thisfile_riff_WAVE_cart_0_["data"], 1772)))
                    thisfile_riff_["comments"]["tag_text"][-1] = php_substr(thisfile_riff_WAVE_cart_0_["data"], 1772)
                    thisfile_riff_["comments"]["artist"][-1] = thisfile_riff_WAVE_cart_0_["artist"]
                    thisfile_riff_["comments"]["title"][-1] = thisfile_riff_WAVE_cart_0_["title"]
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE_["SNDM"][0]["data"])):
                    #// SoundMiner metadata
                    #// shortcuts
                    thisfile_riff_WAVE_SNDM_0_ = thisfile_riff_WAVE_["SNDM"][0]
                    thisfile_riff_WAVE_SNDM_0_data_ = thisfile_riff_WAVE_SNDM_0_["data"]
                    SNDM_startoffset_ = 0
                    SNDM_endoffset_ = thisfile_riff_WAVE_SNDM_0_["size"]
                    while True:
                        
                        if not (SNDM_startoffset_ < SNDM_endoffset_):
                            break
                        # end if
                        SNDM_thisTagOffset_ = 0
                        SNDM_thisTagSize_ = getid3_lib.bigendian2int(php_substr(thisfile_riff_WAVE_SNDM_0_data_, SNDM_startoffset_ + SNDM_thisTagOffset_, 4))
                        SNDM_thisTagOffset_ += 4
                        SNDM_thisTagKey_ = php_substr(thisfile_riff_WAVE_SNDM_0_data_, SNDM_startoffset_ + SNDM_thisTagOffset_, 4)
                        SNDM_thisTagOffset_ += 4
                        SNDM_thisTagDataSize_ = getid3_lib.bigendian2int(php_substr(thisfile_riff_WAVE_SNDM_0_data_, SNDM_startoffset_ + SNDM_thisTagOffset_, 2))
                        SNDM_thisTagOffset_ += 2
                        SNDM_thisTagDataFlags_ = getid3_lib.bigendian2int(php_substr(thisfile_riff_WAVE_SNDM_0_data_, SNDM_startoffset_ + SNDM_thisTagOffset_, 2))
                        SNDM_thisTagOffset_ += 2
                        SNDM_thisTagDataText_ = php_substr(thisfile_riff_WAVE_SNDM_0_data_, SNDM_startoffset_ + SNDM_thisTagOffset_, SNDM_thisTagDataSize_)
                        SNDM_thisTagOffset_ += SNDM_thisTagDataSize_
                        if SNDM_thisTagSize_ != 4 + 4 + 2 + 2 + SNDM_thisTagDataSize_:
                            self.warning("RIFF.WAVE.SNDM.data contains tag not expected length (expected: " + SNDM_thisTagSize_ + ", found: " + 4 + 4 + 2 + 2 + SNDM_thisTagDataSize_ + ") at offset " + SNDM_startoffset_ + " (file offset " + thisfile_riff_WAVE_SNDM_0_["offset"] + SNDM_startoffset_ + ")")
                            break
                        elif SNDM_thisTagSize_ <= 0:
                            self.warning("RIFF.WAVE.SNDM.data contains zero-size tag at offset " + SNDM_startoffset_ + " (file offset " + thisfile_riff_WAVE_SNDM_0_["offset"] + SNDM_startoffset_ + ")")
                            break
                        # end if
                        SNDM_startoffset_ += SNDM_thisTagSize_
                        thisfile_riff_WAVE_SNDM_0_["parsed_raw"][SNDM_thisTagKey_] = SNDM_thisTagDataText_
                        parsedkey_ = self.wavesndmtaglookup(SNDM_thisTagKey_)
                        if parsedkey_:
                            thisfile_riff_WAVE_SNDM_0_["parsed"][parsedkey_] = SNDM_thisTagDataText_
                        else:
                            self.warning("RIFF.WAVE.SNDM contains unknown tag \"" + SNDM_thisTagKey_ + "\" at offset " + SNDM_startoffset_ + " (file offset " + thisfile_riff_WAVE_SNDM_0_["offset"] + SNDM_startoffset_ + ")")
                        # end if
                    # end while
                    tagmapping_ = Array({"tracktitle": "title", "category": "genre", "cdtitle": "album"})
                    for fromkey_,tokey_ in tagmapping_:
                        if (php_isset(lambda : thisfile_riff_WAVE_SNDM_0_["parsed"][fromkey_])):
                            thisfile_riff_["comments"][tokey_][-1] = thisfile_riff_WAVE_SNDM_0_["parsed"][fromkey_]
                        # end if
                    # end for
                # end if
                if (php_isset(lambda : thisfile_riff_WAVE_["iXML"][0]["data"])):
                    #// requires functions simplexml_load_string and get_object_vars
                    parsedXML_ = getid3_lib.xml2array(thisfile_riff_WAVE_["iXML"][0]["data"])
                    if parsedXML_:
                        thisfile_riff_WAVE_["iXML"][0]["parsed"] = parsedXML_
                        if (php_isset(lambda : parsedXML_["SPEED"]["MASTER_SPEED"])):
                            php_no_error(lambda: numerator_, denominator_ = php_explode("/", parsedXML_["SPEED"]["MASTER_SPEED"]))
                            thisfile_riff_WAVE_["iXML"][0]["master_speed"] = numerator_ / denominator_ if denominator_ else 1000
                        # end if
                        if (php_isset(lambda : parsedXML_["SPEED"]["TIMECODE_RATE"])):
                            php_no_error(lambda: numerator_, denominator_ = php_explode("/", parsedXML_["SPEED"]["TIMECODE_RATE"]))
                            thisfile_riff_WAVE_["iXML"][0]["timecode_rate"] = numerator_ / denominator_ if denominator_ else 1000
                        # end if
                        if (php_isset(lambda : parsedXML_["SPEED"]["TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO"])) and (not php_empty(lambda : parsedXML_["SPEED"]["TIMESTAMP_SAMPLE_RATE"])) and (not php_empty(lambda : thisfile_riff_WAVE_["iXML"][0]["timecode_rate"])):
                            samples_since_midnight_ = floatval(php_ltrim(parsedXML_["SPEED"]["TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_HI"] + parsedXML_["SPEED"]["TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO"], "0"))
                            timestamp_sample_rate_ = php_max(parsedXML_["SPEED"]["TIMESTAMP_SAMPLE_RATE"]) if php_is_array(parsedXML_["SPEED"]["TIMESTAMP_SAMPLE_RATE"]) else parsedXML_["SPEED"]["TIMESTAMP_SAMPLE_RATE"]
                            #// XML could possibly contain more than one TIMESTAMP_SAMPLE_RATE tag, returning as array instead of integer [why? does it make sense? perhaps doesn't matter but getID3 needs to deal with it] - see https://github.com/JamesHeinrich/getID3/issues/105
                            thisfile_riff_WAVE_["iXML"][0]["timecode_seconds"] = samples_since_midnight_ / timestamp_sample_rate_
                            h_ = floor(thisfile_riff_WAVE_["iXML"][0]["timecode_seconds"] / 3600)
                            m_ = floor(thisfile_riff_WAVE_["iXML"][0]["timecode_seconds"] - h_ * 3600 / 60)
                            s_ = floor(thisfile_riff_WAVE_["iXML"][0]["timecode_seconds"] - h_ * 3600 - m_ * 60)
                            f_ = thisfile_riff_WAVE_["iXML"][0]["timecode_seconds"] - h_ * 3600 - m_ * 60 - s_ * thisfile_riff_WAVE_["iXML"][0]["timecode_rate"]
                            thisfile_riff_WAVE_["iXML"][0]["timecode_string"] = php_sprintf("%02d:%02d:%02d:%05.2f", h_, m_, s_, f_)
                            thisfile_riff_WAVE_["iXML"][0]["timecode_string_round"] = php_sprintf("%02d:%02d:%02d:%02d", h_, m_, s_, round(f_))
                            samples_since_midnight_ = None
                            timestamp_sample_rate_ = None
                            h_ = None
                            m_ = None
                            s_ = None
                            f_ = None
                        # end if
                        parsedXML_ = None
                    # end if
                # end if
                if (not (php_isset(lambda : thisfile_audio_["bitrate"]))) and (php_isset(lambda : thisfile_riff_audio_[streamindex_]["bitrate"])):
                    thisfile_audio_["bitrate"] = thisfile_riff_audio_[streamindex_]["bitrate"]
                    info_["playtime_seconds"] = php_float(info_["avdataend"] - info_["avdataoffset"] * 8 / thisfile_audio_["bitrate"])
                # end if
                if (not php_empty(lambda : info_["wavpack"])):
                    thisfile_audio_dataformat_ = "wavpack"
                    thisfile_audio_["bitrate_mode"] = "vbr"
                    thisfile_audio_["encoder"] = "WavPack v" + info_["wavpack"]["version"]
                    #// Reset to the way it was - RIFF parsing will have messed this up
                    info_["avdataend"] = Original_["avdataend"]
                    thisfile_audio_["bitrate"] = info_["avdataend"] - info_["avdataoffset"] * 8 / info_["playtime_seconds"]
                    self.fseek(info_["avdataoffset"] - 44)
                    RIFFdata_ = self.fread(44)
                    OrignalRIFFheaderSize_ = getid3_lib.littleendian2int(php_substr(RIFFdata_, 4, 4)) + 8
                    OrignalRIFFdataSize_ = getid3_lib.littleendian2int(php_substr(RIFFdata_, 40, 4)) + 44
                    if OrignalRIFFheaderSize_ > OrignalRIFFdataSize_:
                        info_["avdataend"] -= OrignalRIFFheaderSize_ - OrignalRIFFdataSize_
                        self.fseek(info_["avdataend"])
                        RIFFdata_ += self.fread(OrignalRIFFheaderSize_ - OrignalRIFFdataSize_)
                    # end if
                    #// move the data chunk after all other chunks (if any)
                    #// so that the RIFF parser doesn't see EOF when trying
                    #// to skip over the data chunk
                    RIFFdata_ = php_substr(RIFFdata_, 0, 36) + php_substr(RIFFdata_, 44) + php_substr(RIFFdata_, 36, 8)
                    getid3_riff_ = php_new_class("getid3_riff", lambda : getid3_riff(self.getid3))
                    getid3_riff_.parseriffdata(RIFFdata_)
                    getid3_riff_ = None
                # end if
                if (php_isset(lambda : thisfile_riff_raw_["fmt "]["wFormatTag"])):
                    for case in Switch(thisfile_riff_raw_["fmt "]["wFormatTag"]):
                        if case(1):
                            #// PCM
                            if (not php_empty(lambda : info_["ac3"])):
                                #// Dolby Digital WAV files masquerade as PCM-WAV, but they're not
                                thisfile_audio_["wformattag"] = 8192
                                thisfile_audio_["codec"] = self.wformattaglookup(thisfile_audio_["wformattag"])
                                thisfile_audio_["lossless"] = False
                                thisfile_audio_["bitrate"] = info_["ac3"]["bitrate"]
                                thisfile_audio_["sample_rate"] = info_["ac3"]["sample_rate"]
                            # end if
                            if (not php_empty(lambda : info_["dts"])):
                                #// Dolby DTS files masquerade as PCM-WAV, but they're not
                                thisfile_audio_["wformattag"] = 8193
                                thisfile_audio_["codec"] = self.wformattaglookup(thisfile_audio_["wformattag"])
                                thisfile_audio_["lossless"] = False
                                thisfile_audio_["bitrate"] = info_["dts"]["bitrate"]
                                thisfile_audio_["sample_rate"] = info_["dts"]["sample_rate"]
                            # end if
                            break
                        # end if
                        if case(2222):
                            #// ClearJump LiteWave
                            thisfile_audio_["bitrate_mode"] = "vbr"
                            thisfile_audio_dataformat_ = "litewave"
                            #// typedef struct tagSLwFormat {
                            #// WORD    m_wCompFormat;     // low byte defines compression method, high byte is compression flags
                            #// DWORD   m_dwScale;         // scale factor for lossy compression
                            #// DWORD   m_dwBlockSize;     // number of samples in encoded blocks
                            #// WORD    m_wQuality;        // alias for the scale factor
                            #// WORD    m_wMarkDistance;   // distance between marks in bytes
                            #// WORD    m_wReserved;
                            #// 
                            #// following paramters are ignored if CF_FILESRC is not set
                            #// DWORD   m_dwOrgSize;       // original file size in bytes
                            #// WORD    m_bFactExists;     // indicates if 'fact' chunk exists in the original file
                            #// DWORD   m_dwRiffChunkSize; // riff chunk size in the original file
                            #// 
                            #// PCMWAVEFORMAT m_OrgWf;     // original wave format
                            #// }SLwFormat, *PSLwFormat;
                            #// shortcut
                            thisfile_riff_["litewave"]["raw"] = Array()
                            riff_litewave_ = thisfile_riff_["litewave"]
                            riff_litewave_raw_ = riff_litewave_["raw"]
                            flags_ = Array({"compression_method": 1, "compression_flags": 1, "m_dwScale": 4, "m_dwBlockSize": 4, "m_wQuality": 2, "m_wMarkDistance": 2, "m_wReserved": 2, "m_dwOrgSize": 4, "m_bFactExists": 2, "m_dwRiffChunkSize": 4})
                            litewave_offset_ = 18
                            for flag_,length_ in flags_:
                                riff_litewave_raw_[flag_] = getid3_lib.littleendian2int(php_substr(thisfile_riff_WAVE_["fmt "][0]["data"], litewave_offset_, length_))
                                litewave_offset_ += length_
                            # end for
                            #// $riff_litewave['quality_factor'] = intval(round((2000 - $riff_litewave_raw['m_dwScale']) / 20));
                            riff_litewave_["quality_factor"] = riff_litewave_raw_["m_wQuality"]
                            riff_litewave_["flags"]["raw_source"] = False if riff_litewave_raw_["compression_flags"] & 1 else True
                            riff_litewave_["flags"]["vbr_blocksize"] = False if riff_litewave_raw_["compression_flags"] & 2 else True
                            riff_litewave_["flags"]["seekpoints"] = php_bool(riff_litewave_raw_["compression_flags"] & 4)
                            thisfile_audio_["lossless"] = True if riff_litewave_raw_["m_wQuality"] == 100 else False
                            thisfile_audio_["encoder_options"] = "-q" + riff_litewave_["quality_factor"]
                            break
                        # end if
                        if case():
                            break
                        # end if
                    # end for
                # end if
                if info_["avdataend"] > info_["filesize"]:
                    for case in Switch(thisfile_audio_dataformat_ if (not php_empty(lambda : thisfile_audio_dataformat_)) else ""):
                        if case("wavpack"):
                            pass
                        # end if
                        if case("lpac"):
                            pass
                        # end if
                        if case("ofr"):
                            pass
                        # end if
                        if case("ofs"):
                            break
                        # end if
                        if case("litewave"):
                            if info_["avdataend"] - info_["filesize"] == 1:
                                pass
                            else:
                                #// Short by more than one byte, throw warning
                                self.warning("Probably truncated file - expecting " + thisfile_riff_[RIFFsubtype_]["data"][0]["size"] + " bytes of data, only found " + info_["filesize"] - info_["avdataoffset"] + " (short by " + thisfile_riff_[RIFFsubtype_]["data"][0]["size"] - info_["filesize"] - info_["avdataoffset"] + " bytes)")
                                info_["avdataend"] = info_["filesize"]
                            # end if
                            break
                        # end if
                        if case():
                            if info_["avdataend"] - info_["filesize"] == 1 and thisfile_riff_[RIFFsubtype_]["data"][0]["size"] % 2 == 0 and info_["filesize"] - info_["avdataoffset"] % 2 == 1:
                                #// output file appears to be incorrectly *not* padded to nearest WORD boundary
                                #// Output less severe warning
                                self.warning("File should probably be padded to nearest WORD boundary, but it is not (expecting " + thisfile_riff_[RIFFsubtype_]["data"][0]["size"] + " bytes of data, only found " + info_["filesize"] - info_["avdataoffset"] + " therefore short by " + thisfile_riff_[RIFFsubtype_]["data"][0]["size"] - info_["filesize"] - info_["avdataoffset"] + " bytes)")
                                info_["avdataend"] = info_["filesize"]
                            else:
                                #// Short by more than one byte, throw warning
                                self.warning("Probably truncated file - expecting " + thisfile_riff_[RIFFsubtype_]["data"][0]["size"] + " bytes of data, only found " + info_["filesize"] - info_["avdataoffset"] + " (short by " + thisfile_riff_[RIFFsubtype_]["data"][0]["size"] - info_["filesize"] - info_["avdataoffset"] + " bytes)")
                                info_["avdataend"] = info_["filesize"]
                            # end if
                            break
                        # end if
                    # end for
                # end if
                if (not php_empty(lambda : info_["mpeg"]["audio"]["LAME"]["audio_bytes"])):
                    if info_["avdataend"] - info_["avdataoffset"] - info_["mpeg"]["audio"]["LAME"]["audio_bytes"] == 1:
                        info_["avdataend"] -= 1
                        self.warning("Extra null byte at end of MP3 data assumed to be RIFF padding and therefore ignored")
                    # end if
                # end if
                if (php_isset(lambda : thisfile_audio_dataformat_)) and thisfile_audio_dataformat_ == "ac3":
                    thisfile_audio_["bits_per_sample"] = None
                    if (not php_empty(lambda : info_["ac3"]["bitrate"])) and info_["ac3"]["bitrate"] != thisfile_audio_["bitrate"]:
                        thisfile_audio_["bitrate"] = info_["ac3"]["bitrate"]
                    # end if
                # end if
                break
            # end if
            if case("AVI "):
                info_["fileformat"] = "avi"
                info_["mime_type"] = "video/avi"
                thisfile_video_["bitrate_mode"] = "vbr"
                #// maybe not, but probably
                thisfile_video_["dataformat"] = "avi"
                thisfile_riff_video_current_ = Array()
                if (php_isset(lambda : thisfile_riff_[RIFFsubtype_]["movi"]["offset"])):
                    info_["avdataoffset"] = thisfile_riff_[RIFFsubtype_]["movi"]["offset"] + 8
                    if (php_isset(lambda : thisfile_riff_["AVIX"])):
                        info_["avdataend"] = thisfile_riff_["AVIX"][php_count(thisfile_riff_["AVIX"]) - 1]["chunks"]["movi"]["offset"] + thisfile_riff_["AVIX"][php_count(thisfile_riff_["AVIX"]) - 1]["chunks"]["movi"]["size"]
                    else:
                        info_["avdataend"] = thisfile_riff_["AVI "]["movi"]["offset"] + thisfile_riff_["AVI "]["movi"]["size"]
                    # end if
                    if info_["avdataend"] > info_["filesize"]:
                        self.warning("Probably truncated file - expecting " + info_["avdataend"] - info_["avdataoffset"] + " bytes of data, only found " + info_["filesize"] - info_["avdataoffset"] + " (short by " + info_["avdataend"] - info_["filesize"] + " bytes)")
                        info_["avdataend"] = info_["filesize"]
                    # end if
                # end if
                if (php_isset(lambda : thisfile_riff_["AVI "]["hdrl"]["strl"]["indx"])):
                    #// $bIndexType = array(
                    #// 0x00 => 'AVI_INDEX_OF_INDEXES',
                    #// 0x01 => 'AVI_INDEX_OF_CHUNKS',
                    #// 0x80 => 'AVI_INDEX_IS_DATA',
                    #// );
                    #// $bIndexSubtype = array(
                    #// 0x01 => array(
                    #// 0x01 => 'AVI_INDEX_2FIELD',
                    #// ),
                    #// );
                    for streamnumber_,steamdataarray_ in thisfile_riff_["AVI "]["hdrl"]["strl"]["indx"]:
                        ahsisd_ = thisfile_riff_["AVI "]["hdrl"]["strl"]["indx"][streamnumber_]["data"]
                        thisfile_riff_raw_["indx"][streamnumber_]["wLongsPerEntry"] = self.eitherendian2int(php_substr(ahsisd_, 0, 2))
                        thisfile_riff_raw_["indx"][streamnumber_]["bIndexSubType"] = self.eitherendian2int(php_substr(ahsisd_, 2, 1))
                        thisfile_riff_raw_["indx"][streamnumber_]["bIndexType"] = self.eitherendian2int(php_substr(ahsisd_, 3, 1))
                        thisfile_riff_raw_["indx"][streamnumber_]["nEntriesInUse"] = self.eitherendian2int(php_substr(ahsisd_, 4, 4))
                        thisfile_riff_raw_["indx"][streamnumber_]["dwChunkId"] = php_substr(ahsisd_, 8, 4)
                        thisfile_riff_raw_["indx"][streamnumber_]["dwReserved"] = self.eitherendian2int(php_substr(ahsisd_, 12, 4))
                        ahsisd_ = None
                    # end for
                # end if
                if (php_isset(lambda : thisfile_riff_["AVI "]["hdrl"]["avih"][streamindex_]["data"])):
                    avihData_ = thisfile_riff_["AVI "]["hdrl"]["avih"][streamindex_]["data"]
                    #// shortcut
                    thisfile_riff_raw_["avih"] = Array()
                    thisfile_riff_raw_avih_ = thisfile_riff_raw_["avih"]
                    thisfile_riff_raw_avih_["dwMicroSecPerFrame"] = self.eitherendian2int(php_substr(avihData_, 0, 4))
                    #// frame display rate (or 0L)
                    if thisfile_riff_raw_avih_["dwMicroSecPerFrame"] == 0:
                        self.error("Corrupt RIFF file: avih.dwMicroSecPerFrame == zero")
                        return False
                    # end if
                    flags_ = Array("dwMaxBytesPerSec", "dwPaddingGranularity", "dwFlags", "dwTotalFrames", "dwInitialFrames", "dwStreams", "dwSuggestedBufferSize", "dwWidth", "dwHeight", "dwScale", "dwRate", "dwStart", "dwLength")
                    avih_offset_ = 4
                    for flag_ in flags_:
                        thisfile_riff_raw_avih_[flag_] = self.eitherendian2int(php_substr(avihData_, avih_offset_, 4))
                        avih_offset_ += 4
                    # end for
                    flags_ = Array({"hasindex": 16, "mustuseindex": 32, "interleaved": 256, "trustcktype": 2048, "capturedfile": 65536, "copyrighted": 131088})
                    for flag_,value_ in flags_:
                        thisfile_riff_raw_avih_["flags"][flag_] = php_bool(thisfile_riff_raw_avih_["dwFlags"] & value_)
                    # end for
                    #// shortcut
                    thisfile_riff_video_[streamindex_] = Array()
                    #// @var array $thisfile_riff_video_current
                    thisfile_riff_video_current_ = thisfile_riff_video_[streamindex_]
                    if thisfile_riff_raw_avih_["dwWidth"] > 0:
                        thisfile_riff_video_current_["frame_width"] = thisfile_riff_raw_avih_["dwWidth"]
                        thisfile_video_["resolution_x"] = thisfile_riff_video_current_["frame_width"]
                    # end if
                    if thisfile_riff_raw_avih_["dwHeight"] > 0:
                        thisfile_riff_video_current_["frame_height"] = thisfile_riff_raw_avih_["dwHeight"]
                        thisfile_video_["resolution_y"] = thisfile_riff_video_current_["frame_height"]
                    # end if
                    if thisfile_riff_raw_avih_["dwTotalFrames"] > 0:
                        thisfile_riff_video_current_["total_frames"] = thisfile_riff_raw_avih_["dwTotalFrames"]
                        thisfile_video_["total_frames"] = thisfile_riff_video_current_["total_frames"]
                    # end if
                    thisfile_riff_video_current_["frame_rate"] = round(1000000 / thisfile_riff_raw_avih_["dwMicroSecPerFrame"], 3)
                    thisfile_video_["frame_rate"] = thisfile_riff_video_current_["frame_rate"]
                # end if
                if (php_isset(lambda : thisfile_riff_["AVI "]["hdrl"]["strl"]["strh"][0]["data"])):
                    if php_is_array(thisfile_riff_["AVI "]["hdrl"]["strl"]["strh"]):
                        i_ = 0
                        while i_ < php_count(thisfile_riff_["AVI "]["hdrl"]["strl"]["strh"]):
                            
                            if (php_isset(lambda : thisfile_riff_["AVI "]["hdrl"]["strl"]["strh"][i_]["data"])):
                                strhData_ = thisfile_riff_["AVI "]["hdrl"]["strl"]["strh"][i_]["data"]
                                strhfccType_ = php_substr(strhData_, 0, 4)
                                if (php_isset(lambda : thisfile_riff_["AVI "]["hdrl"]["strl"]["strf"][i_]["data"])):
                                    strfData_ = thisfile_riff_["AVI "]["hdrl"]["strl"]["strf"][i_]["data"]
                                    #// shortcut
                                    thisfile_riff_raw_strf_strhfccType_streamindex_ = thisfile_riff_raw_["strf"][strhfccType_][streamindex_]
                                    for case in Switch(strhfccType_):
                                        if case("auds"):
                                            thisfile_audio_["bitrate_mode"] = "cbr"
                                            thisfile_audio_dataformat_ = "wav"
                                            if (php_isset(lambda : thisfile_riff_audio_)) and php_is_array(thisfile_riff_audio_):
                                                streamindex_ = php_count(thisfile_riff_audio_)
                                            # end if
                                            thisfile_riff_audio_[streamindex_] = self.parsewaveformatex(strfData_)
                                            thisfile_audio_["wformattag"] = thisfile_riff_audio_[streamindex_]["raw"]["wFormatTag"]
                                            #// shortcut
                                            thisfile_audio_["streams"][streamindex_] = thisfile_riff_audio_[streamindex_]
                                            thisfile_audio_streams_currentstream_ = thisfile_audio_["streams"][streamindex_]
                                            if thisfile_audio_streams_currentstream_["bits_per_sample"] == 0:
                                                thisfile_audio_streams_currentstream_["bits_per_sample"] = None
                                            # end if
                                            thisfile_audio_streams_currentstream_["wformattag"] = thisfile_audio_streams_currentstream_["raw"]["wFormatTag"]
                                            thisfile_audio_streams_currentstream_["raw"] = None
                                            #// shortcut
                                            thisfile_riff_raw_["strf"][strhfccType_][streamindex_] = thisfile_riff_audio_[streamindex_]["raw"]
                                            thisfile_riff_audio_[streamindex_]["raw"] = None
                                            thisfile_audio_ = getid3_lib.array_merge_noclobber(thisfile_audio_, thisfile_riff_audio_[streamindex_])
                                            thisfile_audio_["lossless"] = False
                                            for case in Switch(thisfile_riff_raw_strf_strhfccType_streamindex_["wFormatTag"]):
                                                if case(1):
                                                    #// PCM
                                                    thisfile_audio_dataformat_ = "wav"
                                                    thisfile_audio_["lossless"] = True
                                                    break
                                                # end if
                                                if case(80):
                                                    #// MPEG Layer 2 or Layer 1
                                                    thisfile_audio_dataformat_ = "mp2"
                                                    break
                                                # end if
                                                if case(85):
                                                    #// MPEG Layer 3
                                                    thisfile_audio_dataformat_ = "mp3"
                                                    break
                                                # end if
                                                if case(255):
                                                    #// AAC
                                                    thisfile_audio_dataformat_ = "aac"
                                                    break
                                                # end if
                                                if case(353):
                                                    pass
                                                # end if
                                                if case(354):
                                                    pass
                                                # end if
                                                if case(355):
                                                    #// Windows Media Lossess v9
                                                    thisfile_audio_dataformat_ = "wma"
                                                    break
                                                # end if
                                                if case(8192):
                                                    #// AC-3
                                                    thisfile_audio_dataformat_ = "ac3"
                                                    break
                                                # end if
                                                if case(8193):
                                                    #// DTS
                                                    thisfile_audio_dataformat_ = "dts"
                                                    break
                                                # end if
                                                if case():
                                                    thisfile_audio_dataformat_ = "wav"
                                                    break
                                                # end if
                                            # end for
                                            thisfile_audio_streams_currentstream_["dataformat"] = thisfile_audio_dataformat_
                                            thisfile_audio_streams_currentstream_["lossless"] = thisfile_audio_["lossless"]
                                            thisfile_audio_streams_currentstream_["bitrate_mode"] = thisfile_audio_["bitrate_mode"]
                                            break
                                        # end if
                                        if case("iavs"):
                                            pass
                                        # end if
                                        if case("vids"):
                                            #// shortcut
                                            thisfile_riff_raw_["strh"][i_] = Array()
                                            thisfile_riff_raw_strh_current_ = thisfile_riff_raw_["strh"][i_]
                                            thisfile_riff_raw_strh_current_["fccType"] = php_substr(strhData_, 0, 4)
                                            #// same as $strhfccType;
                                            thisfile_riff_raw_strh_current_["fccHandler"] = php_substr(strhData_, 4, 4)
                                            thisfile_riff_raw_strh_current_["dwFlags"] = self.eitherendian2int(php_substr(strhData_, 8, 4))
                                            #// Contains AVITF_* flags
                                            thisfile_riff_raw_strh_current_["wPriority"] = self.eitherendian2int(php_substr(strhData_, 12, 2))
                                            thisfile_riff_raw_strh_current_["wLanguage"] = self.eitherendian2int(php_substr(strhData_, 14, 2))
                                            thisfile_riff_raw_strh_current_["dwInitialFrames"] = self.eitherendian2int(php_substr(strhData_, 16, 4))
                                            thisfile_riff_raw_strh_current_["dwScale"] = self.eitherendian2int(php_substr(strhData_, 20, 4))
                                            thisfile_riff_raw_strh_current_["dwRate"] = self.eitherendian2int(php_substr(strhData_, 24, 4))
                                            thisfile_riff_raw_strh_current_["dwStart"] = self.eitherendian2int(php_substr(strhData_, 28, 4))
                                            thisfile_riff_raw_strh_current_["dwLength"] = self.eitherendian2int(php_substr(strhData_, 32, 4))
                                            thisfile_riff_raw_strh_current_["dwSuggestedBufferSize"] = self.eitherendian2int(php_substr(strhData_, 36, 4))
                                            thisfile_riff_raw_strh_current_["dwQuality"] = self.eitherendian2int(php_substr(strhData_, 40, 4))
                                            thisfile_riff_raw_strh_current_["dwSampleSize"] = self.eitherendian2int(php_substr(strhData_, 44, 4))
                                            thisfile_riff_raw_strh_current_["rcFrame"] = self.eitherendian2int(php_substr(strhData_, 48, 4))
                                            thisfile_riff_video_current_["codec"] = self.fourcclookup(thisfile_riff_raw_strh_current_["fccHandler"])
                                            thisfile_video_["fourcc"] = thisfile_riff_raw_strh_current_["fccHandler"]
                                            if (not thisfile_riff_video_current_["codec"]) and (php_isset(lambda : thisfile_riff_raw_strf_strhfccType_streamindex_["fourcc"])) and self.fourcclookup(thisfile_riff_raw_strf_strhfccType_streamindex_["fourcc"]):
                                                thisfile_riff_video_current_["codec"] = self.fourcclookup(thisfile_riff_raw_strf_strhfccType_streamindex_["fourcc"])
                                                thisfile_video_["fourcc"] = thisfile_riff_raw_strf_strhfccType_streamindex_["fourcc"]
                                            # end if
                                            thisfile_video_["codec"] = thisfile_riff_video_current_["codec"]
                                            thisfile_video_["pixel_aspect_ratio"] = php_float(1)
                                            for case in Switch(thisfile_riff_raw_strh_current_["fccHandler"]):
                                                if case("HFYU"):
                                                    pass
                                                # end if
                                                if case("IRAW"):
                                                    pass
                                                # end if
                                                if case("YUY2"):
                                                    #// Uncompressed YUV 4:2:2
                                                    thisfile_video_["lossless"] = True
                                                    break
                                                # end if
                                                if case():
                                                    thisfile_video_["lossless"] = False
                                                    break
                                                # end if
                                            # end for
                                            for case in Switch(strhfccType_):
                                                if case("vids"):
                                                    thisfile_riff_raw_strf_strhfccType_streamindex_ = self.parsebitmapinfoheader(php_substr(strfData_, 0, 40), self.container == "riff")
                                                    thisfile_video_["bits_per_sample"] = thisfile_riff_raw_strf_strhfccType_streamindex_["biBitCount"]
                                                    if thisfile_riff_video_current_["codec"] == "DV":
                                                        thisfile_riff_video_current_["dv_type"] = 2
                                                    # end if
                                                    break
                                                # end if
                                                if case("iavs"):
                                                    thisfile_riff_video_current_["dv_type"] = 1
                                                    break
                                                # end if
                                            # end for
                                            break
                                        # end if
                                        if case():
                                            self.warning("Unhandled fccType for stream (" + i_ + "): \"" + strhfccType_ + "\"")
                                            break
                                        # end if
                                    # end for
                                # end if
                            # end if
                            if (php_isset(lambda : thisfile_riff_raw_strf_strhfccType_streamindex_)) and (php_isset(lambda : thisfile_riff_raw_strf_strhfccType_streamindex_["fourcc"])):
                                thisfile_video_["fourcc"] = thisfile_riff_raw_strf_strhfccType_streamindex_["fourcc"]
                                if self.fourcclookup(thisfile_video_["fourcc"]):
                                    thisfile_riff_video_current_["codec"] = self.fourcclookup(thisfile_video_["fourcc"])
                                    thisfile_video_["codec"] = thisfile_riff_video_current_["codec"]
                                # end if
                                for case in Switch(thisfile_riff_raw_strf_strhfccType_streamindex_["fourcc"]):
                                    if case("HFYU"):
                                        pass
                                    # end if
                                    if case("IRAW"):
                                        pass
                                    # end if
                                    if case("YUY2"):
                                        #// Uncompressed YUV 4:2:2
                                        thisfile_video_["lossless"] = True
                                        break
                                    # end if
                                    if case():
                                        thisfile_video_["lossless"] = False
                                        break
                                    # end if
                                # end for
                            # end if
                            i_ += 1
                        # end while
                    # end if
                # end if
                break
            # end if
            if case("AMV "):
                info_["fileformat"] = "amv"
                info_["mime_type"] = "video/amv"
                thisfile_video_["bitrate_mode"] = "vbr"
                #// it's MJPEG, presumably contant-quality encoding, thereby VBR
                thisfile_video_["dataformat"] = "mjpeg"
                thisfile_video_["codec"] = "mjpeg"
                thisfile_video_["lossless"] = False
                thisfile_video_["bits_per_sample"] = 24
                thisfile_audio_["dataformat"] = "adpcm"
                thisfile_audio_["lossless"] = False
                break
            # end if
            if case("CDDA"):
                info_["fileformat"] = "cda"
                info_["mime_type"] = None
                thisfile_audio_dataformat_ = "cda"
                info_["avdataoffset"] = 44
                if (php_isset(lambda : thisfile_riff_["CDDA"]["fmt "][0]["data"])):
                    #// shortcut
                    thisfile_riff_CDDA_fmt_0_ = thisfile_riff_["CDDA"]["fmt "][0]
                    thisfile_riff_CDDA_fmt_0_["unknown1"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0_["data"], 0, 2))
                    thisfile_riff_CDDA_fmt_0_["track_num"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0_["data"], 2, 2))
                    thisfile_riff_CDDA_fmt_0_["disc_id"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0_["data"], 4, 4))
                    thisfile_riff_CDDA_fmt_0_["start_offset_frame"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0_["data"], 8, 4))
                    thisfile_riff_CDDA_fmt_0_["playtime_frames"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0_["data"], 12, 4))
                    thisfile_riff_CDDA_fmt_0_["unknown6"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0_["data"], 16, 4))
                    thisfile_riff_CDDA_fmt_0_["unknown7"] = self.eitherendian2int(php_substr(thisfile_riff_CDDA_fmt_0_["data"], 20, 4))
                    thisfile_riff_CDDA_fmt_0_["start_offset_seconds"] = php_float(thisfile_riff_CDDA_fmt_0_["start_offset_frame"]) / 75
                    thisfile_riff_CDDA_fmt_0_["playtime_seconds"] = php_float(thisfile_riff_CDDA_fmt_0_["playtime_frames"]) / 75
                    info_["comments"]["track_number"] = thisfile_riff_CDDA_fmt_0_["track_num"]
                    info_["playtime_seconds"] = thisfile_riff_CDDA_fmt_0_["playtime_seconds"]
                    #// hardcoded data for CD-audio
                    thisfile_audio_["lossless"] = True
                    thisfile_audio_["sample_rate"] = 44100
                    thisfile_audio_["channels"] = 2
                    thisfile_audio_["bits_per_sample"] = 16
                    thisfile_audio_["bitrate"] = thisfile_audio_["sample_rate"] * thisfile_audio_["channels"] * thisfile_audio_["bits_per_sample"]
                    thisfile_audio_["bitrate_mode"] = "cbr"
                # end if
                break
            # end if
            if case("AIFF"):
                pass
            # end if
            if case("AIFC"):
                info_["fileformat"] = "aiff"
                info_["mime_type"] = "audio/x-aiff"
                thisfile_audio_["bitrate_mode"] = "cbr"
                thisfile_audio_dataformat_ = "aiff"
                thisfile_audio_["lossless"] = True
                if (php_isset(lambda : thisfile_riff_[RIFFsubtype_]["SSND"][0]["offset"])):
                    info_["avdataoffset"] = thisfile_riff_[RIFFsubtype_]["SSND"][0]["offset"] + 8
                    info_["avdataend"] = info_["avdataoffset"] + thisfile_riff_[RIFFsubtype_]["SSND"][0]["size"]
                    if info_["avdataend"] > info_["filesize"]:
                        if info_["avdataend"] == info_["filesize"] + 1 and info_["filesize"] % 2 == 1:
                            pass
                        else:
                            self.warning("Probable truncated AIFF file: expecting " + thisfile_riff_[RIFFsubtype_]["SSND"][0]["size"] + " bytes of audio data, only " + info_["filesize"] - info_["avdataoffset"] + " bytes found")
                        # end if
                        info_["avdataend"] = info_["filesize"]
                    # end if
                # end if
                if (php_isset(lambda : thisfile_riff_[RIFFsubtype_]["COMM"][0]["data"])):
                    #// shortcut
                    thisfile_riff_RIFFsubtype_COMM_0_data_ = thisfile_riff_[RIFFsubtype_]["COMM"][0]["data"]
                    thisfile_riff_audio_["channels"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_COMM_0_data_, 0, 2), True)
                    thisfile_riff_audio_["total_samples"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_COMM_0_data_, 2, 4), False)
                    thisfile_riff_audio_["bits_per_sample"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_COMM_0_data_, 6, 2), True)
                    thisfile_riff_audio_["sample_rate"] = php_int(getid3_lib.bigendian2float(php_substr(thisfile_riff_RIFFsubtype_COMM_0_data_, 8, 10)))
                    if thisfile_riff_[RIFFsubtype_]["COMM"][0]["size"] > 18:
                        thisfile_riff_audio_["codec_fourcc"] = php_substr(thisfile_riff_RIFFsubtype_COMM_0_data_, 18, 4)
                        CodecNameSize_ = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_COMM_0_data_, 22, 1), False)
                        thisfile_riff_audio_["codec_name"] = php_substr(thisfile_riff_RIFFsubtype_COMM_0_data_, 23, CodecNameSize_)
                        for case in Switch(thisfile_riff_audio_["codec_name"]):
                            if case("NONE"):
                                thisfile_audio_["codec"] = "Pulse Code Modulation (PCM)"
                                thisfile_audio_["lossless"] = True
                                break
                            # end if
                            if case(""):
                                for case in Switch(thisfile_riff_audio_["codec_fourcc"]):
                                    if case("sowt"):
                                        thisfile_riff_audio_["codec_name"] = "Two's Compliment Little-Endian PCM"
                                        thisfile_audio_["lossless"] = True
                                        break
                                    # end if
                                    if case("twos"):
                                        thisfile_riff_audio_["codec_name"] = "Two's Compliment Big-Endian PCM"
                                        thisfile_audio_["lossless"] = True
                                        break
                                    # end if
                                    if case():
                                        break
                                    # end if
                                # end for
                                break
                            # end if
                            if case():
                                thisfile_audio_["codec"] = thisfile_riff_audio_["codec_name"]
                                thisfile_audio_["lossless"] = False
                                break
                            # end if
                        # end for
                    # end if
                    thisfile_audio_["channels"] = thisfile_riff_audio_["channels"]
                    if thisfile_riff_audio_["bits_per_sample"] > 0:
                        thisfile_audio_["bits_per_sample"] = thisfile_riff_audio_["bits_per_sample"]
                    # end if
                    thisfile_audio_["sample_rate"] = thisfile_riff_audio_["sample_rate"]
                    if thisfile_audio_["sample_rate"] == 0:
                        self.error("Corrupted AIFF file: sample_rate == zero")
                        return False
                    # end if
                    info_["playtime_seconds"] = thisfile_riff_audio_["total_samples"] / thisfile_audio_["sample_rate"]
                # end if
                if (php_isset(lambda : thisfile_riff_[RIFFsubtype_]["COMT"])):
                    offset_ = 0
                    CommentCount_ = getid3_lib.bigendian2int(php_substr(thisfile_riff_[RIFFsubtype_]["COMT"][0]["data"], offset_, 2), False)
                    offset_ += 2
                    i_ = 0
                    while i_ < CommentCount_:
                        
                        info_["comments_raw"][i_]["timestamp"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_[RIFFsubtype_]["COMT"][0]["data"], offset_, 4), False)
                        offset_ += 4
                        info_["comments_raw"][i_]["marker_id"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_[RIFFsubtype_]["COMT"][0]["data"], offset_, 2), True)
                        offset_ += 2
                        CommentLength_ = getid3_lib.bigendian2int(php_substr(thisfile_riff_[RIFFsubtype_]["COMT"][0]["data"], offset_, 2), False)
                        offset_ += 2
                        info_["comments_raw"][i_]["comment"] = php_substr(thisfile_riff_[RIFFsubtype_]["COMT"][0]["data"], offset_, CommentLength_)
                        offset_ += CommentLength_
                        info_["comments_raw"][i_]["timestamp_unix"] = getid3_lib.datemac2unix(info_["comments_raw"][i_]["timestamp"])
                        thisfile_riff_["comments"]["comment"][-1] = info_["comments_raw"][i_]["comment"]
                        i_ += 1
                    # end while
                # end if
                CommentsChunkNames_ = Array({"NAME": "title", "author": "artist", "(c) ": "copyright", "ANNO": "comment"})
                for key_,value_ in CommentsChunkNames_:
                    if (php_isset(lambda : thisfile_riff_[RIFFsubtype_][key_][0]["data"])):
                        thisfile_riff_["comments"][value_][-1] = thisfile_riff_[RIFFsubtype_][key_][0]["data"]
                    # end if
                # end for
                break
            # end if
            if case("8SVX"):
                info_["fileformat"] = "8svx"
                info_["mime_type"] = "audio/8svx"
                thisfile_audio_["bitrate_mode"] = "cbr"
                thisfile_audio_dataformat_ = "8svx"
                thisfile_audio_["bits_per_sample"] = 8
                thisfile_audio_["channels"] = 1
                #// overridden below, if need be
                ActualBitsPerSample_ = 0
                if (php_isset(lambda : thisfile_riff_[RIFFsubtype_]["BODY"][0]["offset"])):
                    info_["avdataoffset"] = thisfile_riff_[RIFFsubtype_]["BODY"][0]["offset"] + 8
                    info_["avdataend"] = info_["avdataoffset"] + thisfile_riff_[RIFFsubtype_]["BODY"][0]["size"]
                    if info_["avdataend"] > info_["filesize"]:
                        self.warning("Probable truncated AIFF file: expecting " + thisfile_riff_[RIFFsubtype_]["BODY"][0]["size"] + " bytes of audio data, only " + info_["filesize"] - info_["avdataoffset"] + " bytes found")
                    # end if
                # end if
                if (php_isset(lambda : thisfile_riff_[RIFFsubtype_]["VHDR"][0]["offset"])):
                    #// shortcut
                    thisfile_riff_RIFFsubtype_VHDR_0_ = thisfile_riff_[RIFFsubtype_]["VHDR"][0]
                    thisfile_riff_RIFFsubtype_VHDR_0_["oneShotHiSamples"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0_["data"], 0, 4))
                    thisfile_riff_RIFFsubtype_VHDR_0_["repeatHiSamples"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0_["data"], 4, 4))
                    thisfile_riff_RIFFsubtype_VHDR_0_["samplesPerHiCycle"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0_["data"], 8, 4))
                    thisfile_riff_RIFFsubtype_VHDR_0_["samplesPerSec"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0_["data"], 12, 2))
                    thisfile_riff_RIFFsubtype_VHDR_0_["ctOctave"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0_["data"], 14, 1))
                    thisfile_riff_RIFFsubtype_VHDR_0_["sCompression"] = getid3_lib.bigendian2int(php_substr(thisfile_riff_RIFFsubtype_VHDR_0_["data"], 15, 1))
                    thisfile_riff_RIFFsubtype_VHDR_0_["Volume"] = getid3_lib.fixedpoint16_16(php_substr(thisfile_riff_RIFFsubtype_VHDR_0_["data"], 16, 4))
                    thisfile_audio_["sample_rate"] = thisfile_riff_RIFFsubtype_VHDR_0_["samplesPerSec"]
                    for case in Switch(thisfile_riff_RIFFsubtype_VHDR_0_["sCompression"]):
                        if case(0):
                            thisfile_audio_["codec"] = "Pulse Code Modulation (PCM)"
                            thisfile_audio_["lossless"] = True
                            ActualBitsPerSample_ = 8
                            break
                        # end if
                        if case(1):
                            thisfile_audio_["codec"] = "Fibonacci-delta encoding"
                            thisfile_audio_["lossless"] = False
                            ActualBitsPerSample_ = 4
                            break
                        # end if
                        if case():
                            self.warning("Unexpected sCompression value in 8SVX.VHDR chunk - expecting 0 or 1, found \"" + thisfile_riff_RIFFsubtype_VHDR_0_["sCompression"] + "\"")
                            break
                        # end if
                    # end for
                # end if
                if (php_isset(lambda : thisfile_riff_[RIFFsubtype_]["CHAN"][0]["data"])):
                    ChannelsIndex_ = getid3_lib.bigendian2int(php_substr(thisfile_riff_[RIFFsubtype_]["CHAN"][0]["data"], 0, 4))
                    for case in Switch(ChannelsIndex_):
                        if case(6):
                            #// Stereo
                            thisfile_audio_["channels"] = 2
                            break
                        # end if
                        if case(2):
                            pass
                        # end if
                        if case(4):
                            #// Right channel only
                            thisfile_audio_["channels"] = 1
                            break
                        # end if
                        if case():
                            self.warning("Unexpected value in 8SVX.CHAN chunk - expecting 2 or 4 or 6, found \"" + ChannelsIndex_ + "\"")
                            break
                        # end if
                    # end for
                # end if
                CommentsChunkNames_ = Array({"NAME": "title", "author": "artist", "(c) ": "copyright", "ANNO": "comment"})
                for key_,value_ in CommentsChunkNames_:
                    if (php_isset(lambda : thisfile_riff_[RIFFsubtype_][key_][0]["data"])):
                        thisfile_riff_["comments"][value_][-1] = thisfile_riff_[RIFFsubtype_][key_][0]["data"]
                    # end if
                # end for
                thisfile_audio_["bitrate"] = thisfile_audio_["sample_rate"] * ActualBitsPerSample_ * thisfile_audio_["channels"]
                if (not php_empty(lambda : thisfile_audio_["bitrate"])):
                    info_["playtime_seconds"] = info_["avdataend"] - info_["avdataoffset"] / thisfile_audio_["bitrate"] / 8
                # end if
                break
            # end if
            if case("CDXA"):
                info_["fileformat"] = "vcd"
                #// Asume Video CD
                info_["mime_type"] = "video/mpeg"
                if (not php_empty(lambda : thisfile_riff_["CDXA"]["data"][0]["size"])):
                    getid3_lib.includedependency(GETID3_INCLUDEPATH + "module.audio-video.mpeg.php", __FILE__, True)
                    getid3_temp_ = php_new_class("getID3", lambda : getID3())
                    getid3_temp_.openfile(self.getid3.filename, None, self.getid3.fp)
                    getid3_mpeg_ = php_new_class("getid3_mpeg", lambda : getid3_mpeg(getid3_temp_))
                    getid3_mpeg_.analyze()
                    if php_empty(lambda : getid3_temp_.info["error"]):
                        info_["audio"] = getid3_temp_.info["audio"]
                        info_["video"] = getid3_temp_.info["video"]
                        info_["mpeg"] = getid3_temp_.info["mpeg"]
                        info_["warning"] = getid3_temp_.info["warning"]
                    # end if
                    getid3_temp_ = None
                    getid3_mpeg_ = None
                # end if
                break
            # end if
            if case("WEBP"):
                #// https://developers.google.com/speed/webp/docs/riff_container
                #// https://tools.ietf.org/html/rfc6386
                #// https://chromium.googlesource.com/webm/libwebp/+/master/doc/webp-lossless-bitstream-spec.txt
                info_["fileformat"] = "webp"
                info_["mime_type"] = "image/webp"
                if (not php_empty(lambda : thisfile_riff_["WEBP"]["VP8 "][0]["size"])):
                    old_offset_ = self.ftell()
                    self.fseek(thisfile_riff_["WEBP"]["VP8 "][0]["offset"] + 8)
                    #// 4 bytes "VP8 " + 4 bytes chunk size
                    WEBP_VP8_header_ = self.fread(10)
                    self.fseek(old_offset_)
                    if php_substr(WEBP_VP8_header_, 3, 3) == "*":
                        thisfile_riff_["WEBP"]["VP8 "][0]["keyframe"] = (not getid3_lib.littleendian2int(php_substr(WEBP_VP8_header_, 0, 3)) & 8388608)
                        thisfile_riff_["WEBP"]["VP8 "][0]["version"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header_, 0, 3)) & 7340032 >> 20
                        thisfile_riff_["WEBP"]["VP8 "][0]["show_frame"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header_, 0, 3)) & 524288
                        thisfile_riff_["WEBP"]["VP8 "][0]["data_bytes"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header_, 0, 3)) & 524287 >> 0
                        thisfile_riff_["WEBP"]["VP8 "][0]["scale_x"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header_, 6, 2)) & 49152 >> 14
                        thisfile_riff_["WEBP"]["VP8 "][0]["width"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header_, 6, 2)) & 16383
                        thisfile_riff_["WEBP"]["VP8 "][0]["scale_y"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header_, 8, 2)) & 49152 >> 14
                        thisfile_riff_["WEBP"]["VP8 "][0]["height"] = getid3_lib.littleendian2int(php_substr(WEBP_VP8_header_, 8, 2)) & 16383
                        info_["video"]["resolution_x"] = thisfile_riff_["WEBP"]["VP8 "][0]["width"]
                        info_["video"]["resolution_y"] = thisfile_riff_["WEBP"]["VP8 "][0]["height"]
                    else:
                        self.error("Expecting 9D 01 2A at offset " + thisfile_riff_["WEBP"]["VP8 "][0]["offset"] + 8 + 3 + ", found \"" + getid3_lib.printhexbytes(php_substr(WEBP_VP8_header_, 3, 3)) + "\"")
                    # end if
                # end if
                if (not php_empty(lambda : thisfile_riff_["WEBP"]["VP8L"][0]["size"])):
                    old_offset_ = self.ftell()
                    self.fseek(thisfile_riff_["WEBP"]["VP8L"][0]["offset"] + 8)
                    #// 4 bytes "VP8L" + 4 bytes chunk size
                    WEBP_VP8L_header_ = self.fread(10)
                    self.fseek(old_offset_)
                    if php_substr(WEBP_VP8L_header_, 0, 1) == "/":
                        width_height_flags_ = getid3_lib.littleendian2bin(php_substr(WEBP_VP8L_header_, 1, 4))
                        thisfile_riff_["WEBP"]["VP8L"][0]["width"] = bindec(php_substr(width_height_flags_, 18, 14)) + 1
                        thisfile_riff_["WEBP"]["VP8L"][0]["height"] = bindec(php_substr(width_height_flags_, 4, 14)) + 1
                        thisfile_riff_["WEBP"]["VP8L"][0]["alpha_is_used"] = php_bool(bindec(php_substr(width_height_flags_, 3, 1)))
                        thisfile_riff_["WEBP"]["VP8L"][0]["version"] = bindec(php_substr(width_height_flags_, 0, 3))
                        info_["video"]["resolution_x"] = thisfile_riff_["WEBP"]["VP8L"][0]["width"]
                        info_["video"]["resolution_y"] = thisfile_riff_["WEBP"]["VP8L"][0]["height"]
                    else:
                        self.error("Expecting 2F at offset " + thisfile_riff_["WEBP"]["VP8L"][0]["offset"] + 8 + ", found \"" + getid3_lib.printhexbytes(php_substr(WEBP_VP8L_header_, 0, 1)) + "\"")
                    # end if
                # end if
                break
            # end if
            if case():
                self.error("Unknown RIFF type: expecting one of (WAVE|RMP3|AVI |CDDA|AIFF|AIFC|8SVX|CDXA|WEBP), found \"" + RIFFsubtype_ + "\" instead")
            # end if
        # end for
        for case in Switch(RIFFsubtype_):
            if case("WAVE"):
                pass
            # end if
            if case("AIFF"):
                pass
            # end if
            if case("AIFC"):
                ID3v2_key_good_ = "id3 "
                ID3v2_keys_bad_ = Array("ID3 ", "tag ")
                for ID3v2_key_bad_ in ID3v2_keys_bad_:
                    if (php_isset(lambda : thisfile_riff_[RIFFsubtype_][ID3v2_key_bad_])) and (not php_array_key_exists(ID3v2_key_good_, thisfile_riff_[RIFFsubtype_])):
                        thisfile_riff_[RIFFsubtype_][ID3v2_key_good_] = thisfile_riff_[RIFFsubtype_][ID3v2_key_bad_]
                        self.warning("mapping \"" + ID3v2_key_bad_ + "\" chunk to \"" + ID3v2_key_good_ + "\"")
                    # end if
                # end for
                if (php_isset(lambda : thisfile_riff_[RIFFsubtype_]["id3 "])):
                    getid3_lib.includedependency(GETID3_INCLUDEPATH + "module.tag.id3v2.php", __FILE__, True)
                    getid3_temp_ = php_new_class("getID3", lambda : getID3())
                    getid3_temp_.openfile(self.getid3.filename, None, self.getid3.fp)
                    getid3_id3v2_ = php_new_class("getid3_id3v2", lambda : getid3_id3v2(getid3_temp_))
                    getid3_id3v2_.StartingOffset = thisfile_riff_[RIFFsubtype_]["id3 "][0]["offset"] + 8
                    thisfile_riff_[RIFFsubtype_]["id3 "][0]["valid"] = getid3_id3v2_.analyze()
                    if thisfile_riff_[RIFFsubtype_]["id3 "][0]["valid"]:
                        info_["id3v2"] = getid3_temp_.info["id3v2"]
                    # end if
                    getid3_temp_ = None
                    getid3_id3v2_ = None
                # end if
                break
            # end if
        # end for
        if (php_isset(lambda : thisfile_riff_WAVE_["DISP"])) and php_is_array(thisfile_riff_WAVE_["DISP"]):
            thisfile_riff_["comments"]["title"][-1] = php_trim(php_substr(thisfile_riff_WAVE_["DISP"][php_count(thisfile_riff_WAVE_["DISP"]) - 1]["data"], 4))
        # end if
        if (php_isset(lambda : thisfile_riff_WAVE_["INFO"])) and php_is_array(thisfile_riff_WAVE_["INFO"]):
            self.parsecomments(thisfile_riff_WAVE_["INFO"], thisfile_riff_["comments"])
        # end if
        if (php_isset(lambda : thisfile_riff_["AVI "]["INFO"])) and php_is_array(thisfile_riff_["AVI "]["INFO"]):
            self.parsecomments(thisfile_riff_["AVI "]["INFO"], thisfile_riff_["comments"])
        # end if
        if php_empty(lambda : thisfile_audio_["encoder"]) and (not php_empty(lambda : info_["mpeg"]["audio"]["LAME"]["short_version"])):
            thisfile_audio_["encoder"] = info_["mpeg"]["audio"]["LAME"]["short_version"]
        # end if
        if (not (php_isset(lambda : info_["playtime_seconds"]))):
            info_["playtime_seconds"] = 0
        # end if
        if (php_isset(lambda : thisfile_riff_raw_["strh"][0]["dwLength"])) and (php_isset(lambda : thisfile_riff_raw_["avih"]["dwMicroSecPerFrame"])):
            #// needed for >2GB AVIs where 'avih' chunk only lists number of frames in that chunk, not entire movie
            info_["playtime_seconds"] = thisfile_riff_raw_["strh"][0]["dwLength"] * thisfile_riff_raw_["avih"]["dwMicroSecPerFrame"] / 1000000
        elif (php_isset(lambda : thisfile_riff_raw_["avih"]["dwTotalFrames"])) and (php_isset(lambda : thisfile_riff_raw_["avih"]["dwMicroSecPerFrame"])):
            info_["playtime_seconds"] = thisfile_riff_raw_["avih"]["dwTotalFrames"] * thisfile_riff_raw_["avih"]["dwMicroSecPerFrame"] / 1000000
        # end if
        if info_["playtime_seconds"] > 0:
            if (php_isset(lambda : thisfile_riff_audio_)) and (php_isset(lambda : thisfile_riff_video_)):
                if (not (php_isset(lambda : info_["bitrate"]))):
                    info_["bitrate"] = info_["avdataend"] - info_["avdataoffset"] / info_["playtime_seconds"] * 8
                # end if
            elif (php_isset(lambda : thisfile_riff_audio_)) and (not (php_isset(lambda : thisfile_riff_video_))):
                if (not (php_isset(lambda : thisfile_audio_["bitrate"]))):
                    thisfile_audio_["bitrate"] = info_["avdataend"] - info_["avdataoffset"] / info_["playtime_seconds"] * 8
                # end if
            elif (not (php_isset(lambda : thisfile_riff_audio_))) and (php_isset(lambda : thisfile_riff_video_)):
                if (not (php_isset(lambda : thisfile_video_["bitrate"]))):
                    thisfile_video_["bitrate"] = info_["avdataend"] - info_["avdataoffset"] / info_["playtime_seconds"] * 8
                # end if
            # end if
        # end if
        if (php_isset(lambda : thisfile_riff_video_)) and (php_isset(lambda : thisfile_audio_["bitrate"])) and thisfile_audio_["bitrate"] > 0 and info_["playtime_seconds"] > 0:
            info_["bitrate"] = info_["avdataend"] - info_["avdataoffset"] / info_["playtime_seconds"] * 8
            thisfile_audio_["bitrate"] = 0
            thisfile_video_["bitrate"] = info_["bitrate"]
            for channelnumber_,audioinfoarray_ in thisfile_riff_audio_:
                thisfile_video_["bitrate"] -= audioinfoarray_["bitrate"]
                thisfile_audio_["bitrate"] += audioinfoarray_["bitrate"]
            # end for
            if thisfile_video_["bitrate"] <= 0:
                thisfile_video_["bitrate"] = None
            # end if
            if thisfile_audio_["bitrate"] <= 0:
                thisfile_audio_["bitrate"] = None
            # end if
        # end if
        if (php_isset(lambda : info_["mpeg"]["audio"])):
            thisfile_audio_dataformat_ = "mp" + info_["mpeg"]["audio"]["layer"]
            thisfile_audio_["sample_rate"] = info_["mpeg"]["audio"]["sample_rate"]
            thisfile_audio_["channels"] = info_["mpeg"]["audio"]["channels"]
            thisfile_audio_["bitrate"] = info_["mpeg"]["audio"]["bitrate"]
            thisfile_audio_["bitrate_mode"] = php_strtolower(info_["mpeg"]["audio"]["bitrate_mode"])
            if (not php_empty(lambda : info_["mpeg"]["audio"]["codec"])):
                thisfile_audio_["codec"] = info_["mpeg"]["audio"]["codec"] + " " + thisfile_audio_["codec"]
            # end if
            if (not php_empty(lambda : thisfile_audio_["streams"])):
                for streamnumber_,streamdata_ in thisfile_audio_["streams"]:
                    if streamdata_["dataformat"] == thisfile_audio_dataformat_:
                        thisfile_audio_["streams"][streamnumber_]["sample_rate"] = thisfile_audio_["sample_rate"]
                        thisfile_audio_["streams"][streamnumber_]["channels"] = thisfile_audio_["channels"]
                        thisfile_audio_["streams"][streamnumber_]["bitrate"] = thisfile_audio_["bitrate"]
                        thisfile_audio_["streams"][streamnumber_]["bitrate_mode"] = thisfile_audio_["bitrate_mode"]
                        thisfile_audio_["streams"][streamnumber_]["codec"] = thisfile_audio_["codec"]
                    # end if
                # end for
            # end if
            getid3_mp3_ = php_new_class("getid3_mp3", lambda : getid3_mp3(self.getid3))
            thisfile_audio_["encoder_options"] = getid3_mp3_.guessencoderoptions()
            getid3_mp3_ = None
        # end if
        if (not php_empty(lambda : thisfile_riff_raw_["fmt "]["wBitsPerSample"])) and thisfile_riff_raw_["fmt "]["wBitsPerSample"] > 0:
            for case in Switch(thisfile_audio_dataformat_):
                if case("ac3"):
                    break
                # end if
                if case():
                    thisfile_audio_["bits_per_sample"] = thisfile_riff_raw_["fmt "]["wBitsPerSample"]
                    break
                # end if
            # end for
        # end if
        if php_empty(lambda : thisfile_riff_raw_):
            thisfile_riff_["raw"] = None
        # end if
        if php_empty(lambda : thisfile_riff_audio_):
            thisfile_riff_["audio"] = None
        # end if
        if php_empty(lambda : thisfile_riff_video_):
            thisfile_riff_["video"] = None
        # end if
        return True
    # end def analyze
    #// 
    #// @param int $startoffset
    #// @param int $maxoffset
    #// 
    #// @return array|false
    #// 
    #// @throws Exception
    #// @throws getid3_exception
    #//
    def parseriffamv(self, startoffset_=None, maxoffset_=None):
        
        
        #// AMV files are RIFF-AVI files with parts of the spec deliberately broken, such as chunk size fields hardcoded to zero (because players known in hardware that these fields are always a certain size
        #// https://code.google.com/p/amv-codec-tools/wiki/AmvDocumentation
        #// typedef struct _amvmainheader {
        #// FOURCC fcc; // 'amvh'
        #// DWORD cb;
        #// DWORD dwMicroSecPerFrame;
        #// BYTE reserve[28];
        #// DWORD dwWidth;
        #// DWORD dwHeight;
        #// DWORD dwSpeed;
        #// DWORD reserve0;
        #// DWORD reserve1;
        #// BYTE bTimeSec;
        #// BYTE bTimeMin;
        #// WORD wTimeHour;
        #// } AMVMAINHEADER;
        info_ = self.getid3.info
        RIFFchunk_ = False
        try: 
            self.fseek(startoffset_)
            maxoffset_ = php_min(maxoffset_, info_["avdataend"])
            AMVheader_ = self.fread(284)
            if php_substr(AMVheader_, 0, 8) != "hdrlamvh":
                raise php_new_class("Exception", lambda : Exception("expecting \"hdrlamv\" at offset " + startoffset_ + 0 + ", found \"" + php_substr(AMVheader_, 0, 8) + "\""))
            # end if
            if php_substr(AMVheader_, 8, 4) != "8   ":
                raise php_new_class("Exception", lambda : Exception("expecting \"0x38000000\" at offset " + startoffset_ + 8 + ", found \"" + getid3_lib.printhexbytes(php_substr(AMVheader_, 8, 4)) + "\""))
            # end if
            RIFFchunk_ = Array()
            RIFFchunk_["amvh"]["us_per_frame"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 12, 4))
            RIFFchunk_["amvh"]["reserved28"] = php_substr(AMVheader_, 16, 28)
            #// null? reserved?
            RIFFchunk_["amvh"]["resolution_x"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 44, 4))
            RIFFchunk_["amvh"]["resolution_y"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 48, 4))
            RIFFchunk_["amvh"]["frame_rate_int"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 52, 4))
            RIFFchunk_["amvh"]["reserved0"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 56, 4))
            #// 1? reserved?
            RIFFchunk_["amvh"]["reserved1"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 60, 4))
            #// 0? reserved?
            RIFFchunk_["amvh"]["runtime_sec"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 64, 1))
            RIFFchunk_["amvh"]["runtime_min"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 65, 1))
            RIFFchunk_["amvh"]["runtime_hrs"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 66, 2))
            info_["video"]["frame_rate"] = 1000000 / RIFFchunk_["amvh"]["us_per_frame"]
            info_["video"]["resolution_x"] = RIFFchunk_["amvh"]["resolution_x"]
            info_["video"]["resolution_y"] = RIFFchunk_["amvh"]["resolution_y"]
            info_["playtime_seconds"] = RIFFchunk_["amvh"]["runtime_hrs"] * 3600 + RIFFchunk_["amvh"]["runtime_min"] * 60 + RIFFchunk_["amvh"]["runtime_sec"]
            #// the rest is all hardcoded(?) and does not appear to be useful until you get to audio info at offset 256, even then everything is probably hardcoded
            if php_substr(AMVheader_, 68, 20) != "LIST" + "    " + "strlstrh" + "8   ":
                raise php_new_class("Exception", lambda : Exception("expecting \"LIST<0x00000000>strlstrh<0x38000000>\" at offset " + startoffset_ + 68 + ", found \"" + getid3_lib.printhexbytes(php_substr(AMVheader_, 68, 20)) + "\""))
            # end if
            #// followed by 56 bytes of null: substr($AMVheader,  88, 56) -> 144
            if php_substr(AMVheader_, 144, 8) != "strf" + "$   ":
                raise php_new_class("Exception", lambda : Exception("expecting \"strf<0x24000000>\" at offset " + startoffset_ + 144 + ", found \"" + getid3_lib.printhexbytes(php_substr(AMVheader_, 144, 8)) + "\""))
            # end if
            #// followed by 36 bytes of null: substr($AMVheader, 144, 36) -> 180
            if php_substr(AMVheader_, 188, 20) != "LIST" + "    " + "strlstrh" + "0   ":
                raise php_new_class("Exception", lambda : Exception("expecting \"LIST<0x00000000>strlstrh<0x30000000>\" at offset " + startoffset_ + 188 + ", found \"" + getid3_lib.printhexbytes(php_substr(AMVheader_, 188, 20)) + "\""))
            # end if
            #// followed by 48 bytes of null: substr($AMVheader, 208, 48) -> 256
            if php_substr(AMVheader_, 256, 8) != "strf" + "   ":
                raise php_new_class("Exception", lambda : Exception("expecting \"strf<0x14000000>\" at offset " + startoffset_ + 256 + ", found \"" + getid3_lib.printhexbytes(php_substr(AMVheader_, 256, 8)) + "\""))
            # end if
            #// followed by 20 bytes of a modified WAVEFORMATEX:
            #// typedef struct {
            #// WORD wFormatTag;       //(Fixme: this is equal to PCM's 0x01 format code)
            #// WORD nChannels;        //(Fixme: this is always 1)
            #// DWORD nSamplesPerSec;  //(Fixme: for all known sample files this is equal to 22050)
            #// DWORD nAvgBytesPerSec; //(Fixme: for all known sample files this is equal to 44100)
            #// WORD nBlockAlign;      //(Fixme: this seems to be 2 in AMV files, is this correct ?)
            #// WORD wBitsPerSample;   //(Fixme: this seems to be 16 in AMV files instead of the expected 4)
            #// WORD cbSize;           //(Fixme: this seems to be 0 in AMV files)
            #// WORD reserved;
            #// } WAVEFORMATEX;
            RIFFchunk_["strf"]["wformattag"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 264, 2))
            RIFFchunk_["strf"]["nchannels"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 266, 2))
            RIFFchunk_["strf"]["nsamplespersec"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 268, 4))
            RIFFchunk_["strf"]["navgbytespersec"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 272, 4))
            RIFFchunk_["strf"]["nblockalign"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 276, 2))
            RIFFchunk_["strf"]["wbitspersample"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 278, 2))
            RIFFchunk_["strf"]["cbsize"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 280, 2))
            RIFFchunk_["strf"]["reserved"] = getid3_lib.littleendian2int(php_substr(AMVheader_, 282, 2))
            info_["audio"]["lossless"] = False
            info_["audio"]["sample_rate"] = RIFFchunk_["strf"]["nsamplespersec"]
            info_["audio"]["channels"] = RIFFchunk_["strf"]["nchannels"]
            info_["audio"]["bits_per_sample"] = RIFFchunk_["strf"]["wbitspersample"]
            info_["audio"]["bitrate"] = info_["audio"]["sample_rate"] * info_["audio"]["channels"] * info_["audio"]["bits_per_sample"]
            info_["audio"]["bitrate_mode"] = "cbr"
        except getid3_exception as e_:
            if e_.getcode() == 10:
                self.warning("RIFFAMV parser: " + e_.getmessage())
            else:
                raise e_
            # end if
        # end try
        return RIFFchunk_
    # end def parseriffamv
    #// 
    #// @param int $startoffset
    #// @param int $maxoffset
    #// 
    #// @return array|false
    #// @throws getid3_exception
    #//
    def parseriff(self, startoffset_=None, maxoffset_=None):
        
        
        info_ = self.getid3.info
        RIFFchunk_ = False
        FoundAllChunksWeNeed_ = False
        try: 
            self.fseek(startoffset_)
            maxoffset_ = php_min(maxoffset_, info_["avdataend"])
            while True:
                
                if not (self.ftell() < maxoffset_):
                    break
                # end if
                chunknamesize_ = self.fread(8)
                #// $chunkname =                          substr($chunknamesize, 0, 4);
                chunkname_ = php_str_replace(" ", "_", php_substr(chunknamesize_, 0, 4))
                #// note: chunk names of 4 null bytes do appear to be legal (has been observed inside INFO and PRMI chunks, for example), but makes traversing array keys more difficult
                chunksize_ = self.eitherendian2int(php_substr(chunknamesize_, 4, 4))
                #// if (strlen(trim($chunkname, "\x00")) < 4) {
                if php_strlen(chunkname_) < 4:
                    self.error("Expecting chunk name at offset " + self.ftell() - 8 + " but found nothing. Aborting RIFF parsing.")
                    break
                # end if
                if chunksize_ == 0 and chunkname_ != "JUNK":
                    self.warning("Chunk (" + chunkname_ + ") size at offset " + self.ftell() - 4 + " is zero. Aborting RIFF parsing.")
                    break
                # end if
                if chunksize_ % 2 != 0:
                    #// all structures are packed on word boundaries
                    chunksize_ += 1
                # end if
                for case in Switch(chunkname_):
                    if case("LIST"):
                        listname_ = self.fread(4)
                        if php_preg_match("#^(movi|rec )$#i", listname_):
                            RIFFchunk_[listname_]["offset"] = self.ftell() - 4
                            RIFFchunk_[listname_]["size"] = chunksize_
                            if (not FoundAllChunksWeNeed_):
                                WhereWeWere_ = self.ftell()
                                AudioChunkHeader_ = self.fread(12)
                                AudioChunkStreamNum_ = php_substr(AudioChunkHeader_, 0, 2)
                                AudioChunkStreamType_ = php_substr(AudioChunkHeader_, 2, 2)
                                AudioChunkSize_ = getid3_lib.littleendian2int(php_substr(AudioChunkHeader_, 4, 4))
                                if AudioChunkStreamType_ == "wb":
                                    FirstFourBytes_ = php_substr(AudioChunkHeader_, 8, 4)
                                    if php_preg_match("/^\\xFF[\\xE2-\\xE7\\xF2-\\xF7\\xFA-\\xFF][\\x00-\\xEB]/s", FirstFourBytes_):
                                        #// MP3
                                        if getid3_mp3.mpegaudioheaderbytesvalid(FirstFourBytes_):
                                            getid3_temp_ = php_new_class("getID3", lambda : getID3())
                                            getid3_temp_.openfile(self.getid3.filename, None, self.getid3.fp)
                                            getid3_temp_.info["avdataoffset"] = self.ftell() - 4
                                            getid3_temp_.info["avdataend"] = self.ftell() + AudioChunkSize_
                                            getid3_mp3_ = php_new_class("getid3_mp3", lambda : getid3_mp3(getid3_temp_, __CLASS__))
                                            getid3_mp3_.getonlympegaudioinfo(getid3_temp_.info["avdataoffset"], False)
                                            if (php_isset(lambda : getid3_temp_.info["mpeg"]["audio"])):
                                                info_["mpeg"]["audio"] = getid3_temp_.info["mpeg"]["audio"]
                                                info_["audio"] = getid3_temp_.info["audio"]
                                                info_["audio"]["dataformat"] = "mp" + info_["mpeg"]["audio"]["layer"]
                                                info_["audio"]["sample_rate"] = info_["mpeg"]["audio"]["sample_rate"]
                                                info_["audio"]["channels"] = info_["mpeg"]["audio"]["channels"]
                                                info_["audio"]["bitrate"] = info_["mpeg"]["audio"]["bitrate"]
                                                info_["audio"]["bitrate_mode"] = php_strtolower(info_["mpeg"]["audio"]["bitrate_mode"])
                                                pass
                                            # end if
                                            getid3_temp_ = None
                                            getid3_mp3_ = None
                                        # end if
                                    elif php_strpos(FirstFourBytes_, getid3_ac3.syncword) == 0:
                                        #// AC3
                                        getid3_temp_ = php_new_class("getID3", lambda : getID3())
                                        getid3_temp_.openfile(self.getid3.filename, None, self.getid3.fp)
                                        getid3_temp_.info["avdataoffset"] = self.ftell() - 4
                                        getid3_temp_.info["avdataend"] = self.ftell() + AudioChunkSize_
                                        getid3_ac3_ = php_new_class("getid3_ac3", lambda : getid3_ac3(getid3_temp_))
                                        getid3_ac3_.analyze()
                                        if php_empty(lambda : getid3_temp_.info["error"]):
                                            info_["audio"] = getid3_temp_.info["audio"]
                                            info_["ac3"] = getid3_temp_.info["ac3"]
                                            if (not php_empty(lambda : getid3_temp_.info["warning"])):
                                                for key_,value_ in getid3_temp_.info["warning"]:
                                                    self.warning(value_)
                                                # end for
                                            # end if
                                        # end if
                                        getid3_temp_ = None
                                        getid3_ac3_ = None
                                    # end if
                                # end if
                                FoundAllChunksWeNeed_ = True
                                self.fseek(WhereWeWere_)
                            # end if
                            self.fseek(chunksize_ - 4, SEEK_CUR)
                        else:
                            if (not (php_isset(lambda : RIFFchunk_[listname_]))):
                                RIFFchunk_[listname_] = Array()
                            # end if
                            LISTchunkParent_ = listname_
                            LISTchunkMaxOffset_ = self.ftell() - 4 + chunksize_
                            parsedChunk_ = self.parseriff(self.ftell(), LISTchunkMaxOffset_)
                            if parsedChunk_:
                                RIFFchunk_[listname_] = php_array_merge_recursive(RIFFchunk_[listname_], parsedChunk_)
                            # end if
                        # end if
                        break
                    # end if
                    if case():
                        if php_preg_match("#^[0-9]{2}(wb|pc|dc|db)$#", chunkname_):
                            self.fseek(chunksize_, SEEK_CUR)
                            break
                        # end if
                        thisindex_ = 0
                        if (php_isset(lambda : RIFFchunk_[chunkname_])) and php_is_array(RIFFchunk_[chunkname_]):
                            thisindex_ = php_count(RIFFchunk_[chunkname_])
                        # end if
                        RIFFchunk_[chunkname_][thisindex_]["offset"] = self.ftell() - 8
                        RIFFchunk_[chunkname_][thisindex_]["size"] = chunksize_
                        for case in Switch(chunkname_):
                            if case("data"):
                                info_["avdataoffset"] = self.ftell()
                                info_["avdataend"] = info_["avdataoffset"] + chunksize_
                                testData_ = self.fread(36)
                                if testData_ == "":
                                    break
                                # end if
                                if php_preg_match("/^\\xFF[\\xE2-\\xE7\\xF2-\\xF7\\xFA-\\xFF][\\x00-\\xEB]/s", php_substr(testData_, 0, 4)):
                                    #// Probably is MP3 data
                                    if getid3_mp3.mpegaudioheaderbytesvalid(php_substr(testData_, 0, 4)):
                                        getid3_temp_ = php_new_class("getID3", lambda : getID3())
                                        getid3_temp_.openfile(self.getid3.filename, None, self.getid3.fp)
                                        getid3_temp_.info["avdataoffset"] = info_["avdataoffset"]
                                        getid3_temp_.info["avdataend"] = info_["avdataend"]
                                        getid3_mp3_ = php_new_class("getid3_mp3", lambda : getid3_mp3(getid3_temp_, __CLASS__))
                                        getid3_mp3_.getonlympegaudioinfo(info_["avdataoffset"], False)
                                        if php_empty(lambda : getid3_temp_.info["error"]):
                                            info_["audio"] = getid3_temp_.info["audio"]
                                            info_["mpeg"] = getid3_temp_.info["mpeg"]
                                        # end if
                                        getid3_temp_ = None
                                        getid3_mp3_ = None
                                    # end if
                                elif php_substr(testData_, 0, 2) == getid3_ac3.syncword or php_substr(testData_, 8, 2) == php_strrev(getid3_ac3.syncword):
                                    isRegularAC3_ = php_substr(testData_, 0, 2) == getid3_ac3.syncword
                                    #// This is probably AC-3 data
                                    getid3_temp_ = php_new_class("getID3", lambda : getID3())
                                    if isRegularAC3_:
                                        getid3_temp_.openfile(self.getid3.filename, None, self.getid3.fp)
                                        getid3_temp_.info["avdataoffset"] = info_["avdataoffset"]
                                        getid3_temp_.info["avdataend"] = info_["avdataend"]
                                    # end if
                                    getid3_ac3_ = php_new_class("getid3_ac3", lambda : getid3_ac3(getid3_temp_))
                                    if isRegularAC3_:
                                        getid3_ac3_.analyze()
                                    else:
                                        #// Dolby Digital WAV
                                        #// AC-3 content, but not encoded in same format as normal AC-3 file
                                        #// For one thing, byte order is swapped
                                        ac3_data_ = ""
                                        i_ = 0
                                        while i_ < 28:
                                            
                                            ac3_data_ += php_substr(testData_, 8 + i_ + 1, 1)
                                            ac3_data_ += php_substr(testData_, 8 + i_ + 0, 1)
                                            i_ += 2
                                        # end while
                                        getid3_ac3_.analyzestring(ac3_data_)
                                    # end if
                                    if php_empty(lambda : getid3_temp_.info["error"]):
                                        info_["audio"] = getid3_temp_.info["audio"]
                                        info_["ac3"] = getid3_temp_.info["ac3"]
                                        if (not php_empty(lambda : getid3_temp_.info["warning"])):
                                            for newerror_ in getid3_temp_.info["warning"]:
                                                self.warning("getid3_ac3() says: [" + newerror_ + "]")
                                            # end for
                                        # end if
                                    # end if
                                    getid3_temp_ = None
                                    getid3_ac3_ = None
                                elif php_preg_match("/^(" + php_implode("|", php_array_map("preg_quote", getid3_dts.syncwords)) + ")/", testData_):
                                    #// This is probably DTS data
                                    getid3_temp_ = php_new_class("getID3", lambda : getID3())
                                    getid3_temp_.openfile(self.getid3.filename, None, self.getid3.fp)
                                    getid3_temp_.info["avdataoffset"] = info_["avdataoffset"]
                                    getid3_dts_ = php_new_class("getid3_dts", lambda : getid3_dts(getid3_temp_))
                                    getid3_dts_.analyze()
                                    if php_empty(lambda : getid3_temp_.info["error"]):
                                        info_["audio"] = getid3_temp_.info["audio"]
                                        info_["dts"] = getid3_temp_.info["dts"]
                                        info_["playtime_seconds"] = getid3_temp_.info["playtime_seconds"]
                                        #// may not match RIFF calculations since DTS-WAV often used 14/16 bit-word packing
                                        if (not php_empty(lambda : getid3_temp_.info["warning"])):
                                            for newerror_ in getid3_temp_.info["warning"]:
                                                self.warning("getid3_dts() says: [" + newerror_ + "]")
                                            # end for
                                        # end if
                                    # end if
                                    getid3_temp_ = None
                                    getid3_dts_ = None
                                elif php_substr(testData_, 0, 4) == "wvpk":
                                    #// This is WavPack data
                                    info_["wavpack"]["offset"] = info_["avdataoffset"]
                                    info_["wavpack"]["size"] = getid3_lib.littleendian2int(php_substr(testData_, 4, 4))
                                    self.parsewavpackheader(php_substr(testData_, 8, 28))
                                else:
                                    pass
                                # end if
                                nextoffset_ = info_["avdataend"]
                                self.fseek(nextoffset_)
                                break
                            # end if
                            if case("iXML"):
                                pass
                            # end if
                            if case("bext"):
                                pass
                            # end if
                            if case("cart"):
                                pass
                            # end if
                            if case("fmt "):
                                pass
                            # end if
                            if case("strh"):
                                pass
                            # end if
                            if case("strf"):
                                pass
                            # end if
                            if case("indx"):
                                pass
                            # end if
                            if case("MEXT"):
                                pass
                            # end if
                            if case("DISP"):
                                pass
                            # end if
                            if case("JUNK"):
                                #// should be: never read data in
                                #// but some programs write their version strings in a JUNK chunk (e.g. VirtualDub, AVIdemux, etc)
                                if chunksize_ < 1048576:
                                    if chunksize_ > 0:
                                        RIFFchunk_[chunkname_][thisindex_]["data"] = self.fread(chunksize_)
                                        if chunkname_ == "JUNK":
                                            if php_preg_match("#^([\\x20-\\x7F]+)#", RIFFchunk_[chunkname_][thisindex_]["data"], matches_):
                                                #// only keep text characters [chr(32)-chr(127)]
                                                info_["riff"]["comments"]["junk"][-1] = php_trim(matches_[1])
                                            # end if
                                            RIFFchunk_[chunkname_][thisindex_]["data"] = None
                                        # end if
                                    # end if
                                else:
                                    self.warning("Chunk \"" + chunkname_ + "\" at offset " + self.ftell() + " is unexpectedly larger than 1MB (claims to be " + number_format(chunksize_) + " bytes), skipping data")
                                    self.fseek(chunksize_, SEEK_CUR)
                                # end if
                                break
                            # end if
                            if case("scot"):
                                #// https://cmsdk.com/node-js/adding-scot-chunk-to-wav-file.html
                                RIFFchunk_[chunkname_][thisindex_]["data"] = self.fread(chunksize_)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["alter"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 0, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["attrib"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 1, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["artnum"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 2, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["title"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 4, 43)
                                #// "name" in other documentation
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["copy"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 47, 4)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["padd"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 51, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["asclen"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 52, 5)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["startseconds"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 57, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["starthundredths"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 59, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["endseconds"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 61, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["endhundreths"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 63, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["sdate"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 65, 6)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["kdate"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 71, 6)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["start_hr"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 77, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["kill_hr"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 78, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["digital"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 79, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["sample_rate"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 80, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["stereo"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 82, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["compress"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 83, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["eomstrt"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 84, 4))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["eomlen"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 88, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["attrib2"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 90, 4))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["future1"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 94, 12)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["catfontcolor"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 106, 4))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["catcolor"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 110, 4))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["segeompos"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 114, 4))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["vt_startsecs"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 118, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["vt_starthunds"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 120, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["priorcat"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 122, 3)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["priorcopy"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 125, 4)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["priorpadd"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 129, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["postcat"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 130, 3)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["postcopy"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 133, 4)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["postpadd"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 137, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["hrcanplay"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 138, 21)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["future2"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 159, 108)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["artist"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 267, 34)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["comment"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 301, 34)
                                #// "trivia" in other documentation
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["intro"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 335, 2)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["end"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 337, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["year"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 338, 4)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["obsolete2"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 342, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["rec_hr"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 343, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["rdate"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 344, 6)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["mpeg_bitrate"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 350, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["pitch"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 352, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["playlevel"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 354, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["lenvalid"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 356, 1)
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["filelength"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 357, 4))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["newplaylevel"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 361, 2))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["chopsize"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 363, 4))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["vteomovr"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 367, 4))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["desiredlen"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 371, 4))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["triggers"] = getid3_lib.littleendian2int(php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 375, 4))
                                RIFFchunk_[chunkname_][thisindex_]["parsed"]["fillout"] = php_substr(RIFFchunk_[chunkname_][thisindex_]["data"], 379, 33)
                                for key_ in Array("title", "artist", "comment"):
                                    if php_trim(RIFFchunk_[chunkname_][thisindex_]["parsed"][key_]):
                                        info_["riff"]["comments"][key_] = Array(RIFFchunk_[chunkname_][thisindex_]["parsed"][key_])
                                    # end if
                                # end for
                                if RIFFchunk_[chunkname_][thisindex_]["parsed"]["filelength"] and (not php_empty(lambda : info_["filesize"])) and RIFFchunk_[chunkname_][thisindex_]["parsed"]["filelength"] != info_["filesize"]:
                                    self.warning("RIFF.WAVE.scot.filelength (" + RIFFchunk_[chunkname_][thisindex_]["parsed"]["filelength"] + ") different from actual filesize (" + info_["filesize"] + ")")
                                # end if
                                break
                            # end if
                            if case():
                                if (not php_empty(lambda : LISTchunkParent_)) and (php_isset(lambda : LISTchunkMaxOffset_)) and RIFFchunk_[chunkname_][thisindex_]["offset"] + RIFFchunk_[chunkname_][thisindex_]["size"] <= LISTchunkMaxOffset_:
                                    RIFFchunk_[LISTchunkParent_][chunkname_][thisindex_]["offset"] = RIFFchunk_[chunkname_][thisindex_]["offset"]
                                    RIFFchunk_[LISTchunkParent_][chunkname_][thisindex_]["size"] = RIFFchunk_[chunkname_][thisindex_]["size"]
                                    RIFFchunk_[chunkname_][thisindex_]["offset"] = None
                                    RIFFchunk_[chunkname_][thisindex_]["size"] = None
                                    if (php_isset(lambda : RIFFchunk_[chunkname_][thisindex_])) and php_empty(lambda : RIFFchunk_[chunkname_][thisindex_]):
                                        RIFFchunk_[chunkname_][thisindex_] = None
                                    # end if
                                    if (php_isset(lambda : RIFFchunk_[chunkname_])) and php_empty(lambda : RIFFchunk_[chunkname_]):
                                        RIFFchunk_[chunkname_] = None
                                    # end if
                                    RIFFchunk_[LISTchunkParent_][chunkname_][thisindex_]["data"] = self.fread(chunksize_)
                                elif chunksize_ < 2048:
                                    #// only read data in if smaller than 2kB
                                    RIFFchunk_[chunkname_][thisindex_]["data"] = self.fread(chunksize_)
                                else:
                                    self.fseek(chunksize_, SEEK_CUR)
                                # end if
                                break
                            # end if
                        # end for
                        break
                    # end if
                # end for
            # end while
        except getid3_exception as e_:
            if e_.getcode() == 10:
                self.warning("RIFF parser: " + e_.getmessage())
            else:
                raise e_
            # end if
        # end try
        return RIFFchunk_
    # end def parseriff
    #// 
    #// @param string $RIFFdata
    #// 
    #// @return bool
    #//
    def parseriffdata(self, RIFFdata_=None):
        
        
        info_ = self.getid3.info
        if RIFFdata_:
            tempfile_ = php_tempnam(GETID3_TEMP_DIR, "getID3")
            fp_temp_ = fopen(tempfile_, "wb")
            RIFFdataLength_ = php_strlen(RIFFdata_)
            NewLengthString_ = getid3_lib.littleendian2string(RIFFdataLength_, 4)
            i_ = 0
            while i_ < 4:
                
                RIFFdata_[i_ + 4] = NewLengthString_[i_]
                i_ += 1
            # end while
            fwrite(fp_temp_, RIFFdata_)
            php_fclose(fp_temp_)
            getid3_temp_ = php_new_class("getID3", lambda : getID3())
            getid3_temp_.openfile(tempfile_)
            getid3_temp_.info["filesize"] = RIFFdataLength_
            getid3_temp_.info["filenamepath"] = info_["filenamepath"]
            getid3_temp_.info["tags"] = info_["tags"]
            getid3_temp_.info["warning"] = info_["warning"]
            getid3_temp_.info["error"] = info_["error"]
            getid3_temp_.info["comments"] = info_["comments"]
            getid3_temp_.info["audio"] = info_["audio"] if (php_isset(lambda : info_["audio"])) else Array()
            getid3_temp_.info["video"] = info_["video"] if (php_isset(lambda : info_["video"])) else Array()
            getid3_riff_ = php_new_class("getid3_riff", lambda : getid3_riff(getid3_temp_))
            getid3_riff_.analyze()
            info_["riff"] = getid3_temp_.info["riff"]
            info_["warning"] = getid3_temp_.info["warning"]
            info_["error"] = getid3_temp_.info["error"]
            info_["tags"] = getid3_temp_.info["tags"]
            info_["comments"] = getid3_temp_.info["comments"]
            getid3_riff_ = None
            getid3_temp_ = None
            unlink(tempfile_)
        # end if
        return False
    # end def parseriffdata
    #// 
    #// @param array $RIFFinfoArray
    #// @param array $CommentsTargetArray
    #// 
    #// @return bool
    #//
    @classmethod
    def parsecomments(self, RIFFinfoArray_=None, CommentsTargetArray_=None):
        
        
        RIFFinfoKeyLookup_ = Array({"IARL": "archivallocation", "IART": "artist", "ICDS": "costumedesigner", "ICMS": "commissionedby", "ICMT": "comment", "ICNT": "country", "ICOP": "copyright", "ICRD": "creationdate", "IDIM": "dimensions", "IDIT": "digitizationdate", "IDPI": "resolution", "IDST": "distributor", "IEDT": "editor", "IENG": "engineers", "IFRM": "accountofparts", "IGNR": "genre", "IKEY": "keywords", "ILGT": "lightness", "ILNG": "language", "IMED": "orignalmedium", "IMUS": "composer", "INAM": "title", "IPDS": "productiondesigner", "IPLT": "palette", "IPRD": "product", "IPRO": "producer", "IPRT": "part", "IRTD": "rating", "ISBJ": "subject", "ISFT": "software", "ISGN": "secondarygenre", "ISHP": "sharpness", "ISRC": "sourcesupplier", "ISRF": "digitizationsource", "ISTD": "productionstudio", "ISTR": "starring", "ITCH": "encoded_by", "IWEB": "url", "IWRI": "writer", "____": "comment"})
        for key_,value_ in RIFFinfoKeyLookup_:
            if (php_isset(lambda : RIFFinfoArray_[key_])):
                for commentid_,commentdata_ in RIFFinfoArray_[key_]:
                    if php_trim(commentdata_["data"]) != "":
                        if (php_isset(lambda : CommentsTargetArray_[value_])):
                            CommentsTargetArray_[value_][-1] = php_trim(commentdata_["data"])
                        else:
                            CommentsTargetArray_[value_] = Array(php_trim(commentdata_["data"]))
                        # end if
                    # end if
                # end for
            # end if
        # end for
        return True
    # end def parsecomments
    #// 
    #// @param string $WaveFormatExData
    #// 
    #// @return array
    #//
    @classmethod
    def parsewaveformatex(self, WaveFormatExData_=None):
        
        
        #// shortcut
        WaveFormatEx_ = Array()
        WaveFormatEx_["raw"] = Array()
        WaveFormatEx_raw_ = WaveFormatEx_["raw"]
        WaveFormatEx_raw_["wFormatTag"] = php_substr(WaveFormatExData_, 0, 2)
        WaveFormatEx_raw_["nChannels"] = php_substr(WaveFormatExData_, 2, 2)
        WaveFormatEx_raw_["nSamplesPerSec"] = php_substr(WaveFormatExData_, 4, 4)
        WaveFormatEx_raw_["nAvgBytesPerSec"] = php_substr(WaveFormatExData_, 8, 4)
        WaveFormatEx_raw_["nBlockAlign"] = php_substr(WaveFormatExData_, 12, 2)
        WaveFormatEx_raw_["wBitsPerSample"] = php_substr(WaveFormatExData_, 14, 2)
        if php_strlen(WaveFormatExData_) > 16:
            WaveFormatEx_raw_["cbSize"] = php_substr(WaveFormatExData_, 16, 2)
        # end if
        WaveFormatEx_raw_ = php_array_map("getid3_lib::LittleEndian2Int", WaveFormatEx_raw_)
        WaveFormatEx_["codec"] = self.wformattaglookup(WaveFormatEx_raw_["wFormatTag"])
        WaveFormatEx_["channels"] = WaveFormatEx_raw_["nChannels"]
        WaveFormatEx_["sample_rate"] = WaveFormatEx_raw_["nSamplesPerSec"]
        WaveFormatEx_["bitrate"] = WaveFormatEx_raw_["nAvgBytesPerSec"] * 8
        WaveFormatEx_["bits_per_sample"] = WaveFormatEx_raw_["wBitsPerSample"]
        return WaveFormatEx_
    # end def parsewaveformatex
    #// 
    #// @param string $WavPackChunkData
    #// 
    #// @return bool
    #//
    def parsewavpackheader(self, WavPackChunkData_=None):
        
        
        #// typedef struct {
        #// char ckID [4];
        #// long ckSize;
        #// short version;
        #// short bits;                // added for version 2.00
        #// short flags, shift;        // added for version 3.00
        #// long total_samples, crc, crc2;
        #// char extension [4], extra_bc, extras [3];
        #// } WavpackHeader;
        #// shortcut
        info_ = self.getid3.info
        info_["wavpack"] = Array()
        thisfile_wavpack_ = info_["wavpack"]
        thisfile_wavpack_["version"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData_, 0, 2))
        if thisfile_wavpack_["version"] >= 2:
            thisfile_wavpack_["bits"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData_, 2, 2))
        # end if
        if thisfile_wavpack_["version"] >= 3:
            thisfile_wavpack_["flags_raw"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData_, 4, 2))
            thisfile_wavpack_["shift"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData_, 6, 2))
            thisfile_wavpack_["total_samples"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData_, 8, 4))
            thisfile_wavpack_["crc1"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData_, 12, 4))
            thisfile_wavpack_["crc2"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData_, 16, 4))
            thisfile_wavpack_["extension"] = php_substr(WavPackChunkData_, 20, 4)
            thisfile_wavpack_["extra_bc"] = getid3_lib.littleendian2int(php_substr(WavPackChunkData_, 24, 1))
            i_ = 0
            while i_ <= 2:
                
                thisfile_wavpack_["extras"][-1] = getid3_lib.littleendian2int(php_substr(WavPackChunkData_, 25 + i_, 1))
                i_ += 1
            # end while
            #// shortcut
            thisfile_wavpack_["flags"] = Array()
            thisfile_wavpack_flags_ = thisfile_wavpack_["flags"]
            thisfile_wavpack_flags_["mono"] = php_bool(thisfile_wavpack_["flags_raw"] & 1)
            thisfile_wavpack_flags_["fast_mode"] = php_bool(thisfile_wavpack_["flags_raw"] & 2)
            thisfile_wavpack_flags_["raw_mode"] = php_bool(thisfile_wavpack_["flags_raw"] & 4)
            thisfile_wavpack_flags_["calc_noise"] = php_bool(thisfile_wavpack_["flags_raw"] & 8)
            thisfile_wavpack_flags_["high_quality"] = php_bool(thisfile_wavpack_["flags_raw"] & 16)
            thisfile_wavpack_flags_["3_byte_samples"] = php_bool(thisfile_wavpack_["flags_raw"] & 32)
            thisfile_wavpack_flags_["over_20_bits"] = php_bool(thisfile_wavpack_["flags_raw"] & 64)
            thisfile_wavpack_flags_["use_wvc"] = php_bool(thisfile_wavpack_["flags_raw"] & 128)
            thisfile_wavpack_flags_["noiseshaping"] = php_bool(thisfile_wavpack_["flags_raw"] & 256)
            thisfile_wavpack_flags_["very_fast_mode"] = php_bool(thisfile_wavpack_["flags_raw"] & 512)
            thisfile_wavpack_flags_["new_high_quality"] = php_bool(thisfile_wavpack_["flags_raw"] & 1024)
            thisfile_wavpack_flags_["cancel_extreme"] = php_bool(thisfile_wavpack_["flags_raw"] & 2048)
            thisfile_wavpack_flags_["cross_decorrelation"] = php_bool(thisfile_wavpack_["flags_raw"] & 4096)
            thisfile_wavpack_flags_["new_decorrelation"] = php_bool(thisfile_wavpack_["flags_raw"] & 8192)
            thisfile_wavpack_flags_["joint_stereo"] = php_bool(thisfile_wavpack_["flags_raw"] & 16384)
            thisfile_wavpack_flags_["extra_decorrelation"] = php_bool(thisfile_wavpack_["flags_raw"] & 32768)
            thisfile_wavpack_flags_["override_noiseshape"] = php_bool(thisfile_wavpack_["flags_raw"] & 65536)
            thisfile_wavpack_flags_["override_jointstereo"] = php_bool(thisfile_wavpack_["flags_raw"] & 131072)
            thisfile_wavpack_flags_["copy_source_filetime"] = php_bool(thisfile_wavpack_["flags_raw"] & 262144)
            thisfile_wavpack_flags_["create_exe"] = php_bool(thisfile_wavpack_["flags_raw"] & 524288)
        # end if
        return True
    # end def parsewavpackheader
    #// 
    #// @param string $BITMAPINFOHEADER
    #// @param bool   $littleEndian
    #// 
    #// @return array
    #//
    @classmethod
    def parsebitmapinfoheader(self, BITMAPINFOHEADER_=None, littleEndian_=None):
        if littleEndian_ is None:
            littleEndian_ = True
        # end if
        
        parsed_["biSize"] = php_substr(BITMAPINFOHEADER_, 0, 4)
        #// number of bytes required by the BITMAPINFOHEADER structure
        parsed_["biWidth"] = php_substr(BITMAPINFOHEADER_, 4, 4)
        #// width of the bitmap in pixels
        parsed_["biHeight"] = php_substr(BITMAPINFOHEADER_, 8, 4)
        #// height of the bitmap in pixels. If biHeight is positive, the bitmap is a 'bottom-up' DIB and its origin is the lower left corner. If biHeight is negative, the bitmap is a 'top-down' DIB and its origin is the upper left corner
        parsed_["biPlanes"] = php_substr(BITMAPINFOHEADER_, 12, 2)
        #// number of color planes on the target device. In most cases this value must be set to 1
        parsed_["biBitCount"] = php_substr(BITMAPINFOHEADER_, 14, 2)
        #// Specifies the number of bits per pixels
        parsed_["biSizeImage"] = php_substr(BITMAPINFOHEADER_, 20, 4)
        #// size of the bitmap data section of the image (the actual pixel data, excluding BITMAPINFOHEADER and RGBQUAD structures)
        parsed_["biXPelsPerMeter"] = php_substr(BITMAPINFOHEADER_, 24, 4)
        #// horizontal resolution, in pixels per metre, of the target device
        parsed_["biYPelsPerMeter"] = php_substr(BITMAPINFOHEADER_, 28, 4)
        #// vertical resolution, in pixels per metre, of the target device
        parsed_["biClrUsed"] = php_substr(BITMAPINFOHEADER_, 32, 4)
        #// actual number of color indices in the color table used by the bitmap. If this value is zero, the bitmap uses the maximum number of colors corresponding to the value of the biBitCount member for the compression mode specified by biCompression
        parsed_["biClrImportant"] = php_substr(BITMAPINFOHEADER_, 36, 4)
        #// number of color indices that are considered important for displaying the bitmap. If this value is zero, all colors are important
        parsed_ = php_array_map("getid3_lib::" + "Little" if littleEndian_ else "Big" + "Endian2Int", parsed_)
        parsed_["fourcc"] = php_substr(BITMAPINFOHEADER_, 16, 4)
        #// compression identifier
        return parsed_
    # end def parsebitmapinfoheader
    #// 
    #// @param string $DIVXTAG
    #// @param bool   $raw
    #// 
    #// @return array
    #//
    @classmethod
    def parsedivxtag(self, DIVXTAG_=None, raw_=None):
        if raw_ is None:
            raw_ = False
        # end if
        
        DIVXTAGgenre_ = Array({0: "Action", 1: "Action/Adventure", 2: "Adventure", 3: "Adult", 4: "Anime", 5: "Cartoon", 6: "Claymation", 7: "Comedy", 8: "Commercial", 9: "Documentary", 10: "Drama", 11: "Home Video", 12: "Horror", 13: "Infomercial", 14: "Interactive", 15: "Mystery", 16: "Music Video", 17: "Other", 18: "Religion", 19: "Sci Fi", 20: "Thriller", 21: "Western"})
        DIVXTAGrating_ = Array({0: "Unrated", 1: "G", 2: "PG", 3: "PG-13", 4: "R", 5: "NC-17"})
        parsed_ = Array()
        parsed_["title"] = php_trim(php_substr(DIVXTAG_, 0, 32))
        parsed_["artist"] = php_trim(php_substr(DIVXTAG_, 32, 28))
        parsed_["year"] = php_intval(php_trim(php_substr(DIVXTAG_, 60, 4)))
        parsed_["comment"] = php_trim(php_substr(DIVXTAG_, 64, 48))
        parsed_["genre_id"] = php_intval(php_trim(php_substr(DIVXTAG_, 112, 3)))
        parsed_["rating_id"] = php_ord(php_substr(DIVXTAG_, 115, 1))
        #// $parsed['padding'] =             substr($DIVXTAG, 116,  5);  // 5-byte null
        #// $parsed['magic']   =             substr($DIVXTAG, 121,  7);  // "DIVXTAG"
        parsed_["genre"] = DIVXTAGgenre_[parsed_["genre_id"]] if (php_isset(lambda : DIVXTAGgenre_[parsed_["genre_id"]])) else parsed_["genre_id"]
        parsed_["rating"] = DIVXTAGrating_[parsed_["rating_id"]] if (php_isset(lambda : DIVXTAGrating_[parsed_["rating_id"]])) else parsed_["rating_id"]
        if (not raw_):
            parsed_["genre_id"] = None
            parsed_["rating_id"] = None
            for key_,value_ in parsed_:
                if php_empty(lambda : value_):
                    parsed_[key_] = None
                # end if
            # end for
        # end if
        for tag_,value_ in parsed_:
            parsed_[tag_] = Array(value_)
        # end for
        return parsed_
    # end def parsedivxtag
    #// 
    #// @param string $tagshortname
    #// 
    #// @return string
    #//
    @classmethod
    def wavesndmtaglookup(self, tagshortname_=None):
        
        
        begin_ = 0
        #// This is not a comment!
        #// ©kwd    keywords
        #// ©BPM    bpm
        #// ©trt    tracktitle
        #// ©des    description
        #// ©gen    category
        #// ©fin    featuredinstrument
        #// ©LID    longid
        #// ©bex    bwdescription
        #// ©pub    publisher
        #// ©cdt    cdtitle
        #// ©alb    library
        #// ©com    composer
        #//
        return getid3_lib.embeddedlookup(tagshortname_, begin_, 0, __FILE__, "riff-sndm")
    # end def wavesndmtaglookup
    #// 
    #// @param int $wFormatTag
    #// 
    #// @return string
    #//
    @classmethod
    def wformattaglookup(self, wFormatTag_=None):
        
        
        begin_ = 0
        #// This is not a comment!
        #// 0x0000  Microsoft Unknown Wave Format
        #// 0x0001  Pulse Code Modulation (PCM)
        #// 0x0002  Microsoft ADPCM
        #// 0x0003  IEEE Float
        #// 0x0004  Compaq Computer VSELP
        #// 0x0005  IBM CVSD
        #// 0x0006  Microsoft A-Law
        #// 0x0007  Microsoft mu-Law
        #// 0x0008  Microsoft DTS
        #// 0x0010  OKI ADPCM
        #// 0x0011  Intel DVI/IMA ADPCM
        #// 0x0012  Videologic MediaSpace ADPCM
        #// 0x0013  Sierra Semiconductor ADPCM
        #// 0x0014  Antex Electronics G.723 ADPCM
        #// 0x0015  DSP Solutions DigiSTD
        #// 0x0016  DSP Solutions DigiFIX
        #// 0x0017  Dialogic OKI ADPCM
        #// 0x0018  MediaVision ADPCM
        #// 0x0019  Hewlett-Packard CU
        #// 0x0020  Yamaha ADPCM
        #// 0x0021  Speech Compression Sonarc
        #// 0x0022  DSP Group TrueSpeech
        #// 0x0023  Echo Speech EchoSC1
        #// 0x0024  Audiofile AF36
        #// 0x0025  Audio Processing Technology APTX
        #// 0x0026  AudioFile AF10
        #// 0x0027  Prosody 1612
        #// 0x0028  LRC
        #// 0x0030  Dolby AC2
        #// 0x0031  Microsoft GSM 6.10
        #// 0x0032  MSNAudio
        #// 0x0033  Antex Electronics ADPCME
        #// 0x0034  Control Resources VQLPC
        #// 0x0035  DSP Solutions DigiREAL
        #// 0x0036  DSP Solutions DigiADPCM
        #// 0x0037  Control Resources CR10
        #// 0x0038  Natural MicroSystems VBXADPCM
        #// 0x0039  Crystal Semiconductor IMA ADPCM
        #// 0x003A  EchoSC3
        #// 0x003B  Rockwell ADPCM
        #// 0x003C  Rockwell Digit LK
        #// 0x003D  Xebec
        #// 0x0040  Antex Electronics G.721 ADPCM
        #// 0x0041  G.728 CELP
        #// 0x0042  MSG723
        #// 0x0050  MPEG Layer-2 or Layer-1
        #// 0x0052  RT24
        #// 0x0053  PAC
        #// 0x0055  MPEG Layer-3
        #// 0x0059  Lucent G.723
        #// 0x0060  Cirrus
        #// 0x0061  ESPCM
        #// 0x0062  Voxware
        #// 0x0063  Canopus Atrac
        #// 0x0064  G.726 ADPCM
        #// 0x0065  G.722 ADPCM
        #// 0x0066  DSAT
        #// 0x0067  DSAT Display
        #// 0x0069  Voxware Byte Aligned
        #// 0x0070  Voxware AC8
        #// 0x0071  Voxware AC10
        #// 0x0072  Voxware AC16
        #// 0x0073  Voxware AC20
        #// 0x0074  Voxware MetaVoice
        #// 0x0075  Voxware MetaSound
        #// 0x0076  Voxware RT29HW
        #// 0x0077  Voxware VR12
        #// 0x0078  Voxware VR18
        #// 0x0079  Voxware TQ40
        #// 0x0080  Softsound
        #// 0x0081  Voxware TQ60
        #// 0x0082  MSRT24
        #// 0x0083  G.729A
        #// 0x0084  MVI MV12
        #// 0x0085  DF G.726
        #// 0x0086  DF GSM610
        #// 0x0088  ISIAudio
        #// 0x0089  Onlive
        #// 0x0091  SBC24
        #// 0x0092  Dolby AC3 SPDIF
        #// 0x0093  MediaSonic G.723
        #// 0x0094  Aculab PLC    Prosody 8kbps
        #// 0x0097  ZyXEL ADPCM
        #// 0x0098  Philips LPCBB
        #// 0x0099  Packed
        #// 0x00FF  AAC
        #// 0x0100  Rhetorex ADPCM
        #// 0x0101  IBM mu-law
        #// 0x0102  IBM A-law
        #// 0x0103  IBM AVC Adaptive Differential Pulse Code Modulation (ADPCM)
        #// 0x0111  Vivo G.723
        #// 0x0112  Vivo Siren
        #// 0x0123  Digital G.723
        #// 0x0125  Sanyo LD ADPCM
        #// 0x0130  Sipro Lab Telecom ACELP NET
        #// 0x0131  Sipro Lab Telecom ACELP 4800
        #// 0x0132  Sipro Lab Telecom ACELP 8V3
        #// 0x0133  Sipro Lab Telecom G.729
        #// 0x0134  Sipro Lab Telecom G.729A
        #// 0x0135  Sipro Lab Telecom Kelvin
        #// 0x0140  Windows Media Video V8
        #// 0x0150  Qualcomm PureVoice
        #// 0x0151  Qualcomm HalfRate
        #// 0x0155  Ring Zero Systems TUB GSM
        #// 0x0160  Microsoft Audio 1
        #// 0x0161  Windows Media Audio V7 / V8 / V9
        #// 0x0162  Windows Media Audio Professional V9
        #// 0x0163  Windows Media Audio Lossless V9
        #// 0x0200  Creative Labs ADPCM
        #// 0x0202  Creative Labs Fastspeech8
        #// 0x0203  Creative Labs Fastspeech10
        #// 0x0210  UHER Informatic GmbH ADPCM
        #// 0x0220  Quarterdeck
        #// 0x0230  I-link Worldwide VC
        #// 0x0240  Aureal RAW Sport
        #// 0x0250  Interactive Products HSX
        #// 0x0251  Interactive Products RPELP
        #// 0x0260  Consistent Software CS2
        #// 0x0270  Sony SCX
        #// 0x0300  Fujitsu FM Towns Snd
        #// 0x0400  BTV Digital
        #// 0x0401  Intel Music Coder
        #// 0x0450  QDesign Music
        #// 0x0680  VME VMPCM
        #// 0x0681  AT&T Labs TPC
        #// 0x08AE  ClearJump LiteWave
        #// 0x1000  Olivetti GSM
        #// 0x1001  Olivetti ADPCM
        #// 0x1002  Olivetti CELP
        #// 0x1003  Olivetti SBC
        #// 0x1004  Olivetti OPR
        #// 0x1100  Lernout & Hauspie Codec (0x1100)
        #// 0x1101  Lernout & Hauspie CELP Codec (0x1101)
        #// 0x1102  Lernout & Hauspie SBC Codec (0x1102)
        #// 0x1103  Lernout & Hauspie SBC Codec (0x1103)
        #// 0x1104  Lernout & Hauspie SBC Codec (0x1104)
        #// 0x1400  Norris
        #// 0x1401  AT&T ISIAudio
        #// 0x1500  Soundspace Music Compression
        #// 0x181C  VoxWare RT24 Speech
        #// 0x1FC4  NCT Soft ALF2CD (www.nctsoft.com)
        #// 0x2000  Dolby AC3
        #// 0x2001  Dolby DTS
        #// 0x2002  WAVE_FORMAT_14_4
        #// 0x2003  WAVE_FORMAT_28_8
        #// 0x2004  WAVE_FORMAT_COOK
        #// 0x2005  WAVE_FORMAT_DNET
        #// 0x674F  Ogg Vorbis 1
        #// 0x6750  Ogg Vorbis 2
        #// 0x6751  Ogg Vorbis 3
        #// 0x676F  Ogg Vorbis 1+
        #// 0x6770  Ogg Vorbis 2+
        #// 0x6771  Ogg Vorbis 3+
        #// 0x7A21  GSM-AMR (CBR, no SID)
        #// 0x7A22  GSM-AMR (VBR, including SID)
        #// 0xFFFE  WAVE_FORMAT_EXTENSIBLE
        #// 0xFFFF  WAVE_FORMAT_DEVELOPMENT
        #//
        return getid3_lib.embeddedlookup("0x" + php_str_pad(php_strtoupper(dechex(wFormatTag_)), 4, "0", STR_PAD_LEFT), begin_, 0, __FILE__, "riff-wFormatTag")
    # end def wformattaglookup
    #// 
    #// @param string $fourcc
    #// 
    #// @return string
    #//
    @classmethod
    def fourcclookup(self, fourcc_=None):
        
        
        begin_ = 0
        #// This is not a comment!
        #// swot    http://developer.apple.com/qa/snd/snd07.html
        #// ____    No Codec (____)
        #// _BIT    BI_BITFIELDS (Raw RGB)
        #// _JPG    JPEG compressed
        #// _PNG    PNG compressed W3C/ISO/IEC (RFC-2083)
        #// _RAW    Full Frames (Uncompressed)
        #// _RGB    Raw RGB Bitmap
        #// _RL4    RLE 4bpp RGB
        #// _RL8    RLE 8bpp RGB
        #// 3IV1    3ivx MPEG-4 v1
        #// 3IV2    3ivx MPEG-4 v2
        #// 3IVX    3ivx MPEG-4
        #// AASC    Autodesk Animator
        #// ABYR    Kensington ?ABYR?
        #// AEMI    Array Microsystems VideoONE MPEG1-I Capture
        #// AFLC    Autodesk Animator FLC
        #// AFLI    Autodesk Animator FLI
        #// AMPG    Array Microsystems VideoONE MPEG
        #// ANIM    Intel RDX (ANIM)
        #// AP41    AngelPotion Definitive
        #// ASV1    Asus Video v1
        #// ASV2    Asus Video v2
        #// ASVX    Asus Video 2.0 (audio)
        #// AUR2    AuraVision Aura 2 Codec - YUV 4:2:2
        #// AURA    AuraVision Aura 1 Codec - YUV 4:1:1
        #// AVDJ    Independent JPEG Group\'s codec (AVDJ)
        #// AVRN    Independent JPEG Group\'s codec (AVRN)
        #// AYUV    4:4:4 YUV (AYUV)
        #// AZPR    Quicktime Apple Video (AZPR)
        #// BGR     Raw RGB32
        #// BLZ0    Blizzard DivX MPEG-4
        #// BTVC    Conexant Composite Video
        #// BINK    RAD Game Tools Bink Video
        #// BT20    Conexant Prosumer Video
        #// BTCV    Conexant Composite Video Codec
        #// BW10    Data Translation Broadway MPEG Capture
        #// CC12    Intel YUV12
        #// CDVC    Canopus DV
        #// CFCC    Digital Processing Systems DPS Perception
        #// CGDI    Microsoft Office 97 Camcorder Video
        #// CHAM    Winnov Caviara Champagne
        #// CJPG    Creative WebCam JPEG
        #// CLJR    Cirrus Logic YUV 4:1:1
        #// CMYK    Common Data Format in Printing (Colorgraph)
        #// CPLA    Weitek 4:2:0 YUV Planar
        #// CRAM    Microsoft Video 1 (CRAM)
        #// cvid    Radius Cinepak
        #// CVID    Radius Cinepak
        #// CWLT    Microsoft Color WLT DIB
        #// CYUV    Creative Labs YUV
        #// CYUY    ATI YUV
        #// D261    H.261
        #// D263    H.263
        #// DIB     Device Independent Bitmap
        #// DIV1    FFmpeg OpenDivX
        #// DIV2    Microsoft MPEG-4 v1/v2
        #// DIV3    DivX ;-) MPEG-4 v3.x Low-Motion
        #// DIV4    DivX ;-) MPEG-4 v3.x Fast-Motion
        #// DIV5    DivX MPEG-4 v5.x
        #// DIV6    DivX ;-) (MS MPEG-4 v3.x)
        #// DIVX    DivX MPEG-4 v4 (OpenDivX / Project Mayo)
        #// divx    DivX MPEG-4
        #// DMB1    Matrox Rainbow Runner hardware MJPEG
        #// DMB2    Paradigm MJPEG
        #// DSVD    ?DSVD?
        #// DUCK    Duck TrueMotion 1.0
        #// DPS0    DPS/Leitch Reality Motion JPEG
        #// DPSC    DPS/Leitch PAR Motion JPEG
        #// DV25    Matrox DVCPRO codec
        #// DV50    Matrox DVCPRO50 codec
        #// DVC     IEC 61834 and SMPTE 314M (DVC/DV Video)
        #// DVCP    IEC 61834 and SMPTE 314M (DVC/DV Video)
        #// DVHD    IEC Standard DV 1125 lines @ 30fps / 1250 lines @ 25fps
        #// DVMA    Darim Vision DVMPEG (dummy for MPEG compressor) (www.darvision.com)
        #// DVSL    IEC Standard DV compressed in SD (SDL)
        #// DVAN    ?DVAN?
        #// DVE2    InSoft DVE-2 Videoconferencing
        #// dvsd    IEC 61834 and SMPTE 314M DVC/DV Video
        #// DVSD    IEC 61834 and SMPTE 314M DVC/DV Video
        #// DVX1    Lucent DVX1000SP Video Decoder
        #// DVX2    Lucent DVX2000S Video Decoder
        #// DVX3    Lucent DVX3000S Video Decoder
        #// DX50    DivX v5
        #// DXT1    Microsoft DirectX Compressed Texture (DXT1)
        #// DXT2    Microsoft DirectX Compressed Texture (DXT2)
        #// DXT3    Microsoft DirectX Compressed Texture (DXT3)
        #// DXT4    Microsoft DirectX Compressed Texture (DXT4)
        #// DXT5    Microsoft DirectX Compressed Texture (DXT5)
        #// DXTC    Microsoft DirectX Compressed Texture (DXTC)
        #// DXTn    Microsoft DirectX Compressed Texture (DXTn)
        #// EM2V    Etymonix MPEG-2 I-frame (www.etymonix.com)
        #// EKQ0    Elsa ?EKQ0?
        #// ELK0    Elsa ?ELK0?
        #// ESCP    Eidos Escape
        #// ETV1    eTreppid Video ETV1
        #// ETV2    eTreppid Video ETV2
        #// ETVC    eTreppid Video ETVC
        #// FLIC    Autodesk FLI/FLC Animation
        #// FLV1    Sorenson Spark
        #// FLV4    On2 TrueMotion VP6
        #// FRWT    Darim Vision Forward Motion JPEG (www.darvision.com)
        #// FRWU    Darim Vision Forward Uncompressed (www.darvision.com)
        #// FLJP    D-Vision Field Encoded Motion JPEG
        #// FPS1    FRAPS v1
        #// FRWA    SoftLab-Nsk Forward Motion JPEG w/ alpha channel
        #// FRWD    SoftLab-Nsk Forward Motion JPEG
        #// FVF1    Iterated Systems Fractal Video Frame
        #// GLZW    Motion LZW (gabest@freemail.hu)
        #// GPEG    Motion JPEG (gabest@freemail.hu)
        #// GWLT    Microsoft Greyscale WLT DIB
        #// H260    Intel ITU H.260 Videoconferencing
        #// H261    Intel ITU H.261 Videoconferencing
        #// H262    Intel ITU H.262 Videoconferencing
        #// H263    Intel ITU H.263 Videoconferencing
        #// H264    Intel ITU H.264 Videoconferencing
        #// H265    Intel ITU H.265 Videoconferencing
        #// H266    Intel ITU H.266 Videoconferencing
        #// H267    Intel ITU H.267 Videoconferencing
        #// H268    Intel ITU H.268 Videoconferencing
        #// H269    Intel ITU H.269 Videoconferencing
        #// HFYU    Huffman Lossless Codec
        #// HMCR    Rendition Motion Compensation Format (HMCR)
        #// HMRR    Rendition Motion Compensation Format (HMRR)
        #// I263    FFmpeg I263 decoder
        #// IF09    Indeo YVU9 ("YVU9 with additional delta-frame info after the U plane")
        #// IUYV    Interlaced version of UYVY (www.leadtools.com)
        #// IY41    Interlaced version of Y41P (www.leadtools.com)
        #// IYU1    12 bit format used in mode 2 of the IEEE 1394 Digital Camera 1.04 spec    IEEE standard
        #// IYU2    24 bit format used in mode 2 of the IEEE 1394 Digital Camera 1.04 spec    IEEE standard
        #// IYUV    Planar YUV format (8-bpp Y plane, followed by 8-bpp 2×2 U and V planes)
        #// i263    Intel ITU H.263 Videoconferencing (i263)
        #// I420    Intel Indeo 4
        #// IAN     Intel Indeo 4 (RDX)
        #// ICLB    InSoft CellB Videoconferencing
        #// IGOR    Power DVD
        #// IJPG    Intergraph JPEG
        #// ILVC    Intel Layered Video
        #// ILVR    ITU-T H.263+
        #// IPDV    I-O Data Device Giga AVI DV Codec
        #// IR21    Intel Indeo 2.1
        #// IRAW    Intel YUV Uncompressed
        #// IV30    Intel Indeo 3.0
        #// IV31    Intel Indeo 3.1
        #// IV32    Ligos Indeo 3.2
        #// IV33    Ligos Indeo 3.3
        #// IV34    Ligos Indeo 3.4
        #// IV35    Ligos Indeo 3.5
        #// IV36    Ligos Indeo 3.6
        #// IV37    Ligos Indeo 3.7
        #// IV38    Ligos Indeo 3.8
        #// IV39    Ligos Indeo 3.9
        #// IV40    Ligos Indeo Interactive 4.0
        #// IV41    Ligos Indeo Interactive 4.1
        #// IV42    Ligos Indeo Interactive 4.2
        #// IV43    Ligos Indeo Interactive 4.3
        #// IV44    Ligos Indeo Interactive 4.4
        #// IV45    Ligos Indeo Interactive 4.5
        #// IV46    Ligos Indeo Interactive 4.6
        #// IV47    Ligos Indeo Interactive 4.7
        #// IV48    Ligos Indeo Interactive 4.8
        #// IV49    Ligos Indeo Interactive 4.9
        #// IV50    Ligos Indeo Interactive 5.0
        #// JBYR    Kensington ?JBYR?
        #// JPEG    Still Image JPEG DIB
        #// JPGL    Pegasus Lossless Motion JPEG
        #// KMVC    Team17 Software Karl Morton\'s Video Codec
        #// LSVM    Vianet Lighting Strike Vmail (Streaming) (www.vianet.com)
        #// LEAD    LEAD Video Codec
        #// Ljpg    LEAD MJPEG Codec
        #// MDVD    Alex MicroDVD Video (hacked MS MPEG-4) (www.tiasoft.de)
        #// MJPA    Morgan Motion JPEG (MJPA) (www.morgan-multimedia.com)
        #// MJPB    Morgan Motion JPEG (MJPB) (www.morgan-multimedia.com)
        #// MMES    Matrox MPEG-2 I-frame
        #// MP2v    Microsoft S-Mpeg 4 version 1 (MP2v)
        #// MP42    Microsoft S-Mpeg 4 version 2 (MP42)
        #// MP43    Microsoft S-Mpeg 4 version 3 (MP43)
        #// MP4S    Microsoft S-Mpeg 4 version 3 (MP4S)
        #// MP4V    FFmpeg MPEG-4
        #// MPG1    FFmpeg MPEG 1/2
        #// MPG2    FFmpeg MPEG 1/2
        #// MPG3    FFmpeg DivX ;-) (MS MPEG-4 v3)
        #// MPG4    Microsoft MPEG-4
        #// MPGI    Sigma Designs MPEG
        #// MPNG    PNG images decoder
        #// MSS1    Microsoft Windows Screen Video
        #// MSZH    LCL (Lossless Codec Library) (www.geocities.co.jp/Playtown-Denei/2837/LRC.htm)
        #// M261    Microsoft H.261
        #// M263    Microsoft H.263
        #// M4S2    Microsoft Fully Compliant MPEG-4 v2 simple profile (M4S2)
        #// m4s2    Microsoft Fully Compliant MPEG-4 v2 simple profile (m4s2)
        #// MC12    ATI Motion Compensation Format (MC12)
        #// MCAM    ATI Motion Compensation Format (MCAM)
        #// MJ2C    Morgan Multimedia Motion JPEG2000
        #// mJPG    IBM Motion JPEG w/ Huffman Tables
        #// MJPG    Microsoft Motion JPEG DIB
        #// MP42    Microsoft MPEG-4 (low-motion)
        #// MP43    Microsoft MPEG-4 (fast-motion)
        #// MP4S    Microsoft MPEG-4 (MP4S)
        #// mp4s    Microsoft MPEG-4 (mp4s)
        #// MPEG    Chromatic Research MPEG-1 Video I-Frame
        #// MPG4    Microsoft MPEG-4 Video High Speed Compressor
        #// MPGI    Sigma Designs MPEG
        #// MRCA    FAST Multimedia Martin Regen Codec
        #// MRLE    Microsoft Run Length Encoding
        #// MSVC    Microsoft Video 1
        #// MTX1    Matrox ?MTX1?
        #// MTX2    Matrox ?MTX2?
        #// MTX3    Matrox ?MTX3?
        #// MTX4    Matrox ?MTX4?
        #// MTX5    Matrox ?MTX5?
        #// MTX6    Matrox ?MTX6?
        #// MTX7    Matrox ?MTX7?
        #// MTX8    Matrox ?MTX8?
        #// MTX9    Matrox ?MTX9?
        #// MV12    Motion Pixels Codec (old)
        #// MWV1    Aware Motion Wavelets
        #// nAVI    SMR Codec (hack of Microsoft MPEG-4) (IRC #shadowrealm)
        #// NT00    NewTek LightWave HDTV YUV w/ Alpha (www.newtek.com)
        #// NUV1    NuppelVideo
        #// NTN1    Nogatech Video Compression 1
        #// NVS0    nVidia GeForce Texture (NVS0)
        #// NVS1    nVidia GeForce Texture (NVS1)
        #// NVS2    nVidia GeForce Texture (NVS2)
        #// NVS3    nVidia GeForce Texture (NVS3)
        #// NVS4    nVidia GeForce Texture (NVS4)
        #// NVS5    nVidia GeForce Texture (NVS5)
        #// NVT0    nVidia GeForce Texture (NVT0)
        #// NVT1    nVidia GeForce Texture (NVT1)
        #// NVT2    nVidia GeForce Texture (NVT2)
        #// NVT3    nVidia GeForce Texture (NVT3)
        #// NVT4    nVidia GeForce Texture (NVT4)
        #// NVT5    nVidia GeForce Texture (NVT5)
        #// PIXL    MiroXL, Pinnacle PCTV
        #// PDVC    I-O Data Device Digital Video Capture DV codec
        #// PGVV    Radius Video Vision
        #// PHMO    IBM Photomotion
        #// PIM1    MPEG Realtime (Pinnacle Cards)
        #// PIM2    Pegasus Imaging ?PIM2?
        #// PIMJ    Pegasus Imaging Lossless JPEG
        #// PVEZ    Horizons Technology PowerEZ
        #// PVMM    PacketVideo Corporation MPEG-4
        #// PVW2    Pegasus Imaging Wavelet Compression
        #// Q1.0    Q-Team\'s QPEG 1.0 (www.q-team.de)
        #// Q1.1    Q-Team\'s QPEG 1.1 (www.q-team.de)
        #// QPEG    Q-Team QPEG 1.0
        #// qpeq    Q-Team QPEG 1.1
        #// RGB     Raw BGR32
        #// RGBA    Raw RGB w/ Alpha
        #// RMP4    REALmagic MPEG-4 (unauthorized XVID copy) (www.sigmadesigns.com)
        #// ROQV    Id RoQ File Video Decoder
        #// RPZA    Quicktime Apple Video (RPZA)
        #// RUD0    Rududu video codec (http://rududu.ifrance.com/rududu/)
        #// RV10    RealVideo 1.0 (aka RealVideo 5.0)
        #// RV13    RealVideo 1.0 (RV13)
        #// RV20    RealVideo G2
        #// RV30    RealVideo 8
        #// RV40    RealVideo 9
        #// RGBT    Raw RGB w/ Transparency
        #// RLE     Microsoft Run Length Encoder
        #// RLE4    Run Length Encoded (4bpp, 16-color)
        #// RLE8    Run Length Encoded (8bpp, 256-color)
        #// RT21    Intel Indeo RealTime Video 2.1
        #// rv20    RealVideo G2
        #// rv30    RealVideo 8
        #// RVX     Intel RDX (RVX )
        #// SMC     Apple Graphics (SMC )
        #// SP54    Logitech Sunplus Sp54 Codec for Mustek GSmart Mini 2
        #// SPIG    Radius Spigot
        #// SVQ3    Sorenson Video 3 (Apple Quicktime 5)
        #// s422    Tekram VideoCap C210 YUV 4:2:2
        #// SDCC    Sun Communication Digital Camera Codec
        #// SFMC    CrystalNet Surface Fitting Method
        #// SMSC    Radius SMSC
        #// SMSD    Radius SMSD
        #// smsv    WorldConnect Wavelet Video
        #// SPIG    Radius Spigot
        #// SPLC    Splash Studios ACM Audio Codec (www.splashstudios.net)
        #// SQZ2    Microsoft VXTreme Video Codec V2
        #// STVA    ST Microelectronics CMOS Imager Data (Bayer)
        #// STVB    ST Microelectronics CMOS Imager Data (Nudged Bayer)
        #// STVC    ST Microelectronics CMOS Imager Data (Bunched)
        #// STVX    ST Microelectronics CMOS Imager Data (Extended CODEC Data Format)
        #// STVY    ST Microelectronics CMOS Imager Data (Extended CODEC Data Format with Correction Data)
        #// SV10    Sorenson Video R1
        #// SVQ1    Sorenson Video
        #// T420    Toshiba YUV 4:2:0
        #// TM2A    Duck TrueMotion Archiver 2.0 (www.duck.com)
        #// TVJP    Pinnacle/Truevision Targa 2000 board (TVJP)
        #// TVMJ    Pinnacle/Truevision Targa 2000 board (TVMJ)
        #// TY0N    Tecomac Low-Bit Rate Codec (www.tecomac.com)
        #// TY2C    Trident Decompression Driver
        #// TLMS    TeraLogic Motion Intraframe Codec (TLMS)
        #// TLST    TeraLogic Motion Intraframe Codec (TLST)
        #// TM20    Duck TrueMotion 2.0
        #// TM2X    Duck TrueMotion 2X
        #// TMIC    TeraLogic Motion Intraframe Codec (TMIC)
        #// TMOT    Horizons Technology TrueMotion S
        #// tmot    Horizons TrueMotion Video Compression
        #// TR20    Duck TrueMotion RealTime 2.0
        #// TSCC    TechSmith Screen Capture Codec
        #// TV10    Tecomac Low-Bit Rate Codec
        #// TY2N    Trident ?TY2N?
        #// U263    UB Video H.263/H.263+/H.263++ Decoder
        #// UMP4    UB Video MPEG 4 (www.ubvideo.com)
        #// UYNV    Nvidia UYVY packed 4:2:2
        #// UYVP    Evans & Sutherland YCbCr 4:2:2 extended precision
        #// UCOD    eMajix.com ClearVideo
        #// ULTI    IBM Ultimotion
        #// UYVY    UYVY packed 4:2:2
        #// V261    Lucent VX2000S
        #// VIFP    VFAPI Reader Codec (www.yks.ne.jp/~hori/)
        #// VIV1    FFmpeg H263+ decoder
        #// VIV2    Vivo H.263
        #// VQC2    Vector-quantised codec 2 (research) http://eprints.ecs.soton.ac.uk/archive/00001310/01/VTC97-js.pdf)
        #// VTLP    Alaris VideoGramPiX
        #// VYU9    ATI YUV (VYU9)
        #// VYUY    ATI YUV (VYUY)
        #// V261    Lucent VX2000S
        #// V422    Vitec Multimedia 24-bit YUV 4:2:2 Format
        #// V655    Vitec Multimedia 16-bit YUV 4:2:2 Format
        #// VCR1    ATI Video Codec 1
        #// VCR2    ATI Video Codec 2
        #// VCR3    ATI VCR 3.0
        #// VCR4    ATI VCR 4.0
        #// VCR5    ATI VCR 5.0
        #// VCR6    ATI VCR 6.0
        #// VCR7    ATI VCR 7.0
        #// VCR8    ATI VCR 8.0
        #// VCR9    ATI VCR 9.0
        #// VDCT    Vitec Multimedia Video Maker Pro DIB
        #// VDOM    VDOnet VDOWave
        #// VDOW    VDOnet VDOLive (H.263)
        #// VDTZ    Darim Vison VideoTizer YUV
        #// VGPX    Alaris VideoGramPiX
        #// VIDS    Vitec Multimedia YUV 4:2:2 CCIR 601 for V422
        #// VIVO    Vivo H.263 v2.00
        #// vivo    Vivo H.263
        #// VIXL    Miro/Pinnacle Video XL
        #// VLV1    VideoLogic/PURE Digital Videologic Capture
        #// VP30    On2 VP3.0
        #// VP31    On2 VP3.1
        #// VP6F    On2 TrueMotion VP6
        #// VX1K    Lucent VX1000S Video Codec
        #// VX2K    Lucent VX2000S Video Codec
        #// VXSP    Lucent VX1000SP Video Codec
        #// WBVC    Winbond W9960
        #// WHAM    Microsoft Video 1 (WHAM)
        #// WINX    Winnov Software Compression
        #// WJPG    AverMedia Winbond JPEG
        #// WMV1    Windows Media Video V7
        #// WMV2    Windows Media Video V8
        #// WMV3    Windows Media Video V9
        #// WNV1    Winnov Hardware Compression
        #// XYZP    Extended PAL format XYZ palette (www.riff.org)
        #// x263    Xirlink H.263
        #// XLV0    NetXL Video Decoder
        #// XMPG    Xing MPEG (I-Frame only)
        #// XVID    XviD MPEG-4 (www.xvid.org)
        #// XXAN    ?XXAN?
        #// YU92    Intel YUV (YU92)
        #// YUNV    Nvidia Uncompressed YUV 4:2:2
        #// YUVP    Extended PAL format YUV palette (www.riff.org)
        #// Y211    YUV 2:1:1 Packed
        #// Y411    YUV 4:1:1 Packed
        #// Y41B    Weitek YUV 4:1:1 Planar
        #// Y41P    Brooktree PC1 YUV 4:1:1 Packed
        #// Y41T    Brooktree PC1 YUV 4:1:1 with transparency
        #// Y42B    Weitek YUV 4:2:2 Planar
        #// Y42T    Brooktree UYUV 4:2:2 with transparency
        #// Y422    ADS Technologies Copy of UYVY used in Pyro WebCam firewire camera
        #// Y800    Simple, single Y plane for monochrome images
        #// Y8      Grayscale video
        #// YC12    Intel YUV 12 codec
        #// YUV8    Winnov Caviar YUV8
        #// YUV9    Intel YUV9
        #// YUY2    Uncompressed YUV 4:2:2
        #// YUYV    Canopus YUV
        #// YV12    YVU12 Planar
        #// YVU9    Intel YVU9 Planar (8-bpp Y plane, followed by 8-bpp 4x4 U and V planes)
        #// YVYU    YVYU 4:2:2 Packed
        #// ZLIB    Lossless Codec Library zlib compression (www.geocities.co.jp/Playtown-Denei/2837/LRC.htm)
        #// ZPEG    Metheus Video Zipper
        #//
        return getid3_lib.embeddedlookup(fourcc_, begin_, 0, __FILE__, "riff-fourcc")
    # end def fourcclookup
    #// 
    #// @param string $byteword
    #// @param bool   $signed
    #// 
    #// @return int|float|false
    #//
    def eitherendian2int(self, byteword_=None, signed_=None):
        if signed_ is None:
            signed_ = False
        # end if
        
        if self.container == "riff":
            return getid3_lib.littleendian2int(byteword_, signed_)
        # end if
        return getid3_lib.bigendian2int(byteword_, False, signed_)
    # end def eitherendian2int
# end class getid3_riff
