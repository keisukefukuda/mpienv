# coding: utf-8

import glob
import os
import os.path

import common

root_dir = os.path.join(os.path.expanduser('~'), '.mpienv')
vers_dir = os.path.join(root_dir, 'versions')

if __name__ == '__main__':
    mpis = common.list_versions()

    max_label_len = max(len(x['label']) for x in mpis)

    print("\nInstalled MPIs:\n")
    for mpi in mpis:
        print(" {} {:<{width}} -> {}".format(
            "*" if mpi['active'] else " ",
            mpi['label'],
            mpi['path'],
            width=max_label_len))

    print()
        
