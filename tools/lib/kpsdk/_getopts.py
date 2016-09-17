# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2016 Jean-Charles Lefebvre <polyvertex@gmail.com>

import re
import sys

__all__ = ["getopts", "breakopt"]

def getopts(args=None, opts=[], ignore_unknown_opts=False):
    """
    A standalone command line arguments parser.

    *args* is the list of the arguments to parse. ``sys.argv[1:]`` by default.

    *opts* is a list of definitions of the options to interpret.
    Each element in the list is a string defining one option and its properties.
    Definition format is as follows:
    ``<name>[,<name2>[,...]][<properties>][=<value_type>[+|N]]]``

    Where ``<name>`` is the name of the option that will directly be used by the
    caller of the script like in ``-name`` or ``--name``. You can optionally
    declare a comma-separated list of one or several additional names as long as
    none of them collide with any other.

    ``<properties>`` is an optional field to specify some properties to your
    option. It is a string of one or several letters in no particular order and
    enclosed by parentheses. Each letter represents a property.
    Accepted properties:

        * ``r``: means this option is required and a ValueError exception will
          be raised if it is missing
        * ``m``: indicates an option that can be specified several times

    ``<value_type>`` is a single letter that indicates two things:

        * this option requires an argument
        * the expected type of the argument is:
          - ``s`` for a string
          - ``u`` for a digit-only string casted to an integer
          - ``i`` for an integer
          - ``f`` for a float

    ``<value_type>`` can be followed by ``+`` to indicate several values are
    required. It is also possible to append a positive integer instead of ``+``,
    in order to require a specific number of values.

    Example:
        getopts(opts=[
            "help,h",
            "dir,d(r)=s",
            "keyval=s+2",
            "verbose,v(rm)",
            "count,loops,c=u",
            "my-long-option-name"])
    """
    args = sys.argv[1:] if args is None else args[:] # copy

    opts_dict = {}     # name: def_dict
    opts_names = {}    # secondary name: name
    opts_required = [] # names of every options marked as 'required'
    opts_out = {}

    # interpret options definitions
    for opt_def in opts:
        # "help,h(rm)[={s|i|f}]"
        m = re.match(r"""^
            (?P<names>[0-9a-zA-Z][0-9a-zA-Z\,\-]*)
            (?:\( (?P<props>[rm]+) \))?
            (?:\= (?P<valtype>[suif]) (?P<valcount>(?:\+|[0-9]+))? )?
            $""", opt_def, re.VERBOSE | re.ASCII)
        if not m:
            raise ValueError(
                "getopts: malformed definition \"" + opt_def + "\"")
        mdict = m.groupdict("")

        # expand properties
        mdict['names'] = " ".join(mdict['names'].split(",")).split()
        mdict['required'] = "r" in mdict['props']
        mdict['multi'] = "m" in mdict['props']
        del mdict['props']
        name = mdict['names'][0]

        if not len(mdict['valcount']):
            mdict['valcount'] = 1
        elif mdict['valcount'] == "+":
            mdict['valcount'] = 0
        else:
            mdict['valcount'] = int(mdict['valcount'])
            if mdict['valcount'] <= 0:
                raise ValueError("getopts: invalid valcount for option '{}'".format(name))

        # 'names' contains the primary name and optional secondary names
        # ensure none of them has been used by an other option already
        if not set(mdict['names']).isdisjoint(opts_names.keys()):
            raise ValueError("getopts: option defined twice")

        # keep option's definition in opts_dict pointed by its primary name
        opts_dict[name] = mdict

        # also, ensure we can easily reference an option by any of its names
        for n in mdict['names']:
            opts_names[n] = name

        # if this option is required, keep track of that somewhere to be able
        # to easily check later
        if mdict['required']:
            opts_required.append(name)

        # populate the output dictionary so the caller doesn't have to check
        # first if a key exists
        if mdict['valtype']:
            opts_out[name] = [] if (mdict['multi'] or mdict['valcount'] != 1) else None
        else:
            opts_out[name] = 0 if mdict['multi'] else False

    if not opts_dict.keys():
        return opts_out, args

    # read args
    idx = 0
    while idx < len(args):
        if args[idx] == "--":
            break # we've reached a stopper

        opt_name, opt_value = breakopt(args[idx])
        if opt_name is None or opt_name not in opts_names:
            if opt_name is not None and not ignore_unknown_opts:
                raise ValueError("unknown option " + args[idx])
            idx += 1
        else:
            opt_info = opts_dict[opts_names[opt_name]]
            opt_name = opt_info['names'][0]

            args.pop(idx)
            if opt_name in opts_required:
                opts_required.remove(opt_name)

            if not opt_info['valtype']:
                if opt_value is not None:
                    raise ValueError("option " + opt_name +
                        " has an unexpected parameter: " + opt_value)
                if not opt_info['multi']:
                    opts_out[opt_name] = True
                else:
                    opts_out[opt_name] += 1
            else:
                if opt_value is not None:
                    args[idx:0] = [opt_value]
                    opt_value = None
                valcount = 0
                while opt_info['valcount'] == 0 or valcount < opt_info['valcount']:
                    valcount += 1
                    try:
                        opt_value = args.pop(idx)
                    except IndexError:
                        raise ValueError(
                            "option " + opt_name + " is missing argument(s)")

                    # ensure end-user did not forget some args
                    if opt_value[0] == "-" and (
                            opt_value in ("-", "--") or
                            opt_value.lstrip("-") in opts_names):
                        if opt_info['valcount'] == 0:
                            args[idx:0] = [opt_value]
                            break
                        else:
                            raise ValueError(
                                "option " + opt_name + " is missing argument(s)")

                    if opt_info['valtype'] == "s":
                        pass
                    elif opt_info['valtype'] == "u":
                        m = re.match(r"^[0-9]+$", opt_value, re.ASCII)
                        if not m:
                            raise ValueError(
                                "not an unsigned integer: " + opt_value)
                        opt_value = int(opt_value)
                    elif opt_info['valtype'] == "i":
                        try:
                            opt_value = int(opt_value)
                        except ValueError:
                            raise ValueError("not an integer: " + opt_value)
                    elif opt_info['valtype'] == "f":
                        try:
                            opt_value = float(opt_value)
                        except ValueError:
                            raise ValueError("not an float: " + opt_value)
                    else:
                        raise ValueError("valtype '" + \
                            opt_info['valtype'] + "' not supported")

                    if opt_info['valcount'] == 1 and not opt_info['multi']:
                        opts_out[opt_name] = opt_value
                    else:
                        opts_out[opt_name].append(opt_value)

    # ensure we've got every required parameters
    if len(opts_required) > 0:
        raise ValueError("missing parameter(s): " + ", ".join(opts_required))

    return opts_out, args

def breakopt(arg):
    m = re.match(r"^\-\-?([0-9a-zA-Z][0-9a-zA-Z\-]*)(?:\=(.+))?$", arg, re.ASCII)
    if m:
        opt_name = m.group(1)
        try:
            return opt_name, m.group(2)
        except IndexError:
            return opt_name, None
    return None, None
