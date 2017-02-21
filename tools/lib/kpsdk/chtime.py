# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2017 Jean-Charles Lefebvre <polyvertex@gmail.com>

import datetime

from . import _cli
from . import _globscan
from . import windll

__all__ = ["chtime", "init_filetime"]

class _WinApi:
    __slots__ = ("symbols")

    def __init__(self):
        self.symbols = {
            #'GENERIC_READ':  0x80000000,
            #'GENERIC_WRITE': 0x40000000,
            'OPEN_EXISTING': 0x00000003,
            'FILE_WRITE_ATTRIBUTES': 0x100,
            'FILE_FLAG_BACKUP_SEMANTICS': 0x02000000,

            'GetLastError': windll.declare_func(
                windll.kernel32, "GetLastError", ret=windll.DWORD, args=[]),

            'CreateFileW': windll.declare_func(
                windll.kernel32, "CreateFileW", ret=windll.HANDLE,
                args=[windll.LPCWSTR, windll.DWORD, windll.DWORD, windll.PVOID,
                      windll.DWORD, windll.DWORD, windll.HANDLE]),

            'CloseHandle': windll.declare_func(
                windll.kernel32, "CloseHandle", ret=windll.BOOL,
                args=[windll.HANDLE]),

            'GetFileTime': windll.declare_func(
                windll.kernel32, "GetFileTime", ret=windll.BOOL,
                args=[windll.HANDLE,
                      windll.LPFILETIME, windll.LPFILETIME, windll.LPFILETIME]),

            'SetFileTime': windll.declare_func(
                windll.kernel32, "SetFileTime", ret=windll.BOOL,
                args=[windll.HANDLE,
                      windll.LPFILETIME, windll.LPFILETIME, windll.LPFILETIME])}

    def __getattr__(self, name):
        return self.symbols[name]

    def raise_apierror(self, winerr=None, msg=None):
        if winerr is None:
            winerr = windll.ct.GetLastError()
        if msg is None:
            msg = windll.ct.FormatError(winerr)
        if winerr:
            raise OSError(0, msg, None, winerr)

def _init_winapi():
    return {
        #'GENERIC_READ':  0x80000000,
        #'GENERIC_WRITE': 0x40000000,
        'OPEN_EXISTING': 0x00000003,
        'FILE_WRITE_ATTRIBUTES': 0x100,
        'FILE_FLAG_BACKUP_SEMANTICS': 0x02000000,

        'GetLastError': windll.declare_func(
            windll.kernel32, "GetLastError", ret=windll.DWORD, args=[]),

        'CreateFileW': windll.declare_func(
            windll.kernel32, "CreateFileW", ret=windll.HANDLE,
            args=[windll.LPCWSTR, windll.DWORD, windll.DWORD, windll.PVOID,
                  windll.DWORD, windll.DWORD, windll.HANDLE]),

        'CloseHandle': windll.declare_func(
            windll.kernel32, "CloseHandle", ret=windll.BOOL,
            args=[windll.HANDLE]),

        'GetFileTime': windll.declare_func(
            windll.kernel32, "GetFileTime", ret=windll.BOOL,
            args=[windll.HANDLE,
                  windll.LPFILETIME, windll.LPFILETIME, windll.LPFILETIME]),

        'SetFileTime': windll.declare_func(
            windll.kernel32, "SetFileTime", ret=windll.BOOL,
            args=[windll.HANDLE,
                  windll.LPFILETIME, windll.LPFILETIME, windll.LPFILETIME])}

def _unix_timestamp_to_win_filetime(unix):
    SECONDS_BETWEEN_WIN_AND_UNIX_EPOCHS = 11644473600
    ft_timestamp = int((unix + SECONDS_BETWEEN_WIN_AND_UNIX_EPOCHS) * 10000000)
    ft_timestamp_hi = (ft_timestamp >> 32) & 0xffffffff
    ft_timestamp_lo = ft_timestamp & 0xffffffff
    return windll.FILETIME(ft_timestamp_lo, ft_timestamp_hi)

def init_filetime(target_time):
    if isinstance(target_time, datetime.datetime):
        return _unix_timestamp_to_win_filetime(dt.timestamp())

    elif isinstance(target_time, (int, float)):
        dt = datetime.fromtimestamp(target_time, datetime.timezone.utc)
        return _unix_timestamp_to_win_filetime(dt.timestamp())

    elif isinstance(target_time, str):
        if target_time.lower() == "now":
            unix = datetime.datetime.now().timestamp()
            return _unix_timestamp_to_win_filetime(unix)
        elif target_time.lower() == "utcnow":
            unix = datetime.datetime.now(datetime.timezone.utc).timestamp()
            return _unix_timestamp_to_win_filetime(unix)
        elif target_time.lower() in ("midnight", "utcmidnight"):
            if target_time.lower().startswith("utc"):
                dt = datetime.datetime.now(datetime.timezone.utc)
                dt = datetime.datetime(dt.year, dt.month, dt.day,
                                       tzinfo=datetime.timezone.utc)
            else:
                dt = datetime.datetime.now()
                dt = datetime.datetime(dt.year, dt.month, dt.day)
            return _unix_timestamp_to_win_filetime(dt.timestamp())
        else:
            raise ValueError("unrecognized time format: " + target_time)

    else:
        raise TypeError

def chtime(target_time, input_patterns, recursive=False, include_hidden=True,
           mtime=True, atime=True, ctime=False, dry_run=False):
    # target_time can be:
    # * a windll.FILETIME
    # * a datetime object
    # * an int/float (unix timestamp)
    # * an str ("now", "utcnow", "midnight" or "utcmidnight")

    if not any((atime, ctime, mtime)):
        raise ValueError("at least mtime, atime or ctime must be true")

    winapi = _WinApi()
    if isinstance(target_time, windll.FILETIME):
        filetime = target_time
    else:
        filetime = init_filetime(target_time)
    atime = filetime if atime else None
    ctime = filetime if ctime else None
    mtime = filetime if mtime else None
    dry_run_output = []

    for entry in _globscan.iglobscan(input_patterns,
                                     recursive=recursive,
                                     include_dirs=True,
                                     include_hidden=include_hidden):
        if dry_run:
            dry_run_output.append(entry.path)
            continue

        fh = None
        try:
            fh = winapi.CreateFileW(
                entry.path, winapi.FILE_WRITE_ATTRIBUTES, 0, None,
                winapi.OPEN_EXISTING, winapi.FILE_FLAG_BACKUP_SEMANTICS, None)
            if not winapi.SetFileTime(fh, ctime, atime, mtime):
                winapi.raise_apierror()
        finally:
            if fh:
                winapi.CloseHandle(fh)

    return dry_run_output if dry_run else True
