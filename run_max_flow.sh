cd paper/satellite_networks_state

time=$1
steps=$2
threads=$3
num_satellites=1584

# Generate GS and satellite data
python main_starlink_550.py $time $steps isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls $threads

python main_helper.py

# Generate graphs from data
cd ../../satgenpy
python satgen/post_analysis/main_generate_graphs.py ~/hypatia/paper/satellite_networks_state/gen_data ~/hypatia/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls $steps 0 $time 1 1

# Generate routes and rtt from the graphs
python satgen/post_analysis/main_print_all_max_flows.py ~/hypatia/paper/satellite_networks_state/gen_data ~/hypatia/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls ~/hypatia/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms $steps $time


# Generate visualization based on route and rtt
# cd ../../satviz/scripts
# python visualize_path.py



