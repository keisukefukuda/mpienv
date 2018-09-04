# coding: utf-8

import argparse

from mpienv import mpienv

parser = argparse.ArgumentParser(
    prog='mpienv use', description='Set the specific MPI environment.')
parser.add_argument('-p', '--mpi4py', action="store_true",
                    dest="mpi4py", default=False,
                    help="Also switch mpi4py library")
parser.add_argument('name', type=str,
                    help="MPI name to use")


def main():
    args = parser.parse_args()
    mpienv.use(args.name, mpi4py=args.mpi4py)


if __name__ == "__main__":
    main()
