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
    
    # Create a link
    manager.add(args.name, args.path)

if __name__ == "__main__":
    main()
    
