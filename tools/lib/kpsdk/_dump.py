# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2017 Jean-Charles Lefebvre <polyvertex@gmail.com>

import sys
import pprint

__all__ = ["dump"]

def dump(
        *args,
        dtitle="DUMP",
        dindent=2,
        dstream=sys.stderr,
        dformat={},
        **kwargs):
    """
    Pretty-print every passed positional and named parameters.

    The formated value of the named parameters will be prepended by their
    respective name.

    Behavior and output format can be tweaked using those special named
    parameters:

    * ``dtitle``:
      The title string to prepend to the output. It may be ``None`` or empty.
    * ``dstream``:
      May you wish to print() the result directly, you can pass a stream object
      (e.g.: ``sys.stdout``) through this option, that will be given to
      ``print()``'s ``file`` keyword argument.
      You can also specify ``None`` in case you just want the output string to
      be returned.
    * ``dformat``:
      The dictionary of keyword arguments to pass to ``pprint.pformat()``
    """
    args_len = len(args) + len(kwargs)
    if not args_len:
        return None if dstream else "" # nothing to format

    if 'indent' in dformat:
        dformat['indent'] += dindent
    else:
        dformat['indent'] = dindent * 2

    output = ""
    if dtitle is not None and len(dtitle):
        output += dtitle + ":"
        output += "\n" if args_len > 1 else " "

    for name, obj in zip(
            [None] * len(args) + list(kwargs.keys()),
            list(args) + list(kwargs.values())):
        if name in ("dtitle", "dindent", "dstream", "dformat"):
            continue
        if args_len > 1:
            output += " " * dindent
        if name is not None:
            output += name + ": "
        output += pprint.pformat(obj, **dformat) + "\n"

    if dstream:
        print(output, end="", file=dstream)
        return None # explicit is better than implicit
    else:
        return output.rstrip()

if __name__ == "__main__":
    my_var = "Foo"
    dump()
    dump(my_var)
    dump(
        my_var, None, True, 123, "Bar", (4, 5, 6),
        dump(1, dstream=None), hello="world",
        dict={'A': 1, 'B': 2, 'C': 3})
