# coding: utf-8

import argparse
import os  # NOQA
import sys

from mpienv import mpienv


parser = argparse.ArgumentParser(
    prog='mpienv exec',
    description='Call mpiexec with appropriate arguments')
parser.add_argument('args', nargs=argparse.REMAINDER,
                    default=[],
                    help='Arguments passed to mpiexec')


def main():
    args = sys.argv[1:]

    # Take mpienv's arguments (if there's any)
    idx = 0
    dry_run = False
    verbose = False
    while True:
        if args[idx] == '--dry-run':
            # --dry-run is mpienv's unique option and is not passed to mpiexec.
            args.pop(idx)
            dry_run = True
        elif args[idx] == '--verbose':
            # The behaviour of '--verbose' is tricky
            # because both mpiexec and mpienv have the option and
            # actives the flag for both of mpiexec and mpienv.
            # Thus, if --verbose is found, on contrast to --dry-run,
            # it is preserved and passed to mpiexec.
            idx += 1
            verbose = True
        else:
            break

    mpienv.exec_(args, dry_run=dry_run, verbose=verbose)


if __name__ == "__main__":
    main()
