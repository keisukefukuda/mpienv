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

def check_valid_paths(paths):
    err = False
    for p in search_paths:
        if not os.path.isdir(p):
            sys.stderr.write("Error: '{}' is not a directory\n".format(p))
            err = True

    if err:
        exit(-1)

def investigate_path(path, to_add):
    mpiexec = os.path.join(path, 'bin', 'mpiexec')
    if os.path.isfile(mpiexec):
        # Exclude mpienv's own directory
        name = manager.is_installed(dirpath)
        if name:
            print("{}\n\t Already known as "
                  "'{}'".format(dirpath, name))
            print()
        else:
            print("--------------------------------------")
            print("Found {}".format(mpiexec))
            pprint.pprint(manager.get_info(dirpath))
            # Install the new MPI
            if to_add:
                try:
                    name = manager.add(dirpath)
                    print("Added {} as {}".format(dirpath, name))
                except RuntimeError as e:
                    print("Error occured while "
                          "adding {}".format(dirpath))
                    print(e)
                    print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--add', dest='add',
                        action="store_true", default=None)
    parser.add_argument('paths', nargs='+')

    args = parser.parse_args()

    search_paths = args.paths
    to_add = args.add

    if len(search_paths) == 0:
        search_paths = default_search_paths

    check_valid_paths(search_paths)

    checked = set()

    for path in search_paths:
        for (dirpath, dirs, files) in os.walk(path):
            if dirpath in checked:
                continue
            investigate_path(dirpath)
            checked.add(dirpath)

if __name__ == "__main__":
    main()
