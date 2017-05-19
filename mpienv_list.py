# coding: utf-8

import glob
import os
import os.path
import pprint

from common import manager

if __name__ == '__main__':
    max_label_len = max(len(name) for name in manager.keys())

    print("\nInstalled MPIs:\n")
    for name, info in manager.items():
        print(" {} {:<{width}} -> {}".format(
            "*" if info['active'] else " ",
            info['name'],
            info['path'],
            width=max_label_len))

    print()
        
