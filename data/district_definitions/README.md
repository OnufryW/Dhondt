# District definition data.

Contains district definitions. The format is a headered SSV file, where
the first column is a prefix of a TERYT code (formally, a TERC code), the
second column is the electoral district ID that all the communities with a
TERC code beginning with that prefix should be assigned, and the third
column is a description of what this row describes, mainly for debugging
purposes.

The TERC codes are always assumed to be six-digit, zero-left-padded.

# District information data (from specific years)

The configs produce a file with the following columns:
 - id (the ID of the district, which is the string form of a number)
 - okw (the name of the city in which the district commission resides)
 - description (the text definition of the district)
 - seats (the number of seats in the Sejm assigned to this district)
 - voters (the number of people registered to vote in the district)
 - citizens (the number of citizens of the district, according to PKW)
 - registered_committees
 - registered_candidates
