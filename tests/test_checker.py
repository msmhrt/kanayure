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
