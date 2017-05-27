# coding: utf-8

import argparse
import json
import sys

from common import manager


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', action="store_true",
                        default=None)
    args = parser.parse_args()

    if len(manager.keys()) == 0:
        exit(0)

    max_label_len = max(len(name) for name in manager.keys())

    lst = [info for name, info in manager.items()]
    lst.sort(key=lambda x: x['name'])
    if args.json:
        lst = {name: info for name, info in manager.items()}
        json.dump(lst, sys.stdout)
    else:
        print("\nInstalled MPIs:\n")
        for info in lst:
            print(" {} {:<{width}} -> {}".format(
                "*" if info['active'] else " ",
                info['name'],
                info['path'],
                width=max_label_len))

        print()
