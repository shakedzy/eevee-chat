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


def run():
    ascii_art()
    init_settings(['config.toml'])
    available_frameworks = get_available_frameworks()
    chatbot = Chatbot(available_frameworks)
    with UI(chatbot, available_frameworks):
        pass
