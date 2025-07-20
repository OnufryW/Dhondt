# The Cadmium CHECK command

The CHECK command is a way to verify that a table schema has the desired
properties. It takes a table and a sequence of properties of columns or
column ranges to check.

A simple usage would be:

```CHECK table COLUMN 1 NAMED id TYPED string
               COLUMN 2: TYPED int;```

This validates that the table has at least 1 column named `id`, which
contains strings, and any subsequent columns (of which there might be none)
contain integers.

The full syntax is:

```CHECK $table [COLUMN $name_or_number_or_range [ NAMED $name ] 
                  [ POSITION $position ] [ TYPED $type ] ]...```

All arguments are [expressions](expression.md) evaluated in the context of
parameters only.

The column can be specified as a column name, a column index, or a range
of indices. If the column is specified by name or index, Cadmium validates
the column exists. If the range is bounded from both sides (e.g., 
`3:5`), Cadmium also checks the columns exists; if it's one-side-bounded
or unbounded (i.e., `:`), it is legitimate for it to be empty.

The `NAMED` clause makes sense if the column is specified by position, it
validates the name of the column. Similarly, the `POSITION` clause makes
sense if the column is specified by name. The `TYPED` clause verifies
the contents of the column(s), checking each entry conforms to the specified
type. Allowed types are `int`, `float`, `string`, `bool` and `number` 
(which means `int` or `float`).
