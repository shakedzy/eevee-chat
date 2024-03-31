import os
from typing import List, Dict, Any, Generator
from .openai_connector import OpenAIConnector
from ..messages import Messages, ChatMessagePiece


class DeepSeekConnector(OpenAIConnector):
    def __init__(self) -> None:
        super().__init__(base_url='https://api.deepseek.com/v1', api_key=os.environ['DEEPSEEK_API_KEY'])

    def get_json_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[ChatMessagePiece, None, None]:
        yield ChatMessagePiece(warning_message="DeepSeek models do not support forcing JSON responses")
        yield from self.get_streaming_response(model, temperature, messages, tools)
