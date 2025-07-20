python3 ../../python_lib/cadmium.py "RUN FILE 'indices.cfg' FROM COMMAND \"RUN FILE '../sejm_election_results/2023_by_community.cfg' > FILE '../sejm_election_results/just_votes.cfg' > FILE '../sejm_election_results/by_district.cfg';\", FILE '../district_definitions/2023.cfg' > COMMAND \"INPUT TABLES t; DUMP t TO result;\";"
diff result reference_2023_result
rm result
