#!/usr/bin/env python3
# vim:fileencoding=utf-8

# Copyright (c) 2012 Masami HIRATA <msmhrt@gmail.com>

import sys


class RedirectStdoutTo:
    def __init__(self, new_stdout):
        self.new_stdout = new_stdout

    def __enter__(self):
        self.saved_stdout = sys.stdout
        sys.stdout = self.new_stdout

    def __exit__(self, *args):
        sys.stdout = self.saved_stdout


class KeyIndex:
    def __init__(self):
        self.table = []
        self.index = {}

    def add(self, key):
        if key is None:
            raise KeyError
        if key not in self.index:
            self.table.append(key)
            number = len(self.table) - 1
            self.index[key] = number
        return self.index[key]

    def get_number(self, key):
        if key not in self.index:
            raise KeyError
        return self.index[key]

    def get_key(self, number):
        if number < 0 or number >= len(self.table):
            raise IndexError
        return self.table[number]

    def sort(self):
        old_table = self.table[:]
        self.table.sort()
        self.index = {}
        for number, key in enumerate(self.table):
            self.index[key] = number
        old2new_index = KeyIndex()
        for number in range(len(self.table)):
            key = self.index[old_table[number]]
            old2new_index.add(key)
        return old2new_index

    def __len__(self):
        return len(self.table)
