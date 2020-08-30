import abc
import dataclasses
import datetime
import enum
import typing
import uuid

import pydantic
import pydantic.generics

AttributesT = typing.TypeVar("AttributesT", bound=pydantic.BaseModel)


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)


class Resource(pydantic.generics.GenericModel, typing.Generic[AttributesT]):
    id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    version: int = 1
    created: datetime.datetime = pydantic.Field(default_factory=utc_now)
    last_updated: datetime.datetime = pydantic.Field(default_factory=utc_now)
    attributes: AttributesT


class Event(pydantic.BaseModel):
    id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    resource_id: uuid.UUID
    created: datetime.datetime = pydantic.Field(default_factory=utc_now)


class EventResourceModel(pydantic.generics.GenericModel, typing.Generic[AttributesT]):
    id: uuid.UUID
    attributes: AttributesT


class EventResource(abc.ABC, typing.Generic[AttributesT]):
    Attributes: typing.Type[AttributesT]

    def __init__(self, resource_id: typing.Optional[uuid.UUID] = None) -> None:
        if resource_id is None:
            resource_id = uuid.uuid4()
        self.resource_id = resource_id
        self.changes: typing.List[Event] = []
        self.attributes = self.Attributes()

    def serialize(self) -> EventResourceModel[AttributesT]:
        return EventResourceModel(id=self.resource_id, attributes=self.attributes)

    def apply(self, event: Event) -> None:
        self.changes.append(event)
        self.when(event)

    @abc.abstractmethod
    def when(self, event: Event) -> None:
        raise NotImplementedError()


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
