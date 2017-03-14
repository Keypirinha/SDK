# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2017 Jean-Charles Lefebvre <polyvertex@gmail.com>

import os.path
import sys
import traceback
import zipfile
import kpsdk
import kpsdk.arch

def print_usage(error=None):
    if error is not None:
        sys.stderr.write("ERROR: " + error + "\n\n")
        sys.stderr.flush()
    sys.stdout.write("""\
Create Keypirinha-compatible archive(s) that will contain the given files and
directories (wildcards are supported).
Several archives may be created in one call by separating the arguments with
-a/--archive.

Usage:
    arch [options] [-a] <archive1> <input_args> [-a <archiveN> <input_args>]

Input Arguments:
    [-n <name>] <input_pattern> [ <input_pattern> ... ]

    -n <name>, --name <name>
        All the following specified input files and directories will be folded
        under the specified <name> in the output archive.
        Note that <name> can contain slashes ('/') to simulate an in-archive
        folder.
        This option can be specified multiple times in-between input files/dirs
        so they can be folded under different names.

Options:
    -h --help
        Print this message and leave.
    --hidden
        Include hidden files.
    --keep
        Do not overwrite the output archive if the specified input files are all
        older than the existing archive itself (by comparing the modification
        time).
        Default behavior is to truncate the existing archive, if any.
        CAUTION: never use this option to build a release archive!
    --readonly
        Set output archive file as "read-only".
    -r --recursive
        Scan given input directories recursively.
\
""")

def main():
    if not sys.argv[1:]:
        print_usage()
        return 0
    try:
        opts, args, missing_opts = kpsdk.getopts(
            opts=("help,h", "hidden", "keep", "readonly", "recursive,r"),
            ignore_unknown_opts=True) # so we can parse "-a" options manually
    except ValueError as exc:
        print_usage(str(exc))
        return 1
    except:
        traceback.print_exc()
        return 1
    if opts['help']:
        print_usage()
        return 0
    if not args:
        print_usage("no output archive specified")
        return 1

    # break the remaining positional args
    # * we need the path of at least one output archive
    # * we need at least one input path pattern
    # * input patterns may be split by "--archive" and "--name" options
    check_output_archive_file = None
    current_archive = ""
    current_name = ""
    archives_def = {}
    while len(args):
        arg = args.pop(0)
        opt_name, opt_value = kpsdk.breakopt(arg)

        if opt_name is None:
            if not current_archive:
                # keep old behavior by accepting the first positional argument
                # to be the path to the first output archive
                check_output_archive_file = arg
                current_archive = arg
            else:
                if current_archive not in archives_def:
                    current_archive = os.path.normpath(os.path.realpath(current_archive))
                    archives_def[current_archive] = {}
                try:
                    archives_def[current_archive][current_name].append(arg)
                except KeyError:
                    archives_def[current_archive][current_name] = [arg]

        elif opt_name in ("a", "archive"):
            if opt_value is not None:
                current_archive = opt_value
            elif not len(args):
                print_usage("-a/--archive is missing an argument")
                return 1
            else:
                current_archive = args.pop(0)

        elif opt_name in ("n", "name"):
            if opt_value is not None:
                current_name = opt_value
            elif not len(args):
                print_usage("name option is missing an argument")
                return 1
            else:
                current_name = args.pop(0)
            current_name = kpsdk.ZipFile.cleanup_name(current_name, is_dir=True)

        else:
            kpsdk.die('unknown option "{}"'.format(opt_name))

    # In case -a(rchive) has not been explicitly specified for the first
    # positional argument, ensure the file does not exist already or if it does,
    # that it is a valid archive.
    # We do that to prevent user from overwriting a file that was meant to be
    # for input only.
    if (check_output_archive_file and
            os.path.exists(check_output_archive_file) and
            not zipfile.is_zipfile(check_output_archive_file)):
        kpsdk.die(
            "specified archive already exists and is not an archive:",
            check_output_archive_file)
        return 1

    # sanity check
    for arch_file, folded_patterns in archives_def.items():
        if not arch_file:
            kpsdk.die("empty archive file name detected")
            return 1
        if not folded_patterns:
            # "Should Never Happen" (c) since archives_def[current_archive]
            # element is created upon insertion of the first input pattern
            kpsdk.die("empty archive:", arch_file)
            return 1

    for arch_file, folded_patterns in archives_def.items():
        kpsdk.arch.archive(
            arch_file, folded_patterns,
            check_modtime=opts['keep'], recursive=opts['recursive'],
            include_hidden=opts['hidden'], apply_readonly=opts['readonly'],
            verbose=True)

    return 0

if __name__ == "__main__":
    sys.exit(main())
