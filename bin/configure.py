# coding: utf-8

import argparse

from mpienv.installer import create_installer
from mpienv import mpienv


parser = argparse.ArgumentParser(
    prog='mpienv configure',
    description='Run configure script in a specific MPI package.')
parser.add_argument('-n', '--name', metavar='name', dest='name',
                    default=None, type=str, nargs='?',
                    help='Name of an MPI installation')
parser.add_argument('-v', '--verbose', dest='verbose',
                    default=False, action='store_true',
                    help='Verbose')
parser.add_argument('mpi', type=str, metavar="[MPI]",
                    help='MPI name', default=None)
parser.add_argument('conf_args', nargs=argparse.REMAINDER,
                    default=[])


def main():
    args = parser.parse_args()

    inst = create_installer(mpienv, args.mpi, args.name,
                            verbose=args.verbose)

    inst.configure()


if __name__ == "__main__":
    main()
