from dataclasses import dataclass, field
from typing import Dict, List
from fiesta_query_lab.schemas import AggregateSpec, LogicalSpec
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
        self._build_where(where=spec.where)

        self.query.limit = spec.limit
        self.query.offset = spec.offset

    def render(self):
        pass

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

    def _build_where(self, where: LogicalSpec) -> None:
        self.query.wheres = [
            f"{where.op} {self._render_condition(con)}" for con in where.conditions
        ]

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

        self.query.group_bys = list(set(res))
