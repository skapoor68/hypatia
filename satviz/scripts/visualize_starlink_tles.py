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

# from astropy import units as u
# from poliastro.bodies import Earth
# from poliastro.twobody import Orbit
# from astropy.time import Time
# from extractor import CZMLExtractor
import math
import ephem
from astropy.time import Time
from astropy import units as u
try:
    from . import util
except (ImportError, SystemError):
    import util

# Generate static visualizations for entire constellation (multiple shells).

EARTH_RADIUS = 6378135.0 # WGS72 value; taken from https://geographiclib.sourceforge.io/html/NET/NETGeographicLib_8h_source.html

# CONSTELLATION GENERATION GENERAL CONSTANTS
ECCENTRICITY = 0.0000001  # Circular orbits are zero, but pyephem does not permit 0, so lowest possible value
ARG_OF_PERIGEE_DEGREE = 0.0
PHASE_DIFF = False
EPOCH = "2022-10-10 18:00:00"

# Shell wise color codes
# COLOR = [[255, 0, 0, 200], [32, 128, 46, 200], [0, 0, 255, 200], [245, 66, 242, 200], [245, 126, 66, 200]]
COLOR = ['CRIMSON', 'FORESTGREEN', 'DODGERBLUE', 'PERU', 'BLUEVIOLET', 'DARKMAGENTA']
# CONSTELLATION SPECIFIC PARAMETERS


# STARLINK
NAME = "Starlink"

SHELL_CNTR = 1

MEAN_MOTION_REV_PER_DAY = [None]*SHELL_CNTR
ALTITUDE_M = [None]*SHELL_CNTR
NUM_ORBS = [None]*SHELL_CNTR
NUM_SATS_PER_ORB = [None]*SHELL_CNTR
INCLINATION_DEGREE = [None]*SHELL_CNTR
BASE_ID = [None]*SHELL_CNTR
ORB_WISE_IDS = [None]*SHELL_CNTR

MEAN_MOTION_REV_PER_DAY[0] = 15.19  # Altitude ~550000 km
ALTITUDE_M[0] = 550000  # Altitude ~550000 km
NUM_ORBS[0] = 72
NUM_SATS_PER_ORB[0] = 22
INCLINATION_DEGREE[0] = 53
BASE_ID[0] = 0
ORB_WISE_IDS[0] = []

# MEAN_MOTION_REV_PER_DAY[1] = 13.4  # Altitude ~1110 km
# ALTITUDE_M[1] = 1110000  # Altitude ~1110 km
# NUM_ORBS[1] = 32
# NUM_SATS_PER_ORB[1] = 50
# INCLINATION_DEGREE[1] = 53.8
# BASE_ID[1] = 1584
# ORB_WISE_IDS[1] = []

# MEAN_MOTION_REV_PER_DAY[2] = 13.35  # Altitude ~1130 km
# ALTITUDE_M[2] = 1130000  # Altitude ~1130 km
# NUM_ORBS[2] = 8
# NUM_SATS_PER_ORB[2] = 50
# INCLINATION_DEGREE[2] = 74
# BASE_ID[2] = 3184
# ORB_WISE_IDS[2] = []

# MEAN_MOTION_REV_PER_DAY[3] = 12.97  # Altitude ~1275 km
# ALTITUDE_M[3] = 1275000  # Altitude ~1275 km
# NUM_ORBS[3] = 5
# NUM_SATS_PER_ORB[3] = 75
# INCLINATION_DEGREE[3] = 81
# BASE_ID[3] = 3584
# ORB_WISE_IDS[3] = []

# MEAN_MOTION_REV_PER_DAY[4] = 12.84  # Altitude ~1325 km
# ALTITUDE_M[4] = 1325000  # Altitude ~1325 km
# NUM_ORBS[4] = 6
# NUM_SATS_PER_ORB[4] = 75
# INCLINATION_DEGREE[4] = 70
# BASE_ID[4] = 3959
# ORB_WISE_IDS[4] = []


"""
# TELESAT
NAME = "Telesat"
SHELL_CNTR = 2

MEAN_MOTION_REV_PER_DAY = [None]*SHELL_CNTR
ALTITUDE_M = [None]*SHELL_CNTR
NUM_ORBS = [None]*SHELL_CNTR
NUM_SATS_PER_ORB = [None]*SHELL_CNTR
INCLINATION_DEGREE = [None]*SHELL_CNTR
BASE_ID = [None]*SHELL_CNTR
ORB_WISE_IDS = [None]*SHELL_CNTR

MEAN_MOTION_REV_PER_DAY[0] = 13.66  # Altitude ~1015 km
ALTITUDE_M[0] = 1015000  # Altitude ~1015 km
NUM_ORBS[0] = 27
NUM_SATS_PER_ORB[0] = 13
INCLINATION_DEGREE[0] = 98.98
BASE_ID[0] = 0
ORB_WISE_IDS[0] = []

MEAN_MOTION_REV_PER_DAY[1] = 12.84  # Altitude ~1325 km
ALTITUDE_M[1] = 1325000  # Altitude ~1325 km
NUM_ORBS[1] = 40
NUM_SATS_PER_ORB[1] = 33
INCLINATION_DEGREE[1] = 50.88
BASE_ID[1] = 351
ORB_WISE_IDS[1] = []
"""

"""
# KUIPER
NAME = "kuiper"
################################################################
# The below constants are taken from Kuiper's FCC filing as below:
# [1]: https://www.itu.int/ITU-R/space/asreceived/Publication/DisplayPublication/8716
################################################################

SHELL_CNTR = 3

MEAN_MOTION_REV_PER_DAY = [None]*SHELL_CNTR
ALTITUDE_M = [None]*SHELL_CNTR
NUM_ORBS = [None]*SHELL_CNTR
NUM_SATS_PER_ORB = [None]*SHELL_CNTR
INCLINATION_DEGREE = [None]*SHELL_CNTR
BASE_ID = [None]*SHELL_CNTR
ORB_WISE_IDS = [None]*SHELL_CNTR

MEAN_MOTION_REV_PER_DAY[0] = 14.80  # Altitude ~630 km
ALTITUDE_M[0] = 630000  # Altitude ~630 km
NUM_ORBS[0] = 34
NUM_SATS_PER_ORB[0] = 34
INCLINATION_DEGREE[0] = 51.9
BASE_ID[0] = 0
ORB_WISE_IDS[0] = []

MEAN_MOTION_REV_PER_DAY[1] = 14.86  # Altitude ~610 km
ALTITUDE_M[1] = 610000  # Altitude ~610 km
NUM_ORBS[1] = 36
NUM_SATS_PER_ORB[1] = 36
INCLINATION_DEGREE[1] = 42
BASE_ID[1] = 1156
ORB_WISE_IDS[1] = []

MEAN_MOTION_REV_PER_DAY[2] = 14.93  # Altitude ~590 km
ALTITUDE_M[2] = 590000  # Altitude ~590 km
NUM_ORBS[2] = 28
NUM_SATS_PER_ORB[2] = 28
INCLINATION_DEGREE[2] = 33
BASE_ID[2] = 2452
ORB_WISE_IDS[2] = []
"""


# General files needed to generate visualizations; Do not change for different simulations
topFile = "../static_html/top.html"
bottomFile = "../static_html/bottom.html"

# Output directory for creating visualization html files
OUT_DIR = "../viz_output/"
# JSON_NAME  = NAME+"_5shell.json"
# OUT_JSON_FILE = OUT_DIR + JSON_NAME
OUT_HTML_FILE = NAME + "_real_tles.html"

# START = Time(EPOCH, scale="tdb")
# END = START + (10*60) * u.second
# sample_points = 10
# extractor = CZMLExtractor(START, END, sample_points)

def read_tles(filename_tles):
    """
    Read a constellation of satellites from the TLES file.

    :param filename_tles:                    Filename of the TLES (typically /path/to/tles.txt)

    :return: Dictionary: {
                    "n_orbits":             Number of orbits
                    "n_sats_per_orbit":     Satellites per orbit
                    "epoch":                Epoch
                    "satellites":           Dictionary of satellite id to
                                            {"ephem_obj_manual": <obj>, "ephem_obj_direct": <obj>}
              }
    """
    satellites = []
    with open(filename_tles, 'r') as f:
        universal_epoch = None
        # i = 0
        for tles_line_1 in f:
            tles_line_2 = f.readline()
            tles_line_3 = f.readline()

            # Retrieve name and identifier
            name = tles_line_1
            # sid = int(name.split()[1])
            # if sid != i:
            #     raise ValueError("Satellite identifier is not increasing by one each line")
            # i += 1

            # Fetch and check the epoch from the TLES data
            # In the TLE, the epoch is given with a Julian data of yyddd.fraction
            # ddd is actually one-based, meaning e.g. 18001 is 1st of January, or 2018-01-01 00:00.
            # As such, to convert it to Astropy Time, we add (ddd - 1) days to it
            # See also: https://www.celestrak.com/columns/v04n03/#FAQ04
            epoch_year = tles_line_2[18:20]
            epoch_day = float(tles_line_2[20:32])
            epoch = Time("20" + epoch_year + "-01-01 00:00:00", scale="tdb") + (epoch_day - 1) * u.day
            # if universal_epoch is None:
            #     universal_epoch = epoch
            # if epoch != universal_epoch:
            #     raise ValueError("The epoch of all TLES must be the same")

            # Finally, store the satellite information
            satellites.append(ephem.readtle(tles_line_1, tles_line_2, tles_line_3))

    return satellites

def generate_orbit_links(sat_objs, raan):
    sats = []
    for j in range(len(sat_objs)):
        if abs(sat_objs[j]._raan - raan) < math.radians(2):
            sats.append((j, sat_objs[j]))

    sats.sort(key = lambda x: float(x[1].sublong))
    links = []
    num_sats = len(sats)
    for i in range(len(sats)):
        sat1 = i
        sat2 = (i + 1) % num_sats
        # print(sats[sat1][1]._raan, sats[sat2][1]._raan, sats[sat1][1]._M, sats[sat2][1]._M)
        links.append((sats[sat1][0], sats[sat2][0]))

    return links
    

def generate_satellite_trajectories():
    """
    Generates and adds satellite orbits to visualization.
    :return: viz_string
    """
    viz_string = ""
    for i in range(0, SHELL_CNTR):
        sat_objs = read_tles("starlink_tles.txt")
        for j in range(len(sat_objs)):
            # if sat_objs[j]._raan > math.radians(5):
            #     continue
            # print(sat_objs[j]._raan)
            sat_objs[j].compute(EPOCH)
            viz_string += "var redSphere = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
                          + str(math.degrees(sat_objs[j].sublong)) + ", " \
                          + str(math.degrees(sat_objs[j].sublat)) + ", " + str(
                550 * 1000) + "), " \
                          + "ellipsoid : {radii : new Cesium.Cartesian3(30000.0, 30000.0, 30000.0), " \
                          + "material : Cesium.Color.BLACK.withAlpha(1),}});\n"

        
        orbit_links = []
        planes = [i for i in range(1, 360, 5)]
        for plane in planes:
            orbit_links.extend(generate_orbit_links(sat_objs, math.radians(plane)))
        
        # print(orbit_links)
        for key in orbit_links:
            sat1, sat2 = key
            viz_string += "viewer.entities.add({name : '', polyline: { positions: Cesium.Cartesian3.fromDegreesArrayHeights([" \
                          + str(math.degrees(sat_objs[sat1].sublong)) + "," \
                          + str(math.degrees(sat_objs[sat1].sublat)) + "," \
                          + str(550 * 1000) + "," \
                          + str(math.degrees(sat_objs[sat2].sublong)) + "," \
                          + str(math.degrees(sat_objs[sat2].sublat)) + "," \
                          + str(550 * 1000) + "]), " \
                          + "width: 0.5, arcType: Cesium.ArcType.NONE, " \
                          + "material: new Cesium.PolylineOutlineMaterialProperty({ " \
                          + "color: Cesium.Color."+COLOR[i]+".withAlpha(0.4), outlineWidth: 0, outlineColor: Cesium.Color.BLACK})}});"
    return viz_string


def write_viz_files():
    """
    Writes JSON and TML files to the output folder
    :return: None
    """
    writer_html = open(OUT_HTML_FILE, 'w')
    with open(topFile, 'r') as fi:
        writer_html.write(fi.read())
    writer_html.write(viz_string)
    with open(bottomFile, 'r') as fb:
        writer_html.write(fb.read())
    writer_html.close()


viz_string = generate_satellite_trajectories()
write_viz_files()