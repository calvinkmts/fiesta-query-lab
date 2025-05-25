from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Any, Union


class SelectSpec(BaseModel):
    field: str
    alias: Optional[str] = None


class FilterSpec(BaseModel):
    field: str
    op: str
    value: Any


class LogicalSpec(BaseModel):
    op: Literal["AND", "OR"]
    conditions: List["Condition"]


Condition = Union[FilterSpec, LogicalSpec]

LogicalSpec.model_rebuild()


class AggregateSpec(BaseModel):
    func: Literal["SUM", "COUNT", "AVG", "MIN", "MAX"]
    field: str
    alias: Optional[str] = None


class QuerySpec(BaseModel):
    table: str
    select: List[SelectSpec] = Field(default_factory=list)
    aggregates: List[AggregateSpec] = Field(default_factory=list)
    where: Optional[LogicalSpec] = None
    group_bys: List[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
