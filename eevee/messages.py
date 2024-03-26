import json
from typing import List, Dict, Any
from dataclasses import dataclass
from .package_types import Role, Framework


@dataclass
class ToolCall:
    call_id: str
    function: str
    arguments: Dict[str, Any]

    def __str__(self) -> str:
        return f"{self.function}: {json.dumps(self.arguments)}"


class Message:
    def __init__(self, role: Role, content: str | None, tool_calls: List[ToolCall] = []) -> None:
        self.role = role
        self.content = content
        self.tool_calls = tool_calls
    
    def __str__(self) -> str:
        return f"{{ role: {self.role}, content: '{self.content or ''}', tool_calls: [{', '.join([str(t) for t in self.tool_calls])}]}}"
    
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
                message = {'role': self.role, 'content': self.content}
                if not message['content'] and self.tool_calls:
                    message['content'] = f"Executing functions: [{', '.join([str(t) for t in self.tool_calls])}]"
                elif message['role'] == 'tool':
                    message['role'] = 'user'
                return message

            case 'mistral':
                pass


class Messages:
    _messages: List[Message] = list()

    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return str([str(m) for m in self._messages])
    
    def __len__(self) -> int:
        return len(self._messages)
    
    def __getitem__(self, i: int) -> Message:
        return self._messages[i]

    @property
    def empty(self) -> bool:
        return not bool(self._messages)
    
    @property
    def last_message_index(self) -> int:
        if self.empty:
            raise ValueError('No messages!')
        return len(self._messages)-1

    def append(self, role: Role, content: str | None, tool_calls: List[ToolCall] = []) -> None:
        self._messages.append(Message(role, content, tool_calls=tool_calls))
    
    def delete(self, i: int) -> None:
        del self._messages[i]
    
    def to(self, framework: Framework):
        return [m.to(framework) for m in self._messages]
    
    def update(self, i: int, content: str | None = None, tool_calls: List[ToolCall] | None = None) -> None:
        self._messages[i].update(content, tool_calls)

    def edit(self, i: int, content: str | None = None, tool_calls: List[ToolCall] | None = None) -> None:
        self._messages[i].edit(content, tool_calls)    
    