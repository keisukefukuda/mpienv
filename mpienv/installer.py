# coding: utf-8

import os
import os.path
import re
import shutil
import sys

_list = {
    'openmpi-1.10.7': {
    },
    'openmpi-2.0.3': {
    },
    'openmpi-2.1.1': {
    },
}


class BaseInstaller(object):
    def __init__(self, manager, mpi, name, config_args):
        self.manager = manager
        self.url = _list[mpi]
        self.name = name
        self.config_args = config_args

        # Downloaded file name
        self.local_file = os.path.join(self.manager.cache_dir(),
                                       os.path.basename(self.url))
        # build directory name
        dir_bname = re.sub(r'(tar\.(gz|bz2))|(\.tgz)$',
                           os.path.basename(self.url))

        self.dir_path = os.path.join(self.manager.build_dir(),
                                     dir_bname)

    def clear(self):
        if os.path.exists(self.local_file):
            os.remove(self.local_file)

        if os.path.exists(self.dir_path):
            shutil.rmtree(self.dir_path)

    def clean(self):
        pass

    def download(self):
        pass

    def configure(self):
        pass

    def build(self):
        pass

    def install(self):
        pass


class OmpiInstaller(BaseInstaller):
    def __init__(self, *args):
        BaseInstaller.__init__(self, *args)


class MpichInstaller(BaseInstaller):
    def __init__(self, *args):
        BaseInstaller.__init__(self, *args)


class MvapichInstaller(BaseInstaller):
    def __init__(self, *args):
        BaseInstaller.__init__(self, *args)


def list_avail():
    for k in _list:
        print(k)


def create_installer(manager, mpi_type, name, conf_args=[]):

    if mpi_type not in _list.keys():
        sys.stderr.write("Error: Unknown MPI: '{}'\n".format(mpi_type))
        exit(-1)

    mpi = _list[mpi_type]['type']
    ver = _list[mpi_type]['ver']

    if mpi == 'openmpi':
        return OmpiInstaller(manager, ver, name, conf_args)
    elif mpi == 'mvapich':
        return MvapichInstaller(manager, ver, name, conf_args)
    elif mpi == 'mpich':
        return MpichInstaller(manager, ver, name, conf_args)

    raise RuntimeError("")
