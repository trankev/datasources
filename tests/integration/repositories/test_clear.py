import pydantic
import pytest

from datasources.repositories import base


class SampleModel(pydantic.BaseModel):
    str_field: str
    int_field: int
    bool_field: bool


@pytest.mark.asyncio
async def test_nominal(datasource: base.DataSource) -> None:
    sample_attributes = SampleModel(str_field="a", int_field=12, bool_field=True)
    await datasource.insert(sample_attributes)

    entries = [entry async for entry in datasource.iterate()]
    assert len(entries) == 1

    await datasource.clear()
    entries = [entry async for entry in datasource.iterate()]
    assert len(entries) == 0
