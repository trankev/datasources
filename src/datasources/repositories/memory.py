import typing
import uuid

from hexagonal.data_sources import models as data_models
from hexagonal import models as hexa_models


AttributesT = typing.TypeVar("AttributesT")


class MemoryDataSource(typing.Generic[AttributesT]):
    def __init__(self, dataset: typing.Sequence[AttributesT]):
        self.dataset = list(dataset)

    async def iterate(
            self,
            sort: typing.Optional[typing.Sequence[data_models.SortOption]] = None,
            offset: typing.Optional[int] = None,
            limit: typing.Optional[int] = None,
    ) -> typing.AsyncIterator[hexa_models.Resource[AttributesT]]:
        dataset = self.dataset
        if sort is not None:
            dataset = sorted(dataset, key=get_sort_key(sort))
        for entry in dataset:
            yield entry

    async def insert(self, attributes: AttributesT) -> hexa_models.Resource[AttributesT]:
        entry = hexa_models.Resource(
            id=str(uuid.uuid4()),
            version=1,
            attributes=attributes,
        )
        self.dataset.append(entry)
        return entry


def get_sort_key(sort_options):
    def wrapped(entry):
        return tuple(
            getattr(entry.attributes, sort_option.field)
            for sort_option in sort_options
        )
    return wrapped
