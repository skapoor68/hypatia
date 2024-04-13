# The MIT License (MIT)
#
# Copyright (c) 2020 ETH Zurich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import math
import os
import exputil
from main_helper import MainHelper
from satgen.post_analysis.generate_all_graphs import generate_all_graphs
from satgen.post_analysis.print_all_max_flows import get_max_flow
from satgen.user_terminals.global_variables import *
import matplotlib.pyplot as plt

# WGS72 value; taken from https://geographiclib.sourceforge.io/html/NET/NETGeographicLib_8h_source.html
EARTH_RADIUS = 6378135.0

# GENERATION CONSTANTS

BASE_NAME = "starlink_550"
NICE_NAME = "Starlink-550"

# STARLINK 550

ECCENTRICITY = 0.0000001  # Circular orbits are zero, but pyephem does not permit 0, so lowest possible value
ARG_OF_PERIGEE_DEGREE = 0.0
PHASE_DIFF = True

################################################################
# The below constants are taken from Starlink's FCC filing as below:
# [1]: https://fcc.report/IBFS/SAT-MOD-20190830-00087
################################################################

MEAN_MOTION_REV_PER_DAY = 15.19  # Altitude ~550 km
ALTITUDE_M = 550000  # Altitude ~550 km

# From https://fcc.report/IBFS/SAT-MOD-20181108-00083/1569860.pdf (minimum angle of elevation: 25 deg)
SATELLITE_CONE_RADIUS_M = 940700

MAX_GSL_LENGTH_M = math.sqrt(math.pow(SATELLITE_CONE_RADIUS_M, 2) + math.pow(ALTITUDE_M, 2))

# ISLs are not allowed to dip below 80 km altitude in order to avoid weather conditions
MAX_ISL_LENGTH_M = 2 * math.sqrt(math.pow(EARTH_RADIUS + ALTITUDE_M, 2) - math.pow(EARTH_RADIUS + 80000, 2))

NUM_ORBS = 72
NUM_SATS_PER_ORB = 22
INCLINATION_DEGREE = 53

################################################################


main_helper = MainHelper(
    BASE_NAME,
    NICE_NAME,
    ECCENTRICITY,
    ARG_OF_PERIGEE_DEGREE,
    PHASE_DIFF,
    MEAN_MOTION_REV_PER_DAY,
    ALTITUDE_M,
    MAX_GSL_LENGTH_M,
    MAX_ISL_LENGTH_M,
    NUM_ORBS,
    NUM_SATS_PER_ORB,
    INCLINATION_DEGREE,
)


def main():
    args = sys.argv[1:]
    if len(args) != 15:
        print("Must supply exactly fifteen arguments")
        print(len(args))
        print("args:",args)
        print("Usage: python main_starlink_550_all_conf.py [start_time (s)] " 
              "[end_time (s)] "
              "[time step (ms)] "
              "[isls_plus_grid / isls_none] "
              "[ground_stations_{top_100, paris_moscow_grid}] "
              "[num_ground_stations] "
              "[user_terminals_{top_100, atlanta}] "
              "[num_user_terminals] "
              "[algorithm_{free_one_only_over_isls, free_one_only_gs_relays, paired_many_only_over_isls}] "
              "[failure_id] "
              "[failure_start]"
              "[failure_end]"
              "[failure_interval]"
              "[allow_multiple_gsl] "
              "[num threads]")
        exit(1)
        
    # parse arguments
    start_time = int(args[0])
    end_time = int(args[1])
    step = int(args[2])
    isl_config = args[3]
    gs_config = args[4]
    num_gateway = int(args[5])
    ut_config = args[6]
    num_terminal = int(args[7])
    algorithm = args[8]
    failure_id = int(args[9])
    failure_start = int(args[10])
    failure_end = int(args[11])
    failure_interval = int(args[12])
    allow_multiple_gsl = int(args[13])
    num_threads = args[14]

    main_helper.calculate(
        "gen_data",
        end_time,
        step,
        isl_config,
        gs_config,
        num_gateway,
        ut_config,
        num_terminal,
        algorithm,
        num_threads,
        failure_id
    )

    gen_data_dir = "/home/hkim3019/hypatia/paper/satellite_networks_state/gen_data"
    core_network_folder_name = "starlink_550_" + isl_config + "_" + gs_config + "_" + algorithm + "_" + ut_config + "_failure_" + str(failure_id)
    graph_dir = "%s/%s/%dms" % (
        gen_data_dir, core_network_folder_name, step
    )
    satellite_network_dir = "%s/%s" % (
        gen_data_dir, core_network_folder_name
    )
    print("Data dir: " + gen_data_dir)
    print("Used data dir to form base output dir: " + graph_dir)
    print("Used data dir to form satellite network dir: " + satellite_network_dir)

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir, exist_ok=True)


    # Hashmap of hashmap holding num_terminal : (num_gs: max_flow) pairings
    max_flow_dict = dict() 

    # ut_start should be from where the last configuration was bottlenecked
    # ut_end should be until we reach the max GS capacity
    max_gs_capacity = num_gateway * ground_station_capacity
    for num_failures in range(failure_end, failure_start-failure_interval, -failure_interval):
        # Check if previous run had maximum demand satisfied despite more failures
        max_demand = num_terminal * ut_default_demand
        skip = False
        for prev_failures in range(failure_end, num_failures, -failure_interval):
            if prev_failures in max_flow_dict:
                if max_flow_dict[prev_failures] == max_demand:
                    # Add data to dictionary
                    max_flow_dict[num_failures] = max_demand
                    skip = True
                if max_flow_dict[prev_failures] == max_gs_capacity:
                    max_flow_dict[num_failures] = max_gs_capacity
                    skip = True
        if skip:
             print("Skipping configuration with num_failures", str(num_failures))
             continue

        generate_all_graphs(
            graph_dir,
            satellite_network_dir,
            step,
            start_time,
            end_time,
            n_shells=1,
            failure_id=failure_id,
            allow_multiple_gsl=allow_multiple_gsl
        )

        max_flow = get_max_flow(
            satellite_network_dir,
            graph_dir, 
            step,
            start_time,
            end_time,
            num_failures
        )
        max_flow_dict[num_failures] = max_flow
    
    # After the loop:
    # gs_to_graph := # Gateway : Dict mapping user terminals to max flow
    plt.plot(max_flow_dict.keys(), max_flow_dict.values())
    
    plt.xlabel("# of Top Edge Failures")
    plt.ylabel("Maximum Network Flow in Timeseries")
    plt.title("Number of Failures vs. Max Flow")
    plt.legend()

    duration_s = end_time - start_time
    pdf_dir = satellite_network_dir + "/output_graphs/"
    local_shell = exputil.LocalShell()
    local_shell.make_full_dir(pdf_dir)
    pdf_file = satellite_network_dir + "/output_graphs/starlink_550_" + "num_failures_" + str(failure_end) + "_" + gs_config + "_" + str(num_gateway) + "_" + ut_config + "_" + str(num_terminal)+ "_duration_" + str(duration_s) + "_max_flow.pdf"
    plt.savefig(pdf_file)
    print("Plot successfully saved to", pdf_file)


if __name__ == "__main__":
    main()
