# coding: utf-8

import argparse

from common import manager


def main():
    parser = argparse.ArgumentParser(description="mpienv-add")
    parser.add_argument('-n', '--name', metavar='name', dest='name', type=str,
                        help='Name of an MPI installation')
    parser.add_argument('path', metavar='path', type=str,
                        help='Path in which an MPI is intalled')

    args = parser.parse_args()

    # Create a link
    manager.add(args.path, args.name)


if __name__ == "__main__":
    main()
