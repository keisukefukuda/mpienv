# coding: utf-8
# Update LD_LIBRARY_PATH

import glob
import os.path
import re
import sys

from common import *

def main():
    proj_root = sys.argv[1]    # the directory where this script is installed
    cur_llp = sys.argv[2]  # the current LD_LIBRARY_PATH
    mpi_type = sys.argv[3]     # selected MPI type

    new_llp = filter_path(proj_root, cur_llp.split(':'))
    
    mpi_link = os.path.join(proj_root, 'links', mpi_type)
    if not (os.path.exists(mpi_link) and os.path.islink(mpi_link)):
        sys.stderr.write("Error: Unknown MPI type: '{}'".format(mpi_type))
        exit(-1)

    new_llp[:0] = [os.path.join(mpi_link, 'lib')]
    print(':'.join(new_llp))

if __name__ == "__main__":
    main()
