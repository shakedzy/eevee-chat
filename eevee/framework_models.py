import os
from typing import get_args, Set, Dict, List
from .settings import Settings
from ._types import Framework


def get_available_frameworks() -> Set[Framework]:
    available: Set[Framework] = set()
    models_dict: Dict = Settings().models
    for framework in get_args(Framework):
        if framework not in models_dict.keys():
            continue
        api_key = os.environ.get(f'{framework.upper()}_API_KEY', None)
        if api_key:
            available.add(framework)
    return available


def get_model_framework(model: str) -> Framework:
    models_dict: Dict[Framework, List[str]] = Settings().models
    for framework, models in models_dict.items():
        if model in models:
            return framework
    raise ValueError(f"Model {model} does not belong to any framework!")
