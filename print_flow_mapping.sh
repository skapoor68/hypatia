# Only run this script after generating max flow graphs
cd satgenpy

time=$1
steps=$2
gs_config=${3:-"ground_stations_atlanta"}
ut_config=${4:-"user_terminals_atlanta"}
target_s=${5:-"0"}

python satgen/post_analysis/main_print_flow_mapping.py ~/hypatia/paper/satellite_networks_state/gen_data ~/hypatia/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_${gs_config}_algorithm_free_one_only_over_isls_${ut_config} $steps $time $target_s


