# coding: utf-8

import os
import os.path
import re
import sys
import pprint

from common import manager

if __name__ == "__main__":
    if len(sys.argv) == 1:
        name = manager.get_current_name()
    else:
        name = sys.argv[1]

    if name in manager:
        print(name)
        pprint.pprint(manager[name])
    else:
        sys.stderr.write("Error: {} is not installed.\n".format(name))
