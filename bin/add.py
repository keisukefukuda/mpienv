# coding: utf-8

import argparse

from mpienv import mpienv


parser = argparse.ArgumentParser(
    prog='mpienv add',
    description='Add a MPI environment already installed in your host.')
parser.add_argument('-n', '--name', metavar='name', dest='name', type=str,
                    help='Name of an MPI installation')
parser.add_argument('path', metavar='path', type=str,
                    help='Path in which an MPI is intalled')


def main():
    args = parser.parse_args()

    # Create a link
    mpienv.add(args.path, args.name)


if __name__ == "__main__":
    main()
