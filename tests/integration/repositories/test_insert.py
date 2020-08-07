import pytest

from datasources.repositories import base
from tests.integration.repositories import models


@pytest.mark.asyncio
async def test_nominal(datasource: base.DataSource) -> None:
    entries = [entry async for entry in datasource.iterate()]
    assert len(entries) == 0
    sample_attributes = models.SampleModel(str_field="a", int_field=12, bool_field=True)
    try:
        await datasource.insert(sample_attributes)

        entries = [entry async for entry in datasource.iterate()]
        assert len(entries) == 1
        attributes = [entry.attributes for entry in entries]
        assert attributes == [sample_attributes]
    finally:
        await datasource.clear()
