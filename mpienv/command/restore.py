# coding: utf-8

import argparse

from mpienv import mpienv


parser = argparse.ArgumentParser(
    prog='mpienv refresh',
    description='Restore the status')


def main():
    args = parser.parse_args()  # NOQA

    # Create a link
    mpienv.restore()


if __name__ == "__main__":
    main()
