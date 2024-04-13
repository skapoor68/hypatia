# Only run this script after generating max flow graphs
cd satgenpy

steps=1000
failure_id=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--target)
      if [[ -n "$2" ]]; then
        target_s="$2"
        shift
      else
        echo "Error: Target time requires a value."
        exit 1
      fi
      ;;
    -e|--endtime)
      if [[ -n "$2" ]]; then
        time="$2"
        shift
      else
        echo "Error: End time requires a value."
        exit 1
      fi
      ;;
    -i|--interval)
      if [[ -n "$2" ]]; then
        steps="$2"
        shift
      else
        echo "Error: Time interval requires a value."
        exit 1
      fi
      ;;
    -G|--gs_config)
      if [[ -n "$2" ]]; then
        gs_config="$2"
        shift
      else
        echo "Error: Ground Station Config requires a value."
        exit 1
      fi
      ;;
    -U|--ut_config)
      if [[ -n "$2" ]]; then
        ut_config="$2"
        shift
      else
        echo "Error: User Terminal Config requires a value."
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


python satgen/post_analysis/main_print_flow_mapping.py ~/hypatia/paper/satellite_networks_state/gen_data ~/hypatia/paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_${gs_config}_algorithm_free_one_only_over_isls_${ut_config}_failure_${failure_id} $steps $time $target_s


