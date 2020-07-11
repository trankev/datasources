import dataclasses
import datetime
import enum
import typing
import uuid

import pydantic
import pydantic.generics


AttributesT = typing.TypeVar("AttributesT")


class Resource(pydantic.generics.GenericModel, typing.Generic[AttributesT]):
    id: uuid.UUID
    version: typing.Optional[int]
    created: datetime.datetime
    last_updated: datetime.datetime
    attributes: AttributesT


class SortDirection(enum.Enum):
    ascending = enum.auto()
    descending = enum.auto()


@dataclasses.dataclass
class SortOption:
    field: str
    direction: SortDirection
