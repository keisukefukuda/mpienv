# coding: utf-8

import os
import os.path
import sys
import pprint

import common

root_dir = os.path.join(os.path.expanduser('~'), '.mpienv')
vers_dir = os.path.join(root_dir, 'versions')

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

    for path in search_paths:
        for (dirpath, dirs, files) in os.walk(path):
            if 'bin'in dirs:
                bin = os.path.join(dirpath, 'bin')

                # Exclude mpienv's own directory
                if root_dir in os.path.realpath(bin):
                    continue
                
                mpiexec = os.path.join(bin,'mpiexec')
                if os.path.exists(mpiexec):
                    print("-------------------------------------")
                    print("Found mpiexec: {}".format(mpiexec))
                    pprint.pprint(common.get_info(dirpath))
                    print()
        
if __name__ == "__main__":
    main()
