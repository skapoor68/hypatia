import sys
sys.path.append("../../satgenpy")
import satgen
import os
import numpy as np
from sgp4.api import Satrec, jday

NICE_NAME = "Starlink"
NUM_ORBS = 72
NUM_SATS_PER_ORB = 22
INCLINATION_DEGREE = 53
ECCENTRICITY = 0.0000001  # Circular orbits are zero, but pyephem does not permit 0, so lowest possible value
ARG_OF_PERIGEE_DEGREE = 0.0
MEAN_MOTION_REV_PER_DAY = 15.19  # Altitude ~550 km


if __name__ == '__main__':
    np.set_printoptions(threshold=sys.maxsize)

    ground_stations = satgen.read_ground_stations_extended("../satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/ground_stations.txt")

    