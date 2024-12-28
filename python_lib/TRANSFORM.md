# The Cadmium TRANSFORM command

The TRANSFORM command is the [Cadmium](./README.md) equivalent of the SQL 
"SELECT" clause. It takes a single input table, and produces another table,
with one row in the output table for each row in the input table.

The full syntax is:

```TRANSFORM $table [TO $table] WITH columns;```

Each of the `$table` table names (the source and the target) can be either
a table name (given as a string without quotes), or a 
[parameter](parameters.md).

The `columns` are a comma-separated list of column definitions. A column
definition can either be a definition of a single column, or a definition
of a range of columns.

## Single column definitons

A single column is defined by `expression AS name`, where the expression
is a valid Cadmium [expression](expressions.md), while the name is an
unquoted string which is the column name.

## Column range definitions

A column range definition is basically a transformation that is defined in
the abstract, and then applied to a range of columns (identified by numeric
indices), to produce a range of columns in the output table.

The column range definition is defined by `expression FOR range AS name`.
The expression is evaluated in a special context, where there is an extra
pseudo-column, `?`, which is an alias for "the column currently being
processed".

The range is written as a Python-style range [beg:end], where beg and end
are 

The range is written as a Python-style range beg:end, where beg
and end are numbers

The column range d
the value of which (in each processed row) is the index
of the column being processed. 

