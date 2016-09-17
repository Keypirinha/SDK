# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2016 Jean-Charles Lefebvre <polyvertex@gmail.com>

import glob
import os
import stat
import sys

import kpsdk

def list_entries(folded_patterns, recursive):
    entries = {}
    most_recent_mtime = 0
    for arch_base_folder, input_patterns in folded_patterns.items():
        for entry in kpsdk.iglobscan(
                                    input_patterns, recursive=recursive,
                                    include_dirs=False, include_hidden=True):
            if entry.name[0] not in "~#":
                try:
                    entries[arch_base_folder].append(entry)
                except KeyError:
                    entries[arch_base_folder] = [entry]
                mtime = entry.stat().st_mtime_ns
                if mtime > most_recent_mtime:
                    most_recent_mtime = mtime
    return entries, most_recent_mtime

def print_usage(error=None):
    if error is not None:
        sys.stderr.write("ERROR: " + error + "\n\n")
        sys.stderr.flush()
    sys.stdout.write("""\
Creates an archive file that will contain the given files and directories
(wildcards are supported).

Usage:
    arch [options] <output_arch> [-n <name>] <input_patterns> [-n <name>] ...

Options:
    -h --help
        Print this message and leave.
    --keep
        Do not overwrite the output archive if the specified input files are all
        older than the existing archive itself (by comparing the modification
        time).
        Default behavior is to truncate the existing archive, if any.
        CAUTION: never use this option to build a release archive!
    -n <name>, --name <name>
        All the following specified files and directories will be folded under
        the specified <name> in the output archive.
        Note that <name> can contain slashes ('/') to simulate an in-archive
        folder.
        This option can be specified multiple times in-between input files
        and/or directories so they can be folded under different names.
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
        opts, args = kpsdk.getopts(opts=(
            "help,h", "keep", "readonly", "recursive,r"),
        ignore_unknown_opts=True) # so we can parse "-name" manually
    except Exception as e:
        print_usage(str(e))
        return 1
    if opts['help']:
        print_usage()
        return 0
    if not args:
        print_usage("no output archive specified")
        return 1

    # break the remaining positional args
    # * we need the path to the output archive
    # * we need at least one input path pattern
    # * input patterns may be split by "--name" option(s)
    current_name = ""
    folded_patterns = {}
    while len(args):
        arg = args.pop(0)
        opt_name, opt_value = kpsdk.breakopt(arg)
        if opt_name is None:
            if 'output' not in opts:
                # the first positional argument is the output archive
                opts['output'] = arg
            else:
                try:
                    folded_patterns[current_name].append(arg)
                except KeyError:
                    folded_patterns[current_name] = [arg]
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
    if 'output' not in opts:
        print_usage("no input file(s) specified")
        return 1

    # get the list of all the files to add to the archive, folded by name
    folded_entries, most_recent_mtime = list_entries(
                                            folded_patterns, opts['recursive'])

    # check archive's modtime, if any, against the most recent modtime of the
    # input files
    if opts['keep']:
        try:
            if kpsdk.file_mtime_ns(opts['output']) > most_recent_mtime:
                kpsdk.info("Archive", os.path.basename(opts['output']), "is up-to-date.")
                return 0
        except:
            pass

    # write the archive
    kpsdk.info("Archive", os.path.basename(opts['output']) + "...")
    try:
        with kpsdk.ZipFile(opts['output'], mode="w") as zfile:
            for arch_base_folder, entries in folded_entries.items():
                for entry in entries:
                    entry_name = kpsdk.ZipFile.join_names(
                                    arch_base_folder, entry.relpath, is_dir=False)
                    zfile.write(entry.path, arcname=entry_name)
            arch_empty = not len(zfile.infolist())
    except:
        if os.path.exists(opts['output']):
            os.remove(opts['output'])
        raise

    # delete the archive if it's empty
    if arch_empty and os.path.exists(opts['output']):
        kpsdk.warn("Empty archive!")
        os.remove(opts['output'])

    # enable the read-only property if needed
    if opts['readonly']:
        kpsdk.file_set_readonly(opts['output'], True)

    return 0

if __name__ == "__main__":
    sys.exit(main())
