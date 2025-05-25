import pytest
from fiesta_query_lab.builder import QueryBuilder
from fiesta_query_lab.schemas import (
    FilterSpec,
    LogicalSpec,
    QuerySpec,
    AggregateSpec,
    OrderBySpec,
)
from fiesta_query_lab.schemas import SelectSpec


cases = [
    (
        "basic where + group",
        QuerySpec(
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
        ),
        ["col_a", "col_b"],
        ["AND col_a = val_a", "AND (col_b >= val_b OR col_c != val_c)"],
        ["SUM(col_d)"],
        ["col_a", "col_b"],
        "\n".join(
            [
                "SELECT",
                "    col_a,",
                "    col_b,",
                "    SUM(col_d)",
                "FROM hello_world",
                "WHERE 1=1",
                "    AND col_a = val_a",
                "    AND (col_b >= val_b OR col_c != val_c)",
                "GROUP BY",
                "    col_a,",
                "    col_b",
            ]
        ),
    ),
    (
        "order_by + limit/offset",
        QuerySpec(
            table="t",
            select=[SelectSpec(field="x")],
            aggregates=[],
            where=None,
            group_bys=[],
            order_bys=[
                OrderBySpec(field="x", direction="DESC"),
                OrderBySpec(field="y", direction="ASC"),
            ],
            limit=5,
            offset=10,
        ),
        ["x"],
        [],
        [],
        [],
        "\n".join(
            [
                "SELECT",
                "    x",
                "FROM t",
                "ORDER BY",
                "    x DESC,",
                "    y ASC",
                "LIMIT 5",
                "OFFSET 10",
            ]
        ),
    ),
]


@pytest.mark.parametrize(
    "desc, spec, exp_cols, exp_wheres, exp_aggs, exp_groupbys, exp_sql",
    cases,
    ids=[c[0] for c in cases],
)
def test_query_builder(
    desc, spec, exp_cols, exp_wheres, exp_aggs, exp_groupbys, exp_sql
):
    qb = QueryBuilder(registry={})
    qb.build(spec)

    assert qb.query.columns == exp_cols
    assert qb.query.wheres == exp_wheres
    assert qb.query.aggregates == exp_aggs
    assert qb.query.group_bys == exp_groupbys

    assert qb.render() == exp_sql
