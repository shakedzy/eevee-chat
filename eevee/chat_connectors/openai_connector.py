import json
import itertools 
from openai import OpenAI
from typing import Generator, List, Dict, Any
from .connector_interface import Connector
from ..messages import ToolCall, Messages


class OpenAIConnector(Connector):
    def __init__(self) -> None:
        super().__init__()
        self.client = OpenAI()

    def _tool_calls_from_chunks(self, chunks) -> Generator:
        tool_calls = list()

        # Build tools_calls from chunks
        for chunk in chunks:
            if chunk.choices[0].finish_reason is not None:
                break
            for i, tool_call in enumerate(chunk.choices[0].delta.tool_calls):
                if len(tool_calls) <= i:
                    tool_call_dict = dict()
                    tool_calls.append(tool_call_dict)
                else:
                    tool_call_dict = tool_calls[i]
                function = chunk.choices[0].delta.tool_calls[0].function
                if function.name is not None:
                    tool_call_dict['id'] = tool_call.id
                    tool_call_dict['function'] = function.name
                    tool_call_dict['arguments'] = ''
                elif function.arguments is not None:
                    tool_call_dict['arguments'] += function.arguments
        
        yield [ToolCall(call_id=tool['id'], function=tool['function'], arguments=json.loads(tool['arguments'])) for tool in tool_calls]

    def get_streaming_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[str | List[ToolCall], None, None]:
        completion = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages.to('openai'),  # type: ignore
            tools=tools,                     # type: ignore
            stream=True
        )

        chunk = None
        for chunk in completion:
            if chunk.choices[0].delta.content is not None or chunk.choices[0].delta.tool_calls is not None:  # type: ignore
                break
        
        if chunk is None: raise RuntimeError('Got empty completion!')
        chunks = itertools.chain([chunk], completion)

        if chunk.choices[0].delta.tool_calls:  # type: ignore
            yield from self._tool_calls_from_chunks(chunks)
        
        else:
            for chunk in chunks:  # type: ignore
                if chunk.choices[0].finish_reason is not None:
                    break

                # sometimes gpt calls tools after starting the message
                if chunk.choices[0].delta.tool_calls is not None:  
                    remaining_chunks = itertools.chain([chunk], chunks)
                    yield from self._tool_calls_from_chunks(remaining_chunks)

                # got part of message content
                token = chunk.choices[0].delta.content
                if token:
                    yield token

    
    def get_json_response(self, model: str, temperature: float, messages: Messages, tools: List[Dict[str, Any]]) -> Generator[str | List[ToolCall], None, None]:
        message = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages.to('openai'),  # type: ignore
            tools=tools,                     # type: ignore
            response_format={"type": "json_object"}
        ).choices[0].message

        if message.tool_calls:
            tool_calls: List[ToolCall] = list()
            for tool_call in message.tool_calls:
                tool_calls.append(ToolCall(call_id=tool_call.id, function=tool_call.function.name, arguments=json.loads(tool_call.function.arguments)))
            yield tool_calls
        elif message.content is None:
            raise RuntimeError('Got empty completion!')
        else:
            yield message.content       
