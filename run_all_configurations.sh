threads=4
gs_config="ground_stations_atlanta"
ut_config="user_terminals_atlanta"

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
      else
        echo "Error: Step requires a value."
        exit 1
      fi
      ;;
    -g|--gs)
      if [[ -n "$2" ]]; then
        gs_config="$2"
        echo "GS config is set to $gs_config."
        shift
      else
        echo "GS config is set to $gs_config."
      fi
      ;;
    -u|--ut)
      if [[ -n "$2" ]]; then
        ut_config="$2"
        echo "UT config is set to $ut_config."
        shift
      else
        echo "UT config is set to $ut_config."
      fi
      ;;
    --gstart)
      if [[ -n "$2" ]]; then
        gstart="$2"
        echo "Ground station range start is set to $gstart."
        shift
      else
        echo "Error: Ground station range start requires a value."
        exit 1
      fi
      ;;
    --gend)
      if [[ -n "$2" ]]; then
        gend="$2"
        echo "Ground station range end is set to $gend."
        shift
      else
        echo "Error: Ground station range end requires a value."
        exit 1
      fi
      ;;
    --ustart)
      if [[ -n "$2" ]]; then
        ustart="$2"
        echo "User terminal range start is set to $ustart."
        shift
      else
        echo "Error: User terminal range start requires a value."
        exit 1
      fi
      ;;
    --uend)
      if [[ -n "$2" ]]; then
        uend="$2"
        echo "User terminal range end is set to $uend."
        shift
      else
        echo "Error: User terminal range end requires a value."
        exit 1
      fi
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
  shift
done


# for i in range [gstart, gend]:
#   max_flow_arr = {}
#   for j in range [ustart, uend]:
#       max_flow = get_max_flow(i, j)
#       max_flow_arr[j] = max_flow
#   plot_graph(max_flow_arr)


cd paper/satellite_networks_state

# Generate GS and satellite data
python main_starlink_550_all_conf.py $start_time $end_time $steps isls_plus_grid $gs_config $gstart $gend $ut_config $ustart $uend algorithm_free_one_only_over_isls $threads
