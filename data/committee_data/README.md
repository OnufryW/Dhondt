This is the tooling for defining and applying the minimal thresholds a
party needs to pass country-wide to get any seats.

`threshold.cfg` is the tooling for importing a CSV file containing threshold
definitions (expressed as integer numbers of percentages).

`apply_threshold.cfg` is the (much more magical) tooling for applying the
threshold - it takes the threshold data and a table that contains vote
counts (for any aggregation - by county, district, voivodship, whatever),
with the standard "one row per geographical location, one column per
party" (with the first column being the ID of the geo). It returns basically
the same table, except with the votes of parties that didn't pass the
threshold zeroed out.

`remove_zero_parties.cfg` takes a table (in the same format - first column
is the geo ID, all subsequent columns are parties), and removes the columns
that sum up to zero (that is, the parties that didn't get any votes,
presumably after applying `apply_threshold.cfg`
