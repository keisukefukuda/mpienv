# coding: utf-8

import argparse

from mpienv import mpienv

parser = argparse.ArgumentParser(
    prog='mpienv rename', description='Rename an environment.')
parser.add_argument('name_from', type=str)
parser.add_argument('name_to', type=str)


def main():
    args = parser.parse_args()
    mpienv.rename(args.name_from, args.name_to)


if __name__ == "__main__":
    main()
