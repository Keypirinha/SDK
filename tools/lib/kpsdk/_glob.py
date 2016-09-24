# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2016 Jean-Charles Lefebvre <polyvertex@gmail.com>

import glob as _glob
import os as _os

_IS_WINDOWS = _os.name.lower() == "nt"
if _IS_WINDOWS:
    import ctypes as _ctypes

__all__ = ["glob", "iglob", "escape", "has_magic"]

escape = _glob.escape
has_magic = _glob.has_magic

def glob(*args, include_hidden=False, **kwargs):
    """
    A :py:func:`glob.glob` that **optionally** but **truly** excludes hidden
    files (i.e. even on *Windows*).

    :py:func:`glob._ishidden`, which is implicitly used by :py:func:`glob.glob`
    and :py:func:`glob.iglob` always filters out *dot* files but does not mind
    about file's *HIDDEN* attribute on Windows.

    **CAUTION:** this function **is not** thread-safe as it installs a trap at
    runtime (i.e. for :py:func:`glob._ishidden`). The ``glob`` module must not
    be used concurrently to this function.
    """
    return list(iglob(*args, include_hidden=include_hidden, **kwargs))

def iglob(*args, include_hidden=False, **kwargs):
    """
    A :py:func:`glob.iglob` that **optionally** but **truly** excludes hidden
    files (i.e. even on *Windows*).

    :py:func:`glob._ishidden`, which is implicitly used by :py:func:`glob.glob`
    and :py:func:`glob.iglob` always filters out *dot* files but does not mind
    about file's *HIDDEN* attribute on Windows.

    **CAUTION:** this function **is not** thread-safe as it installs a trap at
    runtime (i.e. for :py:func:`glob._ishidden`). The ``glob`` module must not
    be used concurrently to this function.
    """
    orig_ishidden = _glob._ishidden
    if include_hidden:
        _glob._ishidden = lambda x: False
    else:
        # original glob._ishidden() only removes "dot" files
        # on windows, files have a "hidden" attribute
        _glob._ishidden = _ishidden
    try:
        yield from _glob.iglob(*args, **kwargs)
    finally:
        _glob._ishidden = orig_ishidden

def _ishidden(path):
    if path[0] in (".", b"."):
        return True
    elif _IS_WINDOWS:
        if not isinstance(path, str):
            raise ValueError
        attr = _ctypes.windll.kernel32.GetFileAttributesW(path)
        if attr != 0xffffffff: # INVALID_FILE_ATTRIBUTES
            return (attr & 0x2) != 0 # FILE_ATTRIBUTE_HIDDEN
    return False
