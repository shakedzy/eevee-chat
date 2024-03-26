from textwrap import dedent
from .ui import UI
from .chatbot import Chatbot
from .settings import init_settings


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
    chatbot = Chatbot({'openai'})
    with UI(chatbot):
        pass
