# coding: utf-8

import argparse
import json
import pprint
import sys

from mpienv import mpienv
from mpienv import UnknownMPI
from mpienv import util

parser = argparse.ArgumentParser(
    prog='mpienv info',
    description='Show information of current MPI environment.')
parser.add_argument('--json', action="store_true", default=None)
parser.add_argument('name', nargs='?', default=None)

if __name__ == "__main__":

    args = parser.parse_args()

    try:
        name = mpienv.get_current_name()
    except UnknownMPI:
        sys.stderr.write("Error: the current MPI is not under control\n")
        exit(-1)

    name = args.name or name

    if name not in mpienv:
        sys.stderr.write("Error: '{}' is unknown.\n".format(name))
    else:
        if args.json:
            print(json.dumps(mpienv[name], default=util.dump_json))
        else:
            print(name)
            pprint.pprint(mpienv[name])
