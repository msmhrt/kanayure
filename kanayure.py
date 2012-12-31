#!/usr/bin/env python3
# vim:fileencoding=utf-8

# Copyright (c) 2012 Masami HIRATA <msmhrt@gmail.com>

if __name__ == '__main__':  # pragma: nocover
    import sys

    from kanayure.checker import KanayureChecker

    checker = KanayureChecker(root_dir=r"..\py33",
                              include_files={"*.po"},
                              boundary=r"\"\s*\"")
    status_code = checker.run()
    sys.exit(status_code)
