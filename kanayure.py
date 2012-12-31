#!/usr/bin/env python3
# vim:fileencoding=utf-8

# Copyright (c) 2012 Masami HIRATA <msmhrt@gmail.com>

if __name__ == '__main__':  # pragma: nocover
    from kanayure.command import KanayureCommand

    command = KanayureCommand(root_dir=r"..\py33",
                              include_files={"*.po"},
                              boundary=r"\"\s*\"")
    command.run()
