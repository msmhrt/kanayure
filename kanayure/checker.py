#!/usr/bin/env python3
# vim:fileencoding=utf-8

# Copyright (c) 2012 Masami HIRATA <msmhrt@gmail.com>

import os

import regex

from kanayure.util import RedirectStdoutTo, KeyIndex
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
RE_CHAR_TABLE = [(r"(?:ディ|ヂ|デ)", r"(?:ディ|ヂ|デ)ー?・?"),
                 (r"(?:ファ|ハ)", r"(?:ファ|ハ)ー?・?"),
                 (r"(?:フィ|ヒ)", r"(?:フィ|ヒ)ー?・?"),
                 #(r"(?:フゥ|フ)", r"(?:フゥ|フ)ー?・?"),  # DON'T USE
                 (r"(?:フェ|ヘ)", r"(?:フェ|ヘ)ー?・?"),
                 (r"(?:フォ|ホ)", r"(?:フォ|ホ)ー?・?"),
                 (r"(?:ヴァ|バ)", r"(?:ヴァ|バ)ー?・?"),
                 (r"(?:ヴィ|ビ)", r"(?:ヴィ|ビ)ー?・?"),
                 (r"(?:ヴェ|ベ)", r"(?:ヴェ|ベ)ー?・?"),
                 (r"(?:ヴォ|ボ)", r"(?:ヴォ|ボ)ー?・?"),
                 (r"(?:ヴ|ブ)", r"(?:ヴ|ブ)ー?・?"),
                 (r"[キク](?=[サシスセソ])", r"[キク]ー?・?"),
                 (r"(?=[キク][サシスセソ])", r"ッ?"),
                 (r"(?:[リレ])", r"(?:[リレ])ー?・?"),
                 (r"(?<=ロ)(?:[カケ])", r"(?:[カケ])ー?・?"),
                 (r"(?<=ー)(?:[サザ])", r"(?:[サザ])ー?・?"),
                 (r"(?<=[イィニヒリ])(?:[ヤア])", r"(?:[ヤア])ー?・?"),
                 (r"(?<=ク)(?:[ォオ])", r"(?:[ォオ])ー?・?"),
                 (r"(?<=[オコゴソゾトドノホボポモヨロ" +
                  r"クグスズツヅヌフブプムユル])(?:[ゥウー])",
                  r"(?:[ゥウー])?・?"),
                 (r"(?<=ェ)(?:[イー])", r"イ?ー?・?"),
                 (r"ッ", r"ッ?ー?・?"),
                 (r"ァ", r"ァ?ー?・?"),
                 (r"ィ", r"ィ?ー?・?"),
                 (r"ゥ", r"ゥ?ー?・?"),
                 (r"ェ", r"ェ?ー?・?"),
                 (r"ォ", r"ォ?ー?・?"),
                 (r"ー", r"ー?・?"),
                 (r"・", r"・?"),
                 (r"(?<anychar>.)", r"{anychar}ー?・?")]


class KanayureChecker:
    def __init__(self,
                 root_dir=".",
                 include_dirs=None,
                 exclude_dirs=None,
                 include_files=None,
                 exclude_files=None,
                 boundary=None):
        self.root_dir = root_dir
        self.include_dirs = include_dirs
        self.exclude_dirs = exclude_dirs
        self.include_files = include_files
        self.exclude_files = exclude_files
        self.word = KeyIndex()
        self.raw_word = KeyIndex()
        self.index = {}
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
        self.run()

    def run(self):
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

    def make_re_katakana(self, boundary):
        return regex.compile(RE_KATAKANA_BASE.format(boundary=boundary))

    def make_re_boundary(self, boundary):
        return regex.compile(RE_BOUNDARY_BASE.format(boundary=boundary))

    def add_index(self, word_number, raw_word_number):
        if word_number in self.index:
            self.index[word_number].add(raw_word_number)
        else:
            self.index[word_number] = {raw_word_number}

    def word_count_up(self, word_number):
        if word_number in self.count:
            self.count[word_number] += 1
        else:
            self.count[word_number] = 1

    def add_summary(self, word_number, word_range, lines, border=False):
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
        self.summary[word_number] = lines[start:end + 1]

    def add_reference(self, word_number, filepath):
        relative_path = os.path.relpath(filepath, self.root_dir)
        self.reference[word_number] = relative_path

    def check_file(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            lines = file.read()
            self.num_files += 1
            for match in self.re_katakana.finditer(lines):
                border = False
                if match.group(1) is None:
                    word = match.group(0)
                    word_number = self.word.add(word)
                else:
                    border = True
                    raw_word = match.group(0)
                    word = self.re_boundary.sub("", raw_word)

                    word_number = self.word.add(word)
                    raw_word_number = self.raw_word.add(raw_word)
                    self.add_index(word_number, raw_word_number)

                word_range = match.span(0)
                if word_number not in self.reference:
                    self.add_reference(word_number, filepath)
                if word_number not in self.summary:
                    self.add_summary(word_number,
                                     word_range,
                                     lines,
                                     border=border)
                self.word_count_up(word_number)

    def output_result(self, filename, function):
        with open(filename, mode='w', encoding='utf-8') as a_file:
            with RedirectStdoutTo(a_file):
                function()

    def make_same_counted_words(self):
        same_counted_words = {}
        for word_number, counted in self.count.items():
            word = self.word.get_key(word_number)
            if counted in same_counted_words:
                same_counted_words[counted].append(word)
            else:
                same_counted_words[counted] = [word]
        return same_counted_words

    def get_re_near_char(self, match):
        group_name = match.lastgroup
        return self.re_near_char_dict[group_name].format(**match.groupdict())

    def make_re_near_word(self, word):
        if self.re_near_char is None or self.re_near_char_dict is None:
            re_near_char_list = []
            re_near_char_dict = {}
            for key, (re_from_char, re_to_char) in enumerate(RE_CHAR_TABLE):
                re_near_char_list.append(r"(?<g{}>{})".format(key,
                                                              re_from_char))
                re_near_char_dict["g" + str(key)] = re_to_char
            re_near_char = r"(?:" + r"|".join(re_near_char_list) + r")"
            self.re_near_char = regex.compile(re_near_char)
            self.re_near_char_dict = re_near_char_dict
        re_near_word = self.re_near_char.sub(self.get_re_near_char, word)
        return r"#(" + re_near_word + r")(?=#)"

    def make_near_index_base(self, word_list):
        near_index_base = {}
        all_words = '#' + "#".join(word_list) + '#'
        for word in word_list:
            for match in regex.finditer(self.make_re_near_word(word),
                                        all_words):
                near_word = match.group(1)
                if near_word == word:
                    continue
                if word in near_index_base:
                    near_index_base[word].add(near_word)
                else:
                    near_index_base[word] = {near_word}
        return near_index_base

    def get_near_words(self, word):
        near_words = set()
        if word in self.typical_word:
            return near_words
        # Don't set word to self.typical_word[word] yet
        self.typical_word[word] = None
        if word not in self.near_index_base:
            return {word}
        for near_word in self.near_index_base[word]:
            near_words.add(near_word)
            near_words |= self.get_near_words(near_word)
        return near_words

    def find_near_words(self, word, near_words):
        if word in near_words:
            return near_words
        near_words.add(word)
        if word not in self.near_index_base:
            return near_words
        for near_word in self.near_index_base[word]:
            if word in self.near_index:
                near_words |= self.near_index(word)
            near_words |= self.get_near_words(near_word)
        return near_words

    def make_near_index(self):
        self.near_index_base = self.make_near_index_base(self.word.table)
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
                for near_word in near_words:
                    self.typical_word[near_word] = word
                self.near_index[word] = near_words
            else:
                near_words -= self.near_index[typical_word]
                for near_word in near_words:
                    self.typical_word[near_word] = typical_word

    def make_near_words_string(self, word, ignore_self=True):
            typical_word = self.typical_word[word]
            near_words = self.near_index[typical_word].copy()
            if ignore_self:
                near_words.discard(word)
            with_count = [(self.count[self.word.get_number(a_word)],
                           a_word) for a_word in near_words]
            with_count.sort(reverse=True)
            near_string = ["{}({})".format(
                           word, counted) for counted, word in with_count]
            return "、".join(near_string)

    def report_katakana_words(self):
        same_counted_words = self.make_same_counted_words()
        for counted in sorted(same_counted_words.keys()):
            for word in sorted(same_counted_words[counted]):
                word_number = self.word.get_number(word)
                typical_word = self.typical_word.get(word, None)
                if typical_word in self.near_index:
                    near_string = self.make_near_words_string(word)
                    print("### {}({}): {}".format(
                        word, counted, near_string))
                else:
                    print("### {}({}):".format(word, counted))
                print("File:", self.reference[word_number])
                print(self.summary[word_number])

    def report_katakana_variants(self):
        near_words_list = []
        for word in self.near_index:
            near_words_string = self.make_near_words_string(word,
                                                            ignore_self=False)
            near_words_list.append(near_words_string)
        near_words_list.sort()
        for near_words in near_words_list:
            print(near_words)
