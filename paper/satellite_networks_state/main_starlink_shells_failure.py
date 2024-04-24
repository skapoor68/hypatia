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
import os
import math
from main_shells_helper import MainShellsHelper
from satgen.post_analysis.generate_all_graphs_shells_failure import generate_all_graphs_shells_failure
from satgen.post_analysis.print_all_max_flows import get_avergage_flow
from satgen.user_terminals.global_variables import *
import matplotlib.pyplot as plt
import exputil

# WGS72 value; taken from https://geographiclib.sourceforge.io/html/NET/NETGeographicLib_8h_source.html
EARTH_RADIUS = 6378135.0

# GENERATION CONSTANTS

BASE_NAME = "starlink_current"
NICE_NAME = "Starlink-Current"

# STARLINK 550

ECCENTRICITY = 0.0000001  # Circular orbits are zero, but pyephem does not permit 0, so lowest possible value
ARG_OF_PERIGEE_DEGREE = 0.0
PHASE_DIFF = True
NUM_SHELLS = 5

################################################################
# The below constants are taken from Starlink's FCC filing as below:
# [1]: https://fcc.report/IBFS/SAT-MOD-20190830-00087
################################################################
# From https://fcc.report/IBFS/SAT-MOD-20181108-00083/1569860.pdf (minimum angle of elevation: 25 deg)
# ALTITUDES_M = [550000, 560000, 540000, 570000, 530000, 580000, 520000, 590000]  # Altitude ~550 km
# ALTITUDES_M = [550000, 1110000, 1130000, 1275000, 1325000]  # older starlink
ALTITUDES_M = [550000, 540000, 570000, 560000, 560000]  # current starlink
theta = math.radians(25)

def generate_constants():
    revs, gsl_lengths, isl_lengths = [], [], []
    for altitude in ALTITUDES_M:
        revs.append((math.sqrt((398600.5 * 1000) / (EARTH_RADIUS + altitude)) * 1000 * 86400) / (2 * math.pi * (EARTH_RADIUS + altitude)))
        cone_radius = math.sqrt((EARTH_RADIUS * math.sin(theta)) ** 2 + altitude ** 2  + 2 * EARTH_RADIUS * altitude) - EARTH_RADIUS * math.sin(theta)
        gsl_lengths.append(math.sqrt(math.pow(cone_radius, 2) + math.pow(altitude, 2)))
        # ISLs are not allowed to dip below 80 km altitude in order to avoid weather conditions
        isl_lengths.append(2 * math.sqrt(math.pow(EARTH_RADIUS + altitude, 2) - math.pow(EARTH_RADIUS + 80000, 2)))

    return revs, gsl_lengths, isl_lengths

MEAN_MOTION_REV_PER_DAY, MAX_GSL_LENGTH_M, MAX_ISL_LENGTH_M = generate_constants()
# print(MEAN_MOTION_REV_PER_DAY, MAX_GSL_LENGTH_M, MAX_ISL_LENGTH_M)

# NUM_ORBS = [72,72,72,72,72,72,72,72]
# NUM_ORBS = [72,32,8,5,6] # older starlink
NUM_ORBS = [72,72,36,6,4] # current starlink

# NUM_SATS_PER_ORB = [22,22,22,22,22,22,22,22]
# NUM_SATS_PER_ORB = [22,50,50,75,75] # older starlink
NUM_SATS_PER_ORB = [22,22,20,58,43] # current starlink

# INCLINATION_DEGREE = [53,53,53,53,53,53,53,53] # same
# INCLINATION_DEGREE = [53,27,72,13,40,62,82,53] # different
# INCLINATION_DEGREE = [53,53.8,74,81,70] # older starlink
INCLINATION_DEGREE = [53,53.2,70,97.6,97.6] # current starlink

################################################################


main_helper = MainShellsHelper(
    BASE_NAME,
    NICE_NAME,
    NUM_SHELLS,
    ECCENTRICITY,
    ARG_OF_PERIGEE_DEGREE,
    PHASE_DIFF,
    MEAN_MOTION_REV_PER_DAY[:NUM_SHELLS],
    ALTITUDES_M[:NUM_SHELLS],
    MAX_GSL_LENGTH_M[:NUM_SHELLS],
    MAX_ISL_LENGTH_M[:NUM_SHELLS],
    NUM_ORBS[:NUM_SHELLS],
    NUM_SATS_PER_ORB[:NUM_SHELLS],
    INCLINATION_DEGREE[:NUM_SHELLS],
)

def main():
    args = sys.argv[1:]
    if len(args) != 15:
        print("Must supply exactly fifteen arguments")
        print("Usage: python main_starlink_shells_failure.py "
              "[start_time (s)] "
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

    main_helper.calculate_shells_failure(
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
        failure_id,
        NUM_SHELLS
    )
    
    gen_data_dir = "/home/skapoor68/hypatia/paper/satellite_networks_state/gen_data"
    core_network_folder_name = "starlink_current_" + str(NUM_SHELLS) + "_shells_" + isl_config + "_" + gs_config + "_" + algorithm + "_" + ut_config + "_failure_" + str(failure_id)
    graph_dir = "%s/%s/%dms" % (
        gen_data_dir, core_network_folder_name, step
    )
    print(graph_dir)
    satellite_network_dir = "%s/%s" % (
        gen_data_dir, core_network_folder_name
    )
    print(satellite_network_dir)

    # Hashmap of hashmap holding num_terminal : (num_gs: max_flow) pairings
    max_flow_dict = dict() 
    for num_failures in range(failure_start, failure_end, failure_interval):
        print(f"Running with {num_failures} failures")
        generate_all_graphs_shells_failure(
            graph_dir,
            satellite_network_dir,
            step,
            start_time,
            end_time,
            n_shells=NUM_SHELLS,
            failure_id=failure_id,
            allow_multiple_gsl=allow_multiple_gsl
        )

        avg_flow = get_avergage_flow(
            satellite_network_dir,
            graph_dir, 
            step,
            start_time,
            end_time,
            num_failures
        )
        max_flow_dict[num_failures] = avg_flow
    

    plt.plot(max_flow_dict.keys(), max_flow_dict.values())
    
    plt.xlabel("Top Betweeness Centrality Link Failures")
    plt.ylabel("Average Network Flow in Timeseries")
    plt.title("Number of Link Failures vs. Average Flow")
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
