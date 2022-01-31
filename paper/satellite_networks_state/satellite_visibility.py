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
total_time = 1000

def generate_infra(satellite_network_dir):
    
    tles = read_tles(satellite_network_dir + "/tles.txt")
    satellites = tles["satellites"]
    list_isls = read_isls(satellite_network_dir + "/isls.txt", len(satellites))
    
    epoch = tles["epoch"]
    print(epoch)
    return satellites, list_isls, epoch

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

def calculate_satellite_visibilities(point, satellite, epoch):
    distances = [0] * total_time
    for tt in range(total_time):
        t = epoch + tt / 86400
        distance_m = distance_m_ground_station_to_satellite(
            point,
            satellite,
            str(epoch),
            str(t)
        )
        if distance_m <= MAX_GSL_LENGTH_M:
            distances[tt] = distance_m

    return distances

def main():    
    satellite_network_dir = "./gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    satellites, list_isls, epoch = generate_infra(satellite_network_dir)

    points = generate_points()
    args = sys.argv[1:]
    point = points[int(args[0])]
    
    satellites_in_range = {}
    for tt in range(total_time):
        t = epoch + tt / 86400
        for sid in range(len(satellites)):
            if sid in satellites_in_range:
                continue

            distance_m = distance_m_ground_station_to_satellite(
                point,
                satellites[sid],
                str(epoch),
                str(t)
            )

            if distance_m <= MAX_GSL_LENGTH_M:
                print(sid, sid // 22)
                satellites_in_range[sid] = calculate_satellite_visibilities(point, satellites[sid], epoch)

    plt_colors = ["b-", "r-", "g-", "c-", "m-", "y-", "k-", "b--", "r--", "g--", "c--", "m--", "y--", "k--", "b:", "r:", "g:", "c:", "m:", "y:", "k:", "b-.", "r-.", "g-.", "c-.", "m-.", "y-.", "k-."]
    orbit_plot_mapping = {}
    i = 0

    for sat in satellites_in_range:
        orbit = sat // 22
        id = i
        if orbit in orbit_plot_mapping:
            id = orbit_plot_mapping[orbit]
        else:
            orbit_plot_mapping[orbit] = id
            i += 1

        x = np.arange(0, total_time)
        y = np.array(satellites_in_range[sat])
        ids = np.nonzero(y)
        plt.plot (x[ids], y[ids] / 1000, plt_colors[id % 28], label = str(sat))

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fontsize=6, ncol=6)
    png_file = "points/pngs/" + args[0] + ".png"
    plt.savefig(png_file)


if __name__ == "__main__":
    main()
