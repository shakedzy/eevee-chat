from abc import abstractmethod
from typing import Generator, List, Dict, Any
from ..messages import Messages, ChatMessagePiece


class Connector:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_streaming_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[ChatMessagePiece, None, None]:
        raise NotImplementedError()
    
    @abstractmethod
    def get_json_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[ChatMessagePiece, None, None]:
        raise NotImplementedError()
