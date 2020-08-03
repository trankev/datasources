import dataclasses
import datetime
import enum
import typing
import uuid

import pydantic
import pydantic.generics

AttributesT = typing.TypeVar("AttributesT", bound=pydantic.BaseModel)


class Resource(pydantic.generics.GenericModel, typing.Generic[AttributesT]):
    id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    version: int = 1
    created: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
    last_updated: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    )
    attributes: AttributesT


class SortDirection(enum.Enum):
    ascending = enum.auto()
    descending = enum.auto()


@dataclasses.dataclass
class SortOption:
    field: str
    direction: SortDirection = SortDirection.ascending


class FilterComparison(enum.Enum):
    equality = enum.auto()


@dataclasses.dataclass
class FilterOption:
    field: str
    value: typing.Any
    comparison: FilterComparison = FilterComparison.equality
