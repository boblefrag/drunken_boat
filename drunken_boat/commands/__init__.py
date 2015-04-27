import sys
import os
import pkgutil
import importlib
import argparse


def find_commands(path):
    return [name for _,
            name,
            is_pkg in pkgutil.iter_modules([path])
            if not is_pkg and not name.startswith('_')and not name == "tests"]


class BaseCommand(object):
    help = "base command"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=find_commands(os.path.dirname(__file__)))

    def get_help(self):
        sys.stdout.write("{}\n".format(self.help))


class UtilCommand(object):
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
        self.commands = find_commands(os.path.dirname(__file__))

    def execute(self):
        if len(self.argv) >= 2 and self.argv[1] in self.commands:
            command = importlib.import_module(
                ".".join([self.__module__, self.argv[1]]))
            command.Command().execute(self.argv)


def run_command(argvs=None):
    command = UtilCommand(argvs)
    command.execute()
