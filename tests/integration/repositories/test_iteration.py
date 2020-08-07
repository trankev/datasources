import typing

import pytest

from datasources import models
from datasources.repositories import base
from tests.integration.repositories import models as test_models

DATASET = [
    test_models.SampleModel(str_field="a", int_field=12, bool_field=False),
    test_models.SampleModel(str_field="b", int_field=7, bool_field=False),
]


@pytest.fixture(name="populated_datasource", scope="module")
async def populated_datasource_fixture(
    datasource: base.DataSource,
) -> typing.AsyncIterator[base.DataSource]:
    for entry in DATASET:
        await datasource.insert(entry)
    yield datasource
    await datasource.clear()


@pytest.mark.asyncio
async def test_nominal(populated_datasource: base.DataSource) -> None:
    attributes = [entry.attributes async for entry in populated_datasource.iterate()]
    assert attributes == DATASET


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("direction", "expected_values"),
    (
        (models.SortDirection.ascending, [7, 12]),
        (models.SortDirection.descending, [12, 7]),
    ),
)
async def test_single_field_sorting(
    populated_datasource: base.DataSource,
    direction: models.SortDirection,
    expected_values: typing.List[int],
) -> None:
    sort = [
        models.SortOption(field="attributes.int_field", direction=direction),
    ]
    entries = [entry async for entry in populated_datasource.iterate(sort=sort)]
    assert len(entries) == 2
    int_values = [entry.attributes.int_field for entry in entries]
    assert int_values == expected_values


@pytest.mark.asyncio
async def test_double_field_sorting(populated_datasource: base.DataSource) -> None:
    sort = [
        models.SortOption(field="attributes.bool_field", direction=models.SortDirection.ascending),
        models.SortOption(field="attributes.str_field", direction=models.SortDirection.descending),
    ]
    entries = [entry async for entry in populated_datasource.iterate(sort=sort)]
    assert len(entries) == 2
    str_values = [entry.attributes.str_field for entry in entries]
    assert str_values == ["b", "a"]


@pytest.mark.asyncio
async def test_limit(populated_datasource: base.DataSource) -> None:
    sort = [
        models.SortOption(field="attributes.str_field", direction=models.SortDirection.ascending),
    ]
    entries = [entry async for entry in populated_datasource.iterate(limit=1, sort=sort)]
    assert len(entries) == 1
    assert entries[0].attributes == DATASET[0]


@pytest.mark.asyncio
async def test_offset(populated_datasource: base.DataSource) -> None:
    sort = [
        models.SortOption(field="attributes.str_field", direction=models.SortDirection.ascending),
    ]
    entries = [entry async for entry in populated_datasource.iterate(offset=1, sort=sort)]
    assert len(entries) == 1
    assert entries[0].attributes == DATASET[1]


@pytest.mark.asyncio
async def test_filter_no_results(populated_datasource: base.DataSource) -> None:
    filters = [
        models.FilterOption(
            field="attributes.int_field",
            value=65,
        ),
    ]
    entries = [entry async for entry in populated_datasource.iterate(filters=filters)]
    assert len(entries) == 0


@pytest.mark.asyncio
async def test_filter_one_entry(populated_datasource: base.DataSource) -> None:
    filters = [
        models.FilterOption(
            field="attributes.int_field",
            value=12,
        ),
    ]
    entries = [entry async for entry in populated_datasource.iterate(filters=filters)]
    assert len(entries) == 1
    assert entries[0].attributes == DATASET[0]
