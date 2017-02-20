# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2017 Jean-Charles Lefebvre <polyvertex@gmail.com>

import os
import re

__all__ = [
    "Unbuffered", "ReMatch",
    "merge_dicts", "is_iterable",
    "dir_is_empty",
    "file_head", "file_mtime_ns", "file_get_readonly", "file_set_readonly",
    "validate_package_name"]

class Unbuffered:
    """
    Unbuffered stream emulation
    Usage: ``sys.stdout = Unbuffered(sys.stdout)``
    """
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    def __getattr__(self, attr):
        return getattr(self.stream, attr)

class ReMatch:
    """
    Small class to re.match() and to hold its result.
    This is convenient if you want to "if re.match(): ... elif re.match(): ..."
    Usage:

    ::
        rem = ReMatch()
        if rem.match(...):
            print(rem.group(1, "default value here"))
        elif rem.match(...):
            ...
    """
    def __init__(self):
        self.m = None
    def __del__(self):
        re.purge()
    def clear(self):
        self.m = None
    def match(self, *objects, **kwargs):
        self.m = re.match(*objects, **kwargs)
        return bool(self.m)
    def group(self, index_or_name, default=None):
        try: return self.m.group(index_or_name)
        except IndexError: return default
    def __bool__(self):
        return bool(self.m)
    def __getattr__(self, attr):
        return getattr(self.m, attr)

def merge_dicts(*dicts):
    """Merge several dicts"""
    final_dict = None
    for d in dicts:
        if final_dict is None:
            final_dict = d.copy()
        else:
            final_dict.update(d)
    return {} if final_dict is None else final_dict

def is_iterable(obj):
    """
    Check if the passed object looks like an iterable, excluding :py:class:`str`
    and :py:class:`bytes` objects.
    """
    return hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes))

def dir_is_empty(path):
    """
    Check if the given directory is empty.
    May raise a FileNotFoundError or a NotADirectoryError exception.
    """
    for entry in os.scandir(path):
        return False
    return True

def file_head(file):
    """Read the first line of a text file."""
    with open(file, "rt") as f:
        return f.readline().rstrip()

def file_mtime_ns(file):
    """Get the ``os.stat(file).st_mtime_ns`` value."""
    return os.stat(file).st_mtime_ns

def file_get_readonly(path, follow_symlinks=True):
    """Check if a file has got the read-only attribute."""
    attr = os.stat(path, follow_symlinks=follow_symlinks).st_mode
    return not (attr & stat.S_IWRITE)

def file_set_readonly(path, enable):
    """Apply or remove the read-only property of a given file."""
    attr = os.stat(path)[stat.ST_MODE]
    new_attr = (
        (attr | stat.S_IREAD) & ~stat.S_IWRITE if enable
        else (attr | stat.S_IWRITE) & ~stat.S_IREAD)
    if new_attr != attr:
        os.chmod(path, new_attr)

def validate_package_name(name):
    """
    Check if the given name is compliant to Keypirinha's package naming rules
    and return a boolean.

    **CAUTION:** this function should just serve an informational purpose as it
    may not be up-to-date with current Keypirinha release.
    """
    ascii_alnum = "0123456789abcdefghijklmnopqrstuvwxyz" # str.isalnum() is unicode-compliant
    extra_chars = "-+=_#@()[]{}"
    name_lc = name.lower()

    if not isinstance(name, str):
        raise TypeError("package name not a str")
    if not (3 <= len(name) <= 50):
        return False
    if name_lc[0] not in ascii_alnum or name_lc[-1] not in ascii_alnum:
        return False

    if "keypirinha" in name_lc:
        return False

    lastc = ""
    for c in name_lc:
        if c in extra_chars:
            if lastc in extra_chars:
                return False
        elif c not in ascii_alnum:
            return False
        lastc = c

    if name_lc in (
            "keypirinha", "all", "app", "application", "builtin", "builtins",
            "cache", "data", "default", "env", "extern", "external", "hook",
            "icon", "image", "intern", "internal", "kpsdk", "local", "locale",
            "main", "name", "nil", "none", "null", "official", "package",
            "plugin", "python", "res", "resource", "sdk", "temp", "theme",
            "tmp", "type", "script", "user", "var"):
        return False

    return True
