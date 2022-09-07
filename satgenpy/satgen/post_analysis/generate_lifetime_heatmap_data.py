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
import csv

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
    f = "../paper/satellite_networks_state/input_data/ground_stations_world_grid_paper.basic.txt"
    points = []
    with open(f) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in spamreader:
            point = {}
            point['pid'] = int(row[0])
            point['name'] = row[1]
            point['latitude_degrees_str'] = float(row[2])
            point['longitude_degrees_str'] = float(row[3])
            point['elevation_m_float'] = float(row[4])
            points.append(point)

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
    points = generate_points()
    src_point = int(sys.argv[1])

    dir = "../paper/satgenpy_analysis/paper_data/starlink_550_isls_plus_grid_ground_stations_world_grid_paper_algorithm_free_one_only_over_isls/1000ms_for_600s/manual/data/"
    # print("src point", src_point)
    src = 1584 + src_point
    for dst_point in range(4, len(points)):
        dst = 1584 + dst_point
        file = "networkx_path_" + str(src) + "_to_" + str(dst) + ".txt"
        f = dir + file
        with open(f, 'r') as fp:
            num_switches = len(fp.readlines())

        file = "networkx_rtt_" + str(src) + "_to_" + str(dst) + ".txt"
        latencies = np.genfromtxt(dir + file, delimiter=",")
        min_rtt = np.min(latencies[:,1]) / 1000000
        max_rtt = np.max(latencies[:,1]) / 1000000

        print(dst_point, points[dst_point]["latitude_degrees_str"], points[dst_point]["longitude_degrees_str"], geodesic_distance_m_between_ground_stations(points[dst_point], points[src_point])/1000, num_switches, max_rtt-min_rtt, max_rtt/min_rtt, min_rtt, max_rtt, sep=",")
            

if __name__ == "__main__":
    main()
    