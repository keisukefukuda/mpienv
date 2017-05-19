# coding: utf-8

import os
import os.path
import sys

from common import manager

default_search_paths = [
    "/usr",
    "/usr/local",
    "/opt/local",
    os.path.expanduser("~"),
    os.path.expanduser("~/local"),
]


def main():
    if len(sys.argv) == 1:
        search_paths = default_search_paths
    else:
        err = False
        for p in sys.argv[1:]:
            if not os.path.isdir(p):
                sys.stderr.write("Error: '{}' is not a directory\n".format(p))
                err = True

        if err:
            exit(-1)

        search_paths = sys.argv[1:]

    checked = set()

    for path in search_paths:
        for (dirpath, dirs, files) in os.walk(path):
            if dirpath in checked:
                continue
            if 'bin'in dirs:
                bin = os.path.join(dirpath, 'bin')
                mpiexec = os.path.join(bin, 'mpiexec')
                if os.path.isfile(mpiexec):
                    # Exclude mpienv's own directory
                    name = manager.is_installed(dirpath)
                    if name:
                        print("{}\n\t Already known as "
                              "'{}'".format(dirpath, name))
                        print()
                    else:
                        # Install the new MPI
                        try:
                            name = manager.add(dirpath)
                            print("Added {} as {}".format(dirpath, name))
                        except RuntimeError as e:
                            print("Error occured while "
                                  "adding {}".format(dirpath))
                            print(e)

                    checked.add(dirpath)

if __name__ == "__main__":
    main()
