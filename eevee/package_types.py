from typing import Literal, TypeAlias, Dict, Callable, List, Tuple, Any


JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
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
