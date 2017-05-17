# coding: utf-8

import distutils.spawn
import glob
import os.path
import re
from subprocess import call, check_output, PIPE, Popen
import sys

root_dir = os.path.join(os.path.expanduser('~'), '.mpienv')
vers_dir = os.path.join(root_dir, 'versions')

def which(cmd):
    return os.path.realpath(distutils.spawn.find_executable(cmd))

def list_versions():
    res = []
    for ver in glob.glob(os.path.join(vers_dir, '*')):
        res.append(get_info(ver))
    return res
        
def filter_path(proj_root, paths):
    vers = glob.glob(os.path.join(proj_root, 'versions', '*'))

    llp = []

    for p in paths:
        root = re.sub(r'/(bin|lib|lib64)/?$', '', p)
        if root not in vers:
            llp.append(p)

    return llp

def get_info(prefix):
    """Obtain information of the MPI installed under prefix.
    """

    mpi_h = os.path.join(prefix, 'include', 'mpi.h')

    # Check mvapich
    ret = call(['grep', '-i', 'MVAPICH2_VERSION', '-q', mpi_h])
    if ret == 0:
        return get_info_mvapich(prefix)

    ret = call(['grep', '-i', 'OMPI_MAJOR_VERSION', '-q', mpi_h])
    if ret == 0:
        return get_info_ompi(prefix)
    
    raise RuntimeError("MPI is not installed on '{}'".format(prefix))

def get_label(prefix):
    if re.search(r'/$', prefix):
        prefix = re.sub(r'/$','',prefix)

    return os.path.split(prefix)[-1]

def is_active(prefix):
    prefix = os.path.realpath(prefix)
    shims = os.path.realpath(os.path.join(root_dir, 'shims'))

def get_info_mvapich(prefix):
    info = {}

    label = get_label(prefix)

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
    active = is_active(prefix)

    info['label'] = label
    info['type'] = 'MVAPICH'
    info['active'] = active
    info['version'] = mv_ver
    info['mpich_ver'] = mch_ver
    info['path'] = path
    info['configure'] = conf_list[0]
    info['conf_params'] = conf_list
    info['default_name'] = "mvapich-{}".format(mv_ver)

    return info

def get_info_ompi(prefix):
    info = {}
    label = get_label(prefix)

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
    active = (which('mpiexec') == mpiexec)

    if os.path.islink(prefix):
        path = os.path.realpath(prefix)
    else:path = prefix

    info['label'] = label
    info['type'] = 'Open MPI'
    info['active'] = active
    info['version'] = ver
    info['prefix'] = prefix
    info['path'] = path
    info['configure'] = ""
    info['conf_params'] = []
    info['default_name'] = "ompi-{}".format(ver)

    return info
