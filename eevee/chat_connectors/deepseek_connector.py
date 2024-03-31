import os
from openai import OpenAI
from typing import List, Dict, Any, Generator
from .connector_interface import Connector
from .openai_connector import OpenAIConnector
from ..messages import Messages, ToolCall


class DeepSeekConnector(OpenAIConnector):
    def __init__(self) -> None:
        Connector.__init__(self)
        self.client = OpenAI(base_url='https://api.deepseek.com/v1', api_key=os.environ['DEEPSEEK_API_KEY'])

    def get_json_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[str | List[ToolCall], None, None]:
        yield self.WARNING_TOKEN + "DeepSeek models do not support forcing JSON responses"
        yield from self.get_streaming_response(model, temperature, messages, tools)
