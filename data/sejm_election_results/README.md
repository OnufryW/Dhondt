Contains results of Sejm elections.

To obtain an SSV (semicolon-separated values) dump of any of the tables,

python3 ../../python_lib/transform.py ../dump.cfg i $CFG_FILE

The tables have the following schema (columns in order)

teryt: The TERYT code of the community
community: Name of the community (no particular format)
county: The name of the county in which the community is. Might be missing.
voivodship: The name of the voivodship. Might be missing.
number_of_commissions: The number of commissions in the community. Might be missing (0).
number_of_considered_commissions: How many of them returned results that were counted.
cards_received: How many voting cards did the commissions in the community receive from PKW
eligible_voters: How many people were eligible to vote in the community, according to PKW
unused_cards: How many cards were not used (out of cards_received).
voters_who_received_cards_in_person: how many voters got their cards in person on election day at the commission.
by_mail_packets_sent: How many "vote by mail" packets were sent, by request, to voters in the community.
voters_who_received_cards_in_total: the sum of the previous two columns.
voters_voting_through_intermediary: the number of voters who voted through an intermediary (a legally specified person entitled to vote on another's behalf)
voters_voting_through_right_to_vote: the number of voters voting using a 'right to vote' certificate granted by some (maybe different) community.
by_mail_packets_received: the number of "vote by mail" packets that came back to the commissions in this community.
by_mail_packets_without_declaration: The number of those packets that did not contain the declaration that the vote was personal and secret.
by_mail_packets_with_unsigned_declaration: The number of those packets where the declaration was present, but not signed.
by_mail_packets_without_envelope: The number of those packets that did not include the envelope (that should contain the voting card)
by_mail_packets_with_unsealed_envelope: The number of those packets where the envelope was present, but was not sealed (which makes it invalid).
by_mail_packets_in_urn: The number of those packets that bypassed all those pitfalls; the envelopes containing votes from those packets were added to the votes overall.
cards_retrieved_from_urn: How many voting cards were retrieved from the ballot boxes
cards_out_of_envelopes: How many of the above voting cards were taken out of by-mail envelopes.
invalid_cards: How many of the cards taken out were invalid (I have no idea what can cause a card to be invalid)
valid_cards: The valid ones.
invalid_votes: The number of votes that were not valid votes.
invalid_too_many_xs: The number of votes invalid because of too many marked candidates (more than one)
invalid_no_x: The number of votes invalid because no candidate was marked
invalid_struck_list: The number of votes invalid because the vote was cast for a committee struck out prior to voting.
valid_votes_total: the number of valid votes.
... And a number of columns, one per party, denoting the number of votes for the given party.
