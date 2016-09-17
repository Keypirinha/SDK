# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2016 Jean-Charles Lefebvre <polyvertex@gmail.com>

import configparser
import os

__all__ = ["Config"]

class Config:
    """
    A replacement of ``configparser.ConfigParser`` that is compliant with
    Keypirinha's configuration file format.
    """
    def __init__(self, defaults={}):
        self.refdir = None
        self.parser = configparser.ConfigParser(
            defaults=defaults,
            delimiters=("="),
            comment_prefixes=("#"),
            strict=True, # disallow section/option duplicates
            interpolation=configparser.ExtendedInterpolation())

    def setrefdir(self, path):
        """Set a reference directory for path values (see ``getpath()``)."""
        self.refdir = os.path.normpath(os.path.realpath(path))

    def getstripped(self, *args, **kwargs):
        """
        Same as ``get()`` but ``str.strip()`` the returned value if
        possible.
        """
        value = self.parser.get(*args, **kwargs)
        return value.strip() if isinstance(value, str) else value

    def getmultiline(self, *args, keep_empty_lines=False, **kwargs):
        """Same as ``getstripped()`` but return an array of lines."""
        value = self.getstripped(*args, **kwargs)
        if isinstance(value, str):
            return [ln.strip() for ln in value.splitlines()
                    if keep_empty_lines or len(ln.strip()) > 0]
        return value

    def getpath(self, *args, accept_empty=False, **kwargs):
        """
        Same as ``getstripped()`` but ensure the returned value (assumed to be a
        path) is prepended the ``refdir`` set with ``setrefdir()`` in case path
        is not absolute.
        """
        value = self.getstripped(*args, **kwargs)
        if isinstance(value, str):
            if not len(value) and not accept_empty:
                raise ValueError('empty value for option "{}" in section "{}"'.format(option, section))
            if self.refdir is not None and not os.path.isabs(value):
                value = os.path.join(self.refdir, value)
            return os.path.normpath(os.path.realpath(value))
        else:
            return value

    def __getattr__(self, attr):
        return getattr(self.parser, attr)
