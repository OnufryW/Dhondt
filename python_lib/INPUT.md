# The Cadmium INPUT TABLES command

The INPUT TABLES command specifies what tables are expected to be present
in the context. It is used as a way to specify the inputs to a runnable
Cadmium file.

The syntax is

```INPUT TABLES $table...```

The `$table` arguments are expressions evaluated in the context of
parameters only, and are expected to evaluate to table names.

Usually, what the command does is simply check that the tables with the
provided names are present, and throw an error if they're not. It also
has a special semantic when used in a runnable file that was invoked with
a RUN ... FROM ... clause. In that case, the tables provided in the FROM
clause are renamed to the names specified in the INPUT TABLES command, in
the same order. So, for example, you can write in your runnable file

```INPUT TABLES a, b;```

and then run the file with 

``` RUN "file.cfg" FROM b, d; ```

and the table `b` from the parent environment will be renamed to `a` in the
child, while `d` from the parent environment will be renamed to `b` in the
child. For that reason, your file should generally include only one 
`INPUT TABLES` command, and it's recommended it's the first command.
