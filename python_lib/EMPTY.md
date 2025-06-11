# The EMPTY command

The EMPTY command creates an empty table. Sample usage:

``EMPTY AS table;``

The words `EMPTY` and `AS` are keywords, and have to be written capitalized.
The `table` is the name of the table, and can be any expression that resolves
to a [valid table name](names.md) that does not exist yet.

The table has zero rows and zero columns. To add columns,
use [TRANSFORM](TRANSFORM.md), to add rows, use [APPEND](APPEND.md).

