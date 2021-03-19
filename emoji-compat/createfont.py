#!/usr/bin/env python3
#
# Copyright (C) 2017 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Creates the EmojiCompat font with the metadata. Metadata is embedded in FlatBuffers binary format
under a meta tag with name 'Emji'.

In order to create the final font the followings are used as inputs:

- NotoColorEmoji.ttf: Emoji font in the Android framework. Currently at
external/noto-fonts/emoji/NotoColorEmoji.ttf

- Unicode files: Unicode files that are in the framework, and lists information about all the
emojis. These files are emoji-data.txt, emoji-sequences.txt, emoji-zwj-sequences.txt,
and emoji-variation-sequences.txt. Currently at external/unicode/.

- additions/emoji-zwj-sequences.txt: Includes emojis that are not defined in Unicode files, but are
in the Android font. Resides in framework and currently under external/unicode/.

- data/emoji_metadata.txt: The file that includes the id, codepoints, the first
Android OS version that the emoji was added (sdkAdded), and finally the first EmojiCompat font
version that the emoji was added (compatAdded). Updated when the script is executed.

- data/emoji_metadata.fbs: The flatbuffer schema file. See http://google.github.io/flatbuffers/.

After execution the following files are generated if they don't exist otherwise, they are updated:
- font/NotoColorEmojiCompat.ttf
- supported-emojis/emojis.txt
- data/emoji_metadata.txt
- src/java/android/support/text/emoji/flatbuffer/*
"""

import contextlib
import csv
import hashlib
import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile
from fontTools import ttLib

########### UPDATE OR CHECK WHEN A NEW FONT IS BEING GENERATED ###########
# Last Android SDK Version
SDK_VERSION = 30
# metadata version that will be embedded into font. If there are updates to the font that would
# cause data/emoji_metadata.txt to change, this integer number should be incremented. This number
# defines in which EmojiCompat metadata version the emoji is added to the font.
METADATA_VERSION = 7

####### main directories where output files are created #######
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
FONT_DIR = os.path.join(SCRIPT_DIR, 'font')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
SUPPORTED_EMOJIS_DIR = os.path.join(SCRIPT_DIR, 'supported-emojis')
JAVA_SRC_DIR = os.path.join('src', 'java')
####### output files #######
# font file
FONT_PATH = os.path.join(FONT_DIR, 'NotoColorEmojiCompat.ttf')
# emoji metadata json output file
OUTPUT_META_FILE = os.path.join(DATA_DIR, 'emoji_metadata.txt')
# emojis test file
TEST_DATA_PATH = os.path.join(SUPPORTED_EMOJIS_DIR, 'emojis.txt')
####### input files #######
# Unicode file names to read emoji data
EMOJI_DATA_FILE = 'emoji-data.txt'
EMOJI_SEQ_FILE = 'emoji-sequences.txt'
EMOJI_ZWJ_FILE = 'emoji-zwj-sequences.txt'
EMOJI_VARIATION_SEQ_FILE = 'emoji-variation-sequences.txt'
# Android OS emoji file for emojis that are not in Unicode files
ANDROID_EMOJI_ZWJ_SEQ_FILE = os.path.join('additions', 'emoji-zwj-sequences.txt')
ANDROID_EMOJIS_SEQ_FILE = os.path.join('additions', 'emoji-sequences.txt')
# Android OS emoji style override file. Codepoints that are rendered with emoji style by default
# even though not defined so in <code>emoji-data.txt</code>.
EMOJI_STYLE_OVERRIDE_FILE = os.path.join('additions', 'emoji-data.txt')
# emoji metadata file
INPUT_META_FILE = OUTPUT_META_FILE
# default flatbuffer module location (if not specified by caller)
FLATBUFFER_MODULE_DIR = os.path.join(SCRIPT_DIR, '..', 'emoji-compat-flatbuffers')
# flatbuffer schema
FLATBUFFER_SCHEMA = os.path.join(FLATBUFFER_MODULE_DIR, 'data', 'emoji_metadata.fbs')
# file path for java header, it will be prepended to flatbuffer java files
FLATBUFFER_HEADER = os.path.join(FLATBUFFER_MODULE_DIR, 'data', 'flatbuffer_header.txt')
# temporary emoji metadata json output file
OUTPUT_JSON_FILE_NAME = 'emoji_metadata.json'
# temporary binary file generated by flatbuffer
FLATBUFFER_BIN = 'emoji_metadata.bin'
# directory representation for flatbuffer java package
FLATBUFFER_PACKAGE_PATH = os.path.join('androidx', 'text', 'emoji', 'flatbuffer', '')
# temporary directory that contains flatbuffer java files
FLATBUFFER_JAVA_PATH = os.path.join(FLATBUFFER_PACKAGE_PATH)
FLATBUFFER_METADATA_LIST_JAVA = "MetadataList.java"
FLATBUFFER_METADATA_ITEM_JAVA = "MetadataItem.java"
# directory under source where flatbuffer java files will be copied into
FLATBUFFER_JAVA_TARGET = os.path.join(FLATBUFFER_MODULE_DIR, JAVA_SRC_DIR, FLATBUFFER_PACKAGE_PATH)
# meta tag name used in the font to embed the emoji metadata. This value is also used in
# MetadataListReader.java in order to locate the metadata location.
EMOJI_META_TAG_NAME = 'Emji'

EMOJI_STR = 'EMOJI'
EMOJI_PRESENTATION_STR = 'EMOJI_PRESENTATION'
ACCEPTED_EMOJI_PROPERTIES = [EMOJI_PRESENTATION_STR, EMOJI_STR]
STD_VARIANTS_EMOJI_STYLE = 'EMOJI STYLE'

DEFAULT_EMOJI_ID = 0xF0001
EMOJI_STYLE_VS = 0xFE0F

def to_hex_str(value):
    """Converts given int value to hex without the 0x prefix"""
    return format(value, 'X')

def hex_str_to_int(string):
    """Convert a hex string into int"""
    return int(string, 16)

def codepoint_to_string(codepoints):
    """Converts a list of codepoints into a string separated with space."""
    return ' '.join([to_hex_str(x) for x in codepoints])

def prepend_header_to_file(file_path, header_path):
    """Prepends the header to the file. Used to update flatbuffer java files with header, comments
    and annotations."""
    with open(file_path, "r+") as original_file:
        with open(header_path, "r") as copyright_file:
            original_content = original_file.read()
            original_file.seek(0)
            original_file.write(copyright_file.read() + "\n" + original_content)


def update_flatbuffer_java_files(flatbuffer_java_dir, header_dir, target_dir):
    """Prepends headers to flatbuffer java files and copies to the final destination"""
    tmp_metadata_list = flatbuffer_java_dir + FLATBUFFER_METADATA_LIST_JAVA
    tmp_metadata_item = flatbuffer_java_dir + FLATBUFFER_METADATA_ITEM_JAVA
    prepend_header_to_file(tmp_metadata_list, header_dir)
    prepend_header_to_file(tmp_metadata_item, header_dir)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    shutil.copy(tmp_metadata_list, os.path.join(target_dir, FLATBUFFER_METADATA_LIST_JAVA))
    shutil.copy(tmp_metadata_item, os.path.join(target_dir, FLATBUFFER_METADATA_ITEM_JAVA))

def create_test_data(unicode_path):
    """Read all the emojis in the unicode files and update the test file"""
    lines = read_emoji_lines(os.path.join(unicode_path, EMOJI_ZWJ_FILE))
    lines += read_emoji_lines(os.path.join(unicode_path, EMOJI_SEQ_FILE))

    lines += read_emoji_lines(os.path.join(unicode_path, ANDROID_EMOJI_ZWJ_SEQ_FILE), optional=True)
    lines += read_emoji_lines(os.path.join(unicode_path, ANDROID_EMOJIS_SEQ_FILE), optional=True)

    # standardized variants contains a huge list of sequences, only read the ones that are emojis
    # and also the ones with FE0F (emoji style)
    standardized_variants_lines = read_emoji_lines(
        os.path.join(unicode_path, EMOJI_VARIATION_SEQ_FILE))
    for line in standardized_variants_lines:
        if STD_VARIANTS_EMOJI_STYLE in line:
            lines.append(line)

    emojis_set = set()
    for line in lines:
        # In unicode 12.0, "emoji-sequences.txt" contains "Basic_Emoji" session. We ignore them
        # here since we are already checking the emoji presentations with
        # emoji-variation-sequences.txt.
        if "BASIC_EMOJI" in line:
            continue
        codepoints = [hex_str_to_int(x) for x in line.split(';')[0].strip().split(' ')]
        emojis_set.add(codepoint_to_string(codepoints).upper())

    emoji_data_lines = read_emoji_lines(os.path.join(unicode_path, EMOJI_DATA_FILE))
    for line in emoji_data_lines:
        codepoints_range, emoji_property = codepoints_and_emoji_prop(line)
        if not emoji_property in ACCEPTED_EMOJI_PROPERTIES:
            continue
        is_emoji_style = emoji_property == EMOJI_PRESENTATION_STR
        if is_emoji_style:
            codepoints = [to_hex_str(x) for x in
                          codepoints_for_emojirange(codepoints_range)]
            emojis_set.update(codepoints)

    emoji_style_exceptions = get_emoji_style_exceptions(unicode_path)
    #  finally add the android default emoji exceptions
    emojis_set.update([to_hex_str(x) for x in emoji_style_exceptions])

    emojis_list = list(emojis_set)
    emojis_list.sort()
    with open(TEST_DATA_PATH, "w") as test_file:
        for line in emojis_list:
            test_file.write("%s\n" % line)

class _EmojiData(object):
    """Holds the information about a single emoji."""

    def __init__(self, codepoints, is_emoji_style):
        self.codepoints = codepoints
        self.emoji_style = is_emoji_style
        self.emoji_id = 0
        self.width = 0
        self.height = 0
        self.sdk_added = SDK_VERSION
        self.compat_added = METADATA_VERSION

    def update_metrics(self, metrics):
        """Updates width/height instance variables with the values given in metrics dictionary.
        :param metrics: a dictionary object that has width and height values.
        """
        self.width = metrics.width
        self.height = metrics.height

    def __repr__(self):
        return '<EmojiData {0} - {1}>'.format(self.emoji_style,
                                              codepoint_to_string(self.codepoints))

    def create_json_element(self):
        """Creates the json representation of EmojiData."""
        json_element = {}
        json_element['id'] = self.emoji_id
        json_element['emojiStyle'] = self.emoji_style
        json_element['sdkAdded'] = self.sdk_added
        json_element['compatAdded'] = self.compat_added
        json_element['width'] = self.width
        json_element['height'] = self.height
        json_element['codepoints'] = self.codepoints
        return json_element

    def create_txt_row(self):
        """Creates array of values for CSV of EmojiData."""
        row = [to_hex_str(self.emoji_id), self.sdk_added, self.compat_added]
        row += [to_hex_str(x) for x in self.codepoints]
        return row

    def update(self, emoji_id, sdk_added, compat_added):
        """Updates current EmojiData with the values in a json element"""
        self.emoji_id = emoji_id
        self.sdk_added = sdk_added
        self.compat_added = compat_added


def read_emoji_lines(file_path, optional=False):
    """Read all lines in an unicode emoji file into a list of uppercase strings. Ignore the empty
    lines and comments
    :param file_path: unicode emoji file path
    :param optional: if True no exception is raised when the file cannot be read
    :return: list of uppercase strings
    """
    result = []
    try:
        with open(file_path) as file_stream:
            for line in file_stream:
                line = line.strip()
                if line and not line.startswith('#'):
                    result.append(line.upper())
    except IOError:
        if optional:
            pass
        else:
            raise

    return result

def get_emoji_style_exceptions(unicode_path):
    """Read EMOJI_STYLE_OVERRIDE_FILE and return the codepoints as integers"""
    lines = read_emoji_lines(os.path.join(unicode_path, EMOJI_STYLE_OVERRIDE_FILE))
    exceptions = []
    for line in lines:
        codepoint = hex_str_to_int(codepoints_and_emoji_prop(line)[0])
        exceptions.append(codepoint)
    return exceptions

def codepoints_for_emojirange(codepoints_range):
    """ Return codepoints given in emoji files. Expand the codepoints that are given as a range
    such as XYZ ... UVT
    """
    codepoints = []
    if '..' in codepoints_range:
        range_start, range_end = codepoints_range.split('..')
        codepoints_range = range(hex_str_to_int(range_start),
                                 hex_str_to_int(range_end) + 1)
        codepoints.extend(codepoints_range)
    else:
        codepoints.append(hex_str_to_int(codepoints_range))
    return codepoints

def codepoints_and_emoji_prop(line):
    """For a given emoji file line, return codepoints and emoji property in the line.
    1F93C..1F93E ; [Emoji|Emoji_Presentation|Emoji_Modifier_Base|Emoji_Component
    |Extended_Pictographic] # [...]"""
    line = line.strip()
    if '#' in line:
        line = line[:line.index('#')]
    else:
        raise ValueError("Line is expected to have # in it")
    line = line.split(';')
    codepoints_range = line[0].strip()
    emoji_property = line[1].strip()

    return codepoints_range, emoji_property

def read_emoji_intervals(emoji_data_map, file_path, emoji_style_exceptions):
    """Read unicode lines of unicode emoji file in which each line describes a set of codepoint
    intervals. Expands the interval on a line and inserts related EmojiDatas into emoji_data_map.
    A line format that is expected is as follows:
    1F93C..1F93E ; [Emoji|Emoji_Presentation|Emoji_Modifier_Base|Emoji_Component
    |Extended_Pictographic] # [...]"""
    lines = read_emoji_lines(file_path)

    for line in lines:
        codepoints_range, emoji_property = codepoints_and_emoji_prop(line)
        if not emoji_property in ACCEPTED_EMOJI_PROPERTIES:
            continue
        is_emoji_style = emoji_property == EMOJI_PRESENTATION_STR
        codepoints = codepoints_for_emojirange(codepoints_range)

        for codepoint in codepoints:
            key = codepoint_to_string([codepoint])
            codepoint_is_emoji_style = is_emoji_style or codepoint in emoji_style_exceptions
            if key in emoji_data_map:
                # since there are multiple definitions of emojis, only update when emoji style is
                # True
                if codepoint_is_emoji_style:
                    emoji_data_map[key].emoji_style = True
            else:
                emoji_data = _EmojiData([codepoint], codepoint_is_emoji_style)
                emoji_data_map[key] = emoji_data


def read_emoji_sequences(emoji_data_map, file_path, optional=False):
    """Reads the content of the file which contains emoji sequences. Creates EmojiData for each
    line and puts into emoji_data_map."""
    lines = read_emoji_lines(file_path, optional)
    # 1F1E6 1F1E8 ; Name ; [...]
    for line in lines:
        # In unicode 12.0, "emoji-sequences.txt" contains "Basic_Emoji" session. We ignore them
        # here since we are already checking the emoji presentations with
        # emoji-variation-sequences.txt.
        if "BASIC_EMOJI" in line:
            continue
        codepoints = [hex_str_to_int(x) for x in line.split(';')[0].strip().split(' ')]
        codepoints = [x for x in codepoints if x != EMOJI_STYLE_VS]
        key = codepoint_to_string(codepoints)
        if not key in emoji_data_map:
            emoji_data = _EmojiData(codepoints, False)
            emoji_data_map[key] = emoji_data


def load_emoji_data_map(unicode_path):
    """Reads the emoji data files, constructs a map of space separated codepoints to EmojiData.
    :return: map of space separated codepoints to EmojiData
    """
    emoji_data_map = {}
    emoji_style_exceptions = get_emoji_style_exceptions(unicode_path)
    read_emoji_intervals(emoji_data_map, os.path.join(unicode_path, EMOJI_DATA_FILE),
                         emoji_style_exceptions)
    read_emoji_sequences(emoji_data_map, os.path.join(unicode_path, EMOJI_ZWJ_FILE))
    read_emoji_sequences(emoji_data_map, os.path.join(unicode_path, EMOJI_SEQ_FILE))

    # Add the optional ANDROID_EMOJI_ZWJ_SEQ_FILE if it exists.
    read_emoji_sequences(emoji_data_map, os.path.join(unicode_path, ANDROID_EMOJI_ZWJ_SEQ_FILE),
                         optional=True)
    # Add the optional ANDROID_EMOJIS_SEQ_FILE if it exists.
    read_emoji_sequences(emoji_data_map, os.path.join(unicode_path, ANDROID_EMOJIS_SEQ_FILE),
                         optional=True)

    return emoji_data_map


def load_previous_metadata(emoji_data_map):
    """Updates emoji data elements in emoji_data_map using the id, sdk_added and compat_added fields
       in emoji_metadata.txt. Returns the smallest available emoji id to use. i.e. if the largest
       emoji id emoji_metadata.txt is 1, function would return 2. If emoji_metadata.txt does not
       exist, or contains no emojis defined returns DEFAULT_EMOJI_ID"""
    current_emoji_id = DEFAULT_EMOJI_ID
    if os.path.isfile(INPUT_META_FILE):
        with open(INPUT_META_FILE) as csvfile:
            reader = csv.reader(csvfile, delimiter=' ')
            for row in reader:
                if row[0].startswith('#'):
                    continue
                emoji_id = hex_str_to_int(row[0])
                sdk_added = int(row[1])
                compat_added = int(row[2])
                key = codepoint_to_string(hex_str_to_int(x) for x in row[3:])
                if key in emoji_data_map:
                    emoji_data = emoji_data_map[key]
                    emoji_data.update(emoji_id, sdk_added, compat_added)
                    if emoji_data.emoji_id >= current_emoji_id:
                        current_emoji_id = emoji_data.emoji_id + 1

    return current_emoji_id


def update_ttlib_orig_sort():
    """Updates the ttLib tag sort with a closure that makes the meta table first."""
    orig_sort = ttLib.sortedTagList

    def meta_first_table_sort(tag_list, table_order=None):
        """Sorts the tables with the original ttLib sort, then makes the meta table first."""
        tag_list = orig_sort(tag_list, table_order)
        tag_list.remove('meta')
        tag_list.insert(0, 'meta')
        return tag_list

    ttLib.sortedTagList = meta_first_table_sort


def inject_meta_into_font(ttf, flatbuffer_bin_filename):
    """inject metadata binary into font"""
    if not 'meta' in ttf:
        ttf['meta'] = ttLib.getTableClass('meta')()
    meta = ttf['meta']
    with open(flatbuffer_bin_filename, 'rb') as flatbuffer_bin_file:
        meta.data[EMOJI_META_TAG_NAME] = flatbuffer_bin_file.read()

    # sort meta tables for faster access
    update_ttlib_orig_sort()


def validate_input_files(font_path, unicode_path, flatbuffer_path):
    """Validate the existence of font file and the unicode files"""
    if not os.path.isfile(font_path):
        raise ValueError("Font file does not exist: " + font_path)

    if not os.path.isdir(unicode_path):
        raise ValueError(
            "Unicode directory does not exist or is not a directory " + unicode_path)

    emoji_filenames = [os.path.join(unicode_path, EMOJI_DATA_FILE),
                       os.path.join(unicode_path, EMOJI_ZWJ_FILE),
                       os.path.join(unicode_path, EMOJI_SEQ_FILE)]
    for emoji_filename in emoji_filenames:
        if not os.path.isfile(emoji_filename):
            raise ValueError("Unicode emoji data file does not exist: " + emoji_filename)

    if not os.path.isdir(flatbuffer_path):
        raise ValueError(
            "Flatbuffer directory does not exist or is not a directory " + flatbuffer_path)

    flatbuffer_filenames = [os.path.join(flatbuffer_path, FLATBUFFER_SCHEMA),
                            os.path.join(flatbuffer_path, FLATBUFFER_HEADER)]
    for flatbuffer_filename in flatbuffer_filenames:
        if not os.path.isfile(flatbuffer_filename):
            raise ValueError("Flatbuffer file does not exist: " + flatbuffer_filename)


def add_file_to_sha(sha_algo, file_path):
    with open(file_path, 'rb') as input_file:
        for data in iter(lambda: input_file.read(8192), b''):
            sha_algo.update(data)

def create_sha_from_source_files(font_paths):
    """Creates a SHA from the given font files"""
    sha_algo = hashlib.sha256()
    for file_path in font_paths:
        add_file_to_sha(sha_algo, file_path)
    return sha_algo.hexdigest()


class EmojiFontCreator(object):
    """Creates the EmojiCompat font"""

    def __init__(self, font_path, unicode_path):
        validate_input_files(font_path, unicode_path, FLATBUFFER_MODULE_DIR)

        self.font_path = font_path
        self.unicode_path = unicode_path
        self.emoji_data_map = {}
        self.remapped_codepoints = {}
        self.glyph_to_image_metrics_map = {}
        # set default emoji id to start of Supplemental Private Use Area-A
        self.emoji_id = DEFAULT_EMOJI_ID

    def update_emoji_data(self, codepoints, glyph_name):
        """Updates the existing EmojiData identified with codepoints. The fields that are set are:
        - emoji_id (if it does not exist)
        - image width/height"""
        key = codepoint_to_string(codepoints)
        if key in self.emoji_data_map:
            # add emoji to final data
            emoji_data = self.emoji_data_map[key]
            emoji_data.update_metrics(self.glyph_to_image_metrics_map[glyph_name])
            if emoji_data.emoji_id == 0:
                emoji_data.emoji_id = self.emoji_id
                self.emoji_id = self.emoji_id + 1
            self.remapped_codepoints[emoji_data.emoji_id] = glyph_name

    def read_cbdt(self, ttf):
        """Read image size data from CBDT."""
        cbdt = ttf['CBDT']
        for strike_data in cbdt.strikeData:
            for key, data in strike_data.items():
                data.decompile()
                self.glyph_to_image_metrics_map[key] = data.metrics

    def read_cmap12(self, ttf, glyph_to_codepoint_map):
        """Reads single code point emojis that are in cmap12, updates glyph_to_codepoint_map and
        finally clears all elements in CMAP 12"""
        cmap = ttf['cmap']
        for table in cmap.tables:
            if table.format == 12 and table.platformID == 3 and table.platEncID == 10:
                for codepoint, glyph_name in table.cmap.items():
                    glyph_to_codepoint_map[glyph_name] = codepoint
                    self.update_emoji_data([codepoint], glyph_name)
                return table
        raise ValueError("Font doesn't contain cmap with format:12, platformID:3 and platEncID:10")

    def read_gsub(self, ttf, glyph_to_codepoint_map):
        """Reads the emoji sequences defined in GSUB and clear all elements under GSUB"""
        gsub = ttf['GSUB']
        ligature_subtables = []
        context_subtables = []
        # this code is font dependent, implementing all gsub rules is out of scope of EmojiCompat
        # and would be expensive with little value
        for lookup in gsub.table.LookupList.Lookup:
            for subtable in lookup.SubTable:
                if subtable.LookupType == 5:
                    context_subtables.append(subtable)
                elif subtable.LookupType == 4:
                    ligature_subtables.append(subtable)

        for subtable in context_subtables:
            self.add_gsub_context_subtable(subtable, gsub.table.LookupList, glyph_to_codepoint_map)

        for subtable in ligature_subtables:
            self.add_gsub_ligature_subtable(subtable, glyph_to_codepoint_map)

    def add_gsub_context_subtable(self, subtable, lookup_list, glyph_to_codepoint_map):
        """Add substitutions defined as OpenType Context Substitution"""
        for sub_class_set in subtable.SubClassSet:
            if sub_class_set:
                for sub_class_rule in sub_class_set.SubClassRule:
                    # prepare holder for substitution list. each rule will have a list that is added
                    # to the subs_list.
                    subs_list = len(sub_class_rule.SubstLookupRecord) * [None]
                    for record in sub_class_rule.SubstLookupRecord:
                        subs_list[record.SequenceIndex] = self.get_substitutions(lookup_list,
                                                                            record.LookupListIndex)
                    # create combinations or all lists. the combinations will be filtered by
                    # emoji_data_map. the first element that contain as a valid glyph will be used
                    # as the final glyph
                    combinations = list(itertools.product(*subs_list))
                    for seq in combinations:
                        glyph_names = [x["input"] for x in seq]
                        codepoints = [glyph_to_codepoint_map[x] for x in glyph_names]
                        outputs = [x["output"] for x in seq if x["output"]]
                        nonempty_outputs = list(filter(lambda x: x.strip() , outputs))
                        if len(nonempty_outputs) == 0:
                            print("Warning: no output glyph is set for " + str(glyph_names))
                            continue
                        elif len(nonempty_outputs) > 1:
                            print(
                                "Warning: multiple glyph is set for "
                                    + str(glyph_names) + ", will use the first one")

                        glyph = nonempty_outputs[0]
                        self.update_emoji_data(codepoints, glyph)

    def get_substitutions(self, lookup_list, index):
        result = []
        for x in lookup_list.Lookup[index].SubTable:
            for input, output in x.mapping.items():
                result.append({"input": input, "output": output})
        return result

    def add_gsub_ligature_subtable(self, subtable, glyph_to_codepoint_map):
        for name, ligatures in subtable.ligatures.items():
            for ligature in ligatures:
                glyph_names = [name] + ligature.Component
                codepoints = [glyph_to_codepoint_map[x] for x in glyph_names]
                self.update_emoji_data(codepoints, ligature.LigGlyph)

    def write_metadata_json(self, output_json_file_path):
        """Writes the emojis into a json file"""
        output_json = {}
        output_json['version'] = METADATA_VERSION
        output_json['sourceSha'] = create_sha_from_source_files(
            [self.font_path, OUTPUT_META_FILE, FLATBUFFER_SCHEMA])
        output_json['list'] = []

        emoji_data_list = sorted(self.emoji_data_map.values(), key=lambda x: x.emoji_id)

        total_emoji_count = 0
        for emoji_data in emoji_data_list:
            element = emoji_data.create_json_element()
            output_json['list'].append(element)
            total_emoji_count = total_emoji_count + 1

        # write the new json file to be processed by FlatBuffers
        with open(output_json_file_path, 'w') as json_file:
            print(json.dumps(output_json, indent=4, sort_keys=True, separators=(',', ':')),
                  file=json_file)

        return total_emoji_count

    def write_metadata_csv(self):
        """Writes emoji metadata into space separated file"""
        with open(OUTPUT_META_FILE, 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=' ')
            emoji_data_list = sorted(self.emoji_data_map.values(), key=lambda x: x.emoji_id)
            csvwriter.writerow(['#id', 'sdkAdded', 'compatAdded', 'codepoints'])
            for emoji_data in emoji_data_list:
                csvwriter.writerow(emoji_data.create_txt_row())

    def create_font(self):
        """Creates the EmojiCompat font.
        :param font_path: path to Android NotoColorEmoji font
        :param unicode_path: path to directory that contains unicode files
        """

        tmp_dir = tempfile.mkdtemp()

        # create emoji codepoints to EmojiData map
        self.emoji_data_map = load_emoji_data_map(self.unicode_path)

        # read previous metadata file to update id, sdkAdded and compatAdded. emoji id that is
        # returned is either default or 1 greater than the largest id in previous data
        self.emoji_id = load_previous_metadata(self.emoji_data_map)

        # recalcTimestamp parameter will keep the modified field same as the original font. Changing
        # the modified field in the font causes the font ttf file to change, which makes it harder
        # to understand if something really changed in the font.
        with contextlib.closing(ttLib.TTFont(self.font_path, recalcTimestamp=False)) as ttf:
            # read image size data
            self.read_cbdt(ttf)

            # glyph name to codepoint map
            glyph_to_codepoint_map = {}

            # read single codepoint emojis under cmap12 and clear the table contents
            cmap12_table = self.read_cmap12(ttf, glyph_to_codepoint_map)

            # read emoji sequences gsub and clear the table contents
            self.read_gsub(ttf, glyph_to_codepoint_map)

            # add all new codepoint to glyph mappings
            cmap12_table.cmap.update(self.remapped_codepoints)

            # final metadata csv will be used to generate the sha, therefore write it before
            # metadata json is written.
            self.write_metadata_csv()

            output_json_file = os.path.join(tmp_dir, OUTPUT_JSON_FILE_NAME)
            flatbuffer_bin_file = os.path.join(tmp_dir, FLATBUFFER_BIN)
            flatbuffer_java_dir = os.path.join(tmp_dir, FLATBUFFER_JAVA_PATH)

            total_emoji_count = self.write_metadata_json(output_json_file)

            # create the flatbuffers binary and java classes
            flatc_command = ['flatc',
                             '-o',
                             tmp_dir,
                             '-b',
                             '-j',
                             FLATBUFFER_SCHEMA,
                             output_json_file]
            subprocess.check_output(flatc_command)

            # inject metadata binary into font
            inject_meta_into_font(ttf, flatbuffer_bin_file)

            # update CBDT and CBLC versions since older android versions cannot read > 2.0
            ttf['CBDT'].version = 2.0
            ttf['CBLC'].version = 2.0

            # save the new font
            ttf.save(FONT_PATH)

            update_flatbuffer_java_files(flatbuffer_java_dir, #tmp dir
                                         FLATBUFFER_HEADER,
                                         FLATBUFFER_JAVA_TARGET)

            create_test_data(self.unicode_path)

            # clear the tmp output directory
            shutil.rmtree(tmp_dir, ignore_errors=True)

            print(
                "{0} emojis are written to\n{1}".format(total_emoji_count, FONT_DIR))


def print_usage():
    """Prints how to use the script."""
    print("Please specify a path to font and unicode files.\n"
          "usage: createfont.py noto-color-emoji-path unicode-dir-path [flatbuffer-project-dir]")

def parse_args(argv):
    # parse manually to avoid any extra dependencies
    if len(argv) < 3:
        print_usage()
        sys.exit(1)
    return (sys.argv[1], sys.argv[2])

def main():
    font_file, unicode_dir = parse_args(sys.argv)
    EmojiFontCreator(font_file, unicode_dir).create_font()


if __name__ == '__main__':
    main()
