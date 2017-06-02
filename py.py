# coding: utf-8

from __future__ import print_function
import glob
import os
import os.path
import platform
import shutil
from subprocess import check_call
from subprocess import check_output
import sys


class PyLib(object):
    def __init__(self, root_dir):
        self._root_dir = root_dir
        lib = self._find_mpi4py_lib()
        if lib:
            self._lib = os.path.abspath(lib)
        else:
            self._lib = None

    def _find_mpi4py_lib(self):
        libs = set()
        for p in sys.path:
            if os.path.isdir(p):
                out = check_output(['find', p,
                                    '-type', 'f',
                                    '-name', '*MPI*.so'])
                if type(out) == bytes:
                    out = out.decode(sys.getdefaultencoding())
                lines = [ln.strip() for ln in out.split("\n")
                         if len(ln) > 0]
                for ln in lines:
                    libs.add(ln)

        if len(libs) > 1:
            sys.stderr.write("Warning: multiple MPI.so found:"
                             " {}".format(libs))

        if len(libs) == 0:
            return None
        else:
            return libs.pop()

    def is_mpi4py_installed(self):
        return (self._lib is None)

    def is_mpi4py_controled(self):
        if self._lib is None:
            return False
        else:
            return self._lib.find(self._root_dir) == 0

    def use(self, name):
        print("self._lib = {}".format(self._lib))
        if self._lib is not None:
            if self._lib.find(self._root_dir) == -1:
                sys.stderr.write("Error: mpi4py is installed but "
                                 "it's not under control of mpienv."
                                 "Please uninstall mpi4py first")
                exit(-1)

            # Remove mpi4py directory from the path
            # This should just remove the symlink to our mpi4py installation
            if self._lib is not None:
                mpi4py_dir = os.path.realpath(os.path.dirname(self._lib))
                print(mpi4py_dir)
                print("Removing {}".format(self._lib))
                cur_name = os.path.basename(mpi4py_dir)
                print("current name = {}".format(name))
                if name != cur_name:
                    check_call(['pip', 'uninstall', '-y', 'mpi4py'])

        # Check if `name` is installed
        if not self.installed(name):
            self.install(name)

        # Actually swich
        
        

    def installed(self, name):
        d = os.path.join(self._root_dir, 'pylibs', name)
        return os.path.exists(d)

    def install(self, name):
        env = os.environ.copy()
        pref = os.path.join(self._root_dir, 'versions', name)
        env['PATH'] = os.path.join(pref, 'bin') + ":" + env['PATH']
        env['LD_LIBRARY_PATH'] = os.path.join(pref, 'lib') + ":" + env['LD_LIBRARY_PATH']

        check_call(['pip', 'install', 'mpi4py', '--no-cache'],
                   env=env)

        lib = self._find_mpi4py_lib()
        mpi4py_dir = os.path.dirname(lib)
        pkg_dir = os.path.abspath(os.path.join(mpi4py_dir, os.pardir))
        print(lib)
        print(mpi4py_dir)
        print(pkg_dir)

        pylibs = os.path.join(self._root_dir, 'pylibs')
        d = os.path.join(pylibs, name)
        shutil.move(mpi4py_dir, d)

        egginfo = glob.glob(os.path.join(pkg_dir, 'mpi4py-*.egg-info'))[0]
        egginfo2 = os.path.join(pylibs, os.path.basename(egginfo))
        if not os.path.exists(egginfo2):
            print("Moving {} -> {}".format(egginfo, egginfo2))
            shutil.move(egginfo, egginfo2)
        else:
            print("Removing {} -> {}".format(egginfo))
            shutil.rmtree(egginfo)

    def _call_otool(self):
        pass

    def _call_ldd(self):
        print(self._lib)

    def get_mpi_prefix(self):
        plt = platform.platform()
        if plt.find('Darwin') >= 0:
            # Mac OS. We use 'otool -L' to find linked libraries
            self._call_otool()
        elif plt.find('Linux') >= 0:
            self._call_ldd()
        else:
            sys.stderr.write("The platform is not "
                             "Linux nor MacOS. Unsupported.\n")
            exit(-1)
