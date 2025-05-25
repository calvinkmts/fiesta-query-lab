import pytest
from fiesta_query_lab.builder import QueryBuilder
from fiesta_query_lab.schemas import FilterSpec, LogicalSpec, QuerySpec, AggregateSpec
from fiesta_query_lab.schemas import SelectSpec


@pytest.fixture
def query_spec():
    return QuerySpec(
        table="hello_world",
        select=[
            SelectSpec(field="col_a"),
            SelectSpec(field="col_b"),
        ],
        aggregates=[AggregateSpec(field="col_d", func="SUM")],
        where=LogicalSpec(
            op="AND",
            conditions=[
                FilterSpec(field="col_a", op="=", value="val_a"),
                LogicalSpec(
                    op="OR",
                    conditions=[
                        FilterSpec(field="col_b", op=">=", value="val_b"),
                        FilterSpec(field="col_c", op="!=", value="val_c"),
                    ],
                ),
            ],
        ),
    )


# def test_unknown_table_raises(query_spec):
#     query_builder = QueryBuilder(registry={}, use_alias=True)

#     with pytest.raises(ValueError) as exc:
#         query_builder.build(query_spec)

#     assert "Unknown table alias" in str(exc.value)


def test_build_columns(query_spec):
    query_builder = QueryBuilder(registry={})

    query_builder.build(query_spec)

    assert query_builder.query.columns == ["col_a", "col_b"]
    assert query_builder.query.wheres == [
        "AND col_a = val_a",
        "AND (col_b >= val_b OR col_c != val_c)",
    ]
    assert query_builder.query.aggregates == ["SUM(col_d)"]
    assert query_builder.query.group_bys == ["col_a", "col_b"]
