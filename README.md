[![Build Status](https://travis-ci.org/keisukefukuda/mpienv.svg?branch=master)](https://travis-ci.org/keisukefukuda/mpienv)
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

# mpienv
MPI environment selector for Pythonisa

## Background and motivation

Managing multiple MPI installations is hard. It's even harder if you use MPI through Python.

### Environmental setting over SSH (non-interactive sessions)

As often asked on Stack Overflow (such as [this question](https://unix.stackexchange.com/questions/170493/login-non-login-and-interactive-non-interactive-shells)),
setting environmental variables on remote hosts are sometimes hard, in particular on Ubuntu 
platforms.

### MPI and mpi4py

When you have multiple MPI installations, it is time-consuming and error-prone situation.
To switch the active MPI, it is not enough to modify `PATH` and `LD_LIBRARY_PATH`.
It is because the `mpi4py` library binary, namely `MPI.so`, is linked to the previous MPI
installation.

To properly switch the MPI installation, you need to reinstall `mpi4py` everytime you
switch MPI.

```
$ pip uninstall -y mpi4py
$ pip install mpi4py --no-cache-dir
``` 

Mpienv is designed to avoid such issues and provide a smooth workflow to work on multiple
Python and MPI combinations.


## Installation

First, install mpienv via `pip`

```bash
$ pip install mpienv
```

## How to start

After installing, insert the following line into your `.bashrc` or any other initialization shell script.
```
$ eval "$(mpienv-init)"
```

OK, let's see what `mpienv` does.

```bash
$ mpienv list

# no output
```

The `list` command prints a list of MPI instances. As of now, there
should be no output from the command because `mpienv` has no
information about your system. Let's find MPI libraries on your system
by hitting:

The `autodiscover` command will traverse the directories of you system
and find all installed MPI libraries. The output would look like the
following (it would take some time):

```bash
$ mpienv autodiscover

$ mpienv autodiscover /usr/local/Cellar

--------------------------------------
Found /usr/local/Cellar/mpich/3.3/bin/mpiexec
Type    : MPICH
Version : 3.3
Path    : /usr/local/Cellar/mpich/3.3

# (...snip...)
```

The command searches several possible locations on your system.  If
you have any idea of location where MPIs are installed, you can
specify them to save time:

```bash
$ mpienv autodiscover path1 path2 ...
```

After you find MPI installations on your system, you can register them
using `mpienv add` command.

```bash
$ mpienv add /opt/local
```

Let's check if the MPI is added properly:

```bash
$ mpienv list

Installed MPIs:

   mpich-3.3a1 -> /opt/local

```

If you are too lazy to add all the found MPIs manually, you can just use

```bash
$ mpienv autodiscover [--add|-a]
```

This command automatically `add`s all the MPI installations.

## Activating an MPI

Let's assume your `mpienv list` shows the folloing:

```bash
$ mpienv list
Installed MPIs:

   mpich-3.2     -> /Users/keisukefukuda/mpi/mpich-3.2
   mpich-3.3a1   -> /opt/local
 * openmpi-2.1.1 -> /Users/keisukefukuda/mpi/openmpi-2.1.1
```

The `*` mark indicates that the MPI `openmpi-2.1.1` is active, which
means it's on the `PATH` and `LD_LIBRARYPATH` environment variables.
You can check that `openmpi-2.1.1` is active.

```bash
$ mpiexec --version
mpiexec (OpenRTE) 2.1.1

Report bugs to http://www.open-mpi.org/community/help/

```

You can switch the active MPI using `use` command.

```bash
$ mpienv use mpich-3.2
$ mpienv list

Installed MPIs:

 * mpich-3.2     -> /Users/keisukefukuda/mpi/mpich-3.2
   mpich-3.3a1   -> /opt/local
   openmpi-2.1.1 -> /Users/keisukefukuda/mpi/openmpi-2.1.1

$ mpiexec --version
HYDRA build details:
    Version:                                 3.2
    Release Date:                            Wed Nov 11 22:06:48 CST 2015
    CC:                              gcc
    CXX:                             g++
    F77:
    F90:
    Configure options:  
    # (snip)
    Process Manager:                         pmi
    Launchers available:                     ssh rsh fork slurm ll lsf sge manual persist
    Topology libraries available:            hwloc
    Resource management kernels available:   user slurm ll lsf sge pbs cobalt
    Checkpointing libraries available:
    Demux engines available:                 poll select
```

"mpich-3.2" is now active. 

## Running MPI applications
To run your MPI application, you need to specify a few options to the `mpiexec` command.

```bash
$ # If you use Open MPI
$ mpienv list

Installed MPIs:

  mvapich2-2.2  -> /usr/local
  openmpi-1.6.5 -> /usr
* openmpi-2.1.1 -> /home/kfukuda/mpi/openmpi-2.1.1

$ mpienv exec -n ${NP} --hostfile ${HOSTFILE} ./your.app
```

```bash
$ # If you use MPICH/MVAPICH
$ mpienv list

Installed MPIs:

* mvapich2-2.2  -> /usr/local
  openmpi-1.6.5 -> /usr
  openmpi-2.1.1 -> /home/kfukuda/mpi/openmpi-2.1.1

$ mpienv exec --genvall -n ${NP} --hostfile ${HOSTFILE} ./your.app
```

If you are curious about what `mpienv exec` does, try `--dry-run`. 
It shows the command to execute and the content of a generated helper shell script.
 
```
$ mpienv exec --dry-run -n 2 hostname
mpienv exec: INFO: tempfile = /tmp/KeisukenoMacBook-Pro.local.50192.20190430150049.mpienv.sh
mpienv exec: INFO: hosts = ['localhost']
/usr/local/Cellar/mpich/3.3/bin/mpiexec -n 2 /tmp/KeisukenoMacBook-Pro.local.50192.20190430150049.mpienv.sh

/tmp/KeisukenoMacBook-Pro.local.50192.20190430150049.mpienv.sh
---
#!/bin/bash

export MPIENV_HOME=/Users/keisukefukuda/.mpienv

export PATH=/usr/local/Cellar/mpich/3.3/bin:/Users/keisukefukuda/.cargo/bin:/Users/keisukefukuda/local/bin:/Users/keisukefukuda/.pyenv/shims:/Users/keisukefukuda/.pyenv/bin:/Users/keisukefukuda/.cargo/bin:/usr/local/bin:/Users/keisukefukuda/lcoal/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/X11/bin:/Library/Frameworks/Mono.framework/Versions/Current/Commands:/Library/TeX/texbin

export LD_LIBRARY_PATH=/usr/local/Cellar/mpich/3.3/lib:

export PYTHONPATH=/Users/keisukefukuda/.mpienv/versions/pylib/Users_keisukefukuda_.pyenv_versions_3.6.1_bin_python3.6/mpich-3.3:

export MPIENV_MPI_TYPE="MPICH"
export MPIENV_MPI_VERSION="3.3"
export MPIENV_MPI_NAME="mpich-3.3"

hostname
 
``` 

Of course, you can use `mpiexec` as usual.

## Using Python together

If you use MPI with Python and want to swtich multiple MPI
installations, what annoys you is that `mpi4py` is tied to a single
MPI instance when it is compiled and installed. This means that you
have to do

```bash
$ pip uninstall mpi4py

$ # switch MPI

$ pip install mpi4py --no-cache
```

every time you swtich to another MPI.

`mpienv` supports this use case.

```bash
$ mpienv use --mpi4py openmpi-2.1.1
```

This command installs an `mpi4py` instance on a specific location
using `pip`'s `-t` option, and set `PYTHONPATH` environment variable
to activate it.

```bash
# Now openmpi-2.1.1 is active
$ mpienv use mpich-3.2
$ mpiexec -n 2 python -c "from mpi4py import MPI; print(MPI.COMM_WORLD.Get_rank())"

### Error!

$ mpienv use --mpi4py mpich-3.2
$ mpiexec -n 2 python -c "from mpi4py import MPI; print(MPI.COMM_WORLD.Get_rank())"
0
1
```

OK, now your `mpi4py` is properly set up. To run Python script on multiple nodes,
you need to pass an additional environment variable `PYTHONPATH`.

```bash
$ # Open MPI
$ mpiexec --prefix /home/kfukuda/mpi/openmpi-2.1.1 -x PYTHONPATH -n ${NP} --hostfile ${HOSTFILE} ./your.app

$ # MPICH/MVAPICH
$ mpiexec --genvall -n ${NP} --hostfile ${HOSTFILE} ./your.app
```
