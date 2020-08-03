import asyncio
import typing

from _pytest import fixtures
import pytest

from datasources.repositories import base
from datasources.repositories import memory


@pytest.fixture(name="event_loop", scope="session")
def event_loop_fixture() -> typing.Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(name="memory_datasource", scope="session")
def memory_datasource_fixture() -> memory.MemoryDataSource:
    return memory.MemoryDataSource([])


@pytest.fixture(name="datasource", scope="session", params=["memory_datasource"])
def datasource_fixture(request: fixtures.SubRequest) -> base.DataSource:
    return request.getfixturevalue(request.param)
