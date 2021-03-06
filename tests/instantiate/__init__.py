# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
import collections
import collections.abc
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from omegaconf import MISSING

from hydra.types import TargetConf


class ArgsClass:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        assert isinstance(args, tuple)
        assert isinstance(kwargs, dict)
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return f"self.args={self.args},self.kwarg={self.kwargs}"

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, ArgsClass):
            return self.args == other.args and self.kwargs == other.kwargs
        else:
            return NotImplemented


def add_values(a: int, b: int) -> int:
    return a + b


def module_function(x: int) -> int:
    return x


@dataclass
class AClass:
    a: Any
    b: Any
    c: Any
    d: Any = "default_value"

    @staticmethod
    def static_method(z: int) -> int:
        return z


@dataclass
class BClass:
    a: Any
    b: Any
    c: Any = "c"
    d: Any = "d"


@dataclass
class UntypedPassthroughConf:
    _target_: str = "tests.instantiate.UntypedPassthroughClass"
    a: Any = MISSING


@dataclass
class UntypedPassthroughClass:
    a: Any


# Type not legal in a config
class IllegalType:
    def __eq__(self, other: Any) -> Any:
        return isinstance(other, IllegalType)


@dataclass
class AnotherClass:
    x: int


class ASubclass(AnotherClass):
    @classmethod
    def class_method(cls, y: int) -> Any:
        return cls(y + 1)

    @staticmethod
    def static_method(z: int) -> int:
        return z


class Parameters:
    def __init__(self, params: List[float]):
        self.params = params

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, Parameters):
            return self.params == other.params
        return False

    def __deepcopy__(self, memodict: Any = {}) -> Any:
        raise NotImplementedError("Pytorch parameters does not support deepcopy")


@dataclass
class Adam:
    params: Parameters
    lr: float = 0.001
    betas: Tuple[float, ...] = (0.9, 0.999)
    eps: float = 1e-08
    weight_decay: int = 0
    amsgrad: bool = False


@dataclass
class NestingClass:
    a: ASubclass = ASubclass(10)


nesting = NestingClass()


class ClassWithMissingModule:
    def __init__(self) -> None:
        import some_missing_module  # type: ignore # noqa: F401

        self.x = 1


@dataclass
class AdamConf:
    _target_: str = "tests.instantiate.Adam"
    lr: float = 0.001
    betas: Tuple[float, ...] = (0.9, 0.999)
    eps: float = 1e-08
    weight_decay: int = 0
    amsgrad: bool = False


@dataclass
class BadAdamConf(TargetConf):
    # Missing str annotation
    _target_ = "tests.instantiate.Adam"


@dataclass
class User:
    name: str = MISSING
    age: int = MISSING


@dataclass
class UserGroup:
    name: str = MISSING
    users: List[User] = MISSING


# RECURSIVE
# Classes
class Transform:
    ...


class CenterCrop(Transform):
    def __init__(self, size: int):
        self.size = size

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, type(self)):
            return self.size == other.size
        else:
            return False


class Rotation(Transform):
    def __init__(self, degrees: int):
        self.degrees = degrees

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, type(self)):
            return self.degrees == other.degrees
        else:
            return False


class Compose:
    transforms: List[Transform]

    def __init__(self, transforms: List[Transform]):
        self.transforms = transforms

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, type(self)):
            return self.transforms == other.transforms
        else:
            return False


class Tree:
    value: Any
    # annotated any because of non recursive instantiation tests
    left: Any = None
    right: Any = None

    def __init__(self, value: Any, left: Any = None, right: Any = None) -> None:
        self.value = value
        self.left = left
        self.right = right

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, type(self)):
            return (
                self.value == other.value
                and self.left == other.left
                and self.right == other.right
            )

        else:
            return False

    def __repr__(self) -> str:
        return f"Tree(value={self.value}, left={self.left}, right={self.right})"


class Mapping:
    dictionary: Optional[Dict[str, "Mapping"]] = None
    value: Any = None

    def __init__(
        self, value: Any = None, dictionary: Optional[Dict[str, "Mapping"]] = None
    ) -> None:
        self.dictionary = dictionary
        self.value = value

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, type(self)):
            return self.dictionary == other.dictionary and self.value == other.value
        else:
            return False

    def __repr__(self) -> str:
        return f"dictionary={self.dictionary}"


# Configs
@dataclass
class TransformConf:
    ...


@dataclass
class CenterCropConf(TransformConf):
    _target_: str = "tests.instantiate.CenterCrop"
    size: int = MISSING


@dataclass
class RotationConf(TransformConf):
    _target_: str = "tests.instantiate.Rotation"
    degrees: int = MISSING


@dataclass
class ComposeConf:
    _target_: str = "tests.instantiate.Compose"
    transforms: List[TransformConf] = MISSING


@dataclass
class TreeConf:
    _target_: str = "tests.instantiate.Tree"
    left: Optional["TreeConf"] = None
    right: Optional["TreeConf"] = None
    value: Any = MISSING


@dataclass
class MappingConf:
    _target_: str = "tests.instantiate.Mapping"
    dictionary: Optional[Dict[str, "MappingConf"]] = None

    def __init__(self, dictionary: Optional[Dict[str, "MappingConf"]] = None):
        self.dictionary = dictionary


@dataclass
class SimpleDataClass:
    a: Any = None
    b: Any = None


class SimpleClass:
    a: Any = None
    b: Any = None

    def __init__(self, a: Any, b: Any) -> None:
        self.a = a
        self.b = b

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, SimpleClass):
            return self.a == other.a and self.b == other.b
        return False


@dataclass
class SimpleClassPrimitiveConf:
    _target_: str = "tests.instantiate.SimpleClass"
    _convert_: str = "partial"
    a: Any = None
    b: Any = None


@dataclass
class SimpleClassNonPrimitiveConf:
    _target_: str = "tests.instantiate.SimpleClass"
    _convert_: str = "none"
    a: Any = None
    b: Any = None


@dataclass
class SimpleClassDefaultPrimitiveConf:
    _target_: str = "tests.instantiate.SimpleClass"
    a: Any = None
    b: Any = None


@dataclass
class NestedConf:
    _target_: str = "tests.instantiate.SimpleClass"
    a: Any = User(name="a", age=1)
    b: Any = User(name="b", age=2)


def recisinstance(got: Any, expected: Any) -> bool:
    """Compare got with expected type, recursively on dict and list."""
    if not isinstance(got, type(expected)):
        return False
    if isinstance(expected, collections.abc.Mapping):
        return all(recisinstance(got[key], expected[key]) for key in expected)
    elif isinstance(expected, collections.abc.Iterable):
        return all(recisinstance(got[idx], exp) for idx, exp in enumerate(expected))
    return True
