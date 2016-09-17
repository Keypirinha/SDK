# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2016 Jean-Charles Lefebvre <polyvertex@gmail.com>

import os
import stat
from . import _glob

__all__ = ["FsEntry", "globscan", "iglobscan"]

_is_windows = os.name.lower() == "nt"

class FsEntry:
    """A :py:class:`os.DirEntry` compatible class."""
    def is_hidden(self, follow_symlinks=True):
        return _is_hidden(self, follow_symlinks=follow_symlinks)

class _FsEntryDirEntry(FsEntry):
    def __init__(self, direntry, basedir):
        # os.DirEntry type may be nt.DirEntry or posix.DirEntry (as of 3.5.2),
        # so a more flexible test has been preferred over a usual isinstance()
        assert(direntry.__class__.__name__ == "DirEntry")
        assert(isinstance(basedir, str))
        self._direntry = direntry
        self.basedir = basedir
        self.relpath = os.path.normpath(direntry.path) # normpath() to remove "./" prefix
        self.path = os.path.join(self.basedir, self.relpath)

    def __getattr__(self, attr):
        return getattr(self._direntry, attr)

class _FsEntryPath(FsEntry):
    def __init__(self, relpath, basedir):
        assert(isinstance(relpath, str))
        assert(isinstance(basedir, str))
        self.relpath = os.path.normpath(relpath) # normpath() to remove "./" prefix
        self.name = os.path.basename(self.relpath)
        self.basedir = basedir
        self.path = os.path.join(self.basedir, self.relpath)
        self._stat = None
        self._lstat = None

    def inode(self):
        return self.stat(follow_symlinks=False).st_ino

    def is_dir(self, *, follow_symlinks=True):
        return stat.S_ISDIR(self.stat(follow_symlinks).st_mode)

    def is_file(self, *, follow_symlinks=True):
        return stat.S_ISREG(self.stat(follow_symlinks).st_mode)

    def is_symlink(self):
        return stat.S_ISLNK(self.stat(follow_symlinks=False).st_mode)

    def stat(self, follow_symlinks=True):
        if follow_symlinks:
            if not self._stat:
                self._stat = os.stat(self.path, follow_symlinks=follow_symlinks)
            return self._stat
        else:
            if not self._lstat:
                self._lstat = os.stat(self.path, follow_symlinks=follow_symlinks)
            return self._lstat

def globscan(
        input_paths, recursive=False, allow_wildcards=True,
        include_dirs=True, include_hidden=False,
        raise_not_found=True):
    """
    :py:func:`glob.glob` then scan *input_paths* and return a list of
    :py:class:`FsEntry` objects.

    *input_paths* can be a single string or an iterable that contains paths
    (wildcard are accepted unless *allow_wildcards* is false).

    A ``FileNotFoundError`` exception will be raised if one of the specified
    input paths is missing, unless the *raise_not_found* flag is false.

    :py:class:`FsEntry` is compatible with Python's :py:class:`os.DirEntry`
    class.

    **CAUTION:** this function **is not** thread-safe as it installs a trap at
    runtime (i.e. for :py:func:`glob._ishidden`). The ``glob`` module must not
    be used concurrently to this function.
    """
    return list(iglobscan(input_paths, recursive, allow_wildcards,
                            include_dirs, include_hidden, raise_not_found))

def iglobscan(
        input_paths, recursive=False, allow_wildcards=True,
        include_dirs=True, include_hidden=False,
        raise_not_found=True,
        _level=0):
    """
    Return an iterator which yields the same values as :py:func:`globscan`
    without actually storing them all simultaneously.

    **CAUTION:** this function **is not** thread-safe as it installs a trap at
    runtime (i.e. for :py:func:`glob._ishidden`). The ``glob`` module must not
    be used concurrently to this function.
    """
    # glob() and normalize input paths first
    if _level == 0:
        if isinstance(input_paths, str):
            input_paths = (input_paths, )
        caller_paths = input_paths[:] # copy
        input_paths = []
        for path in caller_paths:
            if not isinstance(path, str):
                raise TypeError("path is not a str: {}".format(path))
            if _glob.has_magic(path):
                if "**" in path:
                    # we prefer to disallow the use of the "**" wildcard here as
                    # its results would not always feel natural since this
                    # function is meant to be called to resolve paths that has
                    # been specified by an end-user from the command line
                    raise ValueError("'**' wildcard is not supported")
                if not allow_wildcards:
                    raise ValueError("input path has wildcard(s): " + path)
                for globbed_path in _glob.iglob(
                        path, include_hidden=include_hidden, recursive=False):
                    input_paths.append(os.path.realpath(globbed_path))
            elif not os.path.exists(path):
                # at level 0, we want to notify caller that an explicitely
                # specified file/dir is missing
                if raise_not_found:
                    raise FileNotFoundError("file not found: " + path)
            else:
                input_paths.append(os.path.realpath(path))
        oldcwd = os.getcwd()

    for input_path in input_paths:
        if os.path.isdir(input_path):
            try:
                if _level == 0:
                    os.chdir(input_path)
                    parent_dir = input_path
                    scan_dir = "."
                else:
                    parent_dir = os.getcwd()
                    scan_dir = os.path.relpath(input_path, start=parent_dir)

                for entry in os.scandir(scan_dir):
                    if not include_hidden and _is_hidden(entry):
                        continue
                    if entry.is_dir():
                        if include_dirs:
                            yield _FsEntryDirEntry(entry, parent_dir)
                        if recursive:
                            yield from iglobscan(
                                (entry.path, ), recursive, allow_wildcards,
                                include_dirs, include_hidden, raise_not_found,
                                _level + 1)
                    else:
                        yield _FsEntryDirEntry(entry, parent_dir)
            finally:
                if _level == 0:
                    os.chdir(oldcwd)
        else:
            # note: do not do a _is_hidden() test here since this *input_path*
            # has been specified explicitly by the caller
            if _level == 0:
                yield _FsEntryPath(
                    os.path.basename(input_path),
                    os.path.dirname(input_path))
            else:
                yield _FsEntryPath(input_path, os.getcwd())

def _is_hidden(entry, follow_symlinks=True):
    # note: *entry* can be a DirEntry or a FsEntry
    if entry.name[0] is ".":
        return True
    if _is_windows:
        attr = entry.stat(follow_symlinks=follow_symlinks).st_file_attributes
        if attr & stat.FILE_ATTRIBUTE_HIDDEN:
            return True
    return False
