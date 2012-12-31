#!/usr/bin/env python3
# vim:fileencoding=utf-8

import argparse
import sys

from kanayure.checker import KanayureChecker


class KanayureCommand:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.argv = sys.argv[1:]

    def run(self):
        if self.kwargs == {}:
            kwargs = self.parse_args(self.argv)
        else:
            kwargs = self.kwargs

        checker = KanayureChecker(**kwargs)
        status_code = checker.run()
        sys.exit(status_code)

    def parse_args(self, argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('-d',
                            '--root-dir',
                            type=str,
                            help='document root directory')
        parser.add_argument('-b',
                            '--boundary',
                            type=str,
                            help='line boundary')
        parser.add_argument('-id',
                            '--include-dirs',
                            type=str,
                            help='include dirs matching pattern')
        parser.add_argument('-ed',
                            '--exclude-dirs',
                            type=str,
                            help='exclude dirs matching pattern')
        parser.add_argument('-if',
                            '--include-files',
                            type=str,
                            help='include files matching pattern')
        parser.add_argument('-ef',
                            '--exclude-files',
                            type=str,
                            help='exclude files matching pattern')
        args = vars(parser.parse_args(argv))

        for argument in ("include_dirs", "exclude_dirs",
                         "include_files", "exclude_files"):
            if args[argument] is not None:
                args[argument] = set(args[argument].split(","))
        return args
