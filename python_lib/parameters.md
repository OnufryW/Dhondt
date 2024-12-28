# Cadmium parameter syntax

In [Cadmium](./README.md), commands are executed in the context of a set of
parameters. This set is a string-to-string mapping, mapping parameter names
to values.

## Specifying parameters

There are two ways in which parameters can be specified.

First, if Cadmium is used to execute a config file, parameters can be passed in
at the command line. If you run

```python3 cadmium.py "../data/sejm_election_results/by_district.cfg" c "2023_by_community.cfg"```

then the `by_district.cfg` file will be executed in a context where the
parameter name `c` is mapped to the string `2023_by_community.cfg`.

Second, when running an import command, by default the parameter context is
passed to the imported config file. It can, however, be modified in two ways.
You can use the `WITH PARAM` option, to specify a new parameter to add.
This is the standard way in which one config file can reuse another config file
without requiring the user to specify all the params required by the dependency.

You can also use the `WITH PARAM_PREFIX` option. This will select out of the
current parameter context the parameter names beginning with the provided
prefix, and pass to the imported file only those parameters, with names stripped
of the prefix (and values unchanged). This is a good practice to "namespace"
the required paramters of dependencies. In particular, this is needed in the
case there is a diamond dependency on some config file, and we want to pass in
different values of some parameter at the bottom of the diamond to the two
paths.

So, running
```IMPORT "foo.cfg" WITH PARAM a "some_value" WITH PARAM_PREFIX b;```
if our current context contains the parameters `bb`, `bd` and `c` will run
the foo config in a context with parameters `a`, `b` and `d`.

## Reading parameters

In general, parameters are accessed by `$PARAMETER_NAME` --- so, for example, a
parameter named `foo` will be accessed by `$foo`. For now, Cadmium doesn't
support parameter access in all possible places --- most notably, it is not
supported within [expressions](expressions.md). Places that do support
reading parameters are specified in the detailed documentation of every
command, but two important cases where you should expect parameters to work:

 - wherever you specify a table name (as a source or target of some operation),
 - wherever you specify a filesystem path (e.g., in a [LOAD](LOAD.md) or
   [IMPORT](IMPORT.md) command)

In addition, you can use parameters in many places where you specify a column
outside of the expression context (e.g., when you're specifying the data and id
columns in [VISUALIZE](VISUALIZE.md).

An example of reading a parameter would be:

```IMPORT $data WITH PREFIX data;```
