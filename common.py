# coding: utf-8

import distutils.spawn
import glob
import os.path
import re
from subprocess import call, check_output, PIPE, Popen
import sys

def which(cmd):
    return os.path.realpath(distutils.spawn.find_executable(cmd))

def filter_path(proj_root, paths):
    vers = glob.glob(os.path.join(proj_root, 'versions', '*'))

    llp = []

    for p in paths:
        root = re.sub(r'/(bin|lib|lib64)/?$', '', p)
        if root not in vers:
            llp.append(p)

    return llp

def print_info(prefix, name, verbose=True, active_flag=False):
    """Obtain information of the MPI installed under prefix.
    """

    mpi_h = os.path.join(prefix, 'include', 'mpi.h')

    # Check mvapich
    ret = call(['grep', '-i', 'MVAPICH2_VERSION', '-q', mpi_h])
    if ret == 0:
        return print_info_mvapich(prefix, name, verbose, active_flag)

    ret = call(['grep', '-i', 'OMPI_MAJOR_VERSION', '-q', mpi_h])
    if ret == 0:
        return print_info_ompi(prefix, name, verbose, active_flag)
    
    raise RuntimeError("Unknown")

def print_info_mvapich(prefix, name, verbose, active_flag):
    # Get the Mvapich version
    mpi_h = os.path.join(prefix, 'include', 'mpi.h')

    # Parse mvapich version
    mv_ver = check_output(['grep', '-E', 'define *MVAPICH2_VERSION', mpi_h],
                          encoding=sys.getdefaultencoding())
    mch_ver = check_output(['grep', '-E', 'define *MPICH_VERSION', mpi_h],
                          encoding=sys.getdefaultencoding())

    mv_ver = re.search(r'"([.0-9]+)"', mv_ver).group(1)
    mch_ver = re.search(r'"([.0-9]+)"', mch_ver).group(1)

    # Run mpiexec --version and extract some information
    mpiexec = os.path.join(prefix, 'bin', 'mpiexec')
    out = check_output([mpiexec, '--version'],
                       encoding=sys.getdefaultencoding())

    # Parse 'Configure options' section
    # Config options are like this:
    # '--disable-option-checking' '--prefix=NONE' '--enable-cuda' '--disable-fortran' '--cache-file=/dev/null'
    m = re.search(r'Configure options:\s+(.*)$', out, re.MULTILINE)
    conf_str = m.group(1)
    conf_list = [s.replace("'",'') for s in re.findall(r'\'[^\']+\'', conf_str)]

    if os.path.islink(prefix):
        path = os.path.realpath(prefix)
    else:path = prefix
    
    # Check if it's active
    mpiexec = os.path.realpath(os.path.join(prefix, 'bin', 'mpiexec'))
    if which('mpiexec') == mpiexec:
        active = "*"
    else:
        active = " "
        
    # Print the result
    if name is None:
        print(" {} MVAPICH on {}".format(active, prefix))
    else:
        print(" {} {}".format(active, name))

    if verbose:
        print("\tType:              MVAPICH")
        print("\tVersion:           {}".format(mv_ver))
        print("\tMPICH Version:     {}".format(mch_ver))
        print("\tLocation:          {}".format(path))
        print("\tConfigure options: {}".format(conf_list[0]))
        for conf in conf_list[1:]:
            print("\t                   {}".format(conf))
    

def print_info_ompi(prefix, name, verbose, active_flag):
    # Get the Open MPI version
    mpi_h = os.path.join(prefix, 'include', 'mpi.h')

    major_s = check_output(['grep', '-E', 'define OMPI_MAJOR_VERSION', mpi_h],
                           encoding=sys.getdefaultencoding())
    minor_s = check_output(['grep', '-E', 'define OMPI_MINOR_VERSION', mpi_h],
                           encoding=sys.getdefaultencoding())
    rel_s = check_output(['grep', '-E', 'define OMPI_RELEASE_VERSION', mpi_h],
                           encoding=sys.getdefaultencoding())

    major = re.search(r'\d+', major_s).group(0)
    minor = re.search(r'\d+', minor_s).group(0)
    rel = re.search(r'\d+', rel_s).group(0)

    ver = "{}.{}.{}".format(major, minor, rel)

    # Check if it's active
    mpiexec = os.path.realpath(os.path.join(prefix, 'bin', 'mpiexec'))
    if which('mpiexec') == mpiexec:
        active = "*"
    else:
        active = " "
        
    if name is None:
        print(" {} Open MPI on {}".format(active, prefix))
    else:
        print(" {} {}".format(active, name))

    if verbose:
        print("\tType:              MVAPICH")
        print("\tVersion:           {}".format(ver))
        print("\tLocation:          {}".format(path))
