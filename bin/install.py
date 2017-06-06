# coding: utf-8

import argparse
import sys

from common import manager
from mpienv.installer import create_installer
from mpienv.installer import list_avail


def main():
    parser = argparse.ArgumentParser(description="mpienv-install")
    parser.add_argument('-n', '--name', metavar='name', dest='name',
                        default=None, type=str,
                        help='Name of an MPI installation')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        default=False, action='store_true',
                        help='Verbose')

    subcmds = parser.add_subparsers(dest='command')

    # list subcommand
    cmd_list = subcmds.add_parser('list')

    # clean subcommand
    cmd_clean = subcmds.add_parser('clean')
    cmd_clean.add_argument('mpi', type=str,
                           help='MPI name', default=None)

    # configure subcommand
    cmd_conf = subcmds.add_parser('configure')
    cmd_conf.add_argument('mpi', type=str, help='MPI name')
    cmd_conf.add_argument('conf_args', nargs=argparse.REMAINDER,
                          default=[])

    # build subcommand
    cmd_build = subcmds.add_parser('build')
    cmd_build.add_argument('-j', type=int, default=1,
                           help="Number of parallel execution")
    cmd_build.add_argument('mpi', type=str,
                          help='MPI name', default=None)
    
    args = parser.parse_args()

    inst = create_installer(manager, args.mpi, args.name,
                            verbose=args.verbose)

    if args.command == 'clean':
        inst.clean()
    elif args.command == 'configure':
        inst.configure(args.conf_args)

if __name__ == "__main__":
    main()
