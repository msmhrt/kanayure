#!/usr/bin/env python3
# vim:fileencoding=utf-8

import unittest

from mock import patch


class TestKanayureCommand(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_kanayurecommand(self):
        pass

    @patch('kanayure.command.KanayureChecker')
    def test_run(self, checker_mock):
        from kanayure.command import KanayureCommand

        checker_mock.return_value.run.return_value = 0
        with self.assertRaises(SystemExit) as assertion:
            command = KanayureCommand()
            command.argv = ["--root-dir=."]
            command.run()
        self.assertEqual(assertion.exception.code, 0)

        checker_mock.return_value.run.return_value = -1
        with self.assertRaises(SystemExit) as assertion:
            command = KanayureCommand()
            command.argv = ["--root-dir=."]
            command.run()
        self.assertEqual(assertion.exception.code, -1)

    def test_parse_args(self):
        from kanayure.command import KanayureCommand

        args = KanayureCommand().parse_args(["--root-dir=."])
        self.assertEqual(args["root_dir"], ".")
