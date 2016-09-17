# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2016 Jean-Charles Lefebvre <polyvertex@gmail.com>

import glob
import os
import shutil
import sys
import kpsdk

TEMPLATES_ROOT = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)), "templates")
TEMPLATES_EXTENSION = ".tmpl"

def xform_str(text, tmpl_dict):
    for name, value in tmpl_dict.items():
        text = text.replace("{{" + name + "}}", value)
    return text

def xform_file(src_file, dest_file, tmpl_dict):
    with open(src_file, mode="rt", encoding="utf-8", errors="strict") as fin:
        with open(dest_file, mode="wt", encoding="utf-8", errors="strict") as fout:
            for line in fin:
                fout.write(xform_str(line, tmpl_dict))
    shutil.copystat(src_file, dest_file, follow_symlinks=False)

def xform_tree(root_src, root_dest, tmpl_dict, level=0):
    def _mkdir(new_dir, copy_stats_from=None):
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
            if copy_stats_from is not None:
                shutil.copystat(copy_stats_from, new_dir, follow_symlinks=False)
        elif os.path.isdir(new_dir):
            if not kpsdk.dir_is_empty(new_dir):
                kpsdk.die("destination directory not empty: " + new_dir)
        else:
            kpsdk.die("destination exists and is not a directory: " + new_dir)

    if level == 0:
        _mkdir(root_dest)

    for entry in os.scandir(root_src):
        src_path = os.path.join(root_src, entry.name)
        dest_path = os.path.join(root_dest, xform_str(entry.name, tmpl_dict))
        if entry.is_dir():
            _mkdir(dest_path, copy_stats_from=src_path)
            xform_tree(src_path, dest_path, tmpl_dict, level + 1)
        elif entry.is_file():
            if entry.name.endswith(TEMPLATES_EXTENSION):
                dest_path = dest_path[0:-len(TEMPLATES_EXTENSION)]
                xform_file(src_path, dest_path, tmpl_dict)
            else:
                shutil.copy2(src_path, dest_path, follow_symlinks=False)

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
        'plugin_name': package_name.replace(" ", "")}

    kpsdk.info('Creating package "{}" in {}'.format(package_name, dest_dir))
    xform_tree(tmpl_dir, dest_dir, tmpl_dict)
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
        opts, args = kpsdk.getopts(opts=("help,h", ))
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
