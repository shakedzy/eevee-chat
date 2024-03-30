import json
from typing import List, Dict, Any, Generator
from dataclasses import dataclass
from mistralai.models.chat_completion import ChatMessage as MistralChatMessage, ToolCall as MistralToolCall, FunctionCall as MistralFunctionCall
from ._types import Role, Framework


@dataclass
class ToolCall:
    call_id: str
    function: str
    arguments: Dict[str, Any]

    def __str__(self) -> str:
        return f"{self.function}: {json.dumps(self.arguments)}"
    
    def as_dict(self) -> Dict[str, Any]:
        return {
            'call_id': self.call_id,
            'function': self.function,
            'arguments': self.arguments
        }


class Message:
    def __init__(self, role: Role, content: str | None = None, tool_calls: List[ToolCall] = [], *, model: str | None = None) -> None:
        if role == 'assistant' and not model:
            raise ValueError('AI generated messages must be provided with model name')
        self.role: Role = role
        self.content: str | None = content
        self.tool_calls: List[ToolCall] = tool_calls
        self.model: str | None = model
    
    def __str__(self) -> str:
        return f"{{ role: {self.role}, content: '{self.content or ''}', tool_calls: [{', '.join([str(t) for t in self.tool_calls])}]}}"
    
    def as_dict(self) -> Dict[str, Any]:
        dct = {
            'role': self.role,
            'content': self.content
        }
        if self.tool_calls:
            dct['tool_calls'] = [t.as_dict() for t in self.tool_calls]
        if self.model:
            dct['model'] = self.model
        return dct
    
    @property
    def displayed(self) -> bool:
        if self.role == 'user' or (self.role == 'assistant' and not self.tool_calls):
            return True
        else:
            return False
    
    def update(self, content: str | None = None, tool_calls: List[ToolCall] | None = None) -> None:
        if content:
            self.content = (self.content or '') + content
        if tool_calls:
            self.tool_calls = (self.tool_calls or []) + tool_calls

    def edit(self, content: str | None = None, tool_calls: List[ToolCall] | None = None) -> None:
        if content:
            self.content = content
        if tool_calls:
            self.tool_calls = tool_calls
    
    def to(self, framework: Framework):
        match framework:
            case 'openai':
                if self.role == 'tool':
                    tool_call_id = self.tool_calls[0].call_id
                    tool_calls = None
                elif self.tool_calls:
                    tool_call_id = None
                    tool_calls = list()
                    for tool_call in self.tool_calls:
                        tool_call_dict = dict()
                        tool_call_dict['id'] = tool_call.call_id
                        tool_call_dict['type'] = 'function'
                        tool_call_dict['function'] = {'name': tool_call.function, 'arguments': str(tool_call.arguments)}
                        tool_calls.append(tool_call_dict)
                else:
                    tool_calls = None
                    tool_call_id = None
                message = {
                    'role': self.role,
                    'content': self.content,
                    }
                if tool_calls:
                    message['tool_calls'] = tool_calls
                if tool_call_id:
                    message['tool_call_id'] = tool_call_id
                return message
            
            case 'anthropic':
                if self.role == 'system':
                    return None
                message = {'role': self.role, 'content': self.content}
                if not message['content'] and self.tool_calls:
                    message['content'] = f"Executing functions: [{', '.join([str(t) for t in self.tool_calls])}]"
                elif message['role'] == 'tool':
                    message['role'] = 'user'
                return message

            case 'mistral':
                if self.role in ['system', 'user']:
                    message = MistralChatMessage(role=self.role, content=self.content or '')
                elif self.role == 'tool':
                    message = MistralChatMessage(role=self.role, content=self.content or '', name=self.tool_calls[0].function)
                elif self.role == 'assistant':
                    if self.tool_calls:
                        mistral_tool_calls = []
                        for tool_call in self.tool_calls:
                            function_call = MistralFunctionCall(name=tool_call.function, arguments=json.dumps(tool_call.arguments))
                            mistral_tool_calls.append(MistralToolCall(function=function_call))
                    else:
                        mistral_tool_calls = None
                    message = MistralChatMessage(role=self.role, content=self.content or '', tool_calls=mistral_tool_calls)
                return message


class Messages(list[Message]):
    def __init__(self, *args) -> None:
        super().__init__(*args)

    @classmethod
    def from_dict(cls, messages_as_dict: List[Dict[str, Any]]):
        messages = cls()
        for message in messages_as_dict:
            tool_calls: List[ToolCall] = list()
            if 'tool_calls' in message:
                for tool_call in message['tool_calls']:
                    tool_calls.append(
                        ToolCall(
                            call_id=tool_call['call_id'],
                            function=tool_call['function'],
                            arguments=tool_call['arguments']
                        )
                    )
            messages.append(
                role=message['role'],
                content=message['content'],
                tool_calls=tool_calls,
                model=message.get('model', None)
            )
        return messages

    @property
    def empty(self) -> bool:
        return not bool(self)
    
    @property
    def last_message_index(self) -> int:
        if self.empty:
            raise ValueError('No messages!')
        return len(self)-1
    
    @property
    def system_prompt(self) -> str | None:
        if self.empty:
            return None
        message = self[0]
        if message.role == 'system':
            return message.content
        else:
            return None
    
    def as_dict(self) -> List[Dict[str, Any]]:
        return [m.as_dict() for m in self]

    def append(self, role: Role, content: str | None, tool_calls: List[ToolCall] = [], model: str | None = None) -> None:
        super().append(Message(role, content, tool_calls=tool_calls, model=model))
    
    def to(self, framework: Framework):
        msgs = [m.to(framework) for m in self]
        return [m for m in msgs if m]
    
    def update(self, i: int, /, content: str | None = None, tool_calls: List[ToolCall] | None = None) -> None:
        self[i].update(content, tool_calls)

    def edit(self, i: int, /, content: str | None = None, tool_calls: List[ToolCall] | None = None) -> None:
        self[i].edit(content, tool_calls)  
