import sys
from argparse import ArgumentParser
from textwrap import dedent
from .ui import UI
from .chatbot import Chatbot
from .settings import init_settings
from .framework_models import get_available_frameworks


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


def main():
    ascii_art()

    parser = ArgumentParser(description="Eevee Chat run-time arguments")
    parser.add_argument('-p', '--port', dest='port', default=4242, type=int, help='Port to run from', required=False)
    args = parser.parse_args()

    init_settings(['../config.toml'])
    available_frameworks = get_available_frameworks()
    chatbot = Chatbot(available_frameworks)
    with UI(chatbot, available_frameworks, port=args.port):
        pass


if __name__ == '__main__':
    sys.exit(main())
