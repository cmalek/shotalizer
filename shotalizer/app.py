import logging
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

from shotalizer import __version__


class ShotalizerApp(App):

    log = logging.getLogger(__name__)

    def __init__(self):
        super(ShotalizerApp, self).__init__(
            description='Generate random crops from a set of images',
            version=__version__,
            command_manager=CommandManager('shotalizer.main'),
        )

    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)
            return 1


def main(argv=sys.argv[1:]):
    app = ShotalizerApp()
    return app.run(argv)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
