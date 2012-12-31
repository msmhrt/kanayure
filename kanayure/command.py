#!/usr/bin/env python3
# vim:fileencoding=utf-8

import sys

from kanayure.checker import KanayureChecker


class KanayureCommand:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def run(self):
        checker = KanayureChecker(*self.args, **self.kwargs)
        status_code = checker.run()
        sys.exit(status_code)
