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
    if len(args) != 16:
        print("Must supply exactly sixteen arguments")
        print(len(args))
        print("args:",args)
        print("Usage: python main_starlink_550_all_conf.py [start_time (s)] " 
              "[end_time (s)] "
              "[time step (ms)] "
              "[isls_plus_grid / isls_none] "
              "[ground_stations_{top_100, paris_moscow_grid}] "
              "[num_ground_stations_start] "
              "[num_ground_stations_end] "
              "[ground_stations_step] "
              "[user_terminals_{top_100, atlanta}] "
              "[num_user_terminals_start] "
              "[num_user_terminals_end] "
              "[user_terminals_step] "
              "[algorithm_{free_one_only_over_isls, free_one_only_gs_relays, paired_many_only_over_isls}] "
              "[failure_id] "
              "[allow_multiple_gsl] "
              "[num threads]")
        exit(1)
        
    # parse arguments
    start_time = int(args[0])
    end_time = int(args[1])
    step = int(args[2])
    isl_config = args[3]
    gs_config = args[4]
    gs_start = int(args[5])
    gs_end = int(args[6])
    gs_interval = int(args[7])
    ut_config = args[8]
    ut_start = int(args[9])
    ut_end = int(args[10])
    ut_interval = int(args[11])
    algorithm = args[12]
    failure_id = int(args[13])
    allow_multiple_gsl = int(args[14])
    num_threads = args[15]

    # for i in range [gstart, gend]:
    #   max_flow_arr = {}
    #   for j in range [ustart, uend]:
    #       max_flow = get_max_flow(i, j)
    #       max_flow_arr[j] = max_flow
    #   plot_graph(max_flow_arr)

    # Dictionary holding flow values for graphing
    gs_to_graph = dict()
    # Hashmap of hashmap holding num_terminal : (num_gs: max_flow) pairings
    max_flow_dict = dict() 
    for num_gateway in range(gs_start, gs_end + gs_interval, gs_interval):
        ut_to_max_flow = dict()
        # ut_start should be from where the last configuration was bottlenecked
        # ut_end should be until we reach the max GS capacity
        max_gs_capacity = num_gateway * ground_station_capacity
        for num_terminal in range(ut_start, ut_end + ut_interval, ut_interval):
            # if num_terminal, num_gs max flow is already computed
            # where num_gs <= num_gateway and max_flow is max demand
            max_demand = num_terminal * ut_default_demand
            skip = False
            if num_terminal in max_flow_dict:
                for num_gs in max_flow_dict[num_terminal]:
                    if num_gs <= num_gateway:
                        if max_flow_dict[num_terminal][num_gs] == max_demand:
                            # Add data to dictionary
                            ut_to_max_flow[num_terminal] = max_demand
                            skip = True
            # Check if previous run was bottlenecked by GS capacity
            for num_ut in max_flow_dict:
                if num_ut < num_terminal and num_gateway in max_flow_dict[num_ut]:
                    if max_flow_dict[num_ut][num_gateway] == max_gs_capacity:
                        ut_to_max_flow[num_terminal] = max_gs_capacity
                        skip = True

            if skip:
                print("Skipping configuration", (num_gateway, num_terminal), "as result is already computed.")
                continue

            # Generate new data for each configuration
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
                end_time
            )
            # Add data to dictionary
            ut_to_max_flow[num_terminal] = max_flow
            # Create mappings for future use
            if not num_terminal in max_flow_dict:
                max_flow_dict[num_terminal] = dict()
            max_flow_dict[num_terminal][num_gateway] = max_flow
        gs_to_graph[num_gateway] = ut_to_max_flow
    
    # After the loop:
    # gs_to_graph := # Gateway : Dict mapping user terminals to max flow
    for num_gateway, graph_dict in gs_to_graph.items():
        # output graph to satellite_network_dir
        terminals = graph_dict.keys()
        max_flows = graph_dict.values()
        plt.plot(terminals, max_flows, label="GW " + str(num_gateway))
    
    plt.xlabel("# of User Terminals")
    plt.ylabel("Maximum Network Flow in Timeseries")
    plt.title("UT, GW vs. Max Flow")
    plt.legend()

    duration_s = end_time - start_time
    pdf_dir = satellite_network_dir + "/output_graphs/"
    local_shell = exputil.LocalShell()
    local_shell.make_full_dir(pdf_dir)
    pdf_file = satellite_network_dir + "/output_graphs/starlink_550_" + gs_config + "_" + str(gs_end) + "_" + ut_config + "_" + str(ut_end)+ "_duration_" + str(duration_s) + "_max_flow.pdf"
    plt.savefig(pdf_file)
    print("Plot successfully saved. ")


if __name__ == "__main__":
    main()
