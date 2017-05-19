# coding: utf-8

from subprocess import call, check_output, PIPE, Popen
import distutils.spawn
import glob
import os.path
import re
import sys

root_dir = os.path.join(os.path.expanduser('~'), '.mpienv')
vers_dir = os.path.join(root_dir, 'versions')

class Manager():
    def __init__(self, root_dir):
        self._root_dir = root_dir
        self._vers_dir = os.path.join(root_dir, 'versions')

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

    if not os.path.exists(mpi_h):
        sys.stderr.write("Error: {}/include/mpi.h was not found. "
                         "MPI is not intsalled in this path or only runtime".format(
                             prefix))

    # Check MPICH
    ret = call(['grep', 'MPICH_VERSION', '-q', mpi_h])
    if ret == 0:
        return get_info_mpich(prefix)

    # Check mvapich
    ret = call(['grep', 'MVAPICH2_VERSION', '-q', mpi_h])
    if ret == 0:
        return get_info_mvapich(prefix)

    # Check Open MPI
    ret = call(['grep', 'OMPI_MAJOR_VERSION', '-q', mpi_h])
    if ret == 0:
        return get_info_ompi(prefix)
    
    raise RuntimeError("MPI is not installed on '{}'".format(prefix))

def is_active(prefix):
    prefix = os.path.realpath(prefix)
    shims = os.path.realpath(os.path.join(root_dir, 'shims'))

def get_name(path):
    if path.find(vers_dir) == 0:
        path2 = re.sub(r'/?$', '', path)
        return os.path.split(path2)[-1]
    else:
        None

def get_info_mpich(prefix):
    info = {}

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

    m = re.search(r'Version:\s+(\S+)', out, re.MULTILINE)
    ver = m.group(1)

    if os.path.islink(prefix):
        path = os.path.realpath(prefix)
    else:path = prefix

    info['type'] = 'MPICH'
    info['active'] = is_active(prefix)
    info['version'] = ver
    info['path'] = path
    info['configure'] = conf_list[0]
    info['conf_params'] = conf_list
    info['default_name'] = "mpich-{}".format(ver)
    info['name'] = get_name(prefix)

    return info

def get_info_mvapich(prefix):
    info = get_info_mpich(prefix)

    # Parse mvapich version
    mv_ver = check_output(['grep', '-E', 'define *MVAPICH2_VERSION', mpi_h],
                          encoding=sys.getdefaultencoding())
    mch_ver = check_output(['grep', '-E', 'define *MPICH_VERSION', mpi_h],
                          encoding=sys.getdefaultencoding())

    mv_ver = re.search(r'"([.0-9]+)"', mv_ver).group(1)
    mch_ver = re.search(r'"([.0-9]+)"', mch_ver).group(1)

    info['version'] = mv_ver
    info['type'] = 'MVAPICH'
    info['mpich_ver'] = mch_ver
    info['default_name'] = "mvapich-{}".format(mv_ver)

    return info

def get_info_ompi(prefix):
    info = {}

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

    if os.path.islink(prefix):
        path = os.path.realpath(prefix)
    else:path = prefix

    info['type'] = 'Open MPI'
    info['active'] = is_active(prefix)
    info['version'] = ver
    info['prefix'] = prefix
    info['path'] = path
    info['configure'] = ""
    info['conf_params'] = []
    info['default_name'] = "ompi-{}".format(ver)
    info['name'] = get_name(prefix)

    return info
