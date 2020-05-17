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
#// Class for working with MO files
#// 
#// @version $Id: mo.php 1157 2015-11-20 04:30:11Z dd32 $
#// @package pomo
#// @subpackage mo
#//
php_include_file(__DIR__ + "/translations.php", once=True)
php_include_file(__DIR__ + "/streams.php", once=True)
if (not php_class_exists("MO", False)):
    class MO(Gettext_Translations):
        _nplurals = 2
        #// 
        #// Loaded MO file.
        #// 
        #// @var string
        #//
        filename = ""
        #// 
        #// Returns the loaded MO file.
        #// 
        #// @return string The loaded MO file.
        #//
        def get_filename(self):
            
            
            return self.filename
        # end def get_filename
        #// 
        #// Fills up with the entries from MO file $filename
        #// 
        #// @param string $filename MO file to load
        #// @return bool True if the import from file was successful, otherwise false.
        #//
        def import_from_file(self, filename_=None):
            
            
            reader_ = php_new_class("POMO_FileReader", lambda : POMO_FileReader(filename_))
            if (not reader_.is_resource()):
                return False
            # end if
            self.filename = php_str(filename_)
            return self.import_from_reader(reader_)
        # end def import_from_file
        #// 
        #// @param string $filename
        #// @return bool
        #//
        def export_to_file(self, filename_=None):
            
            
            fh_ = fopen(filename_, "wb")
            if (not fh_):
                return False
            # end if
            res_ = self.export_to_file_handle(fh_)
            php_fclose(fh_)
            return res_
        # end def export_to_file
        #// 
        #// @return string|false
        #//
        def export(self):
            
            
            tmp_fh_ = fopen("php://temp", "r+")
            if (not tmp_fh_):
                return False
            # end if
            self.export_to_file_handle(tmp_fh_)
            rewind(tmp_fh_)
            return stream_get_contents(tmp_fh_)
        # end def export
        #// 
        #// @param Translation_Entry $entry
        #// @return bool
        #//
        def is_entry_good_for_export(self, entry_=None):
            
            
            if php_empty(lambda : entry_.translations):
                return False
            # end if
            if (not php_array_filter(entry_.translations)):
                return False
            # end if
            return True
        # end def is_entry_good_for_export
        #// 
        #// @param resource $fh
        #// @return true
        #//
        def export_to_file_handle(self, fh_=None):
            
            
            entries_ = php_array_filter(self.entries, Array(self, "is_entry_good_for_export"))
            ksort(entries_)
            magic_ = 2500072158
            revision_ = 0
            total_ = php_count(entries_) + 1
            #// All the headers are one entry.
            originals_lenghts_addr_ = 28
            translations_lenghts_addr_ = originals_lenghts_addr_ + 8 * total_
            size_of_hash_ = 0
            hash_addr_ = translations_lenghts_addr_ + 8 * total_
            current_addr_ = hash_addr_
            fwrite(fh_, pack("V*", magic_, revision_, total_, originals_lenghts_addr_, translations_lenghts_addr_, size_of_hash_, hash_addr_))
            fseek(fh_, originals_lenghts_addr_)
            #// Headers' msgid is an empty string.
            fwrite(fh_, pack("VV", 0, current_addr_))
            current_addr_ += 1
            originals_table_ = " "
            reader_ = php_new_class("POMO_Reader", lambda : POMO_Reader())
            for entry_ in entries_:
                originals_table_ += self.export_original(entry_) + " "
                length_ = reader_.strlen(self.export_original(entry_))
                fwrite(fh_, pack("VV", length_, current_addr_))
                current_addr_ += length_ + 1
                pass
            # end for
            exported_headers_ = self.export_headers()
            fwrite(fh_, pack("VV", reader_.strlen(exported_headers_), current_addr_))
            current_addr_ += php_strlen(exported_headers_) + 1
            translations_table_ = exported_headers_ + " "
            for entry_ in entries_:
                translations_table_ += self.export_translations(entry_) + " "
                length_ = reader_.strlen(self.export_translations(entry_))
                fwrite(fh_, pack("VV", length_, current_addr_))
                current_addr_ += length_ + 1
            # end for
            fwrite(fh_, originals_table_)
            fwrite(fh_, translations_table_)
            return True
        # end def export_to_file_handle
        #// 
        #// @param Translation_Entry $entry
        #// @return string
        #//
        def export_original(self, entry_=None):
            
            
            #// TODO: Warnings for control characters.
            exported_ = entry_.singular
            if entry_.is_plural:
                exported_ += " " + entry_.plural
            # end if
            if entry_.context:
                exported_ = entry_.context + "" + exported_
            # end if
            return exported_
        # end def export_original
        #// 
        #// @param Translation_Entry $entry
        #// @return string
        #//
        def export_translations(self, entry_=None):
            
            
            #// TODO: Warnings for control characters.
            return php_implode(" ", entry_.translations) if entry_.is_plural else entry_.translations[0]
        # end def export_translations
        #// 
        #// @return string
        #//
        def export_headers(self):
            
            
            exported_ = ""
            for header_,value_ in self.headers:
                exported_ += str(header_) + str(": ") + str(value_) + str("\n")
            # end for
            return exported_
        # end def export_headers
        #// 
        #// @param int $magic
        #// @return string|false
        #//
        def get_byteorder(self, magic_=None):
            
            
            #// The magic is 0x950412de.
            #// bug in PHP 5.0.2, see https://savannah.nongnu.org/bugs/?func=detailitem&item_id=10565
            magic_little_ = php_int(-1794895138)
            magic_little_64_ = php_int(2500072158)
            #// 0xde120495
            magic_big_ = php_int(-569244523) & 4294967295
            if magic_little_ == magic_ or magic_little_64_ == magic_:
                return "little"
            elif magic_big_ == magic_:
                return "big"
            else:
                return False
            # end if
        # end def get_byteorder
        #// 
        #// @param POMO_FileReader $reader
        #// @return bool True if the import was successful, otherwise false.
        #//
        def import_from_reader(self, reader_=None):
            
            
            endian_string_ = MO.get_byteorder(reader_.readint32())
            if False == endian_string_:
                return False
            # end if
            reader_.setendian(endian_string_)
            endian_ = "N" if "big" == endian_string_ else "V"
            header_ = reader_.read(24)
            if reader_.strlen(header_) != 24:
                return False
            # end if
            #// Parse header.
            header_ = unpack(str(endian_) + str("revision/") + str(endian_) + str("total/") + str(endian_) + str("originals_lenghts_addr/") + str(endian_) + str("translations_lenghts_addr/") + str(endian_) + str("hash_length/") + str(endian_) + str("hash_addr"), header_)
            if (not php_is_array(header_)):
                return False
            # end if
            #// Support revision 0 of MO format specs, only.
            if 0 != header_["revision"]:
                return False
            # end if
            #// Seek to data blocks.
            reader_.seekto(header_["originals_lenghts_addr"])
            #// Read originals' indices.
            originals_lengths_length_ = header_["translations_lenghts_addr"] - header_["originals_lenghts_addr"]
            if originals_lengths_length_ != header_["total"] * 8:
                return False
            # end if
            originals_ = reader_.read(originals_lengths_length_)
            if reader_.strlen(originals_) != originals_lengths_length_:
                return False
            # end if
            #// Read translations' indices.
            translations_lenghts_length_ = header_["hash_addr"] - header_["translations_lenghts_addr"]
            if translations_lenghts_length_ != header_["total"] * 8:
                return False
            # end if
            translations_ = reader_.read(translations_lenghts_length_)
            if reader_.strlen(translations_) != translations_lenghts_length_:
                return False
            # end if
            #// Transform raw data into set of indices.
            originals_ = reader_.str_split(originals_, 8)
            translations_ = reader_.str_split(translations_, 8)
            #// Skip hash table.
            strings_addr_ = header_["hash_addr"] + header_["hash_length"] * 4
            reader_.seekto(strings_addr_)
            strings_ = reader_.read_all()
            reader_.close()
            i_ = 0
            while i_ < header_["total"]:
                
                o_ = unpack(str(endian_) + str("length/") + str(endian_) + str("pos"), originals_[i_])
                t_ = unpack(str(endian_) + str("length/") + str(endian_) + str("pos"), translations_[i_])
                if (not o_) or (not t_):
                    return False
                # end if
                #// Adjust offset due to reading strings to separate space before.
                o_["pos"] -= strings_addr_
                t_["pos"] -= strings_addr_
                original_ = reader_.substr(strings_, o_["pos"], o_["length"])
                translation_ = reader_.substr(strings_, t_["pos"], t_["length"])
                if "" == original_:
                    self.set_headers(self.make_headers(translation_))
                else:
                    entry_ = self.make_entry(original_, translation_)
                    self.entries[entry_.key()] = entry_
                # end if
                i_ += 1
            # end while
            return True
        # end def import_from_reader
        #// 
        #// Build a Translation_Entry from original string and translation strings,
        #// found in a MO file
        #// 
        #// @static
        #// @param string $original original string to translate from MO file. Might contain
        #// 0x04 as context separator or 0x00 as singular/plural separator
        #// @param string $translation translation string from MO file. Might contain
        #// 0x00 as a plural translations separator
        #// @return Translation_Entry Entry instance.
        #//
        def make_entry(self, original_=None, translation_=None):
            
            
            entry_ = php_new_class("Translation_Entry", lambda : Translation_Entry())
            #// Look for context, separated by \4.
            parts_ = php_explode("", original_)
            if (php_isset(lambda : parts_[1])):
                original_ = parts_[1]
                entry_.context = parts_[0]
            # end if
            #// Look for plural original.
            parts_ = php_explode(" ", original_)
            entry_.singular = parts_[0]
            if (php_isset(lambda : parts_[1])):
                entry_.is_plural = True
                entry_.plural = parts_[1]
            # end if
            #// Plural translations are also separated by \0.
            entry_.translations = php_explode(" ", translation_)
            return entry_
        # end def make_entry
        #// 
        #// @param int $count
        #// @return string
        #//
        def select_plural_form(self, count_=None):
            
            
            return self.gettext_select_plural_form(count_)
        # end def select_plural_form
        #// 
        #// @return int
        #//
        def get_plural_forms_count(self):
            
            
            return self._nplurals
        # end def get_plural_forms_count
    # end class MO
# end if
