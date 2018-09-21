# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2018 Jean-Charles Lefebvre <polyvertex@gmail.com>

import os
from . import _cli
from . import _globscan
from . import _utils
from . import _zipfile

__all__ = ["archive"]

def _list_entries(folded_patterns, recursive, include_hidden):
    entries = {}
    most_recent_mtime = 0
    for arch_base_folder, input_patterns in folded_patterns.items():
        for entry in _globscan.iglobscan(input_patterns,
                                         recursive=recursive,
                                         include_dirs=False,
                                         include_hidden=include_hidden):
            if entry.name[0] not in "~#":
                try:
                    entries[arch_base_folder].append(entry)
                except KeyError:
                    entries[arch_base_folder] = [entry]
                mtime = entry.stat().st_mtime_ns
                if mtime > most_recent_mtime:
                    most_recent_mtime = mtime
    return entries, most_recent_mtime

def archive(output_file, folded_patterns, check_modtime=False, recursive=False,
            include_hidden=False, apply_readonly=False, verbose=True,
            time_spec=_zipfile.TimeSpec.FILE):
    if not isinstance(folded_patterns, dict):
        folded_patterns = {"": folded_patterns}
    elif not _utils.is_iterable(folded_patterns):
        raise ValueError("folded_patterns")

    if time_spec is None:
        time_spec = _zipfile.TimeSpec.FILE
    elif isinstance(time_spec, str):
        time_spec = _zipfile.string_to_timespec(time_spec)
    elif not isinstance(time_spec, _zipfile.TimeSpec):
        raise TypeError("time_spec")

    # get the list of all the files to add to the archive, folded by name
    folded_entries, most_recent_mtime = _list_entries(
        folded_patterns, recursive, include_hidden)

    # check archive's modtime, if any, against the most recent modtime of the
    # input files
    if check_modtime:
        try:
            if _utils.file_mtime_ns(output_file) > most_recent_mtime:
                if verbose:
                    _cli.info("Archive", os.path.basename(output_file),
                              "is up-to-date.")
                return 0
        except:
            pass

    # write the archive
    if verbose:
        _cli.info("Archive", os.path.basename(output_file) + "...")
    try:
        with _zipfile.ZipFile(output_file, mode="w") as zfile:
            for arch_base_folder, entries in folded_entries.items():
                for entry in entries:
                    entry_name = _zipfile.ZipFile.join_names(
                        arch_base_folder, entry.relpath, is_dir=False)
                    zfile.write(entry.path,
                                arcname=entry_name,
                                time_spec=time_spec)
            arch_empty = not len(zfile.infolist())
    except:
        if os.path.exists(output_file):
            os.remove(output_file)
        raise

    # delete the archive if it's empty
    if arch_empty and os.path.exists(output_file):
        _cli.warn("Empty archive!")
        os.remove(output_file)

    # enable the read-only property if needed
    if apply_readonly:
        _utils.file_set_readonly(output_file, True)
