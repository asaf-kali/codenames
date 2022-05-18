import copy
from dataclasses import dataclass
from typing import Callable, ContextManager, List
from unittest import mock


@dataclass(frozen=True)
class FunctionCall:
    args: tuple
    kwargs: dict
    result: object


class FunctionHook:
    def __init__(self):
        self.calls: List[FunctionCall] = []

    def append(self, call: FunctionCall):
        self.calls.append(call)

    @property
    def results(self) -> list:
        return [call.result for call in self.calls]


def hook_calls(func: Callable) -> Callable:
    hook = FunctionHook()

    def wrapper(*args, **kwargs):
        copy_args, copy_kwargs = copy.deepcopy(args), copy.deepcopy(kwargs)
        result = func(*args, **kwargs)
        call = FunctionCall(copy_args, copy_kwargs, copy.deepcopy(result))
        hook.append(call)
        return result

    wrapper.hook = hook  # type: ignore
    return wrapper


def hook_method(target: object, method_name: str) -> ContextManager:
    wrapper = hook_calls(getattr(target, method_name))
    mock_method = mock.patch.object(target=target, attribute=method_name, new=wrapper)
    return mock_method
