# coding: utf-8

import argparse
import json
import sys

from mpienv import mpienv
from mpienv import util

parser = argparse.ArgumentParser(
    prog='mpienv list', description='List all available MPI environments.')
parser.add_argument('--json', action="store_true", default=None,
                    help="Print in JSON format (useful for parsing)")
parser.add_argument('--simple', action="store_true", default=None,
                    help="Print in a simpler format "
                    "(useful for shell command)")


def _print_info(mpi, max_label_len):
    if mpi.is_broken:
        print("   {:<{width}} -> *** broken ***".format(
            mpi.name,
            width=max_label_len
        ))
    else:
        mark = "*" if mpi.is_active else " "
        print(" {} {:<{width}} -> {}".format(
            mark,
            mpi.name,
            mpi.prefix,
            width=max_label_len))


if __name__ == '__main__':
    args = parser.parse_args()

    if len(mpienv.keys()) == 0:
        exit(0)

    max_label_len = max(len(name) for name in mpienv.keys())

    lst = [info for name, info in mpienv.items()]
    lst.sort(key=lambda x: x.name)
    if args.json:
        lst = {name: info for name, info in mpienv.items()}
        json.dump(lst, sys.stdout, default=util.dump_json)
    elif args.simple:
        lst = [info.name for info in lst]
        print(' '.join(lst))
    else:
        print("\nInstalled MPIs:\n")
        for info in lst:
            _print_info(info, max_label_len)
        print("")
