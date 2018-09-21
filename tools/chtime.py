# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2018 Jean-Charles Lefebvre <polyvertex@gmail.com>

import argparse
import sys
import kpsdk
import kpsdk.chtime

def main():
    argp = argparse.ArgumentParser(
        description="Change file(s) times on Windows")
    argp.add_argument("-t", "--time", metavar="TIME", default="now",
        help="The time to apply (now, utcnow, midnight or utcmidnight)")
    argp.add_argument("-m", "--mtime", action="store_true",
        help="Change the modification time")
    argp.add_argument("-a", "--atime", action="store_true",
        help="Change the 'last access' time")
    argp.add_argument("-c", "--ctime", action="store_true",
        help="Change the creation time")
    argp.add_argument("--all", action="store_true",
        help="Combination of --mtime, --atime and --ctime")
    argp.add_argument("-r", "--recursive", action="store_true",
        help="Scan for files recursively")
    argp.add_argument("--hidden", action="store_true",
        help="Include hidden files")
    argp.add_argument("--dry", action="store_true",
        help="Dry run. Just list the files to be impacted")
    argp.add_argument("patterns", nargs="+",
        help="Input file(s) (may be specified as patterns)")
    args = argp.parse_args();

    if not any((args.all, args.atime, args.ctime, args.mtime)):
        kpsdk.die("missing at least --mtime, --atime or --ctime")
    if args.all:
        args.atime = True
        args.ctime = True
        args.mtime = True

    res = kpsdk.chtime.chtime(
        args.time, args.patterns,
        recursive=args.recursive, include_hidden=args.hidden,
        mtime=args.mtime, atime=args.atime, ctime=args.ctime, dry_run=args.dry)
    if args.dry:
        for file in res:
            kpsdk.info(file, file=sys.stdout)

    return 0

if __name__ == "__main__":
    sys.exit(main())
