from typing import Set, Dict, List, Generator
from .messages import Messages, ToolCall
from .tools import tools_params_definitions
from .color_logger import get_logger
from .framework_models import get_model_framework
from .package_types import Framework, JSON
from .chatbots.bot_interface import Bot
from .chatbots.openai_bot import OpenAIBot


class Chatbot:
    TOOL_TOKEN = "╬"

    def __init__(self, available_frameworks: Set[Framework]) -> None:
        self.clients: Dict[Framework, Bot] = dict()
        self.callables = {f.__name__: f for f in tools_params_definitions.keys()}
        self.tools = self._build_tools()
        self.messages = Messages()
        self.logger = get_logger()

        for framework in available_frameworks:
            match framework:
                case 'openai':
                    client = OpenAIBot()
                case 'mistral':
                    pass
                case 'anthropic':
                    pass
            self.clients[framework] = client
        self.reset()

    def _build_tools(self) -> List[JSON]:
        tools = list()
        for func, v in tools_params_definitions.items():
            params = {}
            required = []
            for p in v:
                params[p[0]] = p[1]
                if p[2]: 
                    required.append(p[0])

            tools.append({
                "type": "function",
                "function": {
                    "name": func.__name__,
                    "description": func.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": params
                    },
                    "required": required
                }
            })
        return tools 

    def reset(self) -> None:
        self.messages = Messages()

    def _prepare_for_response(self, prompt: str, system_prompt: str, model: str) -> Framework:
        if self.messages.empty:
            self.messages.append("system", system_prompt)
        else:
            self.messages.edit(0, content=system_prompt)
        
        self.messages.append('user', prompt)
        framework = get_model_framework(model)
        return framework        

    def get_stream_response(self, prompt: str, *, system_prompt: str, model: str, temperature: float) -> Generator:        
        framework = self._prepare_for_response(prompt=prompt, system_prompt=system_prompt, model=model)

        final_message = False
        while not final_message:
            final_message = True
            generator = self.clients[framework].get_streaming_response(model=model, temperature=temperature, messages=self.messages, tools=self.tools)
            for token in generator:
                if isinstance(token, list):
                    # Only option is list of ToolCall
                    tool_calls: List[ToolCall] = token
                    final_message = False
                    if self.messages[self.messages.last_message_index].role == 'assistant':
                        self.messages.update(self.messages.last_message_index, tool_calls=tool_calls)
                    else:
                        self.messages.append('assistant', content=None, tool_calls=tool_calls)
                    for tool_call in tool_calls:
                        yield self.TOOL_TOKEN + tool_call.function
                        self.logger.info(f"Running tool {tool_call.function}: {str(tool_call.arguments)}", color='yellow')
                        tool_output = self.callables[tool_call.function](**tool_call.arguments)
                        self.logger.debug("Tool output:\n" + tool_output)
                        self.messages.append(role='tool', content=tool_output, tool_calls=[tool_call])
                else:
                    if self.messages[self.messages.last_message_index].role == 'assistant':
                        self.messages.update(self.messages.last_message_index, content=token)
                    else:
                        self.messages.append('assistant', content=token)
                    yield token 

    def get_json_response(self, prompt: str, *, system_prompt: str, model: str, temperature: float) -> Generator:
        framework = self._prepare_for_response(prompt=prompt, system_prompt=system_prompt, model=model)

        final_message = False
        while not final_message:
            response = self.clients[framework].get_json_response(model=model, temperature=temperature, messages=self.messages, tools=self.tools)
            if isinstance(response, list):
                # Only option is list of ToolCall
                tool_calls: List[ToolCall] = response
                self.messages.append(role='assistant', content=None, tool_calls=tool_calls)
                for tool_call in tool_calls:
                    yield self.TOOL_TOKEN + tool_call.function
                    self.logger.info(f"Running tool {tool_call.function}: {str(tool_call.arguments)}", color='yellow')
                    tool_output = self.callables[tool_call.function](**tool_call.arguments)
                    self.logger.debug("Tool output:\n" + tool_output)
                    self.messages.append(role='tool', content=tool_output, tool_calls=[tool_call])
            else:
                final_message = True
                self.messages.append(role='assistant', content=response)
                yield response 
