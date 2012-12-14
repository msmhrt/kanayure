#!/usr/bin/env python3
# vim:fileencoding=utf-8

# Copyright (c) 2012 Masami HIRATA <msmhrt@gmail.com>

import os
from subprocess import check_output, CalledProcessError, STDOUT

from unittest import TestCase


class TestPyflakes(TestCase):
    def test_pyflakes(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        dist_dir = os.path.dirname(test_dir)

        try:
            pyflakes_output = check_output(["pyflakes", dist_dir],
                                           stderr=STDOUT,
                                           shell=True).decode('mbcs')
        except CalledProcessError as exception:
            pyflakes_output = exception.output.decode('mbcs')
        message = "\n" + pyflakes_output
        self.assertEqual(len(pyflakes_output), 0, msg=message)
