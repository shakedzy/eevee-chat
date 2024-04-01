import google.generativeai as genai
from typing import List, Generator, Dict, Any
from .connector_interface import Connector
from ..messages import Messages, ChatMessagePiece


class GoogleConnector(Connector):
    def __init__(self) -> None:
        super().__init__()

    def get_streaming_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[ChatMessagePiece, None, None]:
        gemini_model = genai.GenerativeModel(model)
        response = gemini_model.generate_content(
            contents=messages.to('google'),  # type: ignore
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                temperature=temperature)
        )
        for chunk in response:
            yield ChatMessagePiece(content=chunk.text, model=model)

    def get_json_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[ChatMessagePiece, None, None]:
        yield ChatMessagePiece(warning_message="Google models do not support forcing JSON responses")
        yield from self.get_streaming_response(model, temperature, messages, tools)
