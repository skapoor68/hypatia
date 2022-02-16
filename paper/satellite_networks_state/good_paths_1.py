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
from itertools import islice
from satgen import *
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

lat_values = [5, 20, 35, 55]
dist_limits = [0, 500, 1000, 1500, 2500, 5000, 7500, 10000, 12500, 15000, 17500, 20000, 22500]
total_time = 6000

def generate_groundstations(lon = -80):
    ground_stations = []
    i = 0

    for lat in lat_values:
        ground_station = {}
        ground_station['gid'] = i
        ground_station['latitude_degrees_str'] = str(lat)
        ground_station['longitude_degrees_str'] = str(lon)
        ground_station['name'] = "gid" + str(i)
        ground_station['elevation_m_float'] = 0
        ground_station['cartesian_x'], ground_station['cartesian_x'], ground_station['cartesian_x'] = geodetic2cartesian(lat, lon, 0)
        ground_stations.append(ground_station)
        i = i + 1

    ground_stations[0]["satellites"] = [66, 912, 88, 891]
    ground_stations[1]["satellites"] = [955, 23, 977, 2]
    ground_stations[2]["satellites"] = [998, 1564, 1020, 1543]
    ground_stations[3]["satellites"] = [1325, 1238, 1259, 1303]
    return ground_stations

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

def generate_graph(t, gs, point):
    print(t)
    satellite_network_dir = "./gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    satellites, list_isls, epoch = generate_infra(satellite_network_dir)
    ground_stations = generate_groundstations()
    points = generate_points()
    
    graph_path = "graphs/graph_" + str(t) + ".txt"
    sat_net_graph = nx.read_gpickle(graph_path)
    t = epoch + t / 86400

    for sid in range(len(satellites)):
        distance_m = distance_m_ground_station_to_satellite(
            points[point],
            satellites[sid],
            str(epoch),
            str(t)
        )
        if distance_m <= MAX_GSL_LENGTH_M:
            sat_net_graph.add_edge(1586, sid, weight = distance_m)

        distance_m = distance_m_ground_station_to_satellite(
            ground_stations[gs],
            satellites[sid],
            str(epoch),
            str(t)
        )
        if distance_m <= MAX_GSL_LENGTH_M:
            sat_net_graph.add_edge(1585, sid, weight = distance_m)

    return sat_net_graph

def calculate_path_lengths(graphs, path):
    lengths = [0] * total_time

    for i in range(total_time):
        if nx.is_simple_path(graphs[i], path):
            lengths[i] = compute_path_length_with_graph(path, graphs[i])

    return lengths

def main():
    args = sys.argv[1:]
    
    gs = int(args[0])
    point = int(args[1])
    graphs = {}
    t1 = time.time()
    num_threads = 1
    per_thread = total_time // num_threads
    ths = []
    for i in range(total_time):
        graphs[i] = generate_graph(i, gs, point)

    print(time.time() - t1)

    paths_to_ids = {}
    paths = []

    for t in range(total_time):
        pths = k_shortest_paths(graphs[t], 1585, 1586, 2, weight = "weight")
        for path in pths:
            new_path = copy.deepcopy(path)
            new_path[0] = gs
            new_path[-1] = point
            if str(new_path) not in paths_to_ids:
            
                paths_to_ids[str(new_path)] = len(paths)
                paths.append(calculate_path_lengths(graphs, path))

    plt_colors = ["b-", "r-", "g-", "c-", "m-", "y-", "k-", "b--", "r--", "g--", "c--", "m--", "y--", "k--", "b:", "r:", "g:", "c:", "m:", "y:", "k:", "b-.", "r-.", "g-.", "c-.", "m-.", "y-.", "k-."]
    i = 0
    for path in paths_to_ids:
        print(path, paths[paths_to_ids[path]])
        x = np.arange(0, total_time)
        y = np.array(paths[paths_to_ids[path]])
        ids = np.nonzero(y)
        plt.plot(x[ids], y[ids] / 1000, plt_colors[i % 28], label=path)

        i = i + 1

    plt.legend(bbox_to_anchor=(1.0, 1.05), loc='lower right', fontsize=4)
    plt.tight_layout()
    base_file = args[0] + "_" + args[1]
    png_file = "good_paths_6000/pngs/" + base_file + ".png"
    pdf_file = "good_paths_6000/pdfs/" + base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)
    

if __name__ == "__main__":
    main()
    