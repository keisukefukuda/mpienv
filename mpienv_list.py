# coding: utf-8

import glob
import os
import os.path

from common import print_info

root_dir = os.path.join(os.path.expanduser('~'), '.mpienv')
vers_dir = os.path.join(root_dir, 'versions')

def list_versions():
    for ver in glob.glob(os.path.join(vers_dir, '*')):
        name = os.path.split(ver)[1]
        print_info(ver, name,
                   verbose = False,
                   active_flag = True)

if __name__ == '__main__':
    list_versions()
    
        
