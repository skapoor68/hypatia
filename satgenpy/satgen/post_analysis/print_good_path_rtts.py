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
import math
from itertools import islice
from satgen.isls import *
from satgen.ground_stations import *
from satgen.distance_tools import *
import networkx as nx
import numpy as np
import json
import time
import os, sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
from collections import OrderedDict
from matplotlib.ticker import FormatStrFormatter
import threading
import copy
from satgen import *

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

total_time = 6000

def generate_points():
    points = []
    i = 0
    for lat in range(-60, 60, 4):
        for lon in range(-180, 180, 4):
            point = {}
            point['pid'] = i
            point['latitude_degrees_str'] = str(lat)
            point['longitude_degrees_str'] = str(lon)
            point['name'] = "gid" + str(i)
            point['elevation_m_float'] = 0
            point['cartesian_x'], point['cartesian_x'], point['cartesian_x'] = geodetic2cartesian(lat, lon, 0)
            points.append(point)
            i = i + 1

    return points

def generate_infra(satellite_network_dir):
    
    tles = read_tles(satellite_network_dir + "/tles.txt")
    satellites = tles["satellites"]
    list_isls = read_isls(satellite_network_dir + "/isls.txt", len(satellites))
    
    epoch = tles["epoch"]
    return satellites, list_isls, epoch

def k_shortest_paths(G, source, target, k, weight=None):
    return list(
        islice(nx.shortest_simple_paths(G, source, target, weight=weight), k)
    )

def calculate_path_lengths(graphs, path):
    lengths = [0] * total_time

    for i in range(total_time):
        if nx.is_simple_path(graphs[i], path):
            lengths[i] = compute_path_length_with_graph(path, graphs[i])

    return lengths

def main():    
    # gs = generate_denver_groundstation()
    satellite_network_dir = "../paper/satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_world_grid_paper_algorithm_free_one_only_over_isls"
    satellites, list_isls, epoch = generate_infra(satellite_network_dir)
    points = generate_points()
    src_points = [0,1,2,3,1399]
    shortest_path_length = np.empty((len(src_points), len(points), total_time))
    
    
    for t in range(total_time):
        graph_path = "../paper/satgenpy_analysis/graphs/starlink_550_isls_plus_grid_ground_stations_world_grid_paper_algorithm_free_one_only_over_isls/1000ms/graph_" + str(t*1000*1000*1000) + ".txt"
        graph = nx.read_gpickle(graph_path)
        sat_net_graph_only_satellites_with_isls = graph.subgraph(list(range(len(satellites))))
        dist_sat_net_without_gs = nx.floyd_warshall_numpy(sat_net_graph_only_satellites_with_isls)
        idx = 0
        for src_pt in src_points:
            src = len(satellites) + src_pt
            src_sats = graph[src]
            for pt in range(len(points)):
                dst = pt + 1584 + 4
                dst_sats = graph[dst]
                dst_sats = graph[dst]
                shortest_dist = math.inf
                for src_sat in src_sats.keys():
                    for dst_sat in dst_sats.keys():
                        if not math.isinf(dist_sat_net_without_gs[src_sat][dst_sat]):
                            shortest_dist = min(shortest_dist, src_sats[src_sat]['weight'] + dst_sats[dst_sat]['weight'] + dist_sat_net_without_gs[(src_sat, dst_sat)])
            
                shortest_path_length[idx][pt][t] = shortest_dist
                # print(shortest_dist)
            idx += 1

    for i in range(len(src_points)):
        print("src point", i)
        for j in range(len(points)):
            lengths = shortest_path_length[i][j]
            # print(lengths)
            print(j, np.max(lengths) / np.min(lengths))
            # break
            

    

if __name__ == "__main__":
    main()
    