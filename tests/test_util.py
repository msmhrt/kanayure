#!/usr/bin/env python3
# vim:fileencoding=utf-8

# Copyright (c) 2012 Masami HIRATA <msmhrt@gmail.com>

from itertools import chain
import unittest


class TestRedirectStdoutTo:
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__init__(self):
        pass


class TestKeyIndex(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_index(self):
        from kanayure.util import KeyIndex
        key_list = ['a', 'b', 'c', 'd', 'e']
        reverse_enumerate = lambda a_list: zip(reversed(range(len(a_list))),
                                               reversed(a_list))
        index = KeyIndex()
        self.assertIsInstance(index, KeyIndex)
        for number, key in chain(enumerate(key_list),
                                 reverse_enumerate(key_list)):
            index_number = index.add(key)
            self.assertEqual(index_number, number)
            self.assertEqual(index_number, index.get_number(key))
            self.assertEqual(index.get_key(index_number), key)

    def test_add(self):
        from kanayure.util import KeyIndex

        # create empty index
        index = KeyIndex()

        # tests for empty index
        test_suite = ((KeyError, None),
                      (TypeError, []))
        for exception, key in test_suite:
            with self.assertRaises(exception):
                index.add(key)

        # add keys to index
        for key in ['a', 'b', 'c', 'd', False]:
            index.add(key)

        # tests for index
        for exception, key in test_suite:
            with self.assertRaises(exception):
                index.add(key)

    def test_get_number(self):
        from kanayure.util import KeyIndex

        # create empty index
        index = KeyIndex()

        # tests for empty index
        test_suite = ((KeyError, 0),
                      (KeyError, False),
                      (KeyError, None),
                      (TypeError, []))
        for exception, key in test_suite:
            with self.assertRaises(exception):
                index.get_number(key)

        # add keys to index
        for key in ['a', 'b', 'c', 'd', 'e']:
            index.add(key)

        # tests for index
        for exception, key in test_suite + ((KeyError, 'f'),):
            with self.assertRaises(exception):
                index.get_number(key)

    def test_get_key(self):
        from kanayure.util import KeyIndex

        # create empty index
        index = KeyIndex()

        # tests for empty index
        test_suite = ((IndexError, 0),
                      (IndexError, False),
                      (TypeError, None),
                      (TypeError, []))
        for exception, number in test_suite:
            with self.assertRaises(exception):
                index.get_key(number)

        # add keys to index
        for key in ['a', 'b', 'c', 'd', 'e']:
            index.add(key)

        # tests for index
        test_suite = ((TypeError, None),
                      (TypeError, []),
                      (IndexError, -1),
                      (IndexError, 5))
        for exception, number in test_suite:
            with self.assertRaises(exception):
                index.get_key(number)
        self.assertEqual(index.get_key(False), 'a')

    def test_sort(self):
        from kanayure.util import KeyIndex

        # create empty old2new_index
        index = KeyIndex()
        old2new_index = index.sort()

        # tests for sorted index
        self.assertIsInstance(index, KeyIndex)
        self.assertEqual(len(index), 0)
        with self.assertRaises(IndexError):
            index.get_key(0)

        # tests for empty old2new_index
        self.assertIsInstance(old2new_index, KeyIndex)
        self.assertEqual(len(old2new_index), 0)
        with self.assertRaises(IndexError):
            old2new_index.get_key(0)

        # create sorted index and old2new_index
        key_list = ['a', 'b', 'c', 'd', 'e']
        for key in reversed(key_list):
            index.add(key)
        old2new_index = index.sort()

        # tests for sorted index
        for number, key in enumerate(key_list):
            self.assertEqual(index.get_number(key), number)
            self.assertEqual(index.get_key(number), key)

        # tests for old2new_index
        self.assertIsInstance(old2new_index, KeyIndex)
        self.assertEqual(len(old2new_index), len(key_list))
        for number, key in enumerate(reversed(range(5))):
            self.assertEqual(old2new_index.get_key(number), key)
            self.assertEqual(old2new_index.get_number(key), number)

    def test__len__(self):
        from kanayure.util import KeyIndex
        index = KeyIndex()
        self.assertEqual(len(index), 0)
        for number, key in enumerate(['a', 'b', 'c', 'd', 'e']):
            self.assertEqual(len(index), number)
            index.add(key)
            self.assertEqual(len(index), number + 1)
