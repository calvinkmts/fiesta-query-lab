from typing import Any, Callable, Dict, Type, TypeVar


TABLES: Dict[str, Type[Any]] = {}

T = TypeVar("T")


def register_table(*aliases: str) -> Callable[[Type[T]], Type[T]]:
    def decorate(cls: Type[T]) -> Type[T]:
        names = aliases or (getattr(cls, "__tablename__", None),)
        for name in names:
            if not name:
                continue

            TABLES[name] = cls

        return cls

    return decorate


class Column:
    def __init__(self, alias: str, column_name: str) -> None:
        self.alias = alias
        self.column_name = column_name
