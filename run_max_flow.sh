cd paper/satellite_networks_state

start_time=$1
end_time=$2
steps=$3
threads=${4:-"4"}
gs_config=${5:-"ground_stations_atlanta"}
num_gs=${6:-"100"}
ut_config=${7:-"user_terminals_atlanta"}
num_ut=${8:-"100"}
failure_id=${9:-"0"} # Must match line 70 in generate_all_graphs.py. Use 0 for no failures.
allow_multiple_gsl=${10:-"0"}


# Generate GS and satellite data
python main_starlink_550.py $time $steps isls_plus_grid $gs_config $num_gs $ut_config $num_ut algorithm_free_one_only_over_isls $threads $failure_id

# Generate graphs from data
cd ../../satgenpy
python satgen/post_analysis/main_generate_graphs.py ~/hypatia-robin/paper/satellite_networks_state/gen_data ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id} $steps $start_time $end_time 1 1 $allow_multiple_gsl
# Generate maximum flow from the graphs
python satgen/post_analysis/main_print_all_max_flows.py ~/hypatia-robin/paper/satellite_networks_state/gen_data ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id} ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id}/${steps}ms $steps $start_time $end_time

# Generate routes and rtt from the graphs
# python satgen/post_analysis/main_print_all_ut_to_gw_routes_and_rtt.py ~/hypatia-robin/paper/satellite_networks_state/gen_data ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id} ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id}/${steps}ms $steps $end_time $start_uid $end_uid

# Generate pdf for a src/dest pair
# python satgen/post_analysis/main_print_ut_to_gw_routes_and_rtt.py ~/hypatia-robin/paper/satellite_networks_state/gen_data ~/hypatia-robin/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_$ut_config $steps $time $src $dst

# Generate visualization based on route and rtt
# cd ../../satviz/scripts
# python visualize_path.py



