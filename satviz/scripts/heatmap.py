# MIT License
#
# Copyright (c) 2020 Debopam Bhattacherjee
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

import math
import ephem
import numpy as np
import pandas as pd
import datetime
import csv
import sys

import folium
from folium import plugins
from folium.plugins import HeatMap

try:
    from . import util
except (ImportError, SystemError):
    import util

# Visualizes paths between endpoints at specific time instances

EARTH_RADIUS = 6378135.0 # WGS72 value; taken from https://geographiclib.sourceforge.io/html/NET/NETGeographicLib_8h_source.html

# CONSTELLATION GENERATION GENERAL CONSTANTS
ECCENTRICITY = 0.0000001  # Circular orbits are zero, but pyephem does not permit 0, so lowest possible value
ARG_OF_PERIGEE_DEGREE = 0.0
PHASE_DIFF = True
EPOCH = "2000-01-01 00:00:00"

# CONSTELLATION SPECIFIC PARAMETERS
# STARLINK 550
NAME = "starlink_550"

################################################################
# The below constants are taken from Starlink's FCC filing as below:
# [1]: https://fcc.report/IBFS/SAT-MOD-20190830-00087
################################################################

MEAN_MOTION_REV_PER_DAY = 15.19  # Altitude ~550 km
ALTITUDE_M = 550000  # Altitude ~550 km
SATELLITE_CONE_RADIUS_M = 940700 # From https://fcc.report/IBFS/SAT-MOD-20181108-00083/1569860.pdf (minimum angle of elevation: 25 deg)
MAX_GSL_LENGTH_M = math.sqrt(math.pow(SATELLITE_CONE_RADIUS_M, 2) + math.pow(ALTITUDE_M, 2))
MAX_ISL_LENGTH_M = 2 * math.sqrt(math.pow(EARTH_RADIUS + ALTITUDE_M, 2) - math.pow(EARTH_RADIUS + 80000, 2)) # ISLs are not allowed to dip below 80 km altitude in order to avoid weather conditions
NUM_ORBS = 72
NUM_SATS_PER_ORB = 22
INCLINATION_DEGREE = 53


# KUIPER 630
"""
NAME = "kuiper_630"

################################################################
# The below constants are taken from Kuiper's FCC filing as below:
# [1]: https://www.itu.int/ITU-R/space/asreceived/Publication/DisplayPublication/8716
################################################################

MEAN_MOTION_REV_PER_DAY = 14.80  # Altitude ~630 km
ALTITUDE_M = 630000  # Altitude ~630 km
SATELLITE_CONE_RADIUS_M = ALTITUDE_M / math.tan(math.radians(30.0))  # Considering an elevation angle of 30 degrees; possible values [1]: 20(min)/30/35/45
MAX_GSL_LENGTH_M = math.sqrt(math.pow(SATELLITE_CONE_RADIUS_M, 2) + math.pow(ALTITUDE_M, 2))
MAX_ISL_LENGTH_M = 2 * math.sqrt(math.pow(EARTH_RADIUS + ALTITUDE_M, 2) - math.pow(EARTH_RADIUS + 80000, 2))  # ISLs are not allowed to dip below 80 km altitude in order to avoid weather conditions
NUM_ORBS = 34
NUM_SATS_PER_ORB = 34
INCLINATION_DEGREE = 51.9
"""

# General files needed to generate visualizations; Do not change for different simulations
topFile = "../static_html/top.html"
bottomFile = "../static_html/bottom.html"
city_detail_file = "../../paper/satellite_networks_state/input_data/ground_stations_cities_sorted_by_estimated_2025_pop_top_1000.basic.txt"

# Time in ms for which visualization will be generated
GEN_TIME=46000  #ms

# Input file; Generated during simulation
# Note the file_name consists of the 2 city IDs being offset by the size of the constellation
# City IDs are available in the city_detail_file.
# If city ID is X (for Paris X = 24) and constellation is Starlink_550 (1584 satellites),
# then offset ID is 1584 + 24 = 1608.
path_file = "../../paper/satgenpy_analysis/data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_200s/manual/data/networkx_path_1585_to_1588.txt"

# Output directory for creating visualization html files
OUT_DIR = "../viz_output/"
OUT_HTML_FILE = OUT_DIR + NAME + "_"

lat_values = [5, 20, 35, 55]

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
            points.append(point)
            i = i + 1

    return points

colors = ["RED", "BROWN", "DARKORANGE", "FUCHSIA", "GOLD", "HOTPINK", "INDIGO", "SLATEGREY", "YELLOWGREEN", "BLACK", "YELLOW"]

def load_data(source):
    point_intensity = [None] * 2700
    f = "../../paper/satellite_networks_state/shortest_paths_analysis.txt"

    with open(f) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in spamreader:
            if row[0] == "max ratio" and int(row[1]) == source:
                dest = int(row[2])
                ratio = float(row[3])
                point_intensity[dest] = ratio
            else:
                continue

    # print(point_intensity)
    # print(max(point_intensity.keys()))
    return np.array(point_intensity)
    
def main():
    args = sys.argv[1:]
    source = int(args[0])

    points = generate_points()
    ground_stations = generate_groundstations()
    point_intensity = load_data(source)
    print(np.std(point_intensity), np.max(point_intensity), np.min(point_intensity), np.mean(point_intensity))
    # point_intensity = (point_intensity - np.mean(point_intensity))  * (10 / np.std(point_intensity))

    print(np.std(point_intensity), np.max(point_intensity), np.min(point_intensity))
    # point_intensity = point_intensity - 1
    
    data = []
    for point in points:
        # if point_intensity[point["pid"]] < 1.1:
        #     continue
        lat = int(point["latitude_degrees_str"])
        lon = int(point["longitude_degrees_str"])
        
        data.append([lat, lon, point_intensity[point["pid"]]])
        # data.append([lat+1.5, lon, point_intensity[point["pid"]]])
        # data.append([lat-1.5, lon, point_intensity[point["pid"]]])
        # data.append([lat, lon+1.5, point_intensity[point["pid"]]])
        # data.append([lat, lon-1.5, point_intensity[point["pid"]]])        
        # data.append([lat+1.5, lon+1.5, point_intensity[point["pid"]]])
        # data.append([lat-1.5, lon-1.5, point_intensity[point["pid"]]])
        # data.append([lat-1.5, lon+1.5, point_intensity[point["pid"]]])
        # data.append([lat+1.5, lon-1.5, point_intensity[point["pid"]]])

    # print(data[-1])
    m = folium.Map([5, -80],  zoom_start=3)
    folium.Marker([5, -80]).add_to(m)
    radius = 16
    HeatMap(data,radius=radius,blur=20, gradient={.4:"white",1:"red"}).add_to(folium.FeatureGroup(name='Heat Map').add_to(m))
    folium.LayerControl().add_to(m)
    # f_name = "heatmap_" + str(radius) + "_" + str(blur) + ".html"
    f_name = "heatmap.html"
    m.save(f_name)


if __name__ == "__main__":
    main()