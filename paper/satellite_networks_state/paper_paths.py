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

def generate_points():
    points = []
    i = 0
    
    lat = 40.717042
    lon = -74.003663
    
    point = {}
    point['pid'] = i
    point['latitude_degrees_str'] = str(lat)
    point['longitude_degrees_str'] = str(lon)
    point['name'] = "New York"
    point['elevation_m_float'] = 0
    point['cartesian_x'], point['cartesian_x'], point['cartesian_x'] = geodetic2cartesian(lat, lon, 0)
    points.append(point)
    i = i + 1


    lat = 51.50853
    lon = -0.12574
    point = {}
    point['gid'] = i
    point['latitude_degrees_str'] = str(lat)
    point['longitude_degrees_str'] = str(lon)
    point['name'] = "London"
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
    print(epoch)
    return satellites, list_isls, epoch

def generate_path(src, dst, isl_path):
    path = [src["gid"]]
    path.extend(isl_path)
    path.append(dst)
    return path

def generate_command(src, dst, viz_type, paths):
    command = "cd ../../satviz/scripts/; python visualize_learning_patterns.py " + str(src) + " " + str(dst) + " " + viz_type + " "

    if viz_type == "path":
        path_string = json.dumps(paths).replace(" ", "")
        command += path_string + " "

    else:
        for path in paths:
            command += path_string + " "

    command += "2> ../viz_outputs/err" + str(src) + "_" + str(dst) + "_" + viz_type + ".txt "
    command += "> ../viz_outputs/" + str(src) + "_" + str(dst) + "_" + viz_type + ".txt"
    print(command)
    commands_to_run.append(command)

def k_shortest_paths(G, source, target, k, weight=None):
    return list(
        islice(nx.shortest_simple_paths(G, source, target, weight=weight), k)
    )


def main():
    
    satellite_network_dir = "gen_data/starlink_550_isls_plus_grid_ground_stations_newyork_london_circular_bigger_algorithm_free_one_only_over_isls"
    satellites, list_isls, epoch = generate_infra(satellite_network_dir)
    points = generate_points()
    epoch = epoch+1200/(24*60*60)
    print(epoch)
    
    t = epoch
    sat_net_graph = nx.Graph()
    for i in range(len(satellites)):
        sat_net_graph.add_node(i)

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
        sat_net_graph.add_edge(
            a, b, weight=sat_distance_m
        )

        # Interface mapping of ISLs
        sat_neighbor_to_if[(a, b)] = num_isls_per_sat[a]
        sat_neighbor_to_if[(b, a)] = num_isls_per_sat[b]
        num_isls_per_sat[a] += 1
        num_isls_per_sat[b] += 1
        total_num_isls += 1

    sats = []
    for sid in range(len(satellites)):
        distance_m = distance_m_ground_station_to_satellite(
            points[0],
            satellites[sid],
            str(epoch),
            str(t)
        )
        if distance_m <= MAX_GSL_LENGTH_M:
            sat_net_graph.add_edge(1584, sid, weight = distance_m)

        distance_m = distance_m_ground_station_to_satellite(
            points[1],
            satellites[sid],
            str(epoch),
            str(t)
        )
        if distance_m <= MAX_GSL_LENGTH_M:
            sat_net_graph.add_edge(1585, sid, weight = distance_m)

    

    # for sat in sats:
    #     l = nx.shortest_path(sat_net_graph, sat, 1585, "weight")
    #     print(sat, l)

    print(sat_net_graph[1584])
    paths = k_shortest_paths(sat_net_graph, 1584, 1585, 15, weight = "weight")
    print(paths)
    # for path in paths:
    #     path[0] = point
    #     path[-1] = gs
        
    #     generate_command(gs, point, "path", path)

    # print(paths)

    # print("Running commands (at most %d in parallel)..." % max_num_processes)
    # for i in range(len(commands_to_run)):
    #     print("Starting command %d out of %d: %s" % (i + 1, len(commands_to_run), commands_to_run[i]))
    #     local_shell.detached_exec(commands_to_run[i])
    #     while local_shell.count_screens() >= max_num_processes:
    #         time.sleep(2)

    # # Awaiting final completion before exiting
    # print("Waiting completion of the last %d..." % max_num_processes)
    # while local_shell.count_screens() > 0:
    #     time.sleep(2)
    # print("Finished.")

    

if __name__ == "__main__":
    main()
    