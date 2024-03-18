These are the various data sources used in the various electoral analyses,
and the scripts (usually Python) to convert their formats.

Raw data is provided with sources, universally.

Data is generally transformed into a semicolon-separated values format, with
a header line.

Some sample commands

python3 ../python_lib/transform.py dump.cfg i election_results.cfg vote_data sejm_election_results/just_votes.cfg pure_election_results by_district.cfg c 2023_by_community.cfg seat_data district_definitions/2023.cfg

Calculates and displays the 2023 election results.
