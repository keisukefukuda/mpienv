# coding: utf-8

import sys

from common import manager


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("mpienv: Error: mpienv use [mpi-name]\n")
        exit(-1)
    else:
        manager.use(sys.argv[1])
