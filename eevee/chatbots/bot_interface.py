from abc import abstractmethod
from typing import Generator, List
from ..messages import Messages, ToolCall
from ..package_types import JSON


class Bot:
    @abstractmethod
    def get_streaming_response(self, model: str, temperature: float, messages: Messages, tools: List[JSON]) -> Generator:
        raise NotImplementedError()
    
    @abstractmethod
    def get_json_response(self, model: str, temperature: float, messages: Messages, tools: List[JSON]) -> str | List[ToolCall]:
        raise NotImplementedError()
