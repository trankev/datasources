import datetime
import typing
import uuid

import bson.codec_options
from motor import motor_asyncio
import pydantic
import pymongo

from datasources import models


AttributesT = typing.TypeVar("AttributesT", bound=pydantic.BaseModel)


class MongoDataSource(typing.Generic[AttributesT]):
    def __init__(
            self,
            tracer,
            *,
            host: str,
            database_name: str,
            collection_name: str,
            attributes_type: typing.Type[AttributesT],
    ) -> None:
        client = motor_asyncio.AsyncIOMotorClient(host)
        database = client[database_name]
        options = bson.codec_options.CodecOptions(tz_aware=True)
        self.collection = database.get_collection(collection_name, codec_options=options)
        self.attributes_type = attributes_type
        self.tracer = tracer

    async def iterate(
            self,
            *,
            filters: typing.Optional[typing.Sequence[typing.Tuple[str, typing.Any]]] = None,
            sort: typing.Optional[typing.Sequence[models.SortOption]] = None,
            offset: typing.Optional[int] = None,
            limit: typing.Optional[int] = None,
    ) -> typing.AsyncIterator[models.Resource[AttributesT]]:
        search: dict = {}
        if filters:
            search = {field: value for field, value in filters}
        query = self.collection.find(search)
        if sort is not None:
            query = query.sort([
                (sort_option.field, sort_direction(sort_option.direction))
                for sort_option in sort
            ])
        if offset is not None:
            query = query.skip(offset)
        if limit is not None:
            query = query.limit(limit)
        with self.tracer.start_active_span(
                operation_name="mongo:iterate",
                finish_on_close=True,
                child_of=self.tracer.scope_manager.active.span,
        ):
            async for document in query:
                document.pop("_id")
                item: models.Resource[AttributesT] = models.Resource(**document)
                yield item

    async def insert(self, attributes: AttributesT) -> models.Resource[AttributesT]:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        document: models.Resource[AttributesT] = models.Resource(
            id=uuid.uuid4(),
            created=now,
            last_updated=now,
            version=1,
            attributes=attributes,
        )
        with self.tracer.start_active_span(
                operation_name="mongo:insert",
                finish_on_close=True,
                child_of=self.tracer.scope_manager.active.span,
        ):
            await self.collection.insert_one(document.dict())
        return document


def sort_direction(direction: models.SortDirection) -> int:
    if direction is models.SortDirection.ascending:
        return pymongo.ASCENDING
    elif direction is models.SortDirection.descending:
        return pymongo.DESCENDING
    else:
        raise ValueError(direction)
