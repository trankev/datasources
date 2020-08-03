import typing

from datasources import models
from datasources.repositories import base

AttributesT = typing.TypeVar("AttributesT")


class MemoryDataSource(base.DataSource, typing.Generic[AttributesT]):

    def __init__(self, dataset: typing.Sequence[models.Resource[AttributesT]]):
        self.dataset = list(dataset)

    async def iterate(
        self,
        *,
        filters: typing.Optional[typing.Sequence[typing.Tuple[str, typing.Any]]] = None,
        sort: typing.Optional[typing.Sequence[models.SortOption]] = None,
        offset: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
    ) -> typing.AsyncIterator[models.Resource[AttributesT]]:
        dataset = self.dataset
        if sort is not None:
            for sort_option in reversed(sort):
                dataset = sorted(
                    dataset,
                    key=lambda x: getattr(x.attributes, sort_option.field),
                    reverse=sort_option.direction == models.SortDirection.descending,
                )
        start = 0 if offset is None else offset
        end = None if limit is None else start + limit
        for entry in dataset[start:end]:
            yield entry

    async def insert(self, attributes: AttributesT) -> models.Resource[AttributesT]:
        entry: models.Resource[AttributesT] = models.Resource(attributes=attributes)
        self.dataset.append(entry)
        return entry

    async def clear(self) -> None:
        self.dataset = []
