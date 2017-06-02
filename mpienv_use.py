# coding: utf-8

import argparse

from common import manager


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--python', action="store_true",
                        dest="python", default=False,
                        help="Also switch mpi4py library")
    parser.add_argument('name', type=str,
                        help="MPI name to use")

    args = parser.parse_args()
    manager.use(args.name, python=args.python)


if __name__ == "__main__":
    main()
