echo 'Testing attendance'
cd attendance; ./test.sh; cd ..;
echo 'Testing district definitions'
cd district_definitions; ./test.sh; cd ..;
echo 'Testing presidential election results';
cd presidential_election_results; ./test.sh; cd ..;
echo 'Testing relocation stats';
cd relocation_stats; ./test.sh; cd ..;
echo 'Testing sejm election results';
cd sejm_election_results; ./test.sh; cd ..;
echo 'Testing inequality indices';
cd vote_strength_inequality; ./test.sh; cd ..echo 'Testing inequality indices';
cd vote_strength_inequality; ./test.sh; cd ..;

echo 'Integration test for 2015 elections'
# Integration test for committee data, district definitions, election 
# results, sejm_election_results.

python3 ../python_lib/cadmium.py "RUN FILE 'election_results.cfg' FROM FILE 'sejm_election_results/2015_by_community.cfg', FILE 'committee_data/2015.cfg', FILE 'district_definitions/2019.cfg' > COMMAND 'INPUT TABLES table; DUMP table TO results;';"
diff results 2015_election_results_real.txt
rm results
