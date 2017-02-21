# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2017 Jean-Charles Lefebvre <polyvertex@gmail.com>

import os
import stat
import time
import zipfile
import zlib
from . import _glob

_IS_WINDOWS = os.name.lower() == "nt"
if _IS_WINDOWS:
    import ctypes

__all__ = ["ZipFile"]

# Setup maximum compression level
# * This is a dirty hack. The zipfile module doesn't offer us to change the
#   compression level.
# * When the zipfile.ZIP_DEFLATED method is used, the ZipFile class implicitly
#   relies on the default compression level defined internally by the zlib
#   module with the zlib.Z_DEFAULT_COMPRESSION constant.
# * Note that this hack is not thread-safe but we don't mind here.
zlib.Z_DEFAULT_COMPRESSION = zlib.Z_BEST_COMPRESSION

class ZipFile:
    """
    A ``zipfile.ZipFile`` replacement to properly create Zip archives.

    **CAUTION:** This code is not thread-safe
    """
    def __init__(self, file, mode="r", compression=zipfile.ZIP_DEFLATED, **kwargs):
        self.compression = compression
        self.zfile = zipfile.ZipFile(file, mode=mode, compression=compression, **kwargs)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __getattr__(self, attr):
        return getattr(self.zfile, attr)

    def close(self):
        if self.zfile:
            zf = self.zfile
            self.zfile = None
            self.compression = None
            zf.close()

    def write(self, file, arcname=None, compress_type=None, comment=None):
        """
        A replacement of zipfile.write() that keeps original file attributes on
        Unix **and** Windows systems, and optionally allows to specify the
        content of the ``comment`` field.
        """
        self._checkzfile()

        if compress_type is None:
            compress_type = self.compression
        comment_is_utf8 = False

        # stat file
        file_stat = os.stat(file)
        is_dir = stat.S_ISDIR(file_stat.st_mode)
        file_mtime = time.localtime(file_stat.st_mtime)

        # entry name
        if arcname is None:
            arcname = file
        arcname = self.cleanup_name(arcname, is_dir)
        arcname_enc, arcname_is_utf8 = self.encode_name(arcname)

        # init the ZipInfo structure
        zinfo = zipfile.ZipInfo(arcname_enc)
        #zinfo.filename = arcname_enc
        zinfo.date_time = file_mtime[0:6]
        zinfo.compress_type = compress_type
        if comment is not None:
            zinfo.comment, comment_is_utf8 = self.encode_name(comment)
        if arcname_is_utf8 or comment_is_utf8:
            zinfo.flag_bits |= 1 << 11

        if _IS_WINDOWS:
            # ms-dos attributes
            winattr = ctypes.windll.kernel32.GetFileAttributesW(file)
            if winattr != 0xffffffff: # INVALID_FILE_ATTRIBUTES
                winattr &= ~0x800 # forcefully remove the 'compressed' flag
                zinfo.external_attr |= winattr & 0xffff
        else:
            # unix attributes
            zinfo.external_attr |= (file_stat.st_mode & 0xffff) << 16

        # write entry
        if is_dir:
            zinfo.compress_type = zipfile.ZIP_STORED
            zinfo.external_attr |= 0x10 # force MS-DOS directory flag
            self.zfile.writestr(zinfo, b'')
        else:
            with open(file, "rb") as f:
                self.zfile.writestr(zinfo, f.read())

    def write_empty_dir(self, arcname, comment=None):
        """Explicitly add an empty directory entry to the archive"""
        self._checkzfile()

        arcname = self.cleanup_name(arcname, True)
        arcname_enc, arcname_is_utf8 = self.encode_name(arcname)
        comment_is_utf8 = False

        zinfo = zipfile.ZipInfo(arcname_enc)
        #zinfo.filename = arcname_enc
        zinfo.compress_type = zipfile.ZIP_STORED
        zinfo.external_attr = 0o40775 << 16 # unix attributes drwxr-xr-x
        zinfo.external_attr |= 0x10 # MS-DOS directory flag
        if comment is not None:
            zinfo.comment, comment_is_utf8 = self.encode_name(comment)
        if arcname_is_utf8 or comment_is_utf8:
            zinfo.flag_bits |= 1 << 11

        self.zfile.writestr(zinfo, b'')

    def write_mapped(
            self, files, arcname_prefix="", include_base_dirname=False,
            include_hidden=False, include_empty_dirs=True, compress_type=None):
        self._checkzfile()

        if isinstance(files, str):
            files = (files, )
        elif not isinstance(files, (list, tuple)):
            raise TypeError("files")
        arcname_prefix = self.cleanup_name(arcname_prefix, True)

        # first pass to expand wildcards if needed
        caller_files = files
        files = []
        for file in caller_files:
            if "**" in file:
                raise ValueError("recursive wildcard '**' not accepted")
            elif _glob.has_magic(file):
                for f in _glob.iglob(file, recursive=False, include_hidden=include_hidden):
                    files.append(f)
            else:
                files.append(file)

        for file in files:
            # note: do not do a _is_hidden() test here since this *file* is has
            # been specified explicitly by the caller
            is_dir = os.path.isdir(file)
            if is_dir:
                entry_base_name = os.path.basename(file) if include_base_dirname else ""
            else:
                entry_base_name = os.path.basename(file)
            entry_base_name = self.cleanup_name(entry_base_name, is_dir)
            entry_base_name = arcname_prefix + entry_base_name

            if is_dir:
                oldcwd = os.getcwd()
                empty_dir = True
                entry_base_name += "/"
                try:
                    os.chdir(file)
                    for src_relative in _glob.iglob("**", recursive=True, include_hidden=include_hidden):
                        src_path = os.path.join(file, src_relative)
                        if os.path.isfile(src_path):
                            entry_name = entry_base_name + self.cleanup_name(src_relative, False)
                            empty_dir = False
                            self.write(src_path, entry_name, compress_type)
                finally:
                    os.chdir(oldcwd)
                if empty_dir and include_empty_dirs:
                    zfile.write_empty_dir(arc_basename)
            else:
                self.write(file, entry_base_name, compress_type)

    def _checkzfile(self):
        if not self.zfile:
            raise RuntimeError("zip archive is closed")

    @classmethod
    def cleanup_name(cls, arcname, is_dir):
        arcname = arcname.strip()

        # remove drive prefix, if any
        arcname = os.path.normpath(os.path.splitdrive(arcname)[1])

        # convert to unix-style and strip slashes on both ends
        if os.sep != "/" and os.sep in arcname:
            arcname = arcname.replace(os.sep, "/")
        arcname = arcname.strip("/")

        # "//" to "/"
        while "//" in arcname:
            arcname = arcname.replace("//", "/")

        # ensure we've got a trailing "/" if is_dir is true
        if is_dir:
            if len(arcname) and arcname[-1] != "/":
                arcname += "/"
        else:
            arcname.rstrip("/")

        return arcname

    @classmethod
    def join_names(cls, name, *names, is_dir=False):
        arcname = ""
        for n in (name, *names):
            n = cls.cleanup_name(n, is_dir=False)
            if len(n):
                if len(arcname):
                    arcname += "/"
                arcname += n
        if is_dir and len(arcname):
            arcname += "/"
        return arcname

    @classmethod
    def encode_name(cls, arcname, force_cp437=False):
        for encoding in ("cp437", "utf-8"):
            try:
                encoded = arcname.encode(encoding=encoding, errors="strict")
                return (str(encoded, encoding=encoding), encoding != "cp437")
            except UnicodeError:
                if encoding != "cp437" or force_cp437:
                    raise ValueError('zip entry name not {} compliant: "{}"'.format(encoding.upper(), arcname))
        raise Exception # Should Never Get Here (c)
