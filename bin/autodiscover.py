# coding: utf-8

import argparse
import os
import os.path
import pprint
import sys

from common import manager


parser = argparse.ArgumentParser(
    prog='mpienv autodiscover',
    description='Find MPI environments already installed in your host.')
parser.add_argument('-a', '--add', dest='add',
                    action="store_true", default=None)
parser.add_argument('-v', '--verbose', dest='verbose',
                    action="store_true", default=None)
parser.add_argument('-q', '--quiet', dest='quiet',
                    action="store_true", default=None)
parser.add_argument('paths', nargs='*')


default_search_paths = [
    "/usr",
    "/usr/local",
    "/opt/local",
    os.path.expanduser("~"),
    os.path.expanduser("~/local"),
]

_verbose = None
_quiet = None


def printv(s):
    if _verbose:
        sys.stderr.write(s + "\n")


def prints(s=""):
    if not _quiet:
        print(s)


def filter_valid_paths(paths, warn=True):
    ret = []
    for p in paths:
        if os.path.isdir(p):
            ret.append(p)
        else:
            if warn:
                sys.stderr.write("Error: '{}' is not a directory\n".format(p))

    return ret


def investigate_path(path, to_add):
    mpiexec = os.path.join(path, 'bin', 'mpiexec')
    if os.path.isfile(mpiexec):
        printv("checking {}".format(mpiexec))

        # Exclude mpienv's own directory
        name = manager.is_installed(path)
        if name:
            prints("{}\n\t Already known as "
                   "'{}'".format(path, name))
            prints()
        else:
            prints("--------------------------------------")
            prints("Found {}".format(mpiexec))
            prints(pprint.pformat(manager.get_mpi_from_prefix(path)))
            # Install the new MPI
            if to_add:
                try:
                    name = manager.add(path)
                    prints("Added {} as {}".format(path, name))
                except RuntimeError as e:
                    prints("Error occured while "
                           "adding {}".format(path))
                    prints(e)
                    prints()
    else:
        printv("No such file '{}'".format(mpiexec))


def main():
    global _verbose
    global _quiet

    args = parser.parse_args()

    search_paths = args.paths
    to_add = args.add
    _verbose = args.verbose
    _quiet = args.quiet

    if _verbose and _quiet:
        sys.stderr.write("Error: -q and -v cannot "
                         "specified at the same time.\n")
        exit(-1)

    if len(search_paths) == 0:
        search_paths = default_search_paths
        using_default = True
    else:
        using_default = False

    search_paths = filter_valid_paths(search_paths,
                                      warn=(not using_default))

    checked = set()

    for path in search_paths:
        for (dirpath, dirs, files) in os.walk(path):
            if dirpath in checked:
                continue
            investigate_path(dirpath, to_add)
            checked.add(dirpath)


if __name__ == "__main__":
    main()
