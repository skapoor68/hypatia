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
import ephem

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
total_time = 1000

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
    print(epoch)
    return satellites, list_isls, epoch

def generate_path(src, dst, isl_path):
    path = [src["gid"]]
    path.extend(isl_path)
    path.append(dst)
    return path

def get_graphs():
    # TODO: fill in the remaining two dictionaries
    graphs = {}
    dist_sat_nets = {}
    shortest_path_nets = {}
    for i in range(total_time):
        graph_path = "./graphs/graph_" + str(i) + ".txt"
        graphs[i] = nx.read_gpickle(graph_path)

    return graphs, dist_sat_nets, shortest_path_nets

def calculate_longest_living_path(gs, point, tt, epoch, gs_satellites_in_range, point_satellites_in_range, graph, shortest_paths, satellites):
    src_sid = -1
    val = -math.inf
    gs_obs = ephem.Observer()
    for sid in gs_satellites_in_range:
        print(satellites[sid])

def main():    
    satellite_network_dir = "./gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    satellites, list_isls, epoch = generate_infra(satellite_network_dir)
    ground_stations = generate_groundstations()
    points = generate_points()

    graphs, dist_sat_nets, shortest_path_nets = get_graphs()
    
    for point in points:
        for gs in ground_stations:
            longest_living_path = None
            longest_living_path_lengths = []
            shortest_path_lengths = []
            ratio = []
            difference = []
            for tt in range(total_time):
                t = epoch + tt / 86400
                # TODO: replace with access from the dictionary instead of recomputing
                dist_sat_net = nx.floyd_warshall_numpy(graphs[tt])
                shortest_paths = dict(nx.all_pairs_shortest_path(graphs[tt]))

                point_satellites_in_range = {}
                for sid in range(len(satellites)):
                    distance_m = distance_m_ground_station_to_satellite(
                        point,
                        satellites[sid],
                        str(epoch),
                        str(t)
                    )
                    if distance_m <= MAX_GSL_LENGTH_M:
                        point_satellites_in_range[sid] = distance_m

                gs_satellites_in_range = {}
                for sid in range(len(satellites)):
                    distance_m = distance_m_ground_station_to_satellite(
                        gs,
                        satellites[sid],
                        str(epoch),
                        str(t)
                    )
                    if distance_m <= MAX_GSL_LENGTH_M:
                        gs_satellites_in_range[sid] = distance_m

                if longest_living_path is None \
                    or longest_living_path[0] not in gs_satellites_in_range \
                    or longest_living_path[-1] not in point_satellites_in_range \
                    or not nx.is_simple_path(graphs[tt], longest_living_path):
                    longest_living_path, longest_living_path_length = calculate_longest_living_path(gs, point, tt, epoch, gs_satellites_in_range, point_satellites_in_range, graphs[tt], shortest_paths, satellites)
                else:                
                    longest_living_path_length = gs_satellites_in_range[longest_living_path[0]] \
                                            + point_satellites_in_range[longest_living_path[-1]] \
                                            + nx.classes.function.path_weight(graphs[tt], longest_living_path, "weight")

                longest_living_path_lengths.append(longest_living_path_length)
                
                shortest_path_length = math.inf
                for src_sid in gs_satellites_in_range:
                    for dst_sid in point_satellites_in_range:
                        if not math.isinf(dist_sat_net[(src_sid, dst,sid)]) and gs_satellites_in_range[src_sid] + point_satellites_in_range[dst_sid] + dist_sat_net[(src_sid, dst,sid)] < shortest_path_length:
                            shortest_path_length = gs_satellites_in_range[src_sid] + point_satellites_in_range[dst_sid] + dist_sat_net[(src_sid, dst,sid)]

                shortest_path_lengths.append(shortest_path_length)

                ratio.append(longest_living_path / shortest_path_length)
                difference.append(longest_living_path - shortest_path_length)
            
            print(gs['gid'])
            print(point['pid'])
            print(longest_living_path_lengths)
            print(shortest_path_lengths)
            print(ratio)
            print(difference)
            break



if __name__ == "__main__":
    main()
