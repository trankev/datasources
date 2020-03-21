import dataclasses
import enum
import typing

import pydantic
import pydantic.generics


AttributesT = typing.TypeVar("AttributesT")


class Resource(pydantic.generics.GenericModel, typing.Generic[AttributesT]):
    id: str
    version: typing.Optional[int]
    attributes: AttributesT


class SortDirection(enum.Enum):
    ascending = enum.auto()
    descending = enum.auto()


@dataclasses.dataclass
class SortOption:
    field: str
    direction: SortDirection
