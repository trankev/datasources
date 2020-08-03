import abc
import typing
import uuid

import pydantic

from datasources import models

AttributesT = typing.TypeVar("AttributesT", bound=pydantic.BaseModel)


class DataSource(abc.ABC, typing.Generic[AttributesT]):

    async def iterate(
        self,
        *,
        filters: typing.Optional[typing.Sequence[models.FilterOption]] = None,
        sort: typing.Optional[typing.Sequence[models.SortOption]] = None,
        offset: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
    ) -> typing.AsyncIterator[models.Resource[AttributesT]]:
        raise NotImplementedError()
        yield  # pragma: no cover

    async def insert(self, attributes: AttributesT) -> models.Resource[AttributesT]:
        raise NotImplementedError()

    async def update(
        self,
        item_id: uuid.UUID,
        version: int,
        attributes: pydantic.BaseModel,
    ) -> bool:
        raise NotImplementedError()

    async def clear(self) -> None:
        raise NotImplementedError()
