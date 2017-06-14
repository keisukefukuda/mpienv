# coding: utf-8

import argparse
import sys

from common import manager

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('name', nargs='?', default=None)

    args = parser.parse_args()

    name = args.name or manager.get_current_name()

    if name in manager:
        sys.stdout.write(manager[name]['prefix'])
        if sys.stdout.isatty():
            sys.stdout.write("\n")

    else:
        sys.stderr.write("Error: {} is not installed.\n".format(name))
