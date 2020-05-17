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
#// module.tag.id3v1.php
#// module for analyzing ID3v1 tags
#// dependencies: NONE
#// 
#//
class getid3_id3v1(getid3_handler):
    #// 
    #// @return bool
    #//
    def analyze(self):
        
        
        info_ = self.getid3.info
        if (not getid3_lib.intvaluesupported(info_["filesize"])):
            self.warning("Unable to check for ID3v1 because file is larger than " + round(PHP_INT_MAX / 1073741824) + "GB")
            return False
        # end if
        self.fseek(-256, SEEK_END)
        preid3v1_ = self.fread(128)
        id3v1tag_ = self.fread(128)
        if php_substr(id3v1tag_, 0, 3) == "TAG":
            info_["avdataend"] = info_["filesize"] - 128
            ParsedID3v1_["title"] = self.cutfield(php_substr(id3v1tag_, 3, 30))
            ParsedID3v1_["artist"] = self.cutfield(php_substr(id3v1tag_, 33, 30))
            ParsedID3v1_["album"] = self.cutfield(php_substr(id3v1tag_, 63, 30))
            ParsedID3v1_["year"] = self.cutfield(php_substr(id3v1tag_, 93, 4))
            ParsedID3v1_["comment"] = php_substr(id3v1tag_, 97, 30)
            #// can't remove nulls yet, track detection depends on them
            ParsedID3v1_["genreid"] = php_ord(php_substr(id3v1tag_, 127, 1))
            #// If second-last byte of comment field is null and last byte of comment field is non-null
            #// then this is ID3v1.1 and the comment field is 28 bytes long and the 30th byte is the track number
            if id3v1tag_[125] == " " and id3v1tag_[126] != " ":
                ParsedID3v1_["track_number"] = php_ord(php_substr(ParsedID3v1_["comment"], 29, 1))
                ParsedID3v1_["comment"] = php_substr(ParsedID3v1_["comment"], 0, 28)
            # end if
            ParsedID3v1_["comment"] = self.cutfield(ParsedID3v1_["comment"])
            ParsedID3v1_["genre"] = self.lookupgenrename(ParsedID3v1_["genreid"])
            if (not php_empty(lambda : ParsedID3v1_["genre"])):
                ParsedID3v1_["genreid"] = None
            # end if
            if (php_isset(lambda : ParsedID3v1_["genre"])) and php_empty(lambda : ParsedID3v1_["genre"]) or ParsedID3v1_["genre"] == "Unknown":
                ParsedID3v1_["genre"] = None
            # end if
            for key_,value_ in ParsedID3v1_:
                ParsedID3v1_["comments"][key_][0] = value_
            # end for
            #// ID3v1 encoding detection hack START
            #// ID3v1 is defined as always using ISO-8859-1 encoding, but it is not uncommon to find files tagged with ID3v1 using Windows-1251 or other character sets
            #// Since ID3v1 has no concept of character sets there is no certain way to know we have the correct non-ISO-8859-1 character set, but we can guess
            ID3v1encoding_ = "ISO-8859-1"
            for tag_key_,valuearray_ in ParsedID3v1_["comments"]:
                for key_,value_ in valuearray_:
                    if php_preg_match("#^[\\x00-\\x40\\xA8\\xB8\\x80-\\xFF]+$#", value_):
                        for id3v1_bad_encoding_ in Array("Windows-1251", "KOI8-R"):
                            if php_function_exists("mb_convert_encoding") and php_no_error(lambda: mb_convert_encoding(value_, id3v1_bad_encoding_, id3v1_bad_encoding_)) == value_:
                                ID3v1encoding_ = id3v1_bad_encoding_
                                break
                            elif php_function_exists("iconv") and php_no_error(lambda: iconv(id3v1_bad_encoding_, id3v1_bad_encoding_, value_)) == value_:
                                ID3v1encoding_ = id3v1_bad_encoding_
                                break
                            # end if
                        # end for
                    # end if
                # end for
            # end for
            #// ID3v1 encoding detection hack END
            #// ID3v1 data is supposed to be padded with NULL characters, but some taggers pad with spaces
            GoodFormatID3v1tag_ = self.generateid3v1tag(ParsedID3v1_["title"], ParsedID3v1_["artist"], ParsedID3v1_["album"], ParsedID3v1_["year"], self.lookupgenreid(ParsedID3v1_["genre"]) if (php_isset(lambda : ParsedID3v1_["genre"])) else False, ParsedID3v1_["comment"], ParsedID3v1_["track_number"] if (not php_empty(lambda : ParsedID3v1_["track_number"])) else "")
            ParsedID3v1_["padding_valid"] = True
            if id3v1tag_ != GoodFormatID3v1tag_:
                ParsedID3v1_["padding_valid"] = False
                self.warning("Some ID3v1 fields do not use NULL characters for padding")
            # end if
            ParsedID3v1_["tag_offset_end"] = info_["filesize"]
            ParsedID3v1_["tag_offset_start"] = ParsedID3v1_["tag_offset_end"] - 128
            info_["id3v1"] = ParsedID3v1_
            info_["id3v1"]["encoding"] = ID3v1encoding_
        # end if
        if php_substr(preid3v1_, 0, 3) == "TAG":
            #// The way iTunes handles tags is, well, brain-damaged.
            #// It completely ignores v1 if ID3v2 is present.
            #// This goes as far as adding a new v1 tag *even if there already is one
            #// A suspected double-ID3v1 tag has been detected, but it could be that
            #// the "TAG" identifier is a legitimate part of an APE or Lyrics3 tag
            if php_substr(preid3v1_, 96, 8) == "APETAGEX":
                pass
            elif php_substr(preid3v1_, 119, 6) == "LYRICS":
                pass
            else:
                #// APE and Lyrics3 footers not found - assume double ID3v1
                self.warning("Duplicate ID3v1 tag detected - this has been known to happen with iTunes")
                info_["avdataend"] -= 128
            # end if
        # end if
        return True
    # end def analyze
    #// 
    #// @param string $str
    #// 
    #// @return string
    #//
    @classmethod
    def cutfield(self, str_=None):
        
        
        return php_trim(php_substr(str_, 0, strcspn(str_, " ")))
    # end def cutfield
    #// 
    #// @param bool $allowSCMPXextended
    #// 
    #// @return string[]
    #//
    @classmethod
    def arrayofgenres(self, allowSCMPXextended_=None):
        if allowSCMPXextended_ is None:
            allowSCMPXextended_ = False
        # end if
        
        GenreLookup_ = Array({0: "Blues", 1: "Classic Rock", 2: "Country", 3: "Dance", 4: "Disco", 5: "Funk", 6: "Grunge", 7: "Hip-Hop", 8: "Jazz", 9: "Metal", 10: "New Age", 11: "Oldies", 12: "Other", 13: "Pop", 14: "R&B", 15: "Rap", 16: "Reggae", 17: "Rock", 18: "Techno", 19: "Industrial", 20: "Alternative", 21: "Ska", 22: "Death Metal", 23: "Pranks", 24: "Soundtrack", 25: "Euro-Techno", 26: "Ambient", 27: "Trip-Hop", 28: "Vocal", 29: "Jazz+Funk", 30: "Fusion", 31: "Trance", 32: "Classical", 33: "Instrumental", 34: "Acid", 35: "House", 36: "Game", 37: "Sound Clip", 38: "Gospel", 39: "Noise", 40: "Alt. Rock", 41: "Bass", 42: "Soul", 43: "Punk", 44: "Space", 45: "Meditative", 46: "Instrumental Pop", 47: "Instrumental Rock", 48: "Ethnic", 49: "Gothic", 50: "Darkwave", 51: "Techno-Industrial", 52: "Electronic", 53: "Pop-Folk", 54: "Eurodance", 55: "Dream", 56: "Southern Rock", 57: "Comedy", 58: "Cult", 59: "Gangsta Rap", 60: "Top 40", 61: "Christian Rap", 62: "Pop/Funk", 63: "Jungle", 64: "Native American", 65: "Cabaret", 66: "New Wave", 67: "Psychedelic", 68: "Rave", 69: "Showtunes", 70: "Trailer", 71: "Lo-Fi", 72: "Tribal", 73: "Acid Punk", 74: "Acid Jazz", 75: "Polka", 76: "Retro", 77: "Musical", 78: "Rock & Roll", 79: "Hard Rock", 80: "Folk", 81: "Folk/Rock", 82: "National Folk", 83: "Swing", 84: "Fast-Fusion", 85: "Bebob", 86: "Latin", 87: "Revival", 88: "Celtic", 89: "Bluegrass", 90: "Avantgarde", 91: "Gothic Rock", 92: "Progressive Rock", 93: "Psychedelic Rock", 94: "Symphonic Rock", 95: "Slow Rock", 96: "Big Band", 97: "Chorus", 98: "Easy Listening", 99: "Acoustic", 100: "Humour", 101: "Speech", 102: "Chanson", 103: "Opera", 104: "Chamber Music", 105: "Sonata", 106: "Symphony", 107: "Booty Bass", 108: "Primus", 109: "Porn Groove", 110: "Satire", 111: "Slow Jam", 112: "Club", 113: "Tango", 114: "Samba", 115: "Folklore", 116: "Ballad", 117: "Power Ballad", 118: "Rhythmic Soul", 119: "Freestyle", 120: "Duet", 121: "Punk Rock", 122: "Drum Solo", 123: "A Cappella", 124: "Euro-House", 125: "Dance Hall", 126: "Goa", 127: "Drum & Bass", 128: "Club-House", 129: "Hardcore", 130: "Terror", 131: "Indie", 132: "BritPop", 133: "Negerpunk", 134: "Polsk Punk", 135: "Beat", 136: "Christian Gangsta Rap", 137: "Heavy Metal", 138: "Black Metal", 139: "Crossover", 140: "Contemporary Christian", 141: "Christian Rock", 142: "Merengue", 143: "Salsa", 144: "Thrash Metal", 145: "Anime", 146: "JPop", 147: "Synthpop", 255: "Unknown", "CR": "Cover", "RX": "Remix"})
        GenreLookupSCMPX_ = Array()
        if allowSCMPXextended_ and php_empty(lambda : GenreLookupSCMPX_):
            GenreLookupSCMPX_ = GenreLookup_
            #// http://www.geocities.co.jp/SiliconValley-Oakland/3664/alittle.html#GenreExtended
            #// Extended ID3v1 genres invented by SCMPX
            #// Note that 255 "Japanese Anime" conflicts with standard "Unknown"
            GenreLookupSCMPX_[240] = "Sacred"
            GenreLookupSCMPX_[241] = "Northern Europe"
            GenreLookupSCMPX_[242] = "Irish & Scottish"
            GenreLookupSCMPX_[243] = "Scotland"
            GenreLookupSCMPX_[244] = "Ethnic Europe"
            GenreLookupSCMPX_[245] = "Enka"
            GenreLookupSCMPX_[246] = "Children's Song"
            GenreLookupSCMPX_[247] = "Japanese Sky"
            GenreLookupSCMPX_[248] = "Japanese Heavy Rock"
            GenreLookupSCMPX_[249] = "Japanese Doom Rock"
            GenreLookupSCMPX_[250] = "Japanese J-POP"
            GenreLookupSCMPX_[251] = "Japanese Seiyu"
            GenreLookupSCMPX_[252] = "Japanese Ambient Techno"
            GenreLookupSCMPX_[253] = "Japanese Moemoe"
            GenreLookupSCMPX_[254] = "Japanese Tokusatsu"
            pass
        # end if
        return GenreLookupSCMPX_ if allowSCMPXextended_ else GenreLookup_
    # end def arrayofgenres
    #// 
    #// @param string $genreid
    #// @param bool   $allowSCMPXextended
    #// 
    #// @return string|false
    #//
    @classmethod
    def lookupgenrename(self, genreid_=None, allowSCMPXextended_=None):
        if allowSCMPXextended_ is None:
            allowSCMPXextended_ = True
        # end if
        
        for case in Switch(genreid_):
            if case("RX"):
                pass
            # end if
            if case("CR"):
                break
            # end if
            if case():
                if (not php_is_numeric(genreid_)):
                    return False
                # end if
                genreid_ = php_intval(genreid_)
                break
            # end if
        # end for
        GenreLookup_ = self.arrayofgenres(allowSCMPXextended_)
        return GenreLookup_[genreid_] if (php_isset(lambda : GenreLookup_[genreid_])) else False
    # end def lookupgenrename
    #// 
    #// @param string $genre
    #// @param bool   $allowSCMPXextended
    #// 
    #// @return string|false
    #//
    @classmethod
    def lookupgenreid(self, genre_=None, allowSCMPXextended_=None):
        if allowSCMPXextended_ is None:
            allowSCMPXextended_ = False
        # end if
        
        GenreLookup_ = self.arrayofgenres(allowSCMPXextended_)
        LowerCaseNoSpaceSearchTerm_ = php_strtolower(php_str_replace(" ", "", genre_))
        for key_,value_ in GenreLookup_:
            if php_strtolower(php_str_replace(" ", "", value_)) == LowerCaseNoSpaceSearchTerm_:
                return key_
            # end if
        # end for
        return False
    # end def lookupgenreid
    #// 
    #// @param string $OriginalGenre
    #// 
    #// @return string|false
    #//
    @classmethod
    def standardiseid3v1genrename(self, OriginalGenre_=None):
        
        
        GenreID_ = self.lookupgenreid(OriginalGenre_)
        if GenreID_ != False:
            return self.lookupgenrename(GenreID_)
        # end if
        return OriginalGenre_
    # end def standardiseid3v1genrename
    #// 
    #// @param string     $title
    #// @param string     $artist
    #// @param string     $album
    #// @param string     $year
    #// @param int        $genreid
    #// @param string     $comment
    #// @param int|string $track
    #// 
    #// @return string
    #//
    @classmethod
    def generateid3v1tag(self, title_=None, artist_=None, album_=None, year_=None, genreid_=None, comment_=None, track_=""):
        
        
        ID3v1Tag_ = "TAG"
        ID3v1Tag_ += php_str_pad(php_trim(php_substr(title_, 0, 30)), 30, " ", STR_PAD_RIGHT)
        ID3v1Tag_ += php_str_pad(php_trim(php_substr(artist_, 0, 30)), 30, " ", STR_PAD_RIGHT)
        ID3v1Tag_ += php_str_pad(php_trim(php_substr(album_, 0, 30)), 30, " ", STR_PAD_RIGHT)
        ID3v1Tag_ += php_str_pad(php_trim(php_substr(year_, 0, 4)), 4, " ", STR_PAD_LEFT)
        if (not php_empty(lambda : track_)) and track_ > 0 and track_ <= 255:
            ID3v1Tag_ += php_str_pad(php_trim(php_substr(comment_, 0, 28)), 28, " ", STR_PAD_RIGHT)
            ID3v1Tag_ += " "
            if gettype(track_) == "string":
                track_ = php_int(track_)
            # end if
            ID3v1Tag_ += chr(track_)
        else:
            ID3v1Tag_ += php_str_pad(php_trim(php_substr(comment_, 0, 30)), 30, " ", STR_PAD_RIGHT)
        # end if
        if genreid_ < 0 or genreid_ > 147:
            genreid_ = 255
            pass
        # end if
        for case in Switch(gettype(genreid_)):
            if case("string"):
                pass
            # end if
            if case("integer"):
                ID3v1Tag_ += chr(php_intval(genreid_))
                break
            # end if
            if case():
                ID3v1Tag_ += chr(255)
                break
            # end if
        # end for
        return ID3v1Tag_
    # end def generateid3v1tag
# end class getid3_id3v1
