import json
import itertools 
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ToolCall as MistralToolCall
from typing import List, Generator, Dict, Any
from .connector_interface import Connector
from ..messages import Messages, ToolCall


class MistralConnector(Connector):
    def __init__(self) -> None:
        self.supports_json_response = True
        self.client = MistralClient()

    def _tool_calls_from_chunks(self, chunks) -> Generator[List[ToolCall], None, None]:
        tool_calls = list()
        for chunk in chunks:
            mistral_tool_calls: List[MistralToolCall] = chunk.choices[0].delta.tool_calls
            for t in mistral_tool_calls:
                tool_calls.append(ToolCall(
                    call_id=t.id,
                    function=t.function.name,
                    arguments=json.loads(t.function.arguments)
                ))
        yield tool_calls

    def get_streaming_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator:
        response = self.client.chat_stream(
            model=model, 
            temperature=temperature,
            messages=messages.to('mistral'), 
            tools=tools)

        chunk = None
        for chunk in response:
            if chunk.choices[0].delta.content is not None or chunk.choices[0].delta.tool_calls is not None:  # type: ignore
                break
        
        if chunk is None: raise RuntimeError('Got empty completion!')
        chunks = itertools.chain([chunk], response)

        if chunk.choices[0].delta.tool_calls:  # type: ignore
            yield from self._tool_calls_from_chunks(chunks)
        
        else:
            for chunk in chunks:  # type: ignore
                if chunk.choices[0].finish_reason is not None:
                    break

                # in case tools calls begin after some content was sent
                if chunk.choices[0].delta.tool_calls is not None:  
                    remaining_chunks = itertools.chain([chunk], chunks)
                    yield from self._tool_calls_from_chunks(remaining_chunks)

                # got part of message content
                token = chunk.choices[0].delta.content
                if token:
                    yield token
        
    def get_json_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[str | List[ToolCall], None, None]:
        if tools:
            yield self.WARNING_TOKEN + "Mistral models do not support tools when forcing JSON response"
        
        response = self.client.chat(
            model=model, 
            temperature=temperature,
            messages=messages.to('mistral'), 
            tools=tools)
        
        content = response.choices[0].message.content
        if isinstance(content, list):
            content = ' '.join(content)
        yield content
