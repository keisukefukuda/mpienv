# coding: utf-8

import argparse
import glob
import importlib
import os


def _get_command_description(command):
    mod = importlib.import_module(command)
    return mod.parser.description


class MpienvHelpFormatter(argparse.HelpFormatter):
    def _format_command(self, *name):
        command = ''.join(name)
        return '  {:<15} {}\n'.format(
            command, _get_command_description(command))

    def add_command(self, command):
        self._add_item(self._format_command, command)


class MpienvHelpArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(
            MpienvHelpArgumentParser,
            self).__init__(
            *args,
            formatter_class=MpienvHelpFormatter,
            **kwargs)

    def format_help(self):
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # commands
        formatter.start_section('Commands')
        for path in glob.glob(os.path.join(os.path.dirname(__file__), '*.py')):
            command, _ = os.path.splitext(os.path.basename(path))
            formatter.add_command(command)
        formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()


parser = MpienvHelpArgumentParser(
    usage='mpienv <command> [<args>]',
    description='Show this help message.',
    epilog="""
See 'mpienv help <command>' for information on a specific command.
""")
parser.add_argument('command', type=str, default=None, nargs='?',
                    help='mpienv command name')


if __name__ == '__main__':
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
    else:
        try:
            command = "mpienv.command.{}".format(args.command)
            print("command = {}".format(command))
            mod = importlib.import_module(command)
            mod.parser.print_help()
        except BaseException:
            print('mpienv: no such command {}'.format(args.command))
