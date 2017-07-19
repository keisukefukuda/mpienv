# coding: utf-8

import argparse
import sys

from mpienv.installer import create_installer
from mpienv.installer import list_avail
from mpienv import mpienv

parser = argparse.ArgumentParser(
    prog='mpienv build', description='Install a new MPI environment.')
parser.add_argument('-n', '--name', metavar='name', dest='name',
                    default=None, type=str,
                    help='Name of an MPI installation')
parser.add_argument('-v', '--verbose', dest='verbose',
                    default=False, action='store_true',
                    help='Verbose')
parser.add_argument('-j', type=int, default=1, dest='npar',
                    help="Number of parallel make jobs")
parser.add_argument('mpi', type=str, metavar="[MPI]",
                    help='MPI name')


def main():
    try:
        if sys.argv[1:].index('--list') >= 0:
            list_avail()
            exit(0)
    except ValueError:
        pass

    args = parser.parse_args()

    inst = create_installer(mpienv, args.mpi, args.name,
                            verbose=args.verbose)

    inst.install(npar=args.npar)


if __name__ == "__main__":
    main()
