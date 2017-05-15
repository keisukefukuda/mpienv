# coding: utf-8

import os
import os.path
import re
import sys

import common

root_dir = os.path.join(os.path.expanduser('~'), '.mpienv')
vers_dir = os.path.join(root_dir, 'versions')

if __name__ == "__main__":
    if len(sys.argv) > 2:
        name = sys.argv[2]
    else:
        name = None
    print(common.get_info(sys.argv[1], name))
