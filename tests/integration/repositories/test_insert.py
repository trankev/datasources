import pydantic
import pytest

from datasources.repositories import base


class SampleModel(pydantic.BaseModel):
    str_field: str
    int_field: int
    bool_field: bool


@pytest.mark.asyncio
async def test_nominal(datasource: base.DataSource) -> None:
    entries = [entry async for entry in datasource.iterate()]
    assert len(entries) == 0
    sample_attributes = SampleModel(str_field="a", int_field=12, bool_field=True)
    try:
        await datasource.insert(sample_attributes)

        entries = [entry async for entry in datasource.iterate()]
        assert len(entries) == 1
        attributes = [entry.attributes for entry in entries]
        assert attributes == [sample_attributes]
    finally:
        await datasource.clear()
