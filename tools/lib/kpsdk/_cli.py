# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2017 Jean-Charles Lefebvre <polyvertex@gmail.com>

import sys
from .packages import colorama

__all__ = [
    "enable_colors",
    "die", "info", "hinfo", "warn", "err",
    "ask", "ask_yesno"]
    #"cmd_output"]

_colors_enabled = False

class _ColoredStream:
    __slots__ = ("_stream", )
    def __init__(self, stream):
        convert = False if not _colors_enabled else None
        self._stream = colorama.initialise.wrap_stream(
                stream, convert=convert, strip=None, autoreset=None, wrap=True)
    def __getattr__(self, attr):
        return getattr(self._stream, attr)

def enable_colors(enable):
    """Allow/disallow colors on TTY output."""
    global _colors_enabled
    _colors_enabled = enable

def die(msg, exit_code=1, file=sys.stderr, **kwargs):
    """Print a message and ``sys.exit`` using the given code"""
    ostream = _ColoredStream(file)
    ostream.write(colorama.Fore.RED + "ERROR: ")
    print(*objects, file=ostream, flush=False, **kwargs)
    ostream.write(colorama.Style.RESET_ALL)
    ostream.flush()
    sys.exit(exit_code)

def info(*objects, file=sys.stderr, flush=True, **kwargs):
    """Print a informational message"""
    print(*objects, file=file, flush=flush, **kwargs)

def hinfo(*objects, file=sys.stderr, flush=True, **kwargs):
    """Print a highlighted informational message"""
    ostream = _ColoredStream(file)
    ostream.write(colorama.Fore.CYAN)
    print(*objects, file=ostream, flush=False, **kwargs)
    ostream.write(colorama.Style.RESET_ALL)
    if flush:
        ostream.flush()

def warn(*objects, file=sys.stderr, flush=True, **kwargs):
    """Print a warning message"""
    ostream = _ColoredStream(file)
    ostream.write(colorama.Fore.YELLOW + "WARNING: ")
    print(*objects, file=ostream, flush=False, **kwargs)
    ostream.write(colorama.Style.RESET_ALL)
    if flush:
        ostream.flush()

def err(*objects, file=sys.stderr, flush=True, **kwargs):
    """Print an error message"""
    ostream = _ColoredStream(file)
    ostream.write(colorama.Fore.RED + "ERROR: ")
    print(*objects, file=ostream, flush=False, **kwargs)
    ostream.write(colorama.Style.RESET_ALL)
    if flush:
        ostream.flush()

def ask(message, ofile=sys.stdout, ifile=sys.stdin):
    """
    Print a question on *ofile* and wait for an answer on *ifile* using
    :py:meth:`io.TextIOBase.readline`.
    """
    ofile.write(message)
    ofile.flush()
    return ifile.readline()

def ask_yesno(question, default=None, ofile=sys.stdout, ifile=sys.stdin):
    """
    Same as :py:func:`ask` but expect a yes/no answer.
    *default* must be ``None`` or a boolean.
    """
    question = question.rstrip().rstrip("?").rstrip() + "?"
    if default is None:
        question += " (y/n) "
    elif default:
        question += " [Y/n] "
    else:
        question += " [y/N] "

    while True:
        ofile.write(question)
        ofile.flush()
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

def cmd_output(args=[], splitlines=False, raise_error=False):
    """
    Run a command and return a tuple containing the return code and a list of
    split lines from the decoded output
    """
    try:
        exit_code = 0
        output = subprocess.check_output(args, **kwargs)
    except subprocess.CalledProcessError as exc:
        if raise_error:
            raise
        exit_code = exc.returncode
        output = exc.output

    if output is None:
        output = []
    else:
        output = output.decode(
                sys.__stdout__.encoding if sys.__stdout__
                else locale.getpreferredencoding())
        output = output.splitlines() if splitlines else output.rstrip()

    return (exit_code, output)
