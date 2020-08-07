import pytest

from datasources.repositories import base
from tests.integration.repositories import models


@pytest.mark.asyncio
async def test_nominal(datasource: base.DataSource) -> None:
    sample_attributes = models.SampleModel(str_field="a", int_field=12, bool_field=True)
    await datasource.insert(sample_attributes)

    entries = [entry async for entry in datasource.iterate()]
    assert len(entries) == 1

    await datasource.clear()
    entries = [entry async for entry in datasource.iterate()]
    assert len(entries) == 0
