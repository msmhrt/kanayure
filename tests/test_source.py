#!/usr/bin/env python3
# vim:fileencoding=utf-8

# Copyright (c) 2012 Masami HIRATA <msmhrt@gmail.com>

import os
import unittest

IGNORED_DIRS = {
    '__pycache__', 'CVS', '.bzr', '.git', '.hg', '.svn'}
IGNORED_FILES = {}
LINE_SHEBANG = "#!/usr/bin/env python3\n"
LINE_ENCODING = "# vim:fileencoding=utf-8\n"
ERROR_SHEBANG = "{}:1 does not contain a valid shebang"
ERROR_ENCODING = "{}:{} does not contain a valid encoding declaration"


class TestSourceCode(unittest.TestCase):
    def test_source_code(self):
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        dist_dir = os.path.dirname(tests_dir)
        for dirpath, dirnames, filenames in os.walk(dist_dir):
            if os.path.basename(dirpath) in IGNORED_DIRS:
                continue
            for filename in filenames:
                if (not filename.endswith('.py')
                        or filename in IGNORED_FILES):
                    continue
                filepath = os.path.join(dirpath, filename)
                if (filename == '__init__.py' and
                        os.path.getsize(filepath) == 0):
                    continue
                self._check_file(filepath)

    def _check_file(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            shebang = file.readline()
            if shebang.startswith("#!"):
                encoding = file.readline()
                encoding_line_no = 2
            else:
                encoding = shebang
                encoding_line_no = 1
            self.assertEqual(shebang, LINE_SHEBANG,
                             ERROR_SHEBANG.format(filepath))
            self.assertEqual(encoding, LINE_ENCODING,
                             ERROR_ENCODING.format(filepath,
                                                   encoding_line_no,
                                                   encoding))
