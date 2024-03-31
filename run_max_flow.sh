cd paper/satellite_networks_state

time=$1
steps=$2
threads=${3:-"4"}
start_uid=${4:-"0"} # First user terminal id to print routes and rtt to gateways
end_uid=${5:-"1"} # Last user terminal id to print routes and rtt to gateways
gs_config=${6:-"ground_stations_atlanta"}
num_gs=${7:-"100"}
ut_config=${8:-"user_terminals_atlanta"}
num_ut=${9:-"100"}
failure_id=${10:-"0"} # Must match line 70 in generate_all_graphs.py. Use 0 for no failures.


# Generate GS and satellite data
python main_starlink_550.py $time $steps isls_plus_grid $gs_config $num_gs $ut_config $num_ut algorithm_free_one_only_over_isls $threads $failure_id

# Generate graphs from data
cd ../../satgenpy
python satgen/post_analysis/main_generate_graphs.py ~/hypatia-robin/paper/satellite_networks_state/gen_data ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id} $steps 0 $time 1 1

# Generate maximum flow from the graphs
python satgen/post_analysis/main_print_all_max_flows.py ~/hypatia-robin/paper/satellite_networks_state/gen_data ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id} ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id}/1000ms $steps $time

# Generate routes and rtt from the graphs
python satgen/post_analysis/main_print_all_ut_to_gw_routes_and_rtt.py ~/hypatia-robin/paper/satellite_networks_state/gen_data ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id} ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id}/1000ms $steps $time $start_uid $end_uid

# Generate pdf for a src/dest pair
# python satgen/post_analysis/main_print_ut_to_gw_routes_and_rtt.py ~/hypatia-robin/paper/satellite_networks_state/gen_data ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_$ut_config $steps $time $src $dst

# Generate visualization based on route and rtt
# cd ../../satviz/scripts
# python visualize_path.py



