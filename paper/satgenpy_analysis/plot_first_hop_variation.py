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
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
from collections import OrderedDict
from matplotlib.ticker import FormatStrFormatter

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

lat_values = [5, 15, 25, 35, 45, 55]
dist_limits = [0, 500, 1000, 1500, 2500, 5000, 7500, 10000, 12500, 15000, 17500, 20000]

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

def generate_command(src, dst, viz_type, paths):
    command = "cd ../../satviz/scripts/; python visualize_learning_patterns.py " + str(src) + " " + str(dst) + " " + viz_type + " "
    for path in paths:
        path_string = json.dumps(path).replace(" ", "")
        command += path_string + " "

    command += "2> ../viz_outputs/err" + str(src) + "_" + str(dst) + "_" + viz_type + ".txt "
    command += "> ../viz_outputs/" + str(src) + "_" + str(dst) + "_" + viz_type + ".txt"
    commands_to_run.append(command)


def main():
    args = sys.argv[1:]
    kind = args[0]    
    satellite_network_dir = "../satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    satellites, list_isls, epoch = generate_infra(satellite_network_dir)
    ground_stations = generate_groundstations()
    points = generate_points()
    print("setup completed. Total points: ", len(points))
    # print(ground_stations)
    t = epoch
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

        # Interface mapping of ISLs
        sat_neighbor_to_if[(a, b)] = num_isls_per_sat[a]
        sat_neighbor_to_if[(b, a)] = num_isls_per_sat[b]
        num_isls_per_sat[a] += 1
        num_isls_per_sat[b] += 1
        total_num_isls += 1

    dist_sat_net_without_gs = nx.floyd_warshall_numpy(sat_net_graph_only_satellites_with_isls)
    shortest_paths_without_gs = dict(nx.all_pairs_shortest_path(sat_net_graph_only_satellites_with_isls))
    ground_station_satellite_distances = []

    point_satellites_in_range_candidates = {}
    for point in points:
        satellites_in_range = []
        for sid in range(len(satellites)):
            distance_m = distance_m_ground_station_to_satellite(
                point,
                satellites[sid],
                str(epoch),
                str(t)
            )
            if distance_m <= MAX_GSL_LENGTH_M:
                satellites_in_range.append((distance_m, sid))

        point_satellites_in_range_candidates[point["pid"]] = satellites_in_range
    
    print("all points candidate satellites generated")

    ratios_latitude = []
    distances_ratio = []
    for i in range(len(dist_limits[1:])):
        distances_ratio.append([])

    for ground_station in ground_stations:
        # check whether the pre-selected satellites are in range
        satellites_in_range = []
        paths = {}
        geodesic_distances = []
        for pid in range(len(points)):
            paths[pid] = []
            geodesic_distances.append(geodesic_distance_m_between_ground_stations(ground_station, points[pid]) / 1000)

        geodesic_distances = np.array(geodesic_distances)
        # print("geodesic distances", np.mean(geodesic_distances), np.median(geodesic_distances))
        for sid in range(len(satellites)):
            distance_m = distance_m_ground_station_to_satellite(
                ground_station,
                satellites[sid],
                str(epoch),
                str(t)
            )
            if distance_m <= MAX_GSL_LENGTH_M:
                satellites_in_range.append((distance_m, sid))

        satellites_in_range = list(sorted(satellites_in_range[:5]))
        print(ground_station)
        print(len(satellites_in_range), satellites_in_range)

        curr_distances = np.zeros((len(satellites_in_range), len(points)))
        idx = 0
        for (dist,sat) in satellites_in_range:
            for pid in range(len(points)):
                point = points[pid]
                possible_dst_satellites = point_satellites_in_range_candidates[pid]
                possibilities = []
                for b in possible_dst_satellites:
                    if not math.isinf(dist_sat_net_without_gs[(sat, b[1])]):  # Must be reachable
                        possibilities.append(
                            (
                                dist_sat_net_without_gs[(sat, b[1])] + b[0],
                                b[1]
                            )
                        )

                possibilities = list(sorted(possibilities))
                if len(possibilities) > 0:
                    curr_distances[idx][pid] = dist + possibilities[0][0]
                    path = generate_path(ground_station, pid, shortest_paths_without_gs[sat][possibilities[0][1]])
                    paths[pid].append(path)
                else:
                    print("infinite distance", ground_station, sat, pid)
                    curr_distances[idx][pid] = math.inf
            
            idx += 1
        
        #convert from m to km
        curr_distances /= 1000
        if kind == "latitude":
            ratios_latitude.append(np.amax(curr_distances, axis=0) / np.amin(curr_distances, axis=0))
            continue
        elif kind == "distance":
            per_satellite_shortest_dist = np.amin(curr_distances, axis=0)
            print(per_satellite_shortest_dist.shape)

            for idx in range(1, len(dist_limits)):
                d = dist_limits[idx]
                # print("Current distance limit:", d)
                
                nearby_points = np.nonzero(np.logical_and(geodesic_distances <= d, geodesic_distances > dist_limits[idx - 1]))
                nearby_points = nearby_points[0]
                # print("number of such points: ", len(nearby_points))
                if len(nearby_points) > 0:
                    sat_distances = curr_distances[:, nearby_points]
                    # print(sat_distances)
                    actual_distances = np.amin(sat_distances, axis=0)
                    # delta = np.amax(sat_distances, axis=0) - np.amin(sat_distances, axis=0)
                    # max_delta = nearby_points[np.argmax(delta)]
                    # min_delta = nearby_points[np.argmin(delta)]
                    # median_delta = nearby_points[np.argsort(delta)[len(delta)//2]]
                    # delta = (delta * 1e6) / 299792458.0
                    ratio = np.divide(np.amax(sat_distances, axis=0), actual_distances)
                    print(len(distances_ratio[idx-1]))
                    distances_ratio[idx - 1].extend(list(ratio))
                    print(len(distances_ratio[idx-1]))
                    print(np.mean(np.array(distances_ratio[idx - 1])))
                    # max_ratio = nearby_points[np.argmax(ratio)]
                    # actual_rtt = (actual_distances * 1e6) / 299792458.0
                    # print("Type, Mean, Median, 75th Percentile, 90th Percentile, Max, Min, Std Dev")
                    # print("Actual RTT", np.mean(actual_rtt), np.median(actual_rtt), np.percentile(actual_rtt, 75), np.percentile(actual_rtt, 90), np.max(actual_rtt), np.min(actual_rtt), np.std(actual_rtt), sep=',')
                    # print("Delta", np.mean(delta), np.median(delta), np.percentile(delta, 75), np.percentile(delta, 90), np.max(delta), np.min(delta), np.std(delta), sep=',')
                    print("Ratio", np.mean(ratio), np.median(ratio), np.percentile(ratio, 75), np.percentile(ratio, 90), np.max(ratio), np.min(ratio), np.std(ratio), sep=',')
                    
                # print("-/-/-/-/-/-/-/-/-/-/-/-/-/")

        

        # print("======================================")
        
        # ground_station_satellites_in_range.append(satellites_in_range)
    
    if kind == "latitude":
        fig, ax = plt.subplots()
        ratios_latitude = np.array(ratios_latitude)
        print(ratios_latitude.shape)
        ax.errorbar(lat_values, np.mean(ratios_latitude, axis=1), yerr=np.std(ratios_latitude, axis=1), fmt='ro-')
        plt.ylabel("Ratio of first hop distances", fontsize=18)
        plt.xlabel("Latitude of Source", fontsize=18)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.subplots_adjust(bottom=0.15)
        plt.tight_layout()

        plt.savefig("RatioLatitude.png")
        plt.savefig("RatioLatitude.pdf")

    else:
        plt.figure(figsize=(6.4,3.2))
        means, stddevs = [], []
        for i in range(len(distances_ratio)):
            ratios = np.array(distances_ratio[i])
            means.append(np.mean(ratios))
            stddevs.append(np.std(ratios))
            print(i, means[-1], stddevs[-1])
        means = np.array(means)
        stddevs = np.array(stddevs)
        print(means.shape)
        plt.plot(np.array(dist_limits[1:]) / 1000, means, 'c-')
        plt.fill_between(np.array(dist_limits[1:]) / 1000, means - stddevs, means+stddevs, alpha=0.5)

        plt.xlabel("Distance between ground stations\n (in 1000 km)", fontsize=18)
        plt.ylabel("Worst first hop/\nbest first hop", fontsize=18)
        plt.yticks(fontsize=14)
        # plt.xscale("log")
        plt.xticks(fontsize=14)
        plt.grid(linewidth=0.5, linestyle=':')
        plt.tight_layout()

        plt.savefig("paper_plots/RatioDistance.png")
        plt.savefig("paper_plots/RatioDistance.pdf")


if __name__ == "__main__":
    main()
