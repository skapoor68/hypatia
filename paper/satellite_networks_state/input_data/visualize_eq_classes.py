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
import pandas as pd

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
GEN_TIME=46800  #ms

# Input file; Generated during simulation
# Note the file_name consists of the 2 city IDs being offset by the size of the constellation
# City IDs are available in the city_detail_file.
# If city ID is X (for Paris X = 24) and constellation is Starlink_550 (1584 satellites),
# then offset ID is 1584 + 24 = 1608.
path_file = "../../paper/satgenpy_analysis/data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_200s/manual/data/networkx_path_1585_to_1588.txt"

# Output directory for creating visualization html files
OUT_DIR = "../viz_output/"
OUT_HTML_FILE = OUT_DIR + NAME + "_path"

sat_objs = []
city_details = {}
paths_over_time = []

def geodetic2cartesian(lat_degrees, lon_degrees, ele_m):
    """
    Compute geodetic coordinates (latitude, longitude, elevation) to Cartesian coordinates.

    :param lat_degrees: Latitude in degrees (float)
    :param lon_degrees: Longitude in degrees (float)
    :param ele_m:  Elevation in meters

    :return: Cartesian coordinate as 3-tuple of (x, y, z)
    """

    #
    # Adapted from: https://github.com/andykee/pygeodesy/blob/master/pygeodesy/transform.py
    #

    # WGS72 value,
    # Source: https://geographiclib.sourceforge.io/html/NET/NETGeographicLib_8h_source.html
    a = 6378135.0

    # Ellipsoid flattening factor; WGS72 value
    # Taken from https://geographiclib.sourceforge.io/html/NET/NETGeographicLib_8h_source.html
    f = 1.0 / 298.26

    # First numerical eccentricity of ellipsoid
    e = math.sqrt(2.0 * f - f * f)
    lat = lat_degrees * (math.pi / 180.0)
    lon = lon_degrees * (math.pi / 180.0)

    # Radius of curvature in the prime vertical of the surface of the geodetic ellipsoid
    v = a / math.sqrt(1.0 - e * e * math.sin(lat) * math.sin(lat))

    x = (v + ele_m) * math.cos(lat) * math.cos(lon)
    y = (v + ele_m) * math.cos(lat) * math.sin(lon)
    z = (v * (1.0 - e * e) + ele_m) * math.sin(lat)

    return np.array(x / 1000, y / 1000, z / 1000)

def calculate_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0]) * (point2[0] - point1[0]) 
        + (point2[1] - point1[1]) * (point2[1] - point1[1])
     + (point2[2] - point1[2]) * (point2[2] - point1[2]))
     
earth_radius = 6378.135
altitude = 550
theta = math.acos(earth_radius / (earth_radius + altitude))

latency = 15

def get_class_id(distance):
	if distance < 2 * (earth_radius + altitude) * math.sin(theta / 2):
		return 0
	elif distance < 2 * (earth_radius + altitude) * math.sin((2 * theta) / 2):
		return 1
	elif distance < 2 * (earth_radius + altitude) * math.sin((3 * theta) / 2):
		return 2
	elif distance < 2 * (earth_radius + altitude) * math.sin((4 * theta) / 2):
		return 3
	elif distance < 2 * (earth_radius + altitude) * math.sin((5 * theta) / 2):
		return 4
	elif distance < 2 * (earth_radius + altitude) * math.sin((6 * theta) / 2):
		return 5
	elif distance < 2 * (earth_radius + altitude) * math.sin((7 * theta) / 2):
		return 6
	else:
		return 7

sat_mapping = {}

def generate_satellite_eq_classes_mapping(satellites, t):
    for i, sat in enumerate(satellites):
        sat_objs[i]["sat_obj"].compute(shifted_epoch)
        sat_coords = geodetic2cartesian(sat_objs[i]["sat_obj"].sublat, sat_objs[i]["sat_obj"].sublong, 550000)
        city_coords = geodetic2cartesian(city["long_deg"], city["long_deg"], 550000)

        dist = calculate_distance(sat_coords, city_coords)
        sat_mapping[i] = get_class_id(dist)

colors = ["RED", "BROWN", "DARKORANGE", "FUCHSIA", "GOLD", "HOTPINK", "INDIGO", "SLATEGREY", "YELLOWGREEN", "BLACK", "YELLOW"]

def generate_eq_classes_visualization():
    """
    Generates end-to-end path at specified time
    :return: HTML formatted string for visualization
    """
    viz_string = ""
    global src_GS
    global dst_GS
    global paths_over_time
    global OUT_HTML_FILE
    

    shifted_epoch = (pd.to_datetime(EPOCH) + pd.to_timedelta(GEN_TIME, unit='ms')).strftime(format='%Y/%m/%d %H:%M:%S.%f')
    print(shifted_epoch)
    generate_satellite_eq_classes_mapping(sat_objs, shifted_epoch)
    for i in range(len(sat_objs)):
        sat_objs[i]["sat_obj"].compute(shifted_epoch)
        viz_string += "var redSphere = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
                     + str(math.degrees(sat_objs[i]["sat_obj"].sublong)) + ", " \
                     + str(math.degrees(sat_objs[i]["sat_obj"].sublat)) + ", "+str(sat_objs[i]["alt_km"]*1000)+"), "\
                     + "ellipsoid : {radii : new Cesium.Cartesian3(20000.0, 20000.0, 20000.0), "\
                     + "material : Cesium.Color." + colors[sat_mapping[i]] + ".withAlpha(1),}});\n"

    orbit_links = util.find_orbit_links(sat_objs, NUM_ORBS, NUM_SATS_PER_ORB)
    for key in orbit_links:
        sat1 = orbit_links[key]["sat1"]
        sat2 = orbit_links[key]["sat2"]
        viz_string += "viewer.entities.add({name : '', polyline: { positions: Cesium.Cartesian3.fromDegreesArrayHeights([" \
                      + str(math.degrees(sat_objs[sat1]["sat_obj"].sublong)) + "," \
                      + str(math.degrees(sat_objs[sat1]["sat_obj"].sublat)) + "," \
                      + str(sat_objs[sat1]["alt_km"] * 1000) + "," \
                      + str(math.degrees(sat_objs[sat2]["sat_obj"].sublong)) + "," \
                      + str(math.degrees(sat_objs[sat2]["sat_obj"].sublat)) + "," \
                      + str(sat_objs[sat2]["alt_km"] * 1000) + "]), " \
                      + "width: 0.5, arcType: Cesium.ArcType.NONE, " \
                      + "material: new Cesium.PolylineOutlineMaterialProperty({ " \
                      + "color: Cesium.Color.GREY.withAlpha(0.3), outlineWidth: 0, outlineColor: Cesium.Color.BLACK})}});"

    OUT_HTML_FILE += "_"+city["name"] + "_" +str(SEL_PATH[p])
    viz_string += "var redSphere = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
                    + str(city["long_deg"]) + ", " \
                    + str(city["lat_deg"]) + ", " \
                    + str(city["alt_km"] * 1000) + "), " \
                    + "ellipsoid : {radii : new Cesium.Cartesian3(50000.0, 50000.0, 50000.0), " \
                    + "material : Cesium.Color.GREEN.withAlpha(1),}});\n"

    

    OUT_HTML_FILE += "_" + str(GEN_TIME) + ".html"
    return viz_string


city = {
            "name": "Atlanta",
            "lat_deg": 33.76,
            "long_deg": -84.4,
            "alt_km": 0
        }
sat_objs = util.generate_sat_obj_list(
    NUM_ORBS,
    NUM_SATS_PER_ORB,
    EPOCH,
    PHASE_DIFF,
    INCLINATION_DEGREE,
    ECCENTRICITY,
    ARG_OF_PERIGEE_DEGREE,
    MEAN_MOTION_REV_PER_DAY,
    ALTITUDE_M
)
viz_string = generate_eq_classes_visualization()
util.write_viz_files(viz_string, topFile, bottomFile, OUT_HTML_FILE)
