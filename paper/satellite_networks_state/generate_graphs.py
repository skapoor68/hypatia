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

import exputil
import sys
sys.path.append("../../satgenpy")
import math
from satgen import *
import networkx as nx
import numpy as np
import json
import time

local_shell = exputil.LocalShell()
max_num_processes = 16
commands_to_run = []

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

def generate_infra(satellite_network_dir):
    
    tles = read_tles(satellite_network_dir + "/tles.txt")
    satellites = tles["satellites"]
    list_isls = read_isls(satellite_network_dir + "/isls.txt", len(satellites))
    
    epoch = tles["epoch"]
    print(epoch)
    return satellites, list_isls, epoch

def main():    
    satellite_network_dir = "./gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    satellites, list_isls, epoch = generate_infra(satellite_network_dir)
    
    for tt in range(0, 1000):
        t = epoch + tt / 86400
        data_path_filename = "./graphs/graph_" + str(tt) + ".txt"
        sat_net_graph_only_satellites_with_isls = nx.Graph()
        for i in range(len(satellites)):
            sat_net_graph_only_satellites_with_isls.add_node(i)

        total_num_isls = 0
        num_isls_per_sat = [0] * len(satellites)
        sat_neighbor_to_if = {}
        for (a, b) in list_isls:

            # ISLs are not permitted to exceed their maximum distance
            # TODO: Technically, they can (could just be ignored by forwarding state calculation),
            # TODO: but practically, defining a permanent ISL between two satellites which
            # TODO: can go out of distance is generally unwanted
            sat_distance_m = distance_m_between_satellites(satellites[a], satellites[b], str(epoch), str(t))
            if sat_distance_m > MAX_ISL_LENGTH_M:
                raise ValueError(
                    "The distance between two satellites (%d and %d) "
                    "with an ISL exceeded the maximum ISL length (%.2fm > %.2fm at t=%dns)"
                    % (a, b, sat_distance_m, MAX_ISL_LENGTH_M, time_since_epoch_ns)
                )

            # Add to networkx graph
            sat_net_graph_only_satellites_with_isls.add_edge(
                a, b, weight=sat_distance_m
            )

        nx.write_gpickle(sat_net_graph_only_satellites_with_isls, data_path_filename)

if __name__ == "__main__":
    main()
