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
from main_helper import MainHelper
from satgen.post_analysis.generate_all_graphs import generate_all_graphs
from satgen.post_analysis.print_all_max_flows import get_max_flow
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
    if len(args) != 11:
        print("Must supply exactly eleven arguments")
        print(len(args))
        print("args:",args)
        print("Usage: python main_starlink_550_all_conf.py [duration (s)] [time step (ms)] "
              "[isls_plus_grid / isls_none] "
              "[ground_stations_{top_100, paris_moscow_grid}] "
              "[num_ground_stations_start] "
              "[num_ground_stations_end] "
              "[user_terminals_{top_100, atlanta}] "
              "[num_user_terminals_start] "
              "[num_user_terminals_end] "
              "[algorithm_{free_one_only_over_isls, free_one_only_gs_relays, paired_many_only_over_isls}] "
              "[num threads]")
        exit(1)
        
    # parse arguments
    duration = int(args[0])
    step = int(args[1])
    isl_config = args[2]
    gs_config = args[3]
    gs_start = int(args[4])
    gs_end = int(args[5])
    ut_config = args[6]
    ut_start = int(args[7])
    ut_end = int(args[8])
    algorithm = args[9]
    num_threads = args[10]

    # for i in range [gstart, gend]:
    #   max_flow_arr = {}
    #   for j in range [ustart, uend]:
    #       max_flow = get_max_flow(i, j)
    #       max_flow_arr[j] = max_flow
    #   plot_graph(max_flow_arr)

    gs_interval = 10
    ut_interval = 50
    gs_to_graph = dict()
    for num_gateway in range(gs_start, gs_end + 1, gs_interval):
        max_flow_dict = dict()
        for num_terminal in range(ut_start, ut_end + 1, ut_interval):
            # Generate new data for each configuration
            main_helper.calculate(
                "gen_data",
                duration,
                step,
                isl_config,
                gs_config,
                num_gateway,
                ut_config,
                num_terminal,
                algorithm,
                num_threads,
            )
            
            gen_data_dir = "/home/robin/hypatia/paper/satellite_networks_state/gen_data"
            core_network_folder_name = "starlink_550_" + isl_config + "_" + gs_config + "_" + algorithm + "_" + ut_config
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
                0,
                duration,
                n_shells=1,
                use_capacity=True
            )

            max_flow = get_max_flow(
                satellite_network_dir,
                graph_dir, 
                step,
                duration
            )
            max_flow_dict[num_terminal] = max_flow
        gs_to_graph[num_gateway] = max_flow_dict
    
    # After the loop:
    # gs_to_graph := # Gateway : Max Flow Dict mapping user terminals to max flow
    for num_gateway, graph_dict in gs_to_graph.items():
        # output graph to satellite_network_dir
        terminals = graph_dict.keys()
        max_flows = graph_dict.values()
        plt.plot(terminals, max_flows, label="GW " + str(num_gateway))
    
    plt.xlabel("# of User Terminals")
    plt.ylabel("Maximum Network Flow in Timeseries")
    plt.title("UT, GW vs. Max Flow")
    plt.legend()

    pdf_file = satellite_network_dir + "/output_graphs/starlink_550_"+gs_config+"_" +str(gs_end)+"_"+ ut_config +"_"+str(ut_end)+"_max_flow.pdf"
    plt.savefig(pdf_file)
    print("Plot successfully saved. ")

    
    


if __name__ == "__main__":
    main()
