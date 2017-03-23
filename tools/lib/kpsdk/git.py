# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2017 Jean-Charles Lefebvre <polyvertex@gmail.com>

import os.path
import re
import sys
from . import _cli
from . import _utils
from . import _version

__all__ = ["run", "interactive", "repo_info"]

def run(*args, repo_dir=None, git_cmd="git",
        splitlines=False, rstrip=True, **kwargs):
    with _utils.ScopedWorkDirChange(repo_dir): # None arg allowed
        return _cli.run((git_cmd, ) + tuple(*args),
                        splitlines=splitlines, rstrip=rstrip,
                        **kwargs)

def interactive(*args, repo_dir=None, git_cmd="git",
                stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr,
                **kwargs):
    return run(*args, repo_dir=repo_dir, git_cmd=git_cmd,
               stdin=stdin, stdout=stdout, stderr=stderr,
               **kwargs)

def repo_info(repo_dir, opts=[], git_cmd="git"):

    def _git(*args, **kwargs):
        with _utils.ScopedWorkDirChange(repo_dir):
            return run(tuple(*args) + tuple(opts), git_cmd=git_cmd, **kwargs)

    if not repo_dir:
        raise ValueError("invalid repo_dir argument")
    if not os.path.isdir(repo_dir):
        raise ValueError("repo_dir is not a directory")

    info = {
        'describe': None,    # unparsed result of git-describe
        'hash': None,        # full hash
        'short': None,       # short hash
        'branch': None,      # current branch
        'tag': {
            'full': None,     # "v1.2.3-name"
            'version': None,  # optional, the Version obj for the "1.2.3" in "v1.2.3-name"
            'commits': None}, # optional, count of commits since last tag on this branch
        'dirty': False}
    rem = _utils.ReMatch()

    # call git to get every info we need
    # examples of output from git-describe:
    # * 2.2.0
    # * v2.2.0
    # * v2.2.0-dirty
    # * v2.2.0-1-g4ca113d6a2844260d6ba7737697d404e9256cd90
    # * v2.2.0-1-g4ca113d6a2844260d6ba7737697d404e9256cd90-dirty
    # * 4ca113d6a2844260d6ba7737697d404e9256cd90
    # * 4ca113d6a2844260d6ba7737697d404e9256cd90-dirty
    # * arbitrary-tag-name
    # * arbitrary-tag-name-dirty

    # git describe
    info['describe'] = _git("describe", "--always", "--abbrev",
                            "--dirty=-dirty").stdout.lstrip()

    # get HEAD's full hash
    info['hash'] = _git("rev-parse", "HEAD").stdout
    if not rem.match(r"^\s*([a-h\d]{4,40})\s*$", info['hash'], re.A):
        raise RuntimeError("could not parse hash from git repo: " + repo_dir)
    info['hash'] = rem.group(1)

    # get HEAD's branch name
    # there might be several branches, but the one we want is the currently
    # selected branch, which is flagged with a '*' prefix
    for branch in _git("branch", "--list", "--no-color", "--contains=HEAD",
                       splitlines=True).stdout:
        if rem.match(r"^\*\s+(.+?)\s*$", branch):
            info['branch'] = rem.group(1).strip()
            break
    if not info['branch']:
        raise RuntimeError("could not get branch name from git repo: " +
                           repo_dir)

    # extract tag info from git-describe output
    if rem.match(r"^(.+)\-(\d+)\-g?([a-h\d]{4,40})(\-dirty)?$",
                   info['describe'], re.A):
        # here, a tag was found and there have been commits on the top of it
        # possible forms:
        # * v2.2.0-1-g4ca113d
        # * v2.2.0-1-g4ca113d-dirty
        info['tag']['full'] = rem.group(1)
        info['tag']['commits'] = int(rem.group(2), base=10)
        info['short'] = rem.group(3)
        info['dirty'] = True if rem.group(4) else False
    elif rem.match(r"^([a-h\d]{4,40})(\-dirty)?$", info['describe'], re.A):
        # here, no tag was found
        # possible forms:
        # * 4ca113d
        # * 4ca113d-dirty
        info['short'] = rem.group(1)
        info['dirty'] = rem.group(2, False)
    elif rem.match(r"^(.+?)(\-dirty)?$", info['describe'], re.A):
        # +? -> match 1 or more times, NOT GREEDILY
        # important so we can handle BOTH cases: with or without the "-dirty"
        # suffix
        # here, HEAD is on a tag, only its name has been printed
        info['tag']['full'] = rem.group(1)
        info['dirty'] = True if rem.group(2) else False
        info['tag']['commits'] = 0

    # get the short hash from git instead of guessing the right length
    if not info['short']:
        info['short'] = _git("rev-parse", "--short", "HEAD").stdout

    # paranoid check on short hash
    if (not rem.match(r"^\s*([a-h\d]{4,40})\s*$", info['short'], re.A) or
            info['short'] != info['hash'][0:len(info['short'])]):
        raise RuntimeError("could not validate short hash from git repo: " + repo_dir)

    # parse tag if there is one
    if info['tag']['full']:
        try:
            info['tag']['version'] = _version.Version(info['tag']['full'])
        except ValueError as exc:
            raise RuntimeError(
                'could not parse tag "{}" from git repo: {}'.format(
                    info['tag']['full'], repo_dir))

    return info
