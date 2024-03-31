import sys
from argparse import ArgumentParser
from textwrap import dedent
from . import __version__
from .ui import UI
from .chatbot import Chatbot
from .settings import init_settings
from .framework_models import get_available_frameworks
from .color_logger import get_logger, change_default_log_level


def ascii_art():
    art = dedent(
        """
                                     
        ,------.                              
        |  .---' ,---.,--.  ,--.,---.  ,---.  
        |  `--, | .-. :\  `'  /| .-. :| .-. : 
        |  `---.\   --. \    / \   --.\   --. 
        `------' `----'  `--'   `----' `----'                                

        """)
    print(art)


def _validate_log_level(level: str) -> bool:
    return level.upper() in ['DEBUG', 'INFO', 'WARN', 'WARNING', 'ERROR', 'CRITICAL']


def main():
    parser = ArgumentParser(description="Eevee Chat run-time arguments")
    parser.add_argument('-p', '--port', dest='port', default=4242, type=int, help='Port to run from')
    parser.add_argument('-l', '--log-level', default='INFO', dest='log', help='Set logging level', type=str)
    parser.add_argument('--version', help='Show version', dest='show_version', default=False, action='store_true')
    args = parser.parse_args()

    if not _validate_log_level(args.log):
        raise ValueError(f'Invalid log level {args.log}')

    if args.show_version:
        print(f"Eevee Chat version: {__version__}")

    else:
        ascii_art()
        change_default_log_level(args.log.upper())
        get_logger().info(f"Running version: {__version__}")
        init_settings(['../config.toml'])
        available_frameworks = get_available_frameworks()
        chatbot = Chatbot(available_frameworks)
        with UI(chatbot, available_frameworks, port=args.port):
            pass


if __name__ == '__main__':
    sys.exit(main())
