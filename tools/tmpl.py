# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2018 Jean-Charles Lefebvre <polyvertex@gmail.com>

import datetime
import glob
import os
import shutil
import sys
import kpsdk
import kpsdk.tmpl

TEMPLATES_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "templates")

def action_package(opts, args):
    if not os.path.isdir(TEMPLATES_ROOT):
        kpsdk.die("templates directory not found: " + TEMPLATES_ROOT)
    if not args:
        print_usage("no package name specified")
        return 1

    package_name = args.pop(0).strip()
    if not kpsdk.validate_package_name(package_name):
        kpsdk.die("package name does not comply to package naming rules (check documentation)")
    if "/" in package_name or "\\" in package_name: # just to be safe
        kpsdk.die("invalid character(s) in package name")

    dest_dir = args.pop(0) if args else os.getcwd()
    dest_dir = os.path.realpath(dest_dir)
    dest_dir = os.path.join(dest_dir, "keypirinha-" + package_name.lower())

    tmpl_dir = os.path.join(TEMPLATES_ROOT, "package")
    tmpl_dict = {
        'package_name': package_name,
        'package_name_lower': package_name.lower(),
        'plugin_name': package_name.replace(" ", ""),
        'year': str(datetime.datetime.now().year)}

    kpsdk.info('Creating package "{}" in {}'.format(package_name, dest_dir))
    kpsdk.tmpl.do_tree(tmpl_dir, dest_dir, tmpl_dict)
    return 0

def print_usage(error=None):
    if error is not None:
        sys.stderr.write("ERROR: " + error + "\n\n")
        sys.stderr.flush()
    sys.stdout.write("""\
Usage:
    tmpl help
    tmpl package <name> [dest_dir]

Actions:
    h, help
        Print this message and leave.

    pack, package
        Create a ready-to-develop package skeleton at a desired location.
        A directory will be created inside the specified one, or by default in
        the current working directory.
        CAUTION: Keypirinha has pretty strict package naming. You may want to
        check documentation.

Arguments:
    -h --help
        Print this message and leave.
\
""")

def main():
    if not sys.argv[1:]:
        print_usage()
        return 0
    try:
        opts, args, missing_opts = kpsdk.getopts(opts=("help,h", ))
    except Exception as e:
        print_usage(str(e))
        return 1
    if opts['help']:
        print_usage()
        return 0

    if not args:
        print_usage("no action specified")
        return 1
    opts['action'] = args.pop(0)
    if opts['action'] in ("h", "help"):
        print_usage()
        return 0
    elif opts['action'] in ("pack", ):
        opts['action'] = "package"

    action_func_name = "action_" + opts['action']
    if action_func_name not in globals():
        print_usage('unknown action "{}"'.format(opts['action']))
        return 1

    return globals()[action_func_name](opts, args)

if __name__ == "__main__":
    sys.exit(main())
