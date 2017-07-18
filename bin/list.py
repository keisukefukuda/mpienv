# coding: utf-8

import argparse
import json
import sys

from common import manager
import mpienv.util

parser = argparse.ArgumentParser(
    prog='mpienv list', description='List all available MPI environments.')
parser.add_argument('--json', action="store_true",
                    default=None)


def _print_info(mpi, max_label_len):
    if mpi.is_broken:
        print("   {:<{width}} -> *** broken ***".format(
            mpi.name,
            width=max_label_len
        ))
    else:
        print(" {} {:<{width}} -> {}".format(
            "*" if mpi.is_active else " ",
            mpi.name,
            mpi.prefix,
            width=max_label_len))


if __name__ == '__main__':
    args = parser.parse_args()

    if len(manager.keys()) == 0:
        exit(0)

    max_label_len = max(len(name) for name in manager.keys())

    lst = [info for name, info in manager.items()]
    lst.sort(key=lambda x: x.name)
    if args.json:
        lst = {name: info for name, info in manager.items()}
        json.dump(lst, sys.stdout, default=mpienv.util.dump_json)
    else:
        print("\nInstalled MPIs:\n")
        for info in lst:
            _print_info(info, max_label_len)
        print("")
