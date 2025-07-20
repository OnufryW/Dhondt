# The Cadmium RUN command

The RUN command is the Cadmium way of using a pre-prepared Cadmium config
file. It takes a path to a Cadmium file, executes the command in that file,
and adds the resulting table(s) to the execution context.

A simple usage would be:

```RUN FILE "data/sejm_election_results/just_votes.cfg" FROM table INTO table;```

The full (non-streaming) syntax is:

```RUN (FILE $file | COMMAND $command) 
   [FROM ($input_table1 | FILE $file | COMMAND $command) ...] 
   [INTO $output_table] 
   [WITH PARAM $param_name $param_value] ... 
   [WITH PARAM_PREFIX $prefix]```

All the arguments except `$param_name` (`$file`, `$command`, `$input_tableK`,
`$output_table`, `$param_value`, `$prefix`) are 
[expressions](expressions.md) evaluated in the context of parameters only.
Usually, they'd be either strings (quoted in the case of $file and $command,
quoted or not in the other cases) or 
[parameters](parameters.md), but more complex expressions (like
concatenation of parameters) are also allowed. The `$param_name` has to
be an unquoted string.

What this command does is it executes a series of commands in the correct
environment. The series of commands either is given directly (the `COMMAND`
variant), or taken from a file (which should contain the commands as text)
in the `FILE` variant.

The environment includes:
 * In the case of the FILE variant, running in the directory where the file
   lives. This matters for the purpose of any [IMPORT](IMPORT.md) / 
   [RUN](RUN.md) / [LOAD](LOAD.md) commands present in the file, where the
   paths are taken relative to the file itself.
 * Only tables listed in the FROM clause are present in the environment,
   other tables are hidden (see also the [INPUT TABLES](INPUT.md) command).
   These tables are either listed directly (in which case they have to be
   present in the current environment), are the result of running a COMMAND
   (in which case the command given needs to return only one table, e.g., 
   through the use of [OUTPUT TABLES](OUTPUT.md)), or by running a specified
   file. In the `FROM FILE` case, the file will be run in its own environment,
   which will not contain any tables, will include all the parameters of the
   parent, and the file needs to produce only one table. If something more
   complex is needed, you can always `FROM COMMAND "RUN FILE $file ...;"`.
 * If the WITH PARAM_PREFIX clause is specified, only the parameters with
   names starting with the specified prefix are present in the environment.
   Otherwise, all parameters from the parent are passed along. Parameters
   specified with the WITH PARAM clause are also added (and overwrite any
   pre-existing parameters).
After running the command:
  * If no INTO clause was specified, all the tables produced by the child
    are added to the parent. If any of the names of the child tables
    collides with a name of some parent table, an error is thrown.
  * If there is an INTO clause, we expect the child to contain exactly
    one table at the end of the execution (either by not creating more,
    through the use of [DROP](DROP.md), or the use of 
    [OUTPUT TABLE](OUTPUT.md). If there are more (or less), an error is
    thrown. If there is exactly one table, this table will be transferred
    to the parent environment, under the specified name (overwriting any
    present table with that name).

# The streaming RUN syntax

For the common case where where we string together a bunch of RUN commands
where the output of the previous one is the sole input of the next one,
we can use the streaming syntax. There, instead of writing

``` RUN FILE "a.cfg" FROM a, b, c INTO d WITH PARAM "x" 12;
    RUN FILE "b.cfg" FROM d INTO e WITH PARAM "foo" 7;
    RUN FILE "c.cfg" FROM e INTO f;
    RUN FILE "d.cfg" FROM f INTO g;```

we can write

```
   RUN FILE "a.cfg" FROM a, b, c WITH PARAM "x" 12 >
       FILE "b.cfg" WITH PARAM "foo" 7 >
       FILE "c.cfg" >
       FILE "d.cfg" INTO g;
```

This, of course, assumes that we don't care about the intermediate tables
`d`, `e` and `f`, just `g`. This is basically syntactic sugar with temporary
names provided for the output results of the intermediate commands. It only
works if `b.cfg`, `c.cfg` and `d.cfg` use the [INPUT TABLE](INPUT.md)
command to specify their input (since the name of the table that will get
passed in is generated randomly at runtime).

You can also use the COMMAND variant, typically when you don't want to break
a stream, e.g., 

```
RUN FILE "a.cfg" FROM a, b, c WITH PARAM "x" 12 >
    COMMAND "INPUT TABLES t; PIVOT t;" >
    FILE "c.cfg" >
    FILE "d.cfg" INTO g;
```

