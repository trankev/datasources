import typing

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
        self.collection = database[collection_name]
        self.attributes_type = attributes_type
        self.tracer = tracer

    async def iterate(
            self,
            *,
            sort: typing.Optional[typing.Sequence[models.SortOption]] = None,
            offset: typing.Optional[int] = None,
            limit: typing.Optional[int] = None,
    ) -> typing.AsyncIterator[models.Resource[AttributesT]]:
        search: dict = {}
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
                operation_name=f"mongo:iterate",
                finish_on_close=True,
                child_of=self.tracer.scope_manager.active.span,
        ):
            async for document in query:
                item_id = str(document.pop("_id"))
                version = document.pop("version")
                attributes = self.attributes_type(**document)
                item = models.Resource(
                    id=item_id,
                    version=version,
                    attributes=attributes,
                )
                yield item

    async def insert(self, attributes: AttributesT) -> models.Resource[AttributesT]:
        first_version = 1
        document = attributes.dict()
        document["version"] = first_version
        with self.tracer.start_active_span(
                operation_name=f"mongo:insert",
                finish_on_close=True,
                child_of=self.tracer.scope_manager.active.span,
        ):
            response = await self.collection.insert_one(document)
        result = models.Resource(
            id=str(response.inserted_id),
            version=first_version,
            attributes=attributes,
        )
        return result


def sort_direction(direction: models.SortDirection) -> int:
    if direction is models.SortDirection.ascending:
        return pymongo.ASCENDING
    elif direction is models.SortDirection.descending:
        return pymongo.DESCENDING
    else:
        raise ValueError(direction)
