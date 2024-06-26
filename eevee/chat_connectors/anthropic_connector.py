from anthropic import Anthropic
from anthropic._types import NOT_GIVEN
from typing import List, Generator, Dict, Any
from .connector_interface import Connector
from ..messages import Messages, ChatMessagePiece


class AnthropicConnector(Connector):
    def __init__(self) -> None:
        super().__init__()
        self.client = Anthropic()

    def get_streaming_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[ChatMessagePiece, None, None]:
        response = self.client.messages.create(
            messages=messages.to('anthropic'),  # type: ignore
            system=messages.system_prompt or NOT_GIVEN,
            temperature=temperature,
            stream=True,
            model=model,
            max_tokens=4096  # maximum defined by Anthropic
        )
        for chunk in response:
            if chunk.type == 'content_block_delta':
                yield ChatMessagePiece(content=chunk.delta.text)
    
    def get_json_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[ChatMessagePiece, None, None]:
        yield ChatMessagePiece(warning_message="Anthropic models do not support forcing JSON responses")
        yield from self.get_streaming_response(model, temperature, messages, tools)
