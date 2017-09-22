# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2017 Jean-Charles Lefebvre <polyvertex@gmail.com>

import os
import shutil
from . import _utils

__all__ = ["do_tag", "do_text", "do_file", "do_tree", "TAG_DELIMITERS"]

TAG_DELIMITERS = ( ('{{', '}}'), (b'{{', b'}}') )

def do_tag(text, name, value, tag_delim=TAG_DELIMITERS):
    if isinstance(text, bytes):
        tag = (tag_delim[1][0] +
               bytes(name, encoding="utf-8", errors="strict") +
               tag_delim[1][1])
        value = bytes(value, encoding="utf-8", errors="strict")
    else:
        tag = tag_delim[0][0] + name + tag_delim[0][1]

    return text.replace(tag, value)

def do_text(text, tmpl_dict, tag_delim=TAG_DELIMITERS):
    for name, value in tmpl_dict.items():
        text = do_tag(text, name, value, tag_delim)
    return text

def do_file(src_file, dest_file, tmpl_dict, tag_delim=TAG_DELIMITERS):
    with open(src_file, mode="rb") as fin:
        with open(dest_file, mode="wb") as fout:
            # to read the entire file at once is not optimized but this allows
            # not to alter the original encoding and format (line ending)
            fout.write(do_text(fin.read(), tmpl_dict, tag_delim))

    shutil.copystat(src_file, dest_file, follow_symlinks=False)

def do_tree(root_src, root_dest,
            tmpl_dict, tmpl_ext=(".in", ".tmpl"),
            tag_delim=TAG_DELIMITERS):
    _do_tree(root_src, root_dest, tmpl_dict, tmpl_ext, tag_delim)


def _do_tree(root_src, root_dest, tmpl_dict, tmpl_ext, tag_delim, level=0):
    if level == 0:
        _mkdir(root_dest)

    for entry in os.scandir(root_src):
        src_path = os.path.join(root_src, entry.name)
        dest_path = os.path.join(root_dest,
                                 do_text(entry.name, tmpl_dict, tag_delim))

        if entry.is_dir():
            _mkdir(dest_path, copy_stats_from=src_path)
            _do_tree(src_path, dest_path, tmpl_dict, tmpl_ext, tag_delim,
                     level + 1)
        elif entry.is_file():
            was_tmpl = False
            for ext in tmpl_ext:
                ext = ext.lower()
                if entry.name.lower().endswith(ext):
                    was_tmpl = True
                    dest_path = dest_path[0:-len(ext)]
                    do_file(src_path, dest_path, tmpl_dict, tag_delim)
                    break

            if not was_tmpl:
                shutil.copy2(src_path, dest_path, follow_symlinks=False)

def _mkdir(new_dir, copy_stats_from=None):
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
        if copy_stats_from is not None:
            shutil.copystat(copy_stats_from, new_dir, follow_symlinks=False)
    elif os.path.isdir(new_dir):
        if not _utils.dir_is_empty(new_dir):
            raise RuntimeError("destination directory not empty: " + new_dir)
    else:
        raise RuntimeError("destination exists and is not a directory: " +
                           new_dir)
