# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2017 Jean-Charles Lefebvre <polyvertex@gmail.com>

import os
import shutil
from . import _utils

__all__ = ["do_tag", "do_text", "do_file", "do_tree"]

def do_tag(text, name, value):
    if isinstance(text, bytes):
        tag = b'{{' + bytes(name, encoding="utf-8", errors="strict") + b'}}'
        value = bytes(value, encoding="utf-8", errors="strict")
    else:
        tag = '{{' + name + '}}'

    return text.replace(tag, value)

def do_text(text, tmpl_dict):
    for name, value in tmpl_dict.items():
        text = do_tag(text, name, value)
    return text

def do_file(src_file, dest_file, tmpl_dict):
    with open(src_file, mode="rb") as fin:
        with open(dest_file, mode="wb") as fout:
            # to read the entire file at once is not optimized but this allows
            # not to alter the original encoding and format (line ending)
            fout.write(do_text(fin.read(), tmpl_dict))

    shutil.copystat(src_file, dest_file, follow_symlinks=False)

def do_tree(root_src, root_dest, tmpl_dict, tmpl_ext=(".in", ".tmpl")):
    _do_tree(root_src, root_dest, tmpl_dict, tmpl_ext)


def _do_tree(root_src, root_dest, tmpl_dict, tmpl_ext, level=0):
    if level == 0:
        _mkdir(root_dest)

    for entry in os.scandir(root_src):
        src_path = os.path.join(root_src, entry.name)
        dest_path = os.path.join(root_dest, do_text(entry.name, tmpl_dict))

        if entry.is_dir():
            _mkdir(dest_path, copy_stats_from=src_path)
            _do_tree(src_path, dest_path, tmpl_dict, tmpl_ext, level + 1)
        elif entry.is_file():
            was_tmpl = False
            for ext in tmpl_ext:
                ext = ext.lower()
                if entry.name.lower().endswith(ext):
                    was_tmpl = True
                    dest_path = dest_path[0:-len(ext)]
                    do_file(src_path, dest_path, tmpl_dict)
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
        raise RuntimeError("destination exists and is not a directory: " + new_dir)
