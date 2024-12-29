# Expression and Command Contexts

This is a part of the implementation documentation, not the user guide.

## Expression context.

The expression context is the context parameter of the Eval function of
the Expression class.

### Contents

In expressions, the context is a dict containing the following:

 * For each column, the mapping from column name to 1-indexed column number
 * The mapping of `?last` to the number of columns
 * `__params`, mapping to a dict from param name to value

For "standard" statements (filter, transform, join), we also have:
 * `__data`, which maps to the row (list of values, 0-indexed)

For aggregations, we have:
 * `__data`, which maps to the part of the row with the columns that are
   in the grouping key (it's also a dict, not a list, but the keys are
   0-indexed column indices)
 * `__group_data`, which maps to a list of dicts, one for each row grouped
   into the currently processed key, the dict is maps the remaining column
   indices to values.

For aggregations, when we're within an aggregating function, we have
 * `__data`, which is the row, but presented as a dict, not a list.
   (I might consider making it a list, since we're effectively in a 
   "normal" expression now).

For "header" expressions (that is, expressions evaluated in the context of
the header, not a specific row), we only have the column mappings and last,
and `__data` is mapped to None

In all the cases above, if we're in a column range definition, we also have
 * `?` mapping to the name of the column currently being processed.

Finally, in the context of defining a statement, where we don't even have
a columns list, we only have the `__params`.

### Definitions

The expression context is created in the following places:
 * RangeExpression in command.py, which is the thing that covers the
   column range definition, for evaluating header expressions. Created four
   times: for evaluating the beg and end expressions, for evaluating the
   AS expression, and for evaluating the actual values.
 * Within the Filter, Transform and Join commands (twice in the last case),
   to create the contexts for evaluation of expressions.
 * Within the Aggregate command, to create the special aggregation context
 * In the AggregateExpr expression, to create the child context for
   evaluating the individual rows mapped to one key.

## Command Context

The command context (that is, the arguments to Command.Eval) is two
variables: tables and params.

Params is a dict mapping param names to param values.

Tables is a dict mapping table names to individual tables.

A table is represented by a pair:
 * A dict mapping column names to column indices
 * A list of lists (rows), which contain the values.
