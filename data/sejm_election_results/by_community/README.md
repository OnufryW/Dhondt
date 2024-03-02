# Sejm election results, aggregation by community.

Standardized format, using the 2023 format. The format is a headered SSV file,
with the following columns, in order:
1) TERYT of the community.
2) Community name.
3) County name.
4) Voivodship name.

Columns 5 and above exactly match the columns for the by-district aggregation
(see ../by_district/README.md), skipping district ID.

Note this means we have to remove the district ID from the 2023 dataset.

Various datasets treat foreign countries in different ways. However aggregated,
the foreign votes should be assigned an artificial teryt of 1499010

Additionally, the raw datasets generally have six (or five) digit TERYT codes,
without the "type" digit at the end. To make them conform to the standard
seven-digit setup, the transformed data adds a zero at the end of those codes,
and zero-pads them.

The 2019 dataset begins with the same four columns, then it skips the district
name and ID (which the by district 2019 dataset has), and then it continues
as the 2019 by district dataset.

The 2015 dataset has the district ID (which we ignore), it then runs the TERYT
and community name; it's missing the county and voivodship names; and then it
proceeds as the by district data does.
