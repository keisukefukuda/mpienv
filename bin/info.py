# coding: utf-8

import argparse
import json
import pprint
import sys

from common import manager

parser = argparse.ArgumentParser(
    prog='mpienv info',
    description='Show information of current MPI environment.')
parser.add_argument('--json', action="store_true", default=None)
parser.add_argument('name', nargs='?', default=None)

if __name__ == "__main__":

    args = parser.parse_args()

    name = args.name or manager.get_current_name()

    if name in manager:
        if args.json:
            print(json.dumps(manager[name]))
        else:
            print(name)
            pprint.pprint(manager[name])
    else:
        sys.stderr.write("Error: {} is not installed.\n".format(name))
