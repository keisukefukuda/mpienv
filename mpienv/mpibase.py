# coding: utf-8

import datetime
import distutils.spawn
import os.path
import re
import shutil
from subprocess import check_call
from subprocess import Popen
import sys  # NOQA

import mpienv
from mpienv.py import MPI4Py
import mpienv.util as util


def _which(cmd):
    exe = distutils.spawn.find_executable(cmd)
    if exe is None:
        return None

    exe = util.decode(os.path.realpath(exe))
    return exe


def _gen_temp_script_name():
    host_name = os.uname()[1]
    pid = os.getpid()
    tm = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    name = '{}.{:>05}.{}.mpienv.sh'.format(host_name, pid, tm)
    tempfile = os.path.join('/tmp', name)
    return tempfile


def _parse_hostfile(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()

    hosts = []

    for line in lines:
        line = line.strip()
        if line == '':
            continue

        # Remove comments
        line = re.sub(r'#.*$', '', line)

        # Remove options
        line = re.sub(r':.*$', '', line)

        hosts.append(line)

    return hosts


def parse_hosts(cmds):
    hosts = []

    cmds = list(cmds)

    while len(cmds) > 0:
        head = cmds.pop(0)
        if re.match(r'--?(machine|host)file$', head):
            if len(cmds) == 0:
                sys.stderr.write("mpienv: Error: "
                                 "{} needs an argument.".format(head))
                exit(1)
            file_name = cmds.pop(0)
            hosts += _parse_hostfile(file_name)
        elif head in ['-H', '-host', '--host']:
            if len(cmds) == 0:
                sys.stderr.write("mpienv: Error: "
                                 "{} needs an argument.".format(head))
                exit(1)
            hosts2 = cmds.pop(0).split(',')
            # Remote options
            hosts2 = [re.sub(':.*$', '', h) for h in hosts2]
            hosts += hosts2
        else:
            continue

    hosts = sorted(list(set(hosts)))

    if len(hosts) == 0:
        hosts = ['localhost']

    return hosts


def split_mpi_user_prog(cmds):
    """An ad-hoc parser that splits mpiexec args and user program's args"""

    opt_with_one_arg = [
        '-H', '-host', '--host',
        '-machinefile', '--machinefile',
        '-hostfile', '--hostfile',
        '-c', '-n', '--n', '-np',
        '-npersocker', '--npersocker', '-npernode', '--npernode',
        '--map-by', '--rank-by', '--bind-to',
        '-cpus-per-proc', '--cpus-per-proc',
        '-cpus-per-rank', '--cpus-per-rank',
        '-slot-list', '--slot-list',
        '-rf', '--rankfile',
        '-output-filename', '--output-filename',
        '-stdin', '--stdin',
        '-xterm', '--xterm',
        '-path', '--path',
        '--prefix',
        '--preload-files',
        '--preload-files-dest-dir',
        '--tmpdir', '-wd', '-wdir', '-x',
        '-tune', '--tune',
        '-aborted', '--aborted',
        '--app', '-cf', '--cartofile',
        '-ompi-server', '--ompi-server',
        '-report-pid', '--report-pid'
        '-report-uri', '--report-uri',
        '-server-wait-time', '--server-wait-time',

    ]

    opt_with_two_arg = [
        '--gmca', '--mca',
    ]

    idx = 0
    while True:
        if cmds[idx] in opt_with_one_arg:
            idx += 2
        elif cmds[idx] in opt_with_two_arg:
            idx += 3
        elif cmds[idx].startswith('-'):
            idx += 1
        else:
            break

    return cmds[:idx], cmds[idx:]


class MpiBase(object):
    def __init__(self, prefix, mpiexec, mpicc,
                 inc_dir, lib_dir,
                 conf, name=None):
        self._prefix = prefix
        self._mpiexec = mpiexec
        self._mpicc = mpicc
        self._inc_dir = inc_dir
        self._lib_dir = lib_dir
        self._conf = conf
        self._name = name

    def to_dict(self):
        return {
            'active': self.is_active,
            'broken': self.is_broken,
            'conf_params': self.conf_params,
            'default_name': self.default_name,
            'mpicc': self.mpicc,
            'mpicxx': self.mpicxx,
            'mpiexec': self.mpiexec,
            'prefix': self.prefix,
            'symlink': self.is_symlink,
            'type': self.type_,
            'version': self.version,
        }

    @property
    def prefix(self):
        pref = self._prefix
        if os.path.islink(pref):
            pref = os.readlink(pref)
        return pref

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def conf_params(self):
        return self._conf_params

    @property
    def conf(self):
        return self._conf

    @property
    def version(self):
        return self._version

    @property
    def default_name(self):
        return self._default_name

    @property
    def mpiexec(self):
        return self._mpiexec

    @property
    def mpicxx(self):
        return self.mpicc.replace('mpicc', 'mpicxx')

    @property
    def mpicc(self):
        return self._mpicc

    @property
    def is_symlink(self):
        if self._name is None:
            raise RuntimeError("Internal Error:"
                               "is_symlink is not allowed for "
                               "non-installed MPI")
        return os.path.join(self._conf['mpi_dir'], self.name)

    @property
    def is_active(self):
        ex1 = self.mpiexec
        ex2 = _which('mpiexec')

        if ex2 is None or not os.path.exists(ex2):
            return False

        ex1 = os.path.realpath(ex1)
        ex2 = os.path.realpath(ex2)

        return ex1 == ex2

    @property
    def is_broken(self):
        return False

    def _mirror_file(self, f, dst_dir, dst_bname=None):
        if dst_bname is None:
            dst = os.path.join(dst_dir, os.path.basename(f))
        else:
            dst = os.path.join(dst_dir, dst_bname)

        if os.path.islink(f):
            src = os.path.realpath(f)
            # sys.stderr.write("link {} -> {}\n".format(src, dst))
            os.symlink(src, dst)
        elif os.path.isdir(f):
            src = f
            # sys.stderr.write("link {} -> {}\n".format(src, dst))
            os.symlink(src, dst)
        else:
            # ordinary files
            src = f
            # sys.stderr.write("link {} -> {}\n".format(src, dst))
            os.symlink(src, dst)

    @property
    def type_(self):
        return self._type

    def bin_files(self):
        assert False, "Must be overriden"

    def inc_files(self):
        assert False, "Must be overriden"

    def lib_files(self):
        assert False, "Must be overriden"

    def libexec_files(self):
        assert False, "Must be overriden"

    def _generate_exec_script(self, file_name, cmds):
        with open(file_name, 'w') as f:
            for shell in ['/bin/bash', '/bin/ash', '/bin/sh']:
                if os.path.exists(shell):
                    f.write('#!{}\n\n'.format(shell))
                    break
            else:
                assert False

            # Write MPIENV_HOME
            f.write("export MPIENV_HOME={}\n\n".format(self.conf['root_dir']))

            # Write PATH
            path = self._generate_path()
            f.write("export PATH={}\n\n".format(':'.join(path)))

            # Write LD_LIBRARY_PATH
            ldlib = self._generate_ldlib()
            f.write("export LD_LIBRARY_PATH={}\n\n".format(':'.join(ldlib)))

            # Write PYTHONPATH
            cur_name = mpienv.mpienv.config2['DEFAULT']['active']
            py = MPI4Py(self._conf, cur_name)
            pypath = py.gen_pythonpath()
            f.write("export PYTHONPATH={}\n\n".format(':'.join(pypath)))

            # Write some extra environmental variables
            f.write("export MPIENV_MPI_TYPE=\"{}\"\n".format(self.type_))
            f.write("export MPIENV_MPI_VERSION=\"{}\"\n".format(self.version))
            f.write("export MPIENV_MPI_NAME=\"{}\"\n".format(self.name))
            f.write("\n")

            # construct the command line
            _, cmds = split_mpi_user_prog(cmds)
            cmds = mpienv.util.escape_shell_commands(cmds)
            f.write(' '.join(cmds) + "\n")

            # remove the script itself
            f.write('rm -f {}\n'.format(file_name))

        os.chmod(file_name, 0o744)

    def exec_(self, cmds, dry_run=False, verbose=False):
        # Determine the temporary shell script name
        # Determine the remote hosts
        # Transfer the shell script to remote hosts

        # We use '/tmp/%%%%.mpienv.sh as a script name
        # I think this is OK in most cases
        tempfile = _gen_temp_script_name()
        remote_hosts = parse_hosts(cmds)

        if verbose:
            print("tempfile = {}".format(tempfile))
            print("hosts = {}".format(remote_hosts))

        # Generate a proxy shell script that runs user programs
        self._generate_exec_script(tempfile, cmds)

        # Copy script file
        for host in remote_hosts:
            if host not in ['localhost', '127.0.0.1']:
                check_call(['scp', tempfile, '{}:{}'.format(host, tempfile)])

        # Run the mpiexec command
        mpi_args, user_args = split_mpi_user_prog(cmds)

        # Warn if user tries to run python program while --mpi4py is not active
        if user_args[0].startswith('python'):
            if not mpienv.mpienv.config2['DEFAULT'].getboolean('mpi4py'):
                sys.stderr.write("mpienv: Warn: It seems that you are trying"
                                 " to run a pythohn progrma, but mpi4py is not"
                                 " ")

        # Execute mpiexec
        mpiexec = self.mpiexec
        if dry_run:
            print(' '.join([mpiexec] + mpi_args + [tempfile]))
            if verbose:
                print("")
                print(tempfile)
                print("---")
                check_call(['cat', tempfile])
        else:
            sys.stdout.flush()
            sys.stderr.flush()
            os.execv(mpiexec, [mpiexec] + mpi_args + [tempfile])

    def run_cmd(self, cmd, extra_envs):
        envs = os.environ.copy()
        envs.update(extra_envs)

        ld_lib_path = "{}/lib:{}/lib64".format(self.prefix, self.prefix)

        # We need to construct LD_LIBRARY_PATH for the child mpiexec process
        # because setuid-ed programs ignore 'LD_LIBRARY_PATH'.
        if 'LD_LIBRARY_PATH' in envs:
            ld_lib_path = envs['LD_LIBRARY_PATH'] + ":" + ld_lib_path

        envs['LD_LIBRARY_PATH'] = ld_lib_path

        p = Popen(cmd, env=envs)
        p.wait()
        exit(p.returncode)

    def _generate_path(self):
        env_path = os.environ.get('PATH', '').split(':')
        # Remove all directory that contains 'mpiexec' from PATH
        bin_dir = os.path.join(self.prefix, 'bin')
        assert os.path.exists(os.path.join(bin_dir, 'mpiexec'))
        if bin_dir in env_path:
            env_path.remove(bin_dir)
        env_path = [bin_dir] + env_path

        return env_path

    def _generate_ldlib(self):
        env_ldlib = os.environ.get('LD_LIBRARY_PATH', '').split(':')

        for dir_name in ['lib', 'lib64']:
            lib_dir = os.path.join(self.prefix, dir_name)
            if os.path.exists(lib_dir):
                # Remove if lib_is already a part of LD_LIBRARY_PATH
                # to avoid LD_LIBRARY_PATH is too long.
                if lib_dir in env_ldlib:
                    env_ldlib.remove(lib_dir)
                env_ldlib = [lib_dir] + env_ldlib

        return env_ldlib

    def use(self, name, no_mpi4py=False):
        # Check if the specified `name` is the same as the current one
        try:
            cur_name = mpienv.mpienv.config2['DEFAULT']['name']
            cur_mpi4py = mpienv.mpienv.config2.getboolean('DEFAULT', 'mpi4py')
            if cur_name == name and cur_mpi4py == (not no_mpi4py):
                return
        except KeyError:
            pass

        env_path = self._generate_path()
        env_ldlib = self._generate_ldlib()

        mpienv.mpienv.config2['DEFAULT']['active'] = name
        mpienv.mpienv.config2['DEFAULT']['mpi4py'] = str(not no_mpi4py)
        mpienv.mpienv.config_save()

        print('export PATH={}'.format(':'.join(env_path)))
        print('export LD_LIBRARY_PATH={}'.format(':'.join(env_ldlib)))

        env = os.environ.copy()
        env['PATH'] = ':'.join(env_path)
        env['LD_LIBRARY_PATH'] = ':'.join(env_ldlib)

        py = MPI4Py(self._conf, name)
        if not no_mpi4py:
            if not py.is_installed():
                py.install(env)
            py.use()
        else:
            # If --mpi4py is not specified, must modify PYTHONPATH
            # to remove mismatched path to mpi4py module
            py.clear()

    def is_installed_by_mpienv(self):
        if self._name is None:
            return False
        mpi_prefix = os.path.abspath(os.path.join(self.prefix, os.pardir))
        return mpi_prefix == self._conf['mpi_dir']

    def remove(self):
        assert self._name is not None
        if self.is_installed_by_mpienv():
            shutil.rmtree(self.prefix)
        else:
            os.remove(os.path.join(self._conf['mpi_dir'], self.name))

    def describe(self):
        print("Name    : {}".format(self.name))
        print("Type    : {}".format(self.type_))
        print("Version : {}".format(self.version))
        print("Path    : {}".format(self.prefix))
        self._describe()

    def _describe(self):
        pass
