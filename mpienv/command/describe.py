# coding: utf-8

import argparse

from mpienv import mpienv


parser = argparse.ArgumentParser(
    prog='mpienv describe',
    description='Describe a registered MPI')
parser.add_argument('name', metavar='name', type=str,
                    help='Name of an MPI installation')


def main():
    args = parser.parse_args()

    # Create a link
    mpienv.describe(args.name)


if __name__ == "__main__":
    main()
