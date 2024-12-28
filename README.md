# Dhondt

This is a bunch of tools to measure the impact of a single vote in parliamentary elections in Poland.

## The calculation library (Cadmium).

The calculation language (called Cadmium) is [here](python_lib/README.md). It's a pretty powerful, but slow,
tool to process data in a SQL-like fashion, but allowing some stuff I haven't seen SQL do.

## The core data.

The core data is in [here](data/README.md). It's mostly in the form of raw data dumps,
plus Cadmium config files that can reproduce various outputs.
