# District definition data.

Contains district definitions. The format is a headered SSV file, where
the first column is a prefix of a TERYT code (formally, a TERC code), the
second column is the electoral district ID that all the communities with a
TERC code beginning with that prefix should be assigned, and the third
column is a description of what this row describes, mainly for debugging
purposes.

The TERC codes are always assumed to be seven-digit, zero-left-padded.
