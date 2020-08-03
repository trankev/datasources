import copy
import typing

import pydantic

from datasources import models
from datasources.repositories import base

AttributesT = typing.TypeVar("AttributesT", bound=pydantic.BaseModel)


class MemoryDataSource(base.DataSource, typing.Generic[AttributesT]):

    def __init__(self, dataset: typing.Sequence[models.Resource[AttributesT]]):
        self.dataset = list(dataset)

    async def iterate(
        self,
        *,
        filters: typing.Optional[typing.Sequence[models.FilterOption]] = None,
        sort: typing.Optional[typing.Sequence[models.SortOption]] = None,
        offset: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
    ) -> typing.AsyncIterator[models.Resource[AttributesT]]:
        dataset = copy.copy(self.dataset)
        if filters is not None:
            dataset = filter_dataset(dataset, filters)
        if sort is not None:
            dataset = sort_dataset(dataset, sort)
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


def filter_dataset(
    dataset: typing.Sequence[models.Resource[AttributesT]],
    filters: typing.Sequence[models.FilterOption],
) -> typing.List[models.Resource[AttributesT]]:
    result = iter(dataset)
    for filter_option in filters:
        if filter_option.comparison == models.FilterComparison.equality:
            result = (
                entry for entry in result
                if getattr(entry.attributes, filter_option.field) == filter_option.value
            )
        else:
            message = "Unsupported filter comparison for memory datasource: {:r}"
            message = message.format(filter_option.comparison)
            raise ValueError(message)
    return list(result)


def sort_dataset(
    dataset: typing.List[models.Resource[AttributesT]],
    sort: typing.Sequence[models.SortOption],
) -> typing.List[models.Resource[AttributesT]]:
    for sort_option in reversed(sort):
        dataset = sorted(
            dataset,
            key=lambda x: getattr(x.attributes, sort_option.field),
            reverse=sort_option.direction == models.SortDirection.descending,
        )
    return dataset
