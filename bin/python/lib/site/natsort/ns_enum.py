# -*- coding: utf-8 -*-
"""This module defines the "ns" enum for natsort."""
from __future__ import (
    print_function,
    division,
    unicode_literals,
    absolute_import
)


class ns(object):
    """
    Enum to control the `natsort` algorithm.

    This class acts like an enum to control the `natsort` algorithm. The
    user may select several options simultaneously by or'ing the options
    together.  For example, to choose ``ns.INT``, ``ns.PATH``, and
    ``ns.LOCALE``, you could do ``ns.INT | ns.LOCALE | ns.PATH``. Each
    function in the :mod:`natsort` package has an `alg` option that accepts
    this enum to allow fine control over how your input is sorted.

    Each option has a shortened 1- or 2-letter form.

    .. note:: Please read :ref:`locale_issues` before using ``ns.LOCALE``.

    Attributes
    ----------
    INT, I (default)
        The default - parse numbers as integers.
    FLOAT, F
        Tell `natsort` to parse numbers as floats.
    UNSIGNED, U (default)
        Tell `natsort` to ignore any sign (i.e. "-" or "+") to the immediate
        left of a number.  It is the same as setting the old `signed` option
        to `False`. This is the default.
    SIGNED, S
        Tell `natsort` to take into account any sign (i.e. "-" or "+")
        to the immediate left of a number.  It is the same as setting
        the old `signed` option to `True`.
    REAL, R
        This is a shortcut for ``ns.FLOAT | ns.SIGNED``, which is useful
        when attempting to sort real numbers.
    NOEXP, N
        Tell `natsort` to not search for exponents as part of the number.
        For example, with `NOEXP` the number "5.6E5" would be interpreted
        as `5.6`, `"E"`, and `5`.  It is the same as setting the old
        `exp` option to `False`.
    PATH, P
        Tell `natsort` to interpret strings as filesystem paths, so they
        will be split according to the filesystem separator
        (i.e. '/' on UNIX, '\\' on Windows), as well as splitting on the
        file extension, if any. Without this, lists of file paths like
        ``['Folder/', 'Folder (1)/', 'Folder (10)/']`` will not be
        sorted properly; 'Folder/' will be placed at the end, not at the
        front. It is the same as setting the old `as_path` option to
        `True`.
    LOCALE, L
        Tell `natsort` to be locale-aware when sorting. This includes both
        proper sorting of alphabetical characters as well as proper
        handling of locale-dependent decimal separators and thousands
        separators. This is a shortcut for
        ``ns.LOCALEALPHA | ns.LOCALENUM``.
        Your sorting results will vary depending on your current locale.
    LOCALEALPHA, LA
        Tell `natsort` to be locale-aware when sorting, but only for
        alphabetical characters.
    LOCALENUM, LN
        Tell `natsort` to be locale-aware when sorting, but only for
        decimal separators and thousands separators.
    IGNORECASE, IC
        Tell `natsort` to ignore case when sorting.  For example,
        ``['Banana', 'apple', 'banana', 'Apple']`` would be sorted as
        ``['apple', 'Apple', 'Banana', 'banana']``.
    LOWERCASEFIRST, LF
        Tell `natsort` to put lowercase letters before uppercase letters
        when sorting.  For example,
        ``['Banana', 'apple', 'banana', 'Apple']`` would be sorted as
        ``['apple', 'banana', 'Apple', 'Banana']`` (the default order
        would be ``['Apple', 'Banana', 'apple', 'banana']`` which is
        the order from a purely ordinal sort).
        Useless when used with `IGNORECASE`. Please note that if used
        with ``LOCALE``, this actually has the reverse effect and will
        put uppercase first (this is because ``LOCALE`` already puts
        lowercase first); you may use this to your advantage if you
        need to modify the order returned with ``LOCALE``.
    GROUPLETTERS, G
        Tell `natsort` to group lowercase and uppercase letters together
        when sorting.  For example,
        ``['Banana', 'apple', 'banana', 'Apple']`` would be sorted as
        ``['Apple', 'apple', 'Banana', 'banana']``.
        Useless when used with `IGNORECASE`; use with `LOWERCASEFIRST`
        to reverse the order of upper and lower case. Generally not
        needed with `LOCALE`.
    CAPITALFIRST, C
        Only used when `LOCALE` is enabled. Tell `natsort` to put all
        capitalized words before non-capitalized words. This is essentially
        the inverse of `GROUPLETTERS`, and is the default Python sorting
        behavior without `LOCALE`.
    UNGROUPLETTERS, UG
        An alias for `CAPITALFIRST`.
    NANLAST, NL
        If an NaN shows up in the input, this instructs `natsort` to
        treat these as +Infinity and place them after all the other numbers.
        By default, an NaN be treated as -Infinity and be placed first.
    TYPESAFE, T
        Deprecated as of `natsort` version 5.0.0; this option is now
        a no-op because it is always true.
    VERSION, V
        Deprecated as of `natsort` version 5.0.0; this option is now
        a no-op because it is the default.
    DIGIT, D
        Same as `VERSION` above.

    Notes
    -----
    If you prefer to use `import natsort as ns` as opposed to
    `from natsort import natsorted, ns`, the `ns` options are
    available as top-level imports.

        >>> import natsort as ns
        >>> a = ['num5.10', 'num-3', 'num5.3', 'num2']
        >>> # Which is more natural to write?
        >>> ns.natsorted(a, alg=ns.REAL) == ns.natsorted(a, alg=ns.ns.REAL)
        True

    """
    # Following were previously now options but are now defaults.
    TYPESAFE         = T  = 0
    INT              = I  = 0
    VERSION          = V  = 0
    DIGIT            = D  = 0
    UNSIGNED         = U  = 0

    # The below are options. The values are stored as powers of two
    # so bitmasks can be used to extract the user's requested options.
    FLOAT            = F  = 1 << 0
    SIGNED           = S  = 1 << 1
    REAL             = R  = FLOAT | SIGNED
    NOEXP            = N  = 1 << 2
    PATH             = P  = 1 << 3
    LOCALEALPHA      = LA = 1 << 4
    LOCALENUM        = LN = 1 << 5
    LOCALE           = L  = LOCALEALPHA | LOCALENUM
    IGNORECASE       = IC = 1 << 6
    LOWERCASEFIRST   = LF = 1 << 7
    GROUPLETTERS     = G  = 1 << 8
    UNGROUPLETTERS   = UG = 1 << 9
    CAPITALFIRST     = C  = UNGROUPLETTERS
    NANLAST          = NL = 1 << 10

    # The below are private options for internal use only.
    _NUMERIC_ONLY    = REAL | NOEXP
    _DUMB            = 1 << 31
