from cliff.command import Command
from cliff.lister import Lister


class BaseCommand(Command):
    "Base command class, adding some typical arguments"

    def get_parser(self, prog_name):
        parser = super(BaseCommand, self).get_parser(prog_name)
        parser.add_argument('--cropdir', default=".crops", help="directory to which to write crops")
        return parser


class BaseLister(Lister):
    "Base Lister class, adding some typical arguments"

    def get_parser(self, prog_name):
        parser = super(BaseLister, self).get_parser(prog_name)
        return parser
