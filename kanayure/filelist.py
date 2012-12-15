#!/usr/bin/env python3
# vim:fileencoding=utf-8

# Copyright (c) 2012 Masami HIRATA <msmhrt@gmail.com>

import fnmatch
import os
import re

INCLUDE_DIRS = set()
EXCLUDE_DIRS = {'__pycache__', 'CVS', '.bzr', '.git', '.hg', '.svn'}
INCLUDE_FILES = set()
EXCLUDE_FILES = set()


class FileList:
    def __init__(self, root_dir=".",
                 include_dirs=None, exclude_dirs=None,
                 include_files=None, exclude_files=None):
        if root_dir is None:
            root_dir = "."
        if include_dirs is None:
            include_dirs = INCLUDE_DIRS
        if exclude_dirs is None:
            exclude_dirs = EXCLUDE_DIRS
        if include_files is None:
            include_files = INCLUDE_FILES
        if exclude_files is None:
            exclude_files = EXCLUDE_FILES

        self.root_dir = root_dir
        self.re_include_dirs = self.compile_globs(include_dirs)
        self.re_exclude_dirs = self.compile_globs(exclude_dirs)
        self.re_include_files = self.compile_globs(include_files)
        self.re_exclude_files = self.compile_globs(exclude_files)

    def compile_globs(self, glob_set):
        if len(glob_set) == 0:
            return None
        pattern = "|".join([fnmatch.translate(x) for x in glob_set])
        return re.compile(pattern)

    def is_ignored_dir(self, dirpath):
        dirname = os.path.basename(dirpath)
        if (self.re_exclude_dirs is not None and
                self.re_exclude_dirs.match(dirname) is not None):
            return True
        if (self.re_include_dirs is None or
                self.re_include_dirs.match(dirname) is not None):
            return False
        return True

    def is_ignored_file(self, filename):
        if (self.re_exclude_files is not None and
                self.re_exclude_files.match(filename) is not None):
            return True
        if (self.re_include_files is None or
                self.re_include_files.match(filename) is not None):
            return False
        return True

    def find_files(self):
        ignored_dirpath = None
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            if (ignored_dirpath is not None and
                    dirpath.startswith(ignored_dirpath)):
                continue
            if self.is_ignored_dir(dirpath):
                ignored_dirpath = dirpath
                continue
            for filename in filenames:
                yield (dirpath, filename)

    def __iter__(self):
        for dirpath, filename in self.find_files():
            if self.is_ignored_file(filename):
                continue
            filepath = os.path.join(dirpath, filename)
            yield filepath
