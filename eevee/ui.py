import os
import pathlib
import gradio as gr
from datetime import datetime
from typing import List, Tuple, Generator, Set, Tuple
from .saved_chat import SavedChat
from .chatbot import Chatbot
from .settings import Settings
from .utils import path_to_resource
from ._types import Framework


class UI:
    CHAT_FILE_TIME_FORMAT = "%d/%m/%Y"

    def __init__(self, chatbot: Chatbot, available_frameworks: Set[Framework]) -> None:
        self.ui: gr.Blocks | None = None
        self.chatbot = chatbot
        self.available_frameworks = available_frameworks
        self._generate_text = True

    def __enter__(self) -> gr.Blocks:
        self.ui = self._build_ui()
        self.ui.launch(favicon_path=path_to_resource("eevee_50.png"), inbrowser=True, show_error=True)
        return self.ui

    def __exit__(self, *args) -> None:
        if self.ui:
            self.ui.close()

    def _get_list_of_models(self) -> List[str]:
        available_models: List[str] = list()
        for framework in self.available_frameworks:
            models: List[str] = Settings().models[framework]
            available_models += models
        return available_models
    
    def _stop_text_generation(self) -> None:
        self._generate_text = False

    def _add_user_message_to_chat(self, prompt: str, history: List[List[str | None]]) -> Tuple[str, List[List[str | None]]]:
        return '', history + [[prompt, None]]

    def _add_bot_message_to_chat(self, history: List[List[str | None]], model: str, temperature: float, as_json: bool, system_prompt: str) -> Generator:
        self._generate_text = True
        if as_json:
            generator = self.chatbot.get_json_response(history[-1][0] or '', system_prompt=system_prompt, model=model, temperature=temperature)
        else:
            generator = self.chatbot.get_stream_response(history[-1][0] or '', system_prompt=system_prompt, model=model, temperature=temperature)
        
        for chunk in generator:
            if not self._generate_text:
                break
            if chunk.startswith(self.chatbot.INFO_TOKEN):
                gr.Info(chunk.strip(self.chatbot.INFO_TOKEN))
            elif chunk.startswith(self.chatbot.WARNING_TOKEN):
                gr.Warning(chunk.strip(self.chatbot.WARNING_TOKEN))
            else:
                model_name_separator = "\n\n---\n"
                chunk, model = chunk.split(self.chatbot.METADATA_TOKEN, 1)
                current_message: str = history[-1][1] or ''
                current_message = model_name_separator.join(current_message.split(model_name_separator)[:-1])
                current_message += chunk
                current_message += f'{model_name_separator}_{model}_'
                history[-1][1] = current_message
                yield history 

    def _undo_last_message(self, history: List[List[str]]) -> List[List[str]]:
        self._generate_text = False
        history.pop()
        self.chatbot.delete_last_interaction()
        return history

    def _start_new_chat(self) -> Tuple[str, List]:
        self._generate_text = False
        self.chatbot.reset_chat()
        return '', []

    def _title_and_time_to_chat_display_name(self, title: str, time: datetime) -> str:
        return f'{title} ({time.strftime(self.CHAT_FILE_TIME_FORMAT)})'

    def _display_name_to_title_and_time(self, display_name: str) -> Tuple[str, datetime]:
        pieces = display_name.split(' (')
        title = ' ('.join(pieces[:-1])
        time = datetime.strptime(pieces[-1], self.CHAT_FILE_TIME_FORMAT)
        return title, time

    def _save_chat(self) -> None:
        self.chatbot.export_chat()

    def _load_chat(self, display_name: str) -> Tuple[None, List[List[str]]]:
        history: List[List[str]] = list()
        title, start_time = self._display_name_to_title_and_time(display_name)
        self.chatbot.load_chat(title, start_time)
        messages = self.chatbot.get_displayed_messages()
        for message in messages:
            if message.role == 'user':
                history.append([message.content or '', ''])
            elif message.role == 'assistant':
                history[-1][1] = message.content or ''
            else:
                raise ValueError(f"Can't load message with role {message.role}")
        return None, history
    
    def _delete_chat_file(self, display_name: str) -> None:
        title, start_time = self._display_name_to_title_and_time(display_name)
        filename = SavedChat.title_and_time_to_filename(title, start_time)
        file_path = os.path.join(self.chatbot.saved_chats_dir, filename)
        pathlib.Path.unlink(file_path)  # type: ignore

    def _list_saved_chats(self) -> List[str]:
        saved_chats = self.chatbot.list_saved_chats()
        return [self._title_and_time_to_chat_display_name(title, time) for (title, time) in saved_chats]

    def _build_ui(self) -> gr.Blocks:
        scrollable_checkbox_group_css = """
            .files_list {
                height: 35vh;
                min-height: 150px;
                width: 100%;
                overflow-x: auto !important;
                overflow-y: auto !important;
                scrollbar-width: thin !important;
            }  
        """
        available_models = self._get_list_of_models()
        preferred_model = Settings().defaults.model
        if preferred_model not in available_models:
            preferred_model = available_models[0]
        preferred_temperature = min(1., max(0., Settings().defaults.temperature))

        with gr.Blocks(title="Eevee Chat", css=scrollable_checkbox_group_css) as ui:
            with gr.Row():
                with gr.Column(scale=10):
                    gr.Markdown(f"# 💬 Eevee Chat")
                with gr.Column(scale=1):
                    new_chat = gr.Button("New Chat")
            
            with gr.Row():
                with gr.Column(scale=1, variant='panel'):
                    with gr.Group():
                        model = gr.Dropdown(label="Model", interactive=True, choices=available_models, value=preferred_model)  # type: ignore
                        with gr.Accordion(label="System Prompt", open=False):
                            system_prompt = gr.TextArea(value="You are a helpful AI assistance named Bruno, and your task is to assist the user with all its requests in the best way possible", container=False, interactive=True, lines=10)
                        temperature = gr.Slider(label="Temperature", minimum=0., maximum=1., step=.01, value=preferred_temperature)
                        force_json = gr.Checkbox(label="Force JSON", value=False, interactive=True)
                    gr.Markdown("Not all models support all options, see documentation for more information")
                    gr.Markdown("------")
                    with gr.Group():
                        saved_chats = gr.Radio(label="Saved Chats", choices=self._list_saved_chats(), elem_classes="files_list", value=None)  # type: ignore
                        load_chat = gr.Button("Load")
                        delete_chat = gr.Button("Delete", variant='stop')

                with gr.Column(scale=10):
                    chat = gr.Chatbot(show_label=False, show_copy_button=True, height='80vh')
                    with gr.Row():
                        undo_last = gr.Button("Undo Last", variant='stop')
                        msg = gr.Textbox(label="Prompt (Press Enter to Send)", show_label=False, scale=9, container=False)
                        submit = gr.Button("Submit", variant='primary', scale=1)
                        stop = gr.Button("🟥 Stop", variant='stop', scale=1, visible=False)

            submit.click(
                self._add_user_message_to_chat, [msg, chat], [msg, chat]
            ).then(
                lambda: (gr.update(visible=True), gr.update(visible=False)), None, [stop, submit]
            ).then(
                self._add_bot_message_to_chat, [chat, model, temperature, force_json, system_prompt], chat
            ).then(
                self._save_chat
            ).then(
                lambda: (gr.update(visible=True), gr.update(visible=False)), None, [submit, stop]
            ).then(
                lambda: gr.update(choices=self._list_saved_chats()), None, saved_chats
            )

            msg.submit(
                self._add_user_message_to_chat, [msg, chat], [msg, chat]
            ).then(
                lambda: (gr.update(visible=True), gr.update(visible=False)), None, [stop, submit]
            ).then(
                self._add_bot_message_to_chat, [chat, model, temperature, force_json, system_prompt], chat
            ).then(
                self._save_chat
            ).then(
                lambda: (gr.update(visible=True), gr.update(visible=False)), None, [submit, stop]
            ).then(
                lambda: gr.update(choices=self._list_saved_chats()), None, saved_chats
            )

            stop.click(self._stop_text_generation)
            undo_last.click(self._undo_last_message, chat, chat).then(self._save_chat)
            new_chat.click(self._start_new_chat, None, [msg, chat])
            load_chat.click(self._start_new_chat, None, [msg, chat]).then(self._load_chat, saved_chats, [saved_chats, chat])
            delete_chat.click(self._delete_chat_file, saved_chats, None).then(lambda: gr.update(choices=self._list_saved_chats()), None, saved_chats)

        return ui
    