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
sys.path.append("../../satgenpy")
import math
from satgen import *
import networkx as nx
import numpy as np

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
dist_limits = [1500000, 2500000, 5000000, 7500000, 10000000, 12500000, 15000000, 20000000, 30000000, 40000000, 50000000, 60000000]

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
    for lat in range(-60, 60, 2):
        for lon in range(-180, 180, 2):
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



def main():
    args = sys.argv[1:]
    # if len(args) != 6:
    #     print("Must supply exactly six arguments")
    #     print("Usage: python main_starlink_550.py [duration (s)] [time step (ms)] "
    #           "[isls_plus_grid / isls_none] "
    #           "[ground_stations_{top_100, paris_moscow_grid}] "
    #           "[algorithm_{free_one_only_over_isls, free_one_only_gs_relays, paired_many_only_over_isls}] "
    #           "[num threads]")
    #     exit(1)
    # else:
    #     main_helper.calculate(
    #         "gen_data",
    #         int(args[0]),
    #         int(args[1]),
    #         args[2],
    #         args[3],
    #         args[4],
    #         int(args[5]),
    #     )
    
    satellite_network_dir = "./gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    satellites, list_isls, epoch = generate_infra(satellite_network_dir)
    ground_stations = generate_groundstations()
    points = generate_points()
    print("setup completed. Total points: ", len(points))
    # print(ground_stations)
    time = epoch
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
        sat_distance_m = distance_m_between_satellites(satellites[a], satellites[b], str(epoch), str(time))
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
    ground_station_satellite_distances = []

    point_satellites_in_range_candidates = {}
    for point in points:
        satellites_in_range = []
        for sid in range(len(satellites)):
            distance_m = distance_m_ground_station_to_satellite(
                point,
                satellites[sid],
                str(epoch),
                str(time)
            )
            if distance_m <= MAX_GSL_LENGTH_M:
                satellites_in_range.append((distance_m, sid))

        point_satellites_in_range_candidates[point["pid"]] = satellites_in_range
    
    print("all points candidate satellites generated")

    for ground_station in ground_stations:
        # check whether the pre-selected satellites are in range
        satellites_in_range = []
        for sid in ground_station["satellites"]:
            distance_m = distance_m_ground_station_to_satellite(
                ground_station,
                satellites[sid],
                str(epoch),
                str(time)
            )
            if distance_m <= MAX_GSL_LENGTH_M:
                satellites_in_range.append((distance_m, sid))

        satellites_in_range = list(sorted(satellites_in_range))
        print(ground_station)
        print(len(satellites_in_range), satellites_in_range)

        curr_distances = np.zeros((4, len(points)))
        idx = 0
        for (dist,sat) in satellites_in_range:
            for pid in range(len(points)):
                point = points[pid]
                possible_dst_satellites = point_satellites_in_range_candidates[pid]
                possibilities = []
                for b in possible_dst_sats:
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
                else:
                    curr_distances[idx][pid] = math.inf
            
            idx += 1
    
        print(np.amax(curr_distances), np.min(curr_distances))
        print(np.amax(curr_distances[0]), np.min(curr_distances[0]))
        print(np.amax(curr_distances[1]), np.min(curr_distances[1]))
        print(np.amax(curr_distances[2]), np.min(curr_distances[2]))
        print(np.amax(curr_distances[3]), np.min(curr_distances[3]))

        per_satellite_shortest_dist = np.amin(curr_distances, axis=0)
        print(per_satellite_shortest_dist.shape)
        for d in dist_limits:
            print("Current distance limit:", d)
            nearby_satellites = np.nonzero(per_satellite_shortest_dist <= d)
            nearby_satellites = nearby_satellites[0]
            print("number of such satellites: ", nearby_satellites)

            sat_distances = curr_distances[:, nearby_satellites]
            print(sat_distances)
            delta = np.amax(sat_distances, axis=0) - np.amin(sat_distances, axis=0)
            delta = delta / 1000
            print("Mean, Median, 75th Percentile, 90th Percentile")
            print(np.mean(delta), np.median(delta), np.percentile(delta, 75), np.percentile(delta, 90))
            print("-/-/-/-/-/-/-/-/-/-/-/-/-/")

        

        print("======================================")
        break
        # ground_station_satellites_in_range.append(satellites_in_range)
    



if __name__ == "__main__":
    main()
