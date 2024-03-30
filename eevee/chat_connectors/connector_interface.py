from abc import abstractmethod
from typing import Generator, List, Dict, Any
from ..messages import Messages, ToolCall


class Connector:
    INFO_TOKEN = "╬"
    WARNING_TOKEN = "╩"

    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_streaming_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[str | List[ToolCall], None, None]:
        raise NotImplementedError()
    
    @abstractmethod
    def get_json_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[str | List[ToolCall], None, None]:
        raise NotImplementedError()
