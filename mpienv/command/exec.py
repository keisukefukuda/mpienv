# coding: utf-8

import argparse
import os  # NOQA
import sys

from mpienv import mpienv


parser = argparse.ArgumentParser(
    prog='mpienv exec',
    description='Call mpiexec with appropriate arguments')
parser.add_argument('args', nargs=argparse.REMAINDER,
                    default=[])


def main():
    args = sys.argv[1:]

    mpienv.exec_(args)


if __name__ == "__main__":
    main()
