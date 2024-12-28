#!/bin/bash

validate () {
  python3 ../python_lib/validate.py "$@" --allow_partial_success || exit 1 
}

validate_district_data () {
  validate $1 district_definitions/validate.cfg || exit 1
}

validate_election_results () {
  validate $1 sejm_election_results/validate.cfg || exit 1
}

validate_compiles () {
  validate $1 empty.cfg "${@:2}" || exit 1
}

set -e
# attendance
validate_compiles attendance/by_county.cfg
validate_compiles attendance/by_district.cfg
validate_compiles attendance/by_voivodship.cfg

# committee_data (election_results.cfg)
validate election_results.cfg validate_election_results.cfg vote_data committee_data/apply_threshold.cfg threshold_data 2015.csv votes_by_district ../sejm_election_results/just_votes.cfg pure_election_results by_district.cfg c 2015_by_community.cfg seat_data district_definitions/2019.cfg

# district_definitions
validate_district_data district_definitions/2019.cfg
validate_district_data district_definitions/2023.cfg

# presidential_election_results
validate presidential_election_results/2020_by_community.cfg sejm_election_results/validate.cfg

# relocation_stats
validate_compiles relocation_stats/relocation_by_age_and_gender.cfg
validate_compiles relocation_stats/relocation_by_source_community.cfg
validate_compiles relocation_stats/relocation_by_target_community.cfg
validate_compiles relocation_stats/relocation_within_community_by_community.cfg
validate_compiles relocation_stats/relocation_without_registered_location_by_target_community.cfg
validate_compiles relocation_stats/right_to_vote_by_age_and_gender.cfg
validate_compiles relocation_stats/right_to_vote_by_community.cfg
validate_compiles relocation_stats/summary_data_by_community.cfg
validate_compiles relocation_stats/summary_data_by_district.cfg

# sejm_election_results
validate_election_results sejm_election_results/2015_by_community.cfg
validate_election_results sejm_election_results/2019_by_community.cfg
validate_election_results sejm_election_results/2023_by_community.cfg
validate_compiles sejm_election_results/just_votes.cfg pure_election_results by_district.cfg c 2015_by_community.cfg
validate_compiles sejm_election_results/just_votes.cfg pure_election_results by_district.cfg c 2019_by_community.cfg
validate_compiles sejm_election_results/just_votes.cfg pure_election_results by_district.cfg c 2023_by_community.cfg

# vote_strength_inequality
validate_compiles vote_strength_inequality/all_data.cfg

set +e
