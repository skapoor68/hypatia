threads=4
steps=1000
gs_config="atlanta"
ut_config="atlanta"
gstep=10
ustep=100
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
    -G|--gs)
      if [[ -n "$2" ]]; then
        gs_config="$2"
        shift
      fi
      ;;
    -U|--ut)
      if [[ -n "$2" ]]; then
        ut_config="$2"
        shift
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
    --gstep)
      if [[ -n "$2" ]]; then
        gstep="$2"
        shift
      else
        echo "Error: Ground station interval requires a value."
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
    --ustep)
      if [[ -n "$2" ]]; then
        ustep="$2"
        shift
      else
        echo "Error: User terminal interval requires a value."
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

ut_config="user_terminals_${ut_config}"
gs_config="ground_stations_${gs_config}"


echo "Simulation time interval is set to $steps."
echo "UT config is set to $ut_config."
echo "GS config is set to $gs_config."
echo "Ground station interval is set to $gstep."
echo "User Terminal interval is set to $ustep."

# for i in range [gstart, gend]:
#   max_flow_arr = {}
#   for j in range [ustart, uend]:
#       max_flow = get_max_flow(i, j)
#       max_flow_arr[j] = max_flow
#   plot_graph(max_flow_arr)


cd paper/satellite_networks_state

# Generate GS and satellite data
python main_starlink_550_all_conf.py $start_time $end_time $steps isls_plus_grid $gs_config $gstart $gend $gstep $ut_config $ustart $uend $ustep algorithm_free_one_only_over_isls $failure_id $allow_multiple_gsl $threads
