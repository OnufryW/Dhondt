# The APPEND command

The `APPEND` command adds one row to a pre-existing table. Sample usage:

``APPEND 1, "John Doe", 12 + 12 TO salaries;``

The words `APPEND` and `TO` are keywords, and have to be capitalized.

Between `APPEND` and `TO` is a comma-separated list of expressions. The
length of the list has to be equal to the number of columns of the table.
These are standard expressions, evaluated in the
[parameter context](context.md). After `TO` there is one expression, also
evaluated in the [parameter context](context.md), that should resolve to the
name of the table we are appending to.

As usual, there's no static type checking of the schema validity.
