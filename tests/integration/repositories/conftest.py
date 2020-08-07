import asyncio
import typing

from _pytest import config
from _pytest import fixtures
import pytest

from datasources.repositories import base
from datasources.repositories import memory
from datasources.repositories import mongo
from tests.integration.repositories import containers
from tests.integration.repositories import models


@pytest.fixture(name="event_loop", scope="session")
def event_loop_fixture() -> typing.Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(name="memory_datasource", scope="session")
def memory_datasource_fixture() -> memory.MemoryDataSource:
    return memory.MemoryDataSource([])


@pytest.fixture(
    name="datasource",
    scope="session",
    params=["memory_datasource", "mongo_datasource"],
)
def datasource_fixture(request: fixtures.SubRequest) -> base.DataSource:
    return request.getfixturevalue(request.param)


@pytest.fixture(name="mongo_datasource", scope="session")
def mongo_datasource_fixture(pytestconfig: config.Config) -> typing.Iterator[mongo.MongoDataSource]:
    provided_host = pytestconfig.getoption("mongodb_host")
    if provided_host is None:
        mongo_image = pytestconfig.getoption("mongodb_image")
        with containers.container(mongo_image) as mongo_host:
            datasource = mongo.MongoDataSource(
                host=mongo_host,
                database_name="billing_test",
                collection_name="bills",
                attributes_type=models.SampleModel,
            )
            yield datasource
    else:
        datasource = mongo.MongoDataSource(
            host=provided_host,
            database_name="billing_test",
            collection_name="bills",
            attributes_type=models.SampleModel,
        )
        yield datasource
