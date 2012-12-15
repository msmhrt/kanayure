#!/usr/bin/env python3
# vim:fileencoding=utf-8

# Copyright (c) 2012 Masami HIRATA <msmhrt@gmail.com>

import unittest

from mock import patch


class TestKanayureChecker(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('kanayure.checker.KanayureChecker.run')
    def test_make_re_near_word(self, mock_run):
        from kanayure.checker import KanayureChecker
        testdata = (("アー", ["ア"], ["イ"]),
                    ("ア・イ", ["アイ", "アーイ"], ["ア・ン", "ア・"]),
                    ("イアー", ["イヤー"], []),
                    ("ヴァヴィヴヴェヴォ", ["バビブベボ"], []),
                    ("ディストラクタ", ["デストラクタ"], []),
                    ("ウィンドゥ", ["ウィンドウ", "ウィンドー"], []),
                    ("ウィンドウ", ["ウィンドゥ", "ウィンドー"], []),
                    ("ウィンドー", ["ウィンドゥ", "ウィンドウ"], []),
                    ("デストラクタ", ["ディストラクタ"], []),
                    ("バック・ステップ", ["バックステップ"], []),
                    ("バックステップ", ["バック・ステップ"], []))
        for test_input, match_tests, no_match_tests in testdata:
            checker = KanayureChecker()
            re_near_word = checker.make_re_near_word(test_input)
            self.assertRegex("#" + test_input + "#", re_near_word)
            for match_test in match_tests:
                self.assertRegex("#" + match_test + "#", re_near_word)
            for no_match_test in no_match_tests:
                self.assertNotRegex("#" + no_match_test + "#", re_near_word)

    @patch('kanayure.checker.KanayureChecker.run')
    def test_make_near_index_base(self, mock_run):
        from kanayure.checker import KanayureChecker
        testdata = ((["アー", "ア"], {'ア': {'アー'}, 'アー': {'ア'}}),
                    (["ア", "アー"], {'ア': {'アー'}, 'アー': {'ア'}}),
                    (["ア", "ン"], {}),
                    (["ア・", "ア"], {'ア': {'ア・'}, 'ア・': {'ア'}}))
        for test_input, test_output in testdata:
            checker = KanayureChecker()
            near_index_base = checker.make_near_index_base(test_input)
            self.assertEqual(near_index_base, test_output)

    @patch('kanayure.checker.KanayureChecker.run')
    def test_find_near_words(self, mock_run):
        from kanayure.checker import KanayureChecker
        near_index_base = {"A": {"B"},
                           "C": {"B"}}
        testdata = (("A", {}, {}, set(), {"A", "B"}),
                    ("A", {}, {}, {"B"}, {"A", "B"}),
                    ("A", {}, {}, {"A", "B"}, {"A", "B"}),
                    ("C", {}, {}, {"A", "B"}, {"A", "B", "C"}),
                    ("A", {"B": "C"}, {"C": {"B", "C"}},
                     {"B"}, {"A", "B", "C"}))
        for num, (word,
                  typical_word,
                  near_index,
                  near_words_in,
                  near_words_out) in enumerate(testdata):
            checker = KanayureChecker()
            checker.near_index_base = near_index_base
            checker.near_index = near_index
            checker.typical_word = typical_word
            result = checker.find_near_words(word, near_words_in)
            self.assertSetEqual(result,
                                near_words_out,
                                "testdata = " + repr(testdata[num]))
