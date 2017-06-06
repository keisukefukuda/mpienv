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
    parser.add_argument('--list', action="store_true", default=False,
                        help='List all available MPIs')
    parser.add_argument('--clean', action="store_true", default=False,
                        help='Clean build/download cache')
    parser.add_argument('--configure', action="store_true", default=False,
                        help='Run configure script only')
    parser.add_argument('--build', action='store_true', default=False,
                        help='Only build the MPI')
    parser.add_argument('command', type=str, help='Command')
    parser.add_argument('mpi', type=str, nargs='?',
                        help='MPI name', default=None)
    parser.add_argument('conf_args', nargs=argparse.REMAINDER)

    args = parser.parse_args()

    # Create a link
    if args.command == 'list':
        if any([args.clean, args.configure, args.build, args.mpi]):
            sys.stderr.write("Error: --list and other arguments "
                             "cannot specified together.\n")
            exit(1)

        list_avail()
        exit(0)

    if args.mpi is None:
        sys.stderr.write("Error: MPI name must be specified.\n")
        exit(1)

    name = args.name if args.name else args.mpi

    inst = create_installer(manager, args.mpi, name, args.conf_args)

    if args.command == 'clean':
        if any([args.configure, args.build]):
            sys.stderr.write("Error: --clean and other arguments "
                             "cannot specified together.\n")
            exit(1)

        inst.clean()
    elif args.command == 'configure':
        inst.download()
        inst.configure()
    elif args.command == 'build':
        inst.download()
        inst.configure()
        inst.build()
    elif args.command == 'install':
        inst.download()
        inst.configure()
        inst.build()
        inst.install()
    else:
        raise RuntimeError('Unknown command')


if __name__ == "__main__":
    main()
