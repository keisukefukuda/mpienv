# coding: utf-8

import argparse
import os
import sys

import common

root_dir = os.path.join(os.path.expanduser('~'), '.mpienv')
vers_dir = os.path.join(root_dir, 'versions')


def main():
    parser = argparse.ArgumentParser(description="mpienv-add")
    parser.add_argument('-n', '--name', metavar='name', dest='name', type=str,
                        help='Name of an MPI installation')
    parser.add_argument('path', metavar='path', type=str,
                        help='Path in which an MPI is intalled')

    args = parser.parse_args()
    path = args.path
    name = args.name

    # Error check:
    if not os.path.exists(path):
        raise RuntimeError("{} does not exist.".format(path))
    if not os.path.isdir(path):
        raise RuntimeError("{} is not a directory.".format(path))

    try:
        info = common.get_info(args.path)
    except:
        raise RuntimeError("Could not find an MPI installation in {}".format(path))

    name = args.name or info['default_name']

    # Check if the name is already taken:
    if os.path.exists(os.path.join(vers_dir, name)):
        raise RuntimeError("The name '{}' is already used.".format(name))

    # Create a link

if __name__ == "__main__":
    main()
    
