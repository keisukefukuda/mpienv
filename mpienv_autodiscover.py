# coding: utf-8

import argparse
import os
import os.path
import pprint
import sys

from common import manager

default_search_paths = [
    "/usr",
    "/usr/local",
    "/opt/local",
    os.path.expanduser("~"),
    os.path.expanduser("~/local"),
]

_verbose = None


def printv(s):
    if _verbose:
        sys.stderr.write(s + "\n")


def check_valid_paths(paths):
    err = False
    for p in paths:
        if not os.path.isdir(p):
            sys.stderr.write("Error: '{}' is not a directory\n".format(p))
            err = True

    if err:
        exit(-1)


def investigate_path(path, to_add):
    mpiexec = os.path.join(path, 'bin', 'mpiexec')
    if os.path.isfile(mpiexec):
        printv("checking {}".format(mpiexec))

        # Exclude mpienv's own directory
        name = manager.is_installed(path)
        if name:
            print("{}\n\t Already known as "
                  "'{}'".format(path, name))
            print()
        else:
            print("--------------------------------------")
            print("Found {}".format(mpiexec))
            pprint.pprint(manager.get_info(path))
            # Install the new MPI
            if to_add:
                try:
                    name = manager.add(path)
                    print("Added {} as {}".format(path, name))
                except RuntimeError as e:
                    print("Error occured while "
                          "adding {}".format(path))
                    print(e)
                    print()
    else:
        printv("No such file '{}'".format(mpiexec))


def main():
    global _verbose

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--add', dest='add',
                        action="store_true", default=None)
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action="store_true", default=None)
    parser.add_argument('paths', nargs='+')

    args = parser.parse_args()

    search_paths = args.paths
    to_add = args.add
    _verbose = args.verbose

    if len(search_paths) == 0:
        search_paths = default_search_paths

    check_valid_paths(search_paths)

    checked = set()

    for path in search_paths:
        for (dirpath, dirs, files) in os.walk(path):
            if dirpath in checked:
                continue
            investigate_path(dirpath, to_add)
            checked.add(dirpath)


if __name__ == "__main__":
    main()
