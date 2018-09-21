# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2018 Jean-Charles Lefebvre <polyvertex@gmail.com>

import configparser
import ctypes
import os

__all__ = ["Config"]

_IS_WINDOWS = os.name.lower() == "nt"
if _IS_WINDOWS:
    from . import windll

class Config:
    """
    A replacement of ``configparser.ConfigParser`` that is compliant with
    Keypirinha's configuration file format.
    """
    ENV_SECTION_NAME = "env"
    VAR_SECTION_NAME = "var"

    def __init__(self, extra_defaults={}):
        self.refdir = None
        self.parser = configparser.ConfigParser(
            defaults=None,
            delimiters=("="),
            comment_prefixes=("#"),
            strict=True, # disallow section/option duplicates
            interpolation=configparser.ExtendedInterpolation())

        # populate the [env] section
        env_dict = {}
        for name, value in os.environ.items():
            env_dict[name] = os.path.expandvars(value)
        self.parser.read_dict(
            {self.ENV_SECTION_NAME: env_dict},
            source="<env>")

        # populate the [var] section with the KNOWNFOLDER_* and
        # KNOWNFOLDERGUID_* values
        var_dict = {}
        if _IS_WINDOWS:
            for name in dir(windll):
                if name.startswith("FOLDERID_"):
                    value = getattr(windll, name)
                    if isinstance(value, str):
                        kf_name = name[len("FOLDERID_"):].upper()
                        kf_guid = value
                        try:
                            kf_path = windll.get_known_folder_path(kf_guid)
                        except OSError:
                            continue
                        var_dict['KNOWNFOLDER_' + kf_name] = kf_path
                        var_dict['KNOWNFOLDERGUID_' + kf_name] = kf_guid
        self.parser.read_dict(
            {self.VAR_SECTION_NAME: var_dict},
            source="<var>")

        if extra_defaults:
            self.parser.read_dict(extra_defaults, source="<extra_defaults>")

    def __getattr__(self, attr):
        return getattr(self.parser, attr)

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
