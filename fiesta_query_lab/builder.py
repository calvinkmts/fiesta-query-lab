from dataclasses import dataclass, field
from typing import Dict, List, Literal
from fiesta_query_lab.schemas import AggregateSpec, LogicalSpec, OrderBySpec
from typing import Union, Optional
from fiesta_query_lab.schemas import SelectSpec
from fiesta_query_lab.schemas import FilterSpec, QuerySpec


@dataclass
class Query:
    table: str
    columns: List[str] = field(default_factory=list)
    aggregates: List[str] = field(default_factory=list)
    wheres: List[str] = field(default_factory=list)
    group_bys: List[str] = field(default_factory=list)
    havings: List[str] = field(default_factory=list)
    order_bys: List[str] = field(default_factory=list)
    limit: Optional[int] = None
    offset: Optional[int] = None


class QueryBuilder:
    def __init__(
        self, max_joins: int = 3, use_alias: bool = False, registry: Dict = {}
    ) -> None:
        self.max_joins = max_joins
        self.use_alias = use_alias

    def build(self, spec: QuerySpec):
        self.query = Query(table=spec.table)

        self._build_select(columns=spec.select)
        self._build_aggregates(aggregates=spec.aggregates)
        self._build_group_by(group_bys=spec.group_bys)

        if spec.where:
            self._build_conditional(logicals=spec.where, target="wheres")

        if spec.havings:
            self._build_conditional(logicals=spec.havings, target="havings")

        self._build_order_by(order_bys=spec.order_bys)

        self.query.limit = spec.limit
        self.query.offset = spec.offset

    def render(self) -> str:
        lines = []
        lines.append("SELECT")

        temp_cols = self.query.columns + self.query.aggregates
        for i, select in enumerate(temp_cols):
            comma = "," if i < len(temp_cols) - 1 else ""
            lines.append(f"    {select}{comma}")

        lines.append(f"FROM {self.query.table}")

        if len(self.query.wheres) > 0:
            lines.append("WHERE 1=1")

            for i, where in enumerate(self.query.wheres):
                lines.append(f"    {where}")

        if len(self.query.group_bys) > 0:
            lines.append("GROUP BY")

            for i, group_by in enumerate(self.query.group_bys):
                comma = "," if i < len(self.query.group_bys) - 1 else ""
                lines.append(f"    {group_by}{comma}")

        if len(self.query.havings) > 0:
            lines.append("HAVING 1=1")

            for i, having in enumerate(self.query.havings):
                lines.append(f"    {having}")

        if len(self.query.order_bys) > 0:
            lines.append("ORDER BY")

            for i, order_by in enumerate(self.query.order_bys):
                comma = "," if i < len(self.query.order_bys) - 1 else ""
                lines.append(f"    {order_by}{comma}")

        if self.query.limit is not None:
            lines.append(f"LIMIT {self.query.limit}")

        if self.query.offset is not None:
            lines.append(f"OFFSET {self.query.offset}")

        return "\n".join(lines)

    def _build_select(self, columns: List[SelectSpec]) -> None:
        res = []
        for col in columns:
            res.append(col.field)

        self.query.columns = res

    def _build_aggregates(self, aggregates: List[AggregateSpec]) -> None:
        res = []
        for agg in aggregates:
            if not agg.alias:
                res.append(f"{agg.func}({agg.field})")
            else:
                res.append(f"{agg.func}({agg.field}) AS {agg.alias}")

        self.query.aggregates = res

    def _build_conditional(
        self, logicals: LogicalSpec, target: Literal["wheres", "havings"] = "wheres"
    ) -> None:
        res = [
            f"{logicals.op} {self._render_condition(con)}"
            for con in logicals.conditions
        ]

        setattr(self.query, target, res)

    def _render_condition(self, condition: Union[FilterSpec, LogicalSpec]) -> str:
        if isinstance(condition, FilterSpec):
            return self._render_filter(condition)
        return self._render_logical(condition)

    def _render_logical(self, logical: LogicalSpec) -> str:
        parts = [self._render_condition(c) for c in logical.conditions]
        temp_result = f" {logical.op} ".join(parts)
        return f"({temp_result})"

    def _render_filter(self, filter: FilterSpec) -> str:
        return f"{filter.field} {filter.op} {filter.value}"

    def _build_group_by(self, group_bys: List[str]) -> None:
        res = []

        if group_bys:
            for group_by in group_bys:
                res.append(group_by)

        if self.query.columns and self.query.aggregates:
            for field in self.query.columns:
                res.append(field)

        self.query.group_bys = res

    def _build_order_by(self, order_bys: List[OrderBySpec]) -> None:
        res = []

        if order_bys:
            for order_by in order_bys:
                res.append(f"{order_by.field} {order_by.direction}")

        self.query.order_bys = res
