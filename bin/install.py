# coding: utf-8

import argparse
import sys

from common import manager
from mpienv.installer import create_installer
from mpienv.installer import list_avail


def main():
    parser = argparse.ArgumentParser(description="mpienv-install")
    parser.add_argument('-n', '--name', metavar='name', dest='name',
                        default=None, type=str,
                        help='Name of an MPI installation')
    parser.add_argument('--list', action="store_true", default=False,
                        help='List all available MPIs')
    parser.add_argument('--clear', action="store_true", default=False,
                        help='Clear build/download cache')
    parser.add_argument('--configure', action="store_true", default=False,
                        help='Run configure script only')
    parser.add_argument('--build', action='store_true', default=False,
                        help='Only build the MPI')
    parser.add_argument('mpi', type=str, nargs='?',
                        help='MPI name', default=None)

    args = parser.parse_args()

    # Create a link
    if args.list:
        if any([args.clear, args.configure, args.build, args.mpi]):
            sys.stderr.write("Error: --list and other arguments "
                             "cannot specified together.\n")
            exit(1)

        list_avail()
        exit(0)

    inst = create_installer(manager, args.mpi, args.name, sys.argv)

    if args.clear:
        inst.clear()
        exit(0)


if __name__ == "__main__":
    main()
