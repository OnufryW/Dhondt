Source of these stats: https://dane.gov.pl/pl/dataset/3375
Downloaded 26.02.2024

The data covers two types of ways to change the place you vote:
- "One-time relocations", where a person filed to change the location they would vote in this one election.
  This was easier to do (it could be done over the internet). It was roughly 70% of all the cases.
- "Right to vote" papers, where a person obtained a physical sheet of paper that allowed them to vote anywhere
  in the country.
Note that in the first case, the full data (from where and to where the person relocated) is in this dataset.
In the second case, only the fact of obtaining the papers is in this dataset; the number of people who voted based
on such a paper in a given comission is reported by PKW (and I'm not sure individual people are tracked in the
stats at all).

Individual files (renamed by me for convenience):
summary.csv: total numbers of "right to vote" papers granted, and one-time relocations.
summary_2.csv: basically the same numbers. Contains the split of the papers granted by whether the recipient had a registered location
right_to_vote_by_age_and_gender.csv: the number of right-to-vote papers split by age and gender
relocation_by_age_and_gender.csv: the number of relocations split by age and gender
right_to_vote_by_community.csv: the number of right-to-vote papers split by community. This covers the right-to-vote papers granted where
  the recipient had a registered location. This is internally split by whether the registered location was "meldunek" or "zamieszkanie",
  which is totally irrelevant to us.
  The papers granted to those without a registered residence are not trackable by location in any way.
relocation_without_registered_location_by_target_community.csv. This covers the relocation papers granted to the folks without
  a registered location. Sums up to 205820
relocation_within_community_by_community.csv: These are people who asked for a change of commission where they vote within the same
  community. This is obviously not electoral tourism. Sums up to 62460.
relocation_by_target_community.csv: This covers folks with a registered location who relocated outside of their community, split by
  target community. Sums up to 834930.
relocation_by_source_community.csv: This covers the same set of folks, except split by source community. Sums up to 846500, because
  the data is so totally crap.

Generally, relocation_by_*_community + relocation_within_community_by_community + relocation_without_registered_location 
should sum up to the total number of relocations. And it kinda almost does.
