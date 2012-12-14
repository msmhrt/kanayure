#!/usr/bin/env python3
# vim:fileencoding=utf-8

# Copyright (c) 2012 Masami HIRATA <msmhrt@gmail.com>

import unittest

from mock import patch


class TestFileList(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filelist(self):
        pass

    def test_compile_globs(self):
        from kanayure.filelist import FileList
        filelist = FileList()
        self.assertIsNone(filelist.compile_globs(set()))
        self.assertIsNotNone(filelist.compile_globs({'a'}))

    def test_is_ignored_dir(self):
        from kanayure.filelist import FileList
        testcases = ((set(), set(), r"a\b", False),
                     (set(), {'a'}, r"a\b", False),
                     (set(), {'b'}, r"a\b", True),
                     (set(), {'a', 'b'}, r"a\b", True),
                     (set(), {'*'}, r"a\b", True),
                     (set(), {'a', '*'}, r"a\b", True),
                     (set(), {'b', '*'}, r"a\b", True),
                     ({'a'}, set(), r"a\b", True),
                     ({'b'}, set(), r"a\b", False),
                     ({'a', 'b'}, set(), r"a\b", False),
                     ({'*'}, set(), r"a\b", False),
                     ({'a', '*'}, set(), r"a\b", False),
                     ({'b', '*'}, set(), r"a\b", False),
                     ({'*', 'a'}, set(), r"a\b", False),
                     ({'*', 'b'}, set(), r"a\b", False),
                     ({'a'}, {'b'}, r"a\b", True),
                     ({'b'}, {'a'}, r"a\b", False),
                     ({'a'}, {'a'}, r"a\b", True),
                     ({'b'}, {'b'}, r"a\b", True),
                     ({'*'}, {'*'}, r"a\b", True))
        message = ("\n" +
                   "include_dirs = {}\n" +
                   "exclude_dirs = {}\n" +
                   "dirpath = {}\n" +
                   "ignore = {}\n")
        for testcase in testcases:
            include_dirs, exclude_dirs, dirpath, ignore = testcase
            filelist = FileList(include_dirs=include_dirs,
                                exclude_dirs=exclude_dirs)
            if ignore:
                self.assertTrue(filelist.is_ignored_dir(dirpath),
                                message.format(*testcase) +
                                repr(testcase))
            else:
                self.assertFalse(filelist.is_ignored_dir(dirpath),
                                 message.format(*testcase) +
                                 repr(testcase))

    def test_is_ignored_file(self):
        from kanayure.filelist import FileList
        testcases = ((set(), set(), 'a', False),
                     (set(), {'a'}, 'a', True),
                     (set(), {'b'}, 'a', False),
                     (set(), {'a', 'b'}, 'a', True),
                     (set(), {'*'}, 'a', True),
                     (set(), {'a', '*'}, 'a', True),
                     (set(), {'b', '*'}, 'a', True),
                     ({'a'}, set(), 'a', False),
                     ({'b'}, set(), 'a', True),
                     ({'a', 'b'}, set(), 'a', False),
                     ({'*'}, set(), 'a', False),
                     ({'a', '*'}, set(), 'a', False),
                     ({'b', '*'}, set(), 'a', False),
                     ({'*', 'a'}, set(), 'a', False),
                     ({'*', 'b'}, set(), 'a', False),
                     ({'a'}, {'b'}, 'a', False),
                     ({'b'}, {'a'}, 'a', True),
                     ({'a'}, {'a'}, 'a', True),
                     ({'b'}, {'b'}, 'a', True),
                     ({'*'}, {'*'}, 'a', True))
        message = ("\n" +
                   "include_files = {}\n" +
                   "exclude_files = {}\n" +
                   "filename = {}\n" +
                   "ignore = {}\n")
        for testcase in testcases:
            include_files, exclude_files, filename, ignore = testcase
            filelist = FileList(include_files=include_files,
                                exclude_files=exclude_files,)
            if ignore:
                self.assertTrue(filelist.is_ignored_file(filename),
                                message.format(*testcase) +
                                repr(testcase))
            else:
                self.assertFalse(filelist.is_ignored_file(filename),
                                 message.format(*testcase) +
                                 repr(testcase))

    @patch("os.walk")
    def test_find_files(self, mock_walk):
        mock_walk.return_value = iter(((r'a\a', 'b', 'cd'),
                                       (r'a\a\b', 'e', 'fg'),
                                       (r'a\a\b\e', 'h', ''),
                                       (r'a\i', '', 'j'),
                                       (r'k', 'lm', 'no')))
        from kanayure.filelist import FileList
        filenames = FileList(include_dirs={'a', 'e', 'i'},
                             exclude_dirs={'b', 'e', 'k'})
        test_result = [r'a\a\c', r'a\a\d', r'a\i\j']
        self.assertEqual(list(filenames), test_result)

    @patch("kanayure.filelist.FileList.find_files")
    def test_walk_files(self, mock_find_files):
        mock_find_files.return_value = iter((('a', 'b'),
                                             ('c', 'd'),
                                             ('e', 'f'),
                                             ('g', 'h'),
                                             ('i', 'j')))
        from kanayure.filelist import FileList
        filenames = FileList(include_files={'d', 'f', 'h'},
                             exclude_files={'b', 'f', 'j'})
        self.assertEqual(list(filenames), [r'c\d', r'g\h'])
