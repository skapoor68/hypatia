cd paper/satellite_networks_state

threads=4
steps=1000
gs_config="ground_stations_atlanta"
ut_config="user_terminals_atlanta"
allow_multiple_gsl=0
failure_id=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -s|--starttime)
      if [[ -n "$2" ]]; then
        start_time="$2"
        echo "Simulation start time is set to $start_time."
        shift
      else
        echo "Error: Start time requires a value."
        exit 1
      fi
      ;;
    -e|--endtime)
      if [[ -n "$2" ]]; then
        end_time="$2"
        echo "Simulation end time is set to $end_time."
        shift
      else
        echo "Error: End time requires a value."
        exit 1
      fi
      ;;
    -i|--interval)
      if [[ -n "$2" ]]; then
        steps="$2"
        echo "Simulation time interval is set to $steps."
        shift
      fi
      ;;
    -G|--gs_config)
      if [[ -n "$2" ]]; then
        gs_config="$2"
        shift
      fi
      ;;
    -U|--ut_config)
      if [[ -n "$2" ]]; then
        ut_config="$2"
        shift
      fi
      ;;
    -g)
      if [[ -n "$2" ]]; then
        num_gs="$2"
        echo "Allocating $num_gs Ground Stations."
        shift
      else
        echo "Error: Ground Station number requires a value."
        exit 1
      fi
      ;;
    -u)
      if [[ -n "$2" ]]; then
        num_ut="$2"
        echo "Allocating $num_ut User Terminals."
        shift
      else
        echo "Error: User terminal number requires a value."
        exit 1
      fi
      ;;
    -f|--failure)
      if [[ -n "$2" ]]; then
        failure_id="$2"
        echo "Failure id is set to $failure_id."
        shift
      else
        echo "Error: Failure id requires a value."
        exit 1
      fi
      ;;
    --multiple-gsl)
        allow_multiple_gsl=1
        echo "Multiple GSL per Satellite Enabled."
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
  shift
done

echo "Simulation time interval is set to $steps."
echo "UT config is set to $ut_config."
echo "GS config is set to $gs_config."


# Generate GS and satellite data
python main_starlink_550.py $end_time $steps isls_plus_grid $gs_config $num_gs $ut_config $num_ut algorithm_free_one_only_over_isls $threads $failure_id

# Generate graphs from data
cd ../../satgenpy
python satgen/post_analysis/main_generate_graphs.py ~/hypatia/paper/satellite_networks_state/gen_data ~/hypatia/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_${gs_config}_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id} $steps $start_time $end_time 1 $failure_id $allow_multiple_gsl
# Generate maximum flow from the graphs
python satgen/post_analysis/main_print_all_max_flows.py ~/hypatia/paper/satellite_networks_state/gen_data ~/hypatia/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_${gs_config}_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id} ~/hypatia/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_${gs_config}_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id}/${steps}ms $steps $start_time $end_time

# Generate routes and rtt from the graphs
# python satgen/post_analysis/main_print_all_ut_to_gw_routes_and_rtt.py ~/hypatia/paper/satellite_networks_state/gen_data ~/hypatia/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_${gs_config}_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id} ~/hypatia/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_atlanta_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id}/${steps}ms $steps $end_time $start_uid $end_uid

# Generate pdf for a src/dest pair
# python satgen/post_analysis/main_print_ut_to_gw_routes_and_rtt.py ~/hypatia/paper/satellite_networks_state/gen_data ~/hypatia/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_${gs_config}_algorithm_free_one_only_over_isls_${ut_config} $steps $time $src $dst

# Generate visualization based on route and rtt
# cd ../../satviz/scripts
# python visualize_path.py



