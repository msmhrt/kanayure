#!/usr/bin/env python3
# vim:fileencoding=utf-8

# Copyright (c) 2012 Masami HIRATA <msmhrt@gmail.com>

from collections import defaultdict
import os
import time

import regex

from kanayure.util import RedirectStdoutTo
from kanayure.filelist import FileList

RE_CLASS_KATAKANA_WITHOUT_DOT = (r"\u3099-\u309C" +
                                 r"\u30A0-\u30FA" +
                                 r"\u30FC-\u30FF" +
                                 r"\u31F0-\u31FF" +
                                 r"\uFF65" +
                                 r"\uFF9F" +
                                 r"\U0001B000")
RE_CLASS_KATAKANA = r"\u30FB" + RE_CLASS_KATAKANA_WITHOUT_DOT
RE_KATAKANA_BASE = r"""(?V1xm)
    [""" + RE_CLASS_KATAKANA_WITHOUT_DOT + r"""]
    (?: [""" + RE_CLASS_KATAKANA + r"""]*
        (?: ({boundary})
            [""" + RE_CLASS_KATAKANA + r"""]*
        )*
        [""" + RE_CLASS_KATAKANA_WITHOUT_DOT + r"""]
    )?
"""
RE_BOUNDARY_BASE = r"""(?V1xm)
    {boundary}
"""
RE_CHAR_TABLE = [(r"(?:ギュ|[グ])ー?・?", r"(?:ギュ|[グ])ー?・?"),
                 (r"(?:ディ|[デ])ー?・?", r"(?:ディ|[デ])ー?・?"),
                 (r"(?:ティ|[チ])ー?・?", r"(?:ティ|[チ])ー?・?"),
                 (r"(?:トゥー?|ツー)・?", r"(?:トゥー?|ツー)・?"),
                 (r"[ニネ][ィイ]?ー?・?",
                  r"[ニネ]ー?・?[ィイ]?ー?・?"),
                 (r"(?:ファ|ハ)ー?・?", r"(?:ファ|ハ)ー?・?"),
                 (r"(?:フィ|ヒ)ー?・?", r"(?:フィ|ヒ)ー?・?"),
                 #(r"(?:フゥ|フ)ー?・?", r"(?:フゥ|フ)ー?・?"),  # DON'T USE
                 (r"(?:フェ|ヘ)[ィイー]・?",
                  r"(?:フェ|ヘ)ー?・?[ィイー]ー?・?"),
                 (r"(?:フェ|ヘ)・?", r"(?:フェ|ヘ)ー?・?"),
                 (r"(?:フォ|ホ)ー?・?", r"(?:フォ|ホ)ー?・?"),
                 (r"(?:ヴァ|バ)ー?・?", r"(?:ヴァ|バ)ー?・?"),
                 (r"(?:ヴィ|ビ)ー?・?", r"(?:ヴィ|ビ)ー?・?"),
                 (r"(?:ヴェ|ベ)[ィイー]・?",
                  r"(?:ヴェ|ベ)ー?・?[ィイー]ー?・?"),
                 (r"(?:ヴェ|ベ)・?", r"(?:ヴェ|ベ)ー?・?"),
                 (r"(?:ヴォ|ボ)ー?・?", r"(?:ヴォ|ボ)ー?・?"),
                 (r"[ヴブ][ゥウー]・?", r"[ヴブ]ー?・?[ゥウー]ー?・?"),
                 (r"[ヴブ]・?", r"[ヴブ]ー?・?"),
                 (r"[ィイェエ](?=ッ?[キク][サシスセソ])",
                  r"[ィイェエ]ー?・?"),
                 (r"(?<!ッ)(?=[キク][サシスセソ])", r"ッ?ー?・?"),
                 (r"[キク](?=[サシスセソ])", r"[キク]ー?・?"),
                 (r"[リレ]ー?・?", r"[リレ]ー?・?"),
                 (r"(?<=ロ)[カケ]ー?・?", r"[カケ]ー?・?"),
                 (r"(?<=ー)[サザ]ー?・?", r"[サザ]ー?・?"),
                 (r"(?<=[イィニヒリ])[ヤア]ー?・?", r"[ヤア]ー?・?"),
                 (r"(?<xi>[キギシジチヂニヒビピミリ" +
                  r"ェエケゲセゼテデネヘベペメレ" +
                  r"ゥウヴクグスズツヅヌフブプムユル])[ィイー]・?",
                  r"{xi}ー?・?[ィイー]ー?・?"),
                 (r"(?<xu>[ォオコゴソゾトドノホボポモヨロ" +
                  r"ヴクグスズツヅヌフブプムユル])[ゥウー]・?",
                  r"{xu}ー?・?[ゥウー]ー?・?"),
                 (r"(?<xo>[コゴソゾトドノホボポモヨロ" +
                  r"ゥウヴクグスズツヅヌフブプムユル])[ォオー]・?",
                  r"{xo}ー?・?[ォオー]ー?・?"),
                 (r"ッー?・?", r"ッ?ー?・?"),
                 (r"ァー?・?", r"ァ?ー?・?"),
                 (r"ィー?・?", r"ィ?ー?・?"),
                 (r"ゥー?・?", r"ゥ?ー?・?"),
                 (r"ェー?・?", r"ェ?ー?・?"),
                 (r"ォー?・?", r"ォ?ー?・?"),
                 (r"ー・?", r"ー?・?"),
                 (r"・", r"・?"),
                 (r"(?<anychar>.)ー?・?", r"{anychar}ー?・?")]


class KanayureChecker:
    def __init__(self,
                 root_dir=".",
                 include_dirs=None,
                 exclude_dirs=None,
                 include_files=None,
                 exclude_files=None,
                 boundary=None):
        self.status_code = 0
        self.root_dir = root_dir
        self.include_dirs = include_dirs
        self.exclude_dirs = exclude_dirs
        self.include_files = include_files
        self.exclude_files = exclude_files
        self.count = {}
        self.summary = {}
        self.reference = {}
        self.num_files = 0
        self.re_near_char = None
        self.re_near_char_dict = None
        if boundary is None:
            boundary = r"\s*\n\s*"
        self.re_katakana = self.make_re_katakana(boundary=boundary)
        self.re_boundary = self.make_re_boundary(boundary=boundary)

    def run(self):
        start_time = time.time()
        files = FileList(root_dir=self.root_dir,
                         include_dirs=self.include_dirs,
                         exclude_dirs=self.exclude_dirs,
                         include_files=self.include_files,
                         exclude_files=self.exclude_files)
        for filepath in files:
            self.check_file(filepath)
        self.make_near_index()
        self.output_result("katakana_words.txt",
                           self.report_katakana_words)
        self.output_result("katakana_variants.txt",
                           self.report_katakana_variants)
        print("{} files are checked".format(self.num_files))
        end_time = time.time()
        print("Elapsed time: {0:.3f} seconds".format(end_time - start_time))

        return self.status_code

    def make_re_katakana(self, boundary):
        return regex.compile(RE_KATAKANA_BASE.format(boundary=boundary))

    def make_re_boundary(self, boundary):
        return regex.compile(RE_BOUNDARY_BASE.format(boundary=boundary))

    def add_summary(self, word, word_range, lines, border=False):
        start = word_range[0]
        end = word_range[1]
        for x in range(2):
            new_start = lines.rfind("\n", 0, start)
            if new_start == -1:
                new_start = 0
            start = max(new_start, 0)

            new_end = lines.find("\n", end)
            if new_end == -1:
                new_end = len(lines)
            end = min(new_end, len(lines))
        self.summary[word] = lines[start:end + 1]

    def check_file(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            lines = file.read()
            self.num_files += 1
            for match in self.re_katakana.finditer(lines):
                border = False
                if match.group(1) is None:
                    word = match.group(0)
                else:
                    border = True
                    raw_word = match.group(0)
                    word = self.re_boundary.sub("", raw_word)
                if word in self.count:
                    self.count[word] += 1
                else:
                    self.count[word] = 1
                    relative_path = os.path.relpath(filepath, self.root_dir)
                    self.reference[word] = relative_path
                    word_range = match.span(0)
                    self.add_summary(word,
                                     word_range,
                                     lines,
                                     border=border)

    def output_result(self, filename, function):
        with open(filename, mode='w', encoding='utf-8') as a_file:
            with RedirectStdoutTo(a_file):
                function()

    def make_same_counted_words(self):
        same_counted_words = defaultdict(list)
        for word, counted in self.count.items():
            same_counted_words[counted].append(word)
        return same_counted_words

    def get_re_near_char(self, match):
        group_name = match.lastgroup
        group_dict = match.groupdict
        if group_name in self.re_near_char_flag:
            return self.re_near_char_dict[group_name].format(**group_dict())
        else:
            return self.re_near_char_dict[group_name]

    def make_re_near_word(self, word):
        if self.re_near_char is None or self.re_near_char_dict is None:
            re_near_char_list = []
            re_near_char_dict = {}
            re_near_char_flag = set()
            for key, (re_from_char, re_to_char) in enumerate(RE_CHAR_TABLE):
                re_near_char_list.append(r"(?<g{}>{})".format(key,
                                                              re_from_char))
                re_near_char_dict["g" + str(key)] = re_to_char
                try:
                    re_to_char.format()
                except KeyError:
                    re_near_char_flag.add("g" + str(key))
            re_near_char = r"(?:" + r"|".join(re_near_char_list) + r")"
            self.re_near_char = regex.compile(re_near_char)
            self.re_near_char_dict = re_near_char_dict
            self.re_near_char_flag = re_near_char_flag
        re_near_word = self.re_near_char.sub(self.get_re_near_char, word)
        return re_near_word

    def make_near_index_base(self, word_list):
        near_index_base = defaultdict(set)
        all_words = '#' + "#".join(word_list) + '#'
        all_words_dict = defaultdict(list)
        for word in word_list:
            all_words_dict[word[0]].append(word)
        for word in word_list:
            re_near_word = self.make_re_near_word(word)
            if re_near_word[0] not in '([' and re_near_word[1] not in '?':
                regex_near_word = regex.compile(r"\A" + re_near_word + r"\Z")
                variant_words = [a_word for a_word in
                                 all_words_dict[re_near_word[0]]
                                 if word != a_word and
                                 regex_near_word.match(a_word) is not None]
                if variant_words != []:
                    near_index_base[word] = set(variant_words)
            else:
                for match in regex.finditer(r"#(" + re_near_word + r")(?=#)",
                                            all_words):
                    near_word = match.group(1)
                    if near_word == word:
                        continue
                    near_index_base[word].add(near_word)
        return near_index_base

    def find_near_words(self, word, near_words):
        if word in near_words:
            return near_words
        near_words.add(word)
        if word not in self.near_index_base:
            return near_words
        typical_word = None
        for near_word in self.near_index_base[word]:
            if near_word in self.typical_word:
                if typical_word is None:
                    typical_word = self.typical_word[near_word]
                near_words |= self.near_index[self.typical_word[near_word]]
            else:
                if near_word in near_words:
                    continue
                near_words = self.find_near_words(near_word, near_words)
        return near_words

    def make_near_index(self):
        self.near_index_base = self.make_near_index_base(self.count.keys())
        self.near_index = {}
        self.typical_word = {}
        for word in self.near_index_base:
            near_words = self.find_near_words(word, set())
            typical_word = None
            for near_word in near_words:
                if near_word in self.typical_word and near_word is not None:
                    typical_word = self.typical_word[near_word]
                    break
            if typical_word is None:
                typical_word = word
            for near_word in near_words:
                self.typical_word[near_word] = typical_word
            self.near_index[typical_word] = near_words

    def make_near_words_string(self, word, ignore_self=True):
            typical_word = self.typical_word[word]
            near_words = self.near_index[typical_word].copy()
            if ignore_self:
                near_words.discard(word)
            with_count = [(self.count[a_word],
                           a_word) for a_word in near_words]
            with_count.sort(reverse=True)
            near_string = ["{}({})".format(
                           word, counted) for counted, word in with_count]
            return "、".join(near_string)

    def report_katakana_words(self):
        same_counted_words = self.make_same_counted_words()
        for counted in sorted(same_counted_words.keys()):
            for word in sorted(same_counted_words[counted]):
                typical_word = self.typical_word.get(word, None)
                if typical_word in self.near_index:
                    near_string = self.make_near_words_string(word)
                    print("### {}({}): {}".format(
                        word, counted, near_string))
                else:
                    print("### {}({}):".format(word, counted))
                print("File:", self.reference[word])
                print(self.summary[word])

    def report_katakana_variants(self):
        near_words_list = []
        for word in self.near_index:
            near_words_string = self.make_near_words_string(word,
                                                            ignore_self=False)
            near_words_list.append(near_words_string)
        near_words_list.sort()
        for near_words in near_words_list:
            print(near_words)
