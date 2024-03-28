from typing import Literal, TypeAlias, Dict, Callable, List, Tuple, Any


ToolsDefType: TypeAlias = Dict[Callable, List[Tuple[str, Dict[str, Any], bool]]]
Role: TypeAlias = Literal['user', 'assistant', 'tool', 'system']
Framework: TypeAlias = Literal['openai', 'anthropic', 'mistral']

Color: TypeAlias = Literal[
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan"
]
