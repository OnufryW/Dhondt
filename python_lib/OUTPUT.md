# The Cadmium OUTPUT TABLES command

The OUTPUT TABLES command is a way for a Cadmium runnable file to specify
which tables should be considered the output of the script (as opposed to
being auxilliary tables).

The usage is 

```OUTPUT TABLES table1, table2;```

This is the full syntax, there are no extra parameters - it's just

```OUTPUT TABLES table...```

The command does two things:

 * It validates that all the tables specified in the list exist, and throws
   an error otherwise.
 * It drops all the tables not listed.

This command is intended to partially be used as documentation for scripts,
declaring what table is the output of the script.

See also the [DROP](DROP.md) command.
