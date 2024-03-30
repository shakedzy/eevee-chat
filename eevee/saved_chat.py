import os
import json
from datetime import datetime
from typing import Dict, Any, Tuple
from .messages import Messages


class SavedChat:
    FILE_PREFIX = "chat_"
    FILE_SUFFIX = ".json"
    TIME_FORMAT = "%Y-%m-%d-%H-%M-%S"
    MAX_NUM_OF_WORDS_IN_TITLE = 8

    def __init__(self, 
                 messages: Messages, 
                 start_time: datetime, 
                 directory: str, 
                 title: str | None = None,
                 **metadata
                 ) -> None:
        self._messages: Messages = messages
        self._start_time: datetime = start_time
        self._title: str = title or self._create_title()
        self._path: str = os.path.join(directory, self.title_and_time_to_filename(self._title, self._start_time))
        self._metadata: Dict[str, Any] = metadata

    @classmethod
    def from_chat_file(cls, file_path: str):
        with open(file_path, 'r') as f:
            loaded_file: Dict[str, Any] = json.load(f)
        messages = Messages.from_dict(loaded_file['messages'])
        metadata = loaded_file.get('metadata', {})
        pieces = file_path.split('/')
        directory = '/'.join(pieces[:-1])
        title, start_time = cls.filename_to_title_and_time(pieces[-1])
        return cls(messages, start_time, directory, title, **metadata)
    
    @classmethod
    def from_chat_title_and_time(cls, title: str, start_time: datetime, directory: str):
        filename = cls.title_and_time_to_filename(title, start_time)
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r') as f:
            loaded_file: Dict[str, Any] = json.load(f)
        messages = Messages.from_dict(loaded_file['messages'])
        metadata = loaded_file.get('metadata', {})  
        return cls(messages, start_time, directory, title, **metadata)
    
    @property
    def messages(self) -> Messages:
        return self._messages
    
    @property
    def start_time(self) -> datetime:
        return self._start_time
    
    @property
    def path(self) -> str:
        return self._path
    
    @property
    def title(self) -> str:
        return self._title
    
    @classmethod
    def title_and_time_to_filename(cls, title: str, start_time: datetime) -> str:
        return cls.FILE_PREFIX + title.replace(' ', '_') + '_' + start_time.strftime(cls.TIME_FORMAT) + cls.FILE_SUFFIX
    
    @classmethod
    def filename_to_title_and_time(cls, filename: str) -> Tuple[str, datetime]:
        stripped = filename[len(cls.FILE_PREFIX):-len(cls.FILE_SUFFIX)]
        pieces = stripped.split('_')
        time = datetime.strptime(pieces[-1], cls.TIME_FORMAT)
        title = ' '.join(pieces[:-1])
        return title, time
    
    def from_metadata(self, key: str) -> Any:
        return self._metadata.get(key, None)
    
    def _create_title(self) -> str:
        first_message_content = self.messages[1].content if self.messages.system_prompt is not None else self.messages[0].content
        if not first_message_content:
            title = 'untitled'
        else:  
            maxsplit = self.MAX_NUM_OF_WORDS_IN_TITLE + 1
            first_words = first_message_content.split(' ', maxsplit=maxsplit)
            title = ' '.join(first_words[:maxsplit])
            title = ''.join(e for e in title if (e.isalnum() or e==' '))
            if len(first_words) > maxsplit:
                title += '...'
        return title
    
    def save_to_file(self) -> None:
        file_as_dict = {
            "start_time": self.start_time.strftime(self.TIME_FORMAT),
            "messages": self.messages.as_dict(),
            "metadata": self._metadata
        }
        with open(self.path, 'w') as f:
            f.write(json.dumps(file_as_dict, indent=4))
