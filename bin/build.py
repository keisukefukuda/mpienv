# coding: utf-8

import argparse

from common import manager
from mpienv.installer import create_installer


def main():
    parser = argparse.ArgumentParser(description="mpienv-build")
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

    args = parser.parse_args()

    inst = create_installer(manager, args.mpi, args.name,
                            verbose=args.verbose)

    inst.install(npar=args.npar)


if __name__ == "__main__":
    main()