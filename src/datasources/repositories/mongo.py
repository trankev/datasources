import datetime
import typing
import uuid

import bson.codec_options
from motor import motor_asyncio
import pydantic
import pymongo

from datasources import models
from datasources.repositories import base

AttributesT = typing.TypeVar("AttributesT", bound=pydantic.BaseModel)


class MongoDataSource(base.DataSource, typing.Generic[AttributesT]):

    def __init__(
        self,
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

    async def iterate(
        self,
        *,
        filters: typing.Optional[typing.Sequence[models.FilterOption]] = None,
        sort: typing.Optional[typing.Sequence[models.SortOption]] = None,
        offset: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
    ) -> typing.AsyncIterator[models.Resource[AttributesT]]:
        search: dict = {}
        if filters:
            search = {option.field: option.value for option in filters}
        query = self.collection.find(search)
        if sort is not None:
            sort_fields = [
                (sort_option.field, sort_direction(sort_option.direction)) for sort_option in sort
            ]
            print(sort_fields)
            query = query.sort(sort_fields)
        if offset is not None:
            query = query.skip(offset)
        if limit is not None:
            query = query.limit(limit)
        async for document in query:
            document.pop("_id")
            item = models.Resource[self.attributes_type](**document)  # type: ignore
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
        await self.collection.insert_one(document.dict())
        return document

    async def update(
        self,
        item_id: uuid.UUID,
        version: int,
        attributes: pydantic.BaseModel,
    ) -> bool:
        query = {
            "id": item_id,
            "version": version,
        }
        updates = {
            "$set": {
                "attributes": attributes.dict(),
            },
            "$currentDate": {
                "last_updated": True,
            },
            "$inc": {
                "version": 1,
            },
        }
        # TODO: return/log error if any
        update_result = await self.collection.update_one(query, updates)
        return update_result.matched_count == 1

    async def clear(self) -> None:
        await self.collection.delete_many({})


def sort_direction(direction: models.SortDirection) -> int:
    if direction is models.SortDirection.ascending:
        return pymongo.ASCENDING
    elif direction is models.SortDirection.descending:
        return pymongo.DESCENDING
    else:
        raise ValueError(direction)
