# Composable data manipulation language (Cadmium).

This is an introduction to Cadmium. If you're looking for a reference, it's [here](reference.md)

Cadmium allows the processing of tabular data, and dumping it into semicolon-separated tables, or into maps (bitmaps).

Cadmium processes series of commands. These commands can be put into a config file and executed,
or input into the interactive tool. The documentation below describes the language.

To run the interactive tool, `python3 cadmium.py`. To execute a config file,
`python3 cadmium.py FILENAME [PARAM1_NAME PARAM1_VALUE]*`. The introduction below assumes you will input the commands into a session of the interactive tool.

## Loading data / LOAD

Data processing usually begins with loading some CSV or SSV or similar file. You load such data by running LOAD:

```LOAD table FROM "../data/commitee_data/2015.csv";```

The words `LOAD` and `FROM` are keywords. `table` is the name of the table you're loading into, it's an identifier you will use later on; most of Cadmium operates on tables. The quoted (you can use double or single quotes) string is the path (relative to the current directory, which for now is the directory you run Cadmium in) where the data is located.

This particular table happens to contain the committees that ran in the 2015 parliamentary elections in Poland, and what was the percentage threshold of votes they had to get to put any MPs into the Sejm. The threshold, in practice, depends on whether the committee was a coalition (with an 8% threshold), a single party (a 5% threshold), or a minoriy committee (0% threshold). 

Cadmium expects a semicolon-separated file, where the each line except the first contains one row of data, and the first line contains the header (that is, the names of the individual columns). Load will fail if this is not satisified. All the data is loaded as strings. Empty rows or rows beginning with a hash sign (`#`) are ignored.

The full documentation is [here](LOAD.md), see also the [EMPTY](EMPTY.md) command. 

 ## Printing data / DUMP

 You print a previously loaded / created table using `DUMP`. So, after loading the table as above, you can run

 ```DUMP table;```

 And see the contents of the table on the screen. You can also dump the table to a file for further processing, for this, ```DUMP table TO "./dump.ssv";```

 ## Reusing cadmium commands / IMPORT

 A large part of the point of Cadmium is the "composable" part - that you can easily define a Cadmium script that defines some tables, and then import that script into another script, thus reusing the calculation. You do this through the `IMPORT` command:

 ```IMPORT "../data/district_definitions/2019.cfg";```

If you run this after running the LOAD command given above, you'll get an error. This is because we already loaded a table named "table", and Cadmium scripts by convention produce a table named "table" --- and, of course, you can't have two tables with the same name. There are two ways around this. First, we can get rid of the old committee data table:

```DROP table;```

The second way is that you can prefix the names of all tables imported from a script with some string. E.g., running

```IMPORT "../data/district_definitions/2019.cfg" WITH PREFIX "dd_";```

will create a table called `dd_table`.

The `WITH PREFIX` is a standard way of passing options to commands. One more common option to the `IMPORT` command is the `WITH PARAM` option, through which you can pass a string parameter. So, for example, if you want to use the committee thresholds data, you would usually not do that by loading the raw data through `LOAD`, but rather use the accompanying config:

```IMPORT "../data/committee_data/threshold.cfg" WITH PARAM threshold_data "2015.csv";```

(you can also add a `WITH PREFIX`). It's a convention in Cadmium that raw data dumps are accompanied by a config file that can correctly parse them. So, let's look at the contents of the threshold.cfg file that we're importing here.

It contains two commands. The first one is one we know, the `LOAD` command, except it doesn't provide a string as the parameter to the `FROM`, it provides `$threshold_data`. This is a reference to the `threshold_data` parameter we provided. If you run

```IMPORT "../data/committee_data/threshold.cfg";```

without providing the parameter, you will get an error telling you that the parameter threshold_data expected by threshold.cfg is missing. Note that when we provided the parameter, we just provided the value `2015.csv`, without the path. What's up with that? In Cadmium, `IMPORT` commands are executed in the context of the directory in which the imported script is contained (and so, the relative path to the 2015.csv file is `./2015.csv`). This is critical for composability, because it allows scripts to work when referring to other files to load / import regardless of where they're called from.

The second command in the config file is one we didn't encounter yet, `TRANSFORM`. So, let's have a look at that.

## Transforming tables / TRANSFORM

`TRANSFORM` allows us to modify the data in a table, row by row. It's the rough equivalent of SQL's "SELECT", although with a few differences. Here, after a `WITH` keyword, we provide the comma-separated columns we want the table to have. We can refer to column values either by `$1`, `$2` (one-indexed column numbers), or by column names (in this case `Party` and `Threshold`). So, we could instead write

```TRANSFORM table WITH Party AS Party, int(Threshold) AS Threshold;```

We can see here why it's convenient to use the `IMPORT` script instead of loading the data directly --- when data is loaded, all columns are string-typed, while the script already transforms the threshold column (which, in reality, contains integers) to be integer typed. So, we can now do things like

```TRANSFORM table WITH Party AS Party, Threshold * 2 AS Threshold;```

You can see the various functions you can apply to data on the functions list page; and the various power-user expression options on the expression documentation page.

## State and history

In the interactive tool, it's useful to see the current state of the program. You can run `LIST TABLES` to, unsurprisingly, list tables, and `DESCRIBE table` (where `table` is the name of a table) to show the schema (that is, the list of columns, with one sample entry for each) of the table.

In the interactive tool, you can also look at the history of commands with `HISTORY PRINT`, save the history into a `history` file with `HISTORY STORE`, and then load it with `HISTORY LOAD`. This is useful for maintaining sessions, as well as for turning the results of an interactive session into a reusable config file.
