# Sejm election results, aggregation by district.

Standardized format, using the 2023 format. The format is a headered SSV
file, with the following columns, in order:
1) District ID (i.e., District Number)
2) # Commissions in the district.
3) # Commissions taken into account in the district.
4) # Voting cards handed to the commissions
5) # Voters eligible to vote
6) # Unused voting cards
7) # Voters who received voting cards in person
8) # Voters who received voting cards by mail
9) # Voters who received voting cards, in total (should be 7 + 8)
10) # Voters voting through an intermediary
11) # Voters voting based on right-to-vote papers
12) # Vote-by-mail envelopes received (should be 13+14+15+16+17)
13) # Vote-by-mail envelopes without the declaration
14) # Vote-by-mail envelopes where the declaration is not signed
15) # Vote-by-mail envelopes without a vote envelope
16) # Vote-by-mail envelopes where the vote envelope wasn't sealed
17) # Vote-by-mail vote envelopes added to the urn
18) # Cards taken from the urn (should be 20 + 21)
19) # In that, cards taken from vote envelopes (ideally, equal to 17)
20) # Invalid cards
21) # Valid cards (should be 22 + 26)
22) # Invalid votes (should be 23+24+25)
23) # Votes invalid because of too many x-es
24) # Votes invalid because of no x
25) # Votes invalid because of a struck out list
26) # Votes valid, total (should be sum of all remaining columns)
27, onward - # votes towards the individual committees

Transformation for 2019:
1) District ID -> 1
2) District Name -> /null
3) Cards handed to commission -> 4
4) Eligible voters -> 5
5) Unused voting cards -> 6
6) Voters who received voting cards -> 7
7) Voters voting through an intermediary -> 10
8) Voters voting through right-to-vote papers -> 11
9) Voters who received voting cards by mail -> 8
10) Envelopes received -> 12
11) No declaration -> 13
12) Unsigned declaration -> 14
13) No voting envelope -> 15
14) Unsealed voting envelope -> 16
15) Voting envelopes added to urn -> 17
16) Cards out of urn -> 18
17) Cards out of voting envelope -> 19
18) Invalid cards -> 20
19) Valid cards -> 21
20) Invalid votes -> 22
21) Too many Xs -> 23
22) No Xs -> 24
23) Struck out list -> 25
24) All valid votes -> 26
25) and onward: votes towards individual committees

Notes: Commission data is missing, we'll insert zeroes into columns 2 and 3.
Column 9 is missing, we'll insert 7+8

Transformation for 2015:
1) District ID -> 1
2) District seat -> /null
3) Number of commissions -> 2
4) Number of voters -> 5
5) Received cards -> 4
6) Unused cards -> 6
7) Voters who received voting cards -> 7
8) Voters voting through an intermediary -> 10
9) Voters voting based on right-to-vote papers -> 11
10) Voting packets -> 8
11) Envelopes received -> 12
12) No declaration -> 13
13) Unsigned declaration -> 14
14) No vote envelope -> 15
15) Unsealed vote envelope -> 16
16) Vote envelopes tossed in -> 17
17) Cards out of urn -> 18
18) Cards out of vote envelopes -> 19
19) Invalid cards -> 20
20) Valid cards -> 21
21) Invalid votes -> 22
22) Too many Xs -> 23
23) No Xs -> 24
24) Struck out list -> 25
25) Valid votes -> 26
26 and onward): Votes towards individual committes.

Notes: Column 3 is missing, use column 2. Column 9 is missing, use 7+8.
Also, large integers have commas every three digits, remove them. And some
columns use a '-' or an empty space to denote a zero, replace this with a
zero.
