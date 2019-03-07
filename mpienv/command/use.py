# coding: utf-8

import argparse

from mpienv import mpienv
import sys

parser = argparse.ArgumentParser(
    prog='mpienv use', description='Set the specific MPI environment.')
parser.add_argument('-p', '--mpi4py', action="store_true",
                    dest="mpi4py", default=False,
                    help="Activate mpi4py library for "
                         "the current python (default)")
parser.add_argument('--no-mpi4py', action='store_true',
                    dest='no_mpi4py', default=False,
                    help="Do not activate mpi4py library")
parser.add_argument('name', type=str,
                    help="MPI name to use")


def main():
    args = parser.parse_args()

    if args.mpi4py and args.no_mpi4py:
        sys.stderr.write("mpienv: Error: both of --mpi4py "
                         "and --no-mpi4py are specified.")
        exit(1)

    if args.mpi4py:
        sys.stderr.write("mpienv: Info: --mpi4py is ON by default.\n")

    mpienv.use(args.name, no_mpi4py=args.no_mpi4py)


if __name__ == "__main__":
    main()
