[![Build Status](https://travis-ci.org/keisukefukuda/mpienv.svg?branch=master)](https://travis-ci.org/keisukefukuda/mpienv)
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![Code Climate](https://codeclimate.com/github/keisukefukuda/mpienv/badges/gpa.svg)](https://codeclimate.com/github/keisukefukuda/mpienv)
[![Test Coverage](https://codeclimate.com/github/keisukefukuda/mpienv/badges/coverage.svg)](https://codeclimate.com/github//keisukefukuda/mpienv)
[![Issue Count](https://codeclimate.com/github/keisukefukuda/mpienv/badges/issue_count.svg)](https://codeclimate.com/github/keisukefukuda/mpienv)

# mpienv
MPI environment selector, like pyenv or rbenv. 

## Installation

    $ cd $HOME
    $ git clone https://github.com/keisukefukuda/mpienv.git .mpienv
    

## How to start using

First, you need to load the `mpienv` tool into your shell environment.

    $ . ~/.mpienv/init
    
If you downloaded `mpienv` to a different location, just replace the path.

    $ . ${YOUR_MPIENV_DIRECTORY}/init
    
OK, let's see what `mpienv` does.

    $ mpienv list
    
    # no output

The `list` command prints a list of MPI instances. As of now, there
should be no output from the command because `mpienv` has no
information about your system. Let's find MPI libraries on your system
by hitting:

The `autodiscover` command will traverse the directories of you system
and find all installed MPI libraries. The output would look like the
following (it would take some time):

    $ mpienv autodiscover
    
    --------------------------------------
    Found /opt/local/bin/mpiexec
    {'active': False,
    (...snip...)
    'mpicc': '/opt/local/bin/mpicc-mpich-devel-clang39',
    'mpicxx': '/opt/local/bin/mpicxx-mpich-devel-clang39',
    'mpiexec': '/opt/local/bin/mpiexec.hydra-mpich-devel-clang39',
    'path': '/opt/local',
    'type': 'MPICH',
    'version': u'3.3a1'}
    --------------------------------------
    Found /Users/keisukefukuda/.mpienv/shims/bin/mpiexec

    (...snip...)

The command searches several possible locations on your system.  If
you have any idea of location where MPIs are installed, you can
specify them to save time:

    $ mpienv autodiscover path1 path2 ...
    
After you find MPI installations on your system, you can register them
using `mpienv add` command.

    $ mpienv add /opt/local/bin
    
Let's check if the MPI is added properly:

    $ mpienv list
    
    Installed MPIs:

       mpich-3.3a1 -> /opt/local

If you are too lazy to add all the found MPIs manually, you can just use

    $ mpienv autodiscover --add

This command automatically `add`s all the MPI installations.

## Activating an MPI

Let's assume your `mpienv list` shows the folloing:

    $ mpienv list
    Installed MPIs:

       mpich-3.2     -> /Users/keisukefukuda/mpi/mpich-3.2
       mpich-3.3a1   -> /opt/local
     * openmpi-2.1.1 -> /Users/keisukefukuda/mpi/openmpi-2.1.1
     

The '*' mark indicates that the MPI "openmpi-2.1.1" is active, which
means it's on the `$PATH` and `$LD_LIBRARYPATH` environment variables.
You can check that `openmpi-2.1.1` is active.

    $ mpiexec --version
    mpiexec (OpenRTE) 2.1.1

    Report bugs to http://www.open-mpi.org/community/help/

You can switch the active MPI by

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
        Configure options:  (snip)
        Process Manager:                         pmi
        Launchers available:                     ssh rsh fork slurm ll lsf sge manual persist
        Topology libraries available:            hwloc
        Resource management kernels available:   user slurm ll lsf sge pbs cobalt
        Checkpointing libraries available:
        Demux engines available:                 poll select
       
Now the specified "mpich-3.2" is active. 

## Using Python together

If you use MPI with Python and want to swtich multiple MPI
installations, what annoys you is that `mpi4py` is tied to a single
MPI when it is compiled and installed. This means that you have to do

    $ pip uninstall mpi4py
    
    $ # switch MPI
    
    $ pip install mpi4py --no-cache
    
every time you swtich to another MPI.

`mpienv` supports this use case.

    $ mpienv use --mpi4py openmpi-2.1.1
    
This command installs an `mpi4py` instance on a specific location
using `pip`'s `-t` option, and set `PYTHONPATH` environment variable
to activate it.

    # Now openmpi-2.1.1 is active
    $ mpienv use mpich-3.2
    $ mpiexec -n 2 python -c "from mpi4py import MPI; print(MPI.COMM_WORLD.Get_rank())"
    
    ### Error!
    
    $ mpienv use --mpi4py mpich-3.2
    $ mpiexec -n 2 python -c "from mpi4py import MPI; print(MPI.COMM_WORLD.Get_rank())"
    0
    1


