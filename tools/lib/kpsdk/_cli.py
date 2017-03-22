# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2017 Jean-Charles Lefebvre <polyvertex@gmail.com>

import atexit
import getpass
import locale
import os
import pprint
import sys
import subprocess
from .packages import colorama
from .packages.colorama import Fore
from .packages.colorama import Back
from .packages.colorama import Style

__all__ = [
    "enable_colors", "ColoredStream", "ScopedColoredStream",
    "die", "info", "hinfo", "warn", "err",
    "ask", "ask_yesno",
    "CalledProcessError", "TimeoutExpired", "run"]

_colors_enabled = False

class ColoredStream:
    def __init__(self, stream):
        convert = False if not _colors_enabled else None
        self._stream = colorama.initialise.wrap_stream(
                stream, convert=convert, strip=None, autoreset=None, wrap=True)

        for name in ("BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA",
                     "CYAN", "WHITE"):
            def _method(self):
                self.set_style(getattr(colorama.Fore, name))
            setattr(self, "set_" + name.lower(), _method)

    def __getattr__(self, name):
        return getattr(self._stream, name)

    def set_style(self, style):
        if style is not None:
            self._stream.write(style)

    def reset_style(self):
        self._stream.write(colorama.Style.RESET_ALL)

class ScopedColoredStream(ColoredStream):
    __slots__ = ("style", "flush_on_exit")

    def __init__(self, stream, style=None, flush_on_exit=True):
        super().__init__(stream)
        self.style = style
        self.flush_on_exit = flush_on_exit

    def __enter__(self):
        self.set_style(self.style)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.reset_style()
        if self.flush_on_exit:
            self.flush()

def _atexit_disable_colors():
    for stream in (sys.stdout, sys.stderr):
        colstream = ColoredStream(stream)
        colstream.reset_style()
        colstream.flush()

def enable_colors(enable=True):
    """Allow/disallow colors on TTY output."""
    global _colors_enabled
    if enable and not _colors_enabled:
        _colors_enabled = True
        atexit.register(_atexit_disable_colors)
    elif _colors_enabled and not enable:
        _colors_enabled = False
        atexit.unregister(_atexit_disable_colors)

def die(*objects, exit_code=1, file=sys.stderr, style=Fore.RED, **kwargs):
    """Print a message and :py:func:`sys.exit` using the given code"""
    with ScopedColoredStream(file, style, flush_on_exit=True) as stream:
        stream.write("ERROR: ")
        print(*objects, file=stream, flush=False, **kwargs)
    sys.exit(exit_code)

def info(*objects, file=sys.stderr, flush=True, style=None, **kwargs):
    """Print a informational message"""
    with ScopedColoredStream(file, style, flush_on_exit=flush) as stream:
        print(*objects, file=stream, flush=False, **kwargs)

def hinfo(*objects, file=sys.stderr, flush=True, style=Fore.CYAN, **kwargs):
    """Print a highlighted informational message"""
    with ScopedColoredStream(file, style, flush_on_exit=flush) as stream:
        print(*objects, file=stream, flush=False, **kwargs)

def warn(*objects, file=sys.stderr, flush=True, style=Fore.YELLOW, **kwargs):
    """Print a warning message"""
    with ScopedColoredStream(file, style, flush_on_exit=flush) as stream:
        stream.write("WARNING: ")
        print(*objects, file=stream, flush=False, **kwargs)

def err(*objects, file=sys.stderr, flush=True, style=Fore.RED, **kwargs):
    """Print an error message"""
    with ScopedColoredStream(file, style, flush_on_exit=flush) as stream:
        stream.write("ERROR: ")
        print(*objects, file=stream, flush=False, **kwargs)

def ask(message, ofile=sys.stderr, ifile=sys.stdin, style=Fore.MAGENTA,
        noecho=False):
    """
    Print a question on *ofile* and wait for an answer on *ifile* using
    :py:meth:`io.TextIOBase.readline`.

    *style* may be ``None`` for non-colored output (this does not override the
    behavior setup by :py:func:`enable_colors`).
    """
    with ScopedColoredStream(ofile, style, flush_on_exit=True) as stream:
        stream.write(message)

    if not noecho:
        return ifile.readline().rstrip("\n\r")
    else:
        if ifile != sys.stdin:
            raise ValueError("noecho option implies input from stdin")
        return getpass.getpass(prompt="", stream=ofile)

def ask_yesno(question, default=None, ofile=sys.stderr, ifile=sys.stdin,
              style=Fore.MAGENTA):
    """
    Same as :py:func:`ask` but expect a yes/no answer.
    *default* must be ``None`` or a boolean.

    *style* may be ``None`` for non-colored output (this does not override the
    behavior setup by :py:func:`enable_colors`).
    """
    question = question.rstrip().rstrip("?").rstrip() + "?"
    if default is None:
        question += " (y/n) "
    elif default:
        question += " [Y/n] "
    else:
        question += " [y/N] "

    while True:
        with ScopedColoredStream(ofile, style, flush_on_exit=True) as ostream:
            ostream.write(question)

        ans_orig = ifile.readline()
        ans = ans_orig.strip().lower()
        if ans in ("y", "ye", "yes"):
            return True
        elif ans in ("n", "no"):
            return False
        elif not len(ans) and default is not None:
            return default
        if len(ans_orig) and ans_orig[-1] != "\n":
            ofile.write("\n")

CalledProcessError = subprocess.CalledProcessError
TimeoutExpired = subprocess.TimeoutExpired

def run(args=[], splitlines=False, rstrip=True,
        stdin=None, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        timeout=None, encoding=True, errors="strict",
        die_on_error=True, die_on_exc=True,
        die_file=sys.stderr, die_style=Fore.RED,
        **kwargs):
    """
    A wrapper around :py:func:`subprocess.run` to automatically deal with any
    raised exception, error return code, decoding and line splitting.

    Return a :py:class:`subprocess.CompletedProcess` object.

    If *splitlines* is true, ``stdout`` and ``stderr`` members will both be
    line-split if and only if they are instance of either :py:class:`str` or
    :py:class:`bytes` (using their respective ``splitlines()`` method.

    If *rstrip* is true, ``stdout`` and ``stderr`` members will both be
    rstrip'ed if and only if they are instance of either :py:class:`str` or
    :py:class:`bytes` (using their respective ``rstrip()`` method.
    This argument works regardless of the *splitlines* value.

    *stdin*, *stdout*, *stderr*, *timeout*, and *errors* are passed as-is to
    :py:func:`subprocess.run`, as well as the remaining *kwargs*.

    *encoding* is passed as-is as well unless it is exactly ``True``, in which
    case it is assigned the value of ``sys.__stdout__.encoding`` if possible, or
    ``locale.getpreferredencoding(False)`` otherwise.

    Note that you may have to overwrite the default *encoding* value (i.e.
    ``True``) if you happen to also overwrite *stdout* and/or *stderr*.

    If the sub-process exits with an error code, *die_on_error* indicates if
    this function should call :py:func:`sys.exit` after writing some info to
    *die_file*. *die_on_error* can be a boolean value, in which case a return
    code different than ``0`` is assumed to be an error; or it can be a callable
    that accepts the return code as an argument and returns a boolean to
    indicate an error.

    *die_on_exc* is a boolean to indicate if this function should call
    :py:func:`sys.exit` after writing some info to *die_file*, upon Python
    exception.

    *die_file* must be an object file. It used only in case of an
    error/exception and if *die_on_error* or *die_on_exc* evaluates to true.

    *die_style* can be ``None`` or the color to use to print error. Not that it
    does not override the sate defined by :py:func:`enable_colors`.
    """

    if encoding is True:
        if sys.__stdout__ and sys.__stdout__.encoding:
            encoding = sys.__stdout__.encoding
        else:
            encoding = locale.getpreferredencoding(False)

    try:
        res = subprocess.run(args, stdin=stdin, stdout=stdout, stderr=stderr,
                             timeout=timeout, encoding=encoding, errors=errors,
                             **kwargs)

        error_occurred = False
        if callable(die_on_error):
            if die_on_error(res.returncode):
                error_occurred = True
        elif die_on_error and res.returncode != 0:
            error_occurred = True

        if error_occurred:
            # replicate subprocess.CompletedProcess.check_returncode()
            raise CalledProcessError(res.returncode, res.args,
                                     res.stdout, res.stderr)

    except OSError as exc:
        if not die_on_exc:
            raise
        with ScopedColoredStream(die_file, die_style, True) as stream:
            stream.write(
                "ERROR: failed to execute command\n" +
                "  os error {}: {}\n".format(exc.winerror, exc.strerror) +
                "  command: {}\n".format(
                                pprint.pformat(args, indent=2, compact=True)))
        sys.exit(1)

    except (CalledProcessError, TimeoutExpired) as exc:
        if not die_on_exc:
            raise
        with ScopedColoredStream(die_file, die_style, True) as stream:
            if isinstance(exc, TimeoutExpired):
                reason = "time"
                desc = "timeout: {} seconds".format(exc.timeout)
            else:
                assert isinstance(exc, CalledProcessError)
                reason = "error"
                desc = "exit code: {}".format(exc.returncode)

            stream.write(
                "ERROR: command execution {}\n".format(reason) +
                "  {}\n".format(desc) +
                "  command: {}\n".format(exc.cmd))

            # show stdout content if possible
            if stream.encoding and isinstance(exc.stdout, bytes):
                try:
                    exc.stdout = str(exc.stdout, encoding=stream.encoding)
                except:
                    pass
            if isinstance(exc.stdout, str) and exc.stdout:
                stream.write("\nOutput:\n" + exc.stdout.rstrip() + "\n")

            # show stderrcontent if possible
            if (stderr != subprocess.STDOUT and
                    stream.encoding and
                    isinstance(exc.stderr, bytes)):
                try:
                    exc.stderr = str(exc.stderr, encoding=stream.encoding)
                except:
                    pass
            if (stderr != subprocess.STDOUT and
                    isinstance(exc.stderr, str) and exc.stderr):
                stream.write("\nSTDERR:\n" + exc.stderr.rstrip() + "\n")
        sys.exit(1)

    except Exception as exc:
        if not die_on_exc:
            raise
        with ScopedColoredStream(die_file, die_style, True) as stream:
            stream.write(
                "ERROR: failed to execute command\n" +
                "  exception: {}\n".format(str(exc)) +
                "  command: {}\n".format(
                                pprint.pformat(args, indent=2, compact=True)))
        sys.exit(1)

    if splitlines:
        if isinstance(res.stdout, (bytes, str)):
            res.stdout = [line.rstrip() if rstrip else line
                          for line in res.stdout.splitlines()]
        if isinstance(res.stderr, (bytes, str)):
            res.stderr = [line.rstrip() if rstrip else line
                          for line in res.stderr.splitlines()]
    elif rstrip:
        if isinstance(res.stdout, (bytes, str)):
            res.stdout = res.stdout.rstrip()
        if isinstance(res.stderr, (bytes, str)):
            res.stderr = res.stderr.rstrip()

    return res
