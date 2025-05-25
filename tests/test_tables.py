import pytest

from fiesta_query_lab.tables import TABLES, Column, register_table


@pytest.fixture(autouse=True)
def clear_registry():
    TABLES.clear()


cases = [
    ("explicit aliases", ("foo", "bar"), None, ["foo", "bar"]),
    ("fallback tablename", (), "baz_table", ["baz_table"]),
    ("no alias or tablename", (), None, []),
]


@pytest.mark.parametrize(
    "name, aliases, tablename, expected_keys", cases, ids=[c[0] for c in cases]
)
def test_register_table(name, aliases, tablename, expected_keys):
    attrs = {}
    if tablename:
        attrs["__tablename__"] = tablename

    Dummy = type("Dummy", (object,), attrs)

    decorator = register_table(*aliases)
    returned = decorator(Dummy)

    assert returned is Dummy

    assert set(TABLES.keys()) == set(expected_keys)
    for key in expected_keys:
        assert TABLES[key] is Dummy


def test_register_table_duplicates():
    @register_table("dup")
    class First:
        pass

    @register_table("dup")
    class Second:
        pass

    assert list(TABLES.keys()) == ["dup"]
    assert TABLES["dup"] == Second


def test_register_table_store_attributes():
    col = Column(alias="frontend_field", column_name="fnt_fld")
    assert col.alias == "frontend_field"
    assert col.column_name == "fnt_fld"
