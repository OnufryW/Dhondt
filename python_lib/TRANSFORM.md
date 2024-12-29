# The Cadmium TRANSFORM command

The TRANSFORM command is the [Cadmium](./README.md) equivalent of the SQL 
"SELECT" clause. It takes a single input table, and produces another table,
with one row in the output table for each row in the input table.

A simple usage would be:

```TRANSFORM table WITH a AS a, b AS b, sqrt(a * a + b * b) AS c;```

A more complex example would be:

```TRANSFORM $src TO table WITH curr() FOR :, curr() * curr() FOR 4: AS currname() + "_sqr";```

The full syntax is:

```TRANSFORM $source_table [TO $target_table] WITH columns;```

The source table and target table are [expressions](expressions.md)
evaluated in the context of parameters only. Usually, they would be either
table names (as unquoted strings), or [parameters](parameters.md).

If the `TO` clause is missing, the transformation is in-place, which means
the source table is replaced by the output of the transformation.

The `columns` are a comma-separated list of column definitions. A column
definition can either be a definition of a single column, or a definition
of a range of columns.

## Single column definitons

A single column is defined by `expression AS name`, where the expression
is a valid Cadmium [expression](expressions.md), which will be evaluated
in the context of every row to produce an output, while the name is an
[expression](expressions.md) that should return a string, evaluated in the
context of the header of the source table, which will be used as the name of
the column in the output table.

TODO: I should work to make it so that if only one column is referenced in
the expression, the `AS` clause is optional, and skipping it means
preserving the column name. Right now, AS is required.

## Column range definitions

A column range definition is basically a transformation that is defined in
the abstract, and then applied to a range of columns (identified by numeric
indices), to produce a range of columns in the output table.

The column range definition is defined by `expression FOR range [AS name]`.
The `range` is a standard Cadmium [range](ranges.md), with both expressions
evaluated in the context of the header of the source table. The range 
is evaluated once to get a range of columns, the `expression` is applied
once for each column, with the special [functions](functions.md#curr) 
`curr()` and `currname()` being available. The `name` after the `AS`
keyword is an expression (evaluated in the context of the header of the
source table) that should evaluate to a different string for each of the
columns in the range. The special [function](functions.md#currname) is
available.

