# The UNION command

The `UNION` command serves to merge a number of tables
into one table, where the schema is (by default) their shared schema, while the
rows are copied over from all tables (formally, the rows of the output
table are the rows of the first table followed by the rows of the second
table, etc.). Sample usage:

``UNION table1, table2 TO table;``

`UNION` and `TO` are keywords and have to be capitalized. Between `UNION`
and `TO` there can be any number of expressions that denote the tables to
be unioned, separated by commas. These expressions are each evaluated in
the [parameter context](context.md), and should evaluate to names of
existing tables.

After the `TO` there is, again, an expression denoting the name of the target
table (where the unioned results will be stored). This should either resolve
to a [valid table name](names.md) that does not exist yet, or to one of the
unioned tables, in which case that table will be overwritten. It cannot
be skipped.

After the target name, there can be a parameter specifying how to merge
the schemata of the output table. There are five options:

 * WITH EQUAL SCHEMA (the default, does not need to be specified) - we
   require that the schema of each table is exactly the same (same number
   of columns, with the same names, in the same order), and error out
   otherwise.
 * WITH REORDERED SCHEMA - we still require the schema is the same for
   each table, but accept a reordering. The output schema will be in the
   order taken from the first table.
 * WITH SKIP EXTRA COLUMNS - a column name will be present in the output
   if and only if it was present in every of the input tables. Order comes
   from the first table listed.
 * WITH ALL COLUMNS - a column name will be present in the output if it
   appears in any of the input tables. The order of columns is in order
   of appearance - so, a column that first appears in an earlier table will
   be earlier, and between columns that appear for the first time in the
   same table, the order from that table is preserved. The output rows will
   contain an empty string for any column that was not present in the table
   that this row comes from.
 * WITH FIRST TABLE COLUMNS - we take the schema from the first table. We
   drop any columns not present in the first table, and fill in missing
   values as in WITH ALL COLUMNS.
