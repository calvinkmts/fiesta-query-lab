# fiesta-query-lab

## Background

`fiesta-query-lab` is a lightweight Python library for building and rendering SQL queries from structured Pydantic Specifications. It provides:

- *Select, Where, Group By, Having, Order By, Limit/Offset* support.
- A builder pattern that separates AST (the spec) from SQL generation.
- A simple `use_alias` flag for frontend to database mapping.

The library aims to streamline safe, maintainable query generation in applications where SQL needs to adapt dynamically to user input.

## Current State

- *QueryBuilder* can render `SELECT`, `FROM`, `WHERE 1=1`, `GROUP BY`, `HAVING 1=1`, `ORDER BY`, `LIMIT`, and `OFFSET` clauses.
- `use_alias` flag exists, but does nothing.
- *Filter values* are interpolated directly into SQL strings, leading to potential syntax error for strings and exposure to SQL injection risks.

## Improvements

1. Automatic Mapping via `use_alias`

   - On `build()`, when `use_alias=True`, perform a single mapping process on the entire `QuerySpec`:
   - This centralizes alias resolution into one helper function and simplify downstream clause builder.

2. Parameterized SQL generation

   - Change clause builders (_render_filter / _render_logical) to emit placeholdered SQL fragments (e.g. %s or :param) instead of inlining raw values.
   - Collect a parallel params list for WHERE and HAVING conditions, ensuring values are bound via SQLAlchemy or DB driver APIs:
     ```python
     sql, params = builder.render()  # builder.render returns a tuple
     session.execute(text(sql), params)
     ```
   - This guarantees correct quoting, type handling, and robust protection from injection.
